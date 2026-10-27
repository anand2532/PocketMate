"""llama.cpp backend: talks to `llama-server` (one process per model, systemd pm-llm.service)
over a Unix socket at /run/pm/llm.sock with the OpenAI-compatible API (§6.3).

VERIFY on target: llama-server Unix-socket binding (`--host /run/pm/llm.sock`) depends on the
llama.cpp build shipped in the image; TCP 127.0.0.1 is the fallback (`base` = "tcp://127.0.0.1:8080"),
which nftables still confines to loopback for UID pm-llm.
"""
from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Sequence

from ..types import (
    ChatMessage,
    EngineError,
    EngineInfo,
    GenParams,
    Locality,
    RequestContext,
    TokenDelta,
)


async def _open(base: str) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    if base.startswith("tcp://"):
        host, _, port = base[6:].partition(":")
        return await asyncio.open_connection(host, int(port or 8080))
    return await asyncio.open_unix_connection(base)


async def _request(base: str, method: str, path: str, body: dict | None,
                   ) -> tuple[int, asyncio.StreamReader, asyncio.StreamWriter]:
    r, w = await _open(base)
    data = json.dumps(body).encode() if body is not None else b""
    w.write(f"{method} {path} HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\n"
            f"Content-Length: {len(data)}\r\nConnection: close\r\n\r\n".encode() + data)
    await w.drain()
    status_line = await r.readline()
    try:
        status = int(status_line.split()[1])
    except (IndexError, ValueError) as e:
        w.close()
        raise EngineError(f"bad HTTP response {status_line!r}") from e
    while (await r.readline()) not in (b"\r\n", b"\n", b""):
        pass
    return status, r, w


class LlamaCppLLM:
    def __init__(self, base: str = "/run/pm/llm.sock", model: str = "local", ctx: int = 4096, **_: object) -> None:
        self.base, self.model, self.ctx = base, model, ctx
        self._ok = False

    def info(self) -> EngineInfo:
        return EngineInfo("llama.cpp", "server", Locality.LOCAL, ("en", "hi", "hi-Latn"), self.ctx)

    async def load(self) -> None:
        self._ok = await self.health()
        if not self._ok:
            raise EngineError(f"llama-server not reachable at {self.base}", retryable=True)

    async def unload(self) -> None:
        self._ok = False

    async def health(self) -> bool:
        try:
            st, _r, w = await asyncio.wait_for(_request(self.base, "GET", "/health", None), 1.0)
            w.close()
            return st == 200
        except (TimeoutError, OSError, EngineError):
            return False

    async def generate(self, ctx: RequestContext, messages: Sequence[ChatMessage],
                       params: GenParams = GenParams()) -> AsyncIterator[TokenDelta]:
        body: dict = {
            "model": self.model, "stream": True, "max_tokens": params.max_tokens,
            "temperature": params.temperature, "top_p": params.top_p,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        if params.stop:
            body["stop"] = list(params.stop)
        if params.seed is not None:
            body["seed"] = params.seed
        if params.json_schema:
            body["response_format"] = {"type": "json_object", "schema": params.json_schema}
        st, r, w = await _request(self.base, "POST", "/v1/chat/completions", body)
        try:
            if st != 200:
                raise EngineError(f"llama-server HTTP {st}", retryable=st >= 500)
            async for line in _iter_lines(r):
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                ev = json.loads(payload)
                ch = (ev.get("choices") or [{}])[0]
                delta = (ch.get("delta") or {}).get("content") or ""
                fr = ch.get("finish_reason")
                yield TokenDelta(delta, fr, ev.get("usage"))
        finally:
            w.close()

    async def count_tokens(self, text: str) -> int:
        try:
            st, r, w = await _request(self.base, "POST", "/tokenize", {"content": text})
            body = await r.read()
            w.close()
            if st == 200:
                return len(json.loads(body)["tokens"])
        except (OSError, ValueError, KeyError, EngineError):
            pass
        return max(1, len(text) // 3)

    @property
    def context_window(self) -> int:
        return self.ctx


class LlamaCppEmbedding:
    def __init__(self, base: str = "/run/pm/embed.sock", dim: int = 384, **_: object) -> None:
        self.base, self.dim = base, dim

    def info(self) -> EngineInfo:
        return EngineInfo("llama.cpp-embed", "server", Locality.LOCAL, ("en", "hi"), 512)

    async def load(self) -> None:
        pass

    async def unload(self) -> None:
        pass

    async def health(self) -> bool:
        return True

    async def embed(self, ctx: RequestContext, texts: Sequence[str]) -> list[list[float]]:
        st, r, w = await _request(self.base, "POST", "/v1/embeddings", {"input": list(texts)})
        try:
            body = await r.read()
        finally:
            w.close()
        if st != 200:
            raise EngineError(f"embed HTTP {st}")
        text = body.decode()
        if "\r\n" in text and text[:1].isalnum() and not text.startswith("{"):
            text = _dechunk(text)
        return [d["embedding"] for d in json.loads(text)["data"]]


async def _iter_lines(r: asyncio.StreamReader) -> AsyncIterator[str]:
    # tolerate chunked transfer-encoding: chunk-size lines are skipped because they don't start with "data:"
    while True:
        line = await r.readline()
        if not line:
            return
        yield line.decode(errors="replace").strip()


def _dechunk(text: str) -> str:
    out, rest = [], text
    while rest:
        size_s, _, rest = rest.partition("\r\n")
        size = int(size_s or "0", 16)
        if size == 0:
            break
        out.append(rest[:size])
        rest = rest[size + 2:]
    return "".join(out)
