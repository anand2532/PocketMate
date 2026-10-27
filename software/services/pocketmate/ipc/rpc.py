"""Tiny async RPC + signals over framed Unix sockets.
Request {id, method, params}; reply {id, result} | {id, error:{type,msg}}; signal {signal, args}."""
from __future__ import annotations

import asyncio
import contextlib
import logging
import os
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from .framing import FrameError, read_frame, write_frame

log = logging.getLogger("pm.ipc")
Handler = Callable[..., Awaitable[Any] | Any]


class RpcError(Exception):
    def __init__(self, type_: str, msg: str) -> None:
        super().__init__(f"{type_}: {msg}")
        self.type = type_


class RpcServer:
    def __init__(self, path: str | Path, *, mode: int = 0o660) -> None:
        self.path, self.mode = str(path), mode
        self.methods: dict[str, Handler] = {}
        self._clients: set[asyncio.StreamWriter] = set()
        self._server: asyncio.base_events.Server | None = None

    def method(self, name: str) -> Callable[[Handler], Handler]:
        def deco(f: Handler) -> Handler:
            self.methods[name] = f
            return f
        return deco

    async def start(self) -> None:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(self.path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._server = await asyncio.start_unix_server(self._serve, self.path)
        os.chmod(self.path, self.mode)

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        for w in list(self._clients):
            w.close()
        with contextlib.suppress(FileNotFoundError):
            os.unlink(self.path)

    async def emit(self, signal: str, **args: Any) -> None:
        for w in list(self._clients):
            try:
                await write_frame(w, {"signal": signal, "args": args})
            except (ConnectionError, RuntimeError):
                self._clients.discard(w)

    async def _serve(self, r: asyncio.StreamReader, w: asyncio.StreamWriter) -> None:
        self._clients.add(w)
        try:
            while True:
                req = await read_frame(r)
                rid, name = req.get("id"), req.get("method")
                f = self.methods.get(name)
                try:
                    if f is None:
                        raise RpcError("NoSuchMethod", str(name))
                    res = f(**(req.get("params") or {}))
                    if asyncio.iscoroutine(res):
                        res = await res
                    await write_frame(w, {"id": rid, "result": res})
                except Exception as e:  # noqa: BLE001 - errors are returned to the caller
                    await write_frame(w, {"id": rid, "error": {"type": getattr(e, "type", type(e).__name__),
                                                                "msg": str(e)}})
        except (asyncio.IncompleteReadError, ConnectionError, FrameError):
            pass
        finally:
            self._clients.discard(w)
            w.close()


class RpcClient:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._r: asyncio.StreamReader | None = None
        self._w: asyncio.StreamWriter | None = None
        self._id = 0
        self._pending: dict[int, asyncio.Future[Any]] = {}
        self._signals: list[Callable[[str, dict], Any]] = []
        self._task: asyncio.Task[None] | None = None

    async def connect(self) -> None:
        self._r, self._w = await asyncio.open_unix_connection(self.path)
        self._task = asyncio.create_task(self._rx())

    def on_signal(self, cb: Callable[[str, dict], Any]) -> None:
        self._signals.append(cb)

    async def call(self, method: str, timeout: float = 10.0, **params: Any) -> Any:
        assert self._w is not None, "not connected"
        self._id += 1
        fut: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        self._pending[self._id] = fut
        await write_frame(self._w, {"id": self._id, "method": method, "params": params})
        return await asyncio.wait_for(fut, timeout)

    async def _rx(self) -> None:
        assert self._r is not None
        try:
            while True:
                m = await read_frame(self._r)
                if "signal" in m:
                    for cb in self._signals:
                        r = cb(m["signal"], m.get("args") or {})
                        if asyncio.iscoroutine(r):
                            await r
                    continue
                fut = self._pending.pop(m.get("id"), None)
                if fut and not fut.done():
                    if "error" in m:
                        fut.set_exception(RpcError(m["error"]["type"], m["error"]["msg"]))
                    else:
                        fut.set_result(m.get("result"))
        except (asyncio.IncompleteReadError, ConnectionError):
            for fut in self._pending.values():
                if not fut.done():
                    fut.set_exception(ConnectionError("server closed"))

    async def close(self) -> None:
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        if self._w:
            self._w.close()
