"""Async MCU link: seq/ACK/retry (50 ms x3), event dispatch with ACK, heartbeat (§11)."""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

from .frame import Deframer, Frame
from .messages import (
    ACK_TIMEOUT_S,
    BY_NAME,
    HEARTBEAT_PERIOD_S,
    MAX_RETRIES,
    PREAMBLE_GAP_S,
    Message,
    Status,
    msg,
)
from .transport import Transport

log = logging.getLogger("pm.mcu")

EventHandler = Callable[[Message], Awaitable[None] | None]


class LinkDown(RuntimeError):
    pass


class Nak(RuntimeError):
    def __init__(self, name: str, status: Status) -> None:
        super().__init__(f"{name} NAK {status.name}")
        self.status = status


class McuLink:
    def __init__(self, transport: Transport, *, ack_timeout: float = ACK_TIMEOUT_S,
                 retries: int = MAX_RETRIES, preamble_gap: float = PREAMBLE_GAP_S) -> None:
        self.t = transport
        self.ack_timeout = ack_timeout
        self.retries = retries
        self.preamble_gap = preamble_gap
        self._seq = 0
        self._pending: dict[int, asyncio.Future[Message]] = {}
        self._handlers: list[EventHandler] = []
        self._send_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()
        self._rx_task: asyncio.Task[None] | None = None
        self._hb_task: asyncio.Task[None] | None = None
        # Events are dispatched from a separate task so a handler may itself call request()
        # (e.g. PTT abort -> MIC_ENABLE off) without deadlocking the rx loop that reads the ACK.
        self._evt_q: asyncio.Queue[Message] = asyncio.Queue()
        self._evt_task: asyncio.Task[None] | None = None
        self._last_evt_seq: int | None = None
        self.deframer = Deframer()
        self.up = False
        self.stats = {"tx": 0, "rx": 0, "retries": 0, "naks": 0, "dup": 0}
        self._t0 = time.monotonic()

    def on_event(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    async def start(self) -> None:
        self._rx_task = asyncio.create_task(self._rx_loop())
        self._evt_task = asyncio.create_task(self._evt_loop())
        self.up = True

    async def stop(self) -> None:
        for t in (self._hb_task, self._rx_task, self._evt_task):
            if t:
                t.cancel()
        for t in (self._hb_task, self._rx_task):
            if t:
                try:
                    await t
                except (asyncio.CancelledError, Exception):
                    pass

    def start_heartbeat(self, state_fn: Callable[[], int] = lambda: 0,
                        period: float = HEARTBEAT_PERIOD_S) -> None:
        async def _hb() -> None:
            while True:
                try:
                    await self.send(msg("HEARTBEAT", uptime_s=int(time.monotonic() - self._t0),
                                        cm5_state=state_fn()))
                except (LinkDown, Nak) as e:
                    log.warning("heartbeat failed: %s", e)
                await asyncio.sleep(period)
        self._hb_task = asyncio.create_task(_hb())

    def _next_seq(self) -> int:
        self._seq = (self._seq + 1) & 0xFF
        return self._seq

    async def _write_frame(self, f: Frame) -> None:
        async with self._write_lock:
            await self.t.write(b"\x00")
            if self.preamble_gap:
                await asyncio.sleep(self.preamble_gap)
            await self.t.write(f.encode())
            self.stats["tx"] += 1

    async def send(self, m: Message) -> Message:
        """Send a command; returns the ACK message. Raises Nak on a non-OK status, LinkDown after retries."""
        async with self._send_lock:
            seq = self._next_seq()
            f = Frame.from_message(m, seq)
            loop = asyncio.get_running_loop()
            for attempt in range(self.retries + 1):
                fut: asyncio.Future[Message] = loop.create_future()
                self._pending[seq] = fut
                await self._write_frame(f)
                try:
                    ack = await asyncio.wait_for(fut, self.ack_timeout)
                except TimeoutError:
                    self.stats["retries"] += attempt < self.retries
                    continue
                finally:
                    self._pending.pop(seq, None)
                self.up = True
                st = Status(ack.fields["status"])
                if st != Status.OK:
                    self.stats["naks"] += 1
                    raise Nak(m.name, st)
                return ack
            self.up = False
            raise LinkDown(f"{m.name}: no ACK after {self.retries} retries")

    async def _rx_loop(self) -> None:
        while True:
            data = await self.t.read()
            for f in self.deframer.feed(data):
                self.stats["rx"] += 1
                try:
                    m = f.message()
                except (KeyError, ValueError):
                    await self._ack(f.seq, Status.UNKNOWN_TYPE if f.type_id not in _IDS else Status.BAD_LEN)
                    continue
                if m.name == "ACK":
                    fut = self._pending.get(m.fields["acked_seq"])
                    if fut and not fut.done():
                        fut.set_result(m)
                    continue
                await self._ack(f.seq, Status.OK)
                if self._last_evt_seq == f.seq:
                    self.stats["dup"] += 1      # retransmission of an event we already handled
                    continue
                self._last_evt_seq = f.seq
                self._evt_q.put_nowait(m)

    async def _evt_loop(self) -> None:
        while True:
            m = await self._evt_q.get()
            for h in self._handlers:
                try:
                    r = h(m)
                    if asyncio.iscoroutine(r):
                        await r
                except Exception:
                    log.exception("event handler failed for %s", m.name)

    async def _ack(self, seq: int, status: Status) -> None:
        f = Frame.from_message(msg("ACK", acked_seq=seq, status=int(status)), seq)
        await self._write_frame(f)


_IDS = {d.type_id for d in BY_NAME.values()}
