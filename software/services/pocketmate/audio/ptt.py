"""PTT session control.

Rules (§5.1, §8.2, §13 P1/P3):
- capture opens ONLY inside a PTT session the MCU accepted (ACK to MIC_ENABLE + EVT_MIC_RAIL{on});
- refuse to start while muted or while mute status is invalid ("Mic off (hardware)");
- mute (or rail off) mid-session: close capture within 20 ms and DISCARD the partial buffer;
  no frame captured after the edge is delivered to ASR.
The MIC_ENABLE path is injected: production -> pm-power over IPC; tests -> McuLink directly."""
from __future__ import annotations

import asyncio
import enum
import logging
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field

from ..engines.types import AudioChunk, AudioFormat
from ..mcu.messages import MicMode, Status
from .capture import CaptureSource

log = logging.getLogger("pm.audio")

RAIL_ON_TIMEOUT_S = 0.5
CAPS_S = {MicMode.HOLD: 120, MicMode.TAP: 120, MicMode.DICTATION: 600}


class Refusal(enum.Enum):
    MUTED = "Mic is muted, slide the switch to talk"
    MUTE_INVALID = "Mic off (hardware)"
    NO_PTT = "Hold the button to talk"
    MCU_DOWN = "Mic unavailable"
    BUSY = "Already listening"
    RAIL_TIMEOUT = "Mic didn't power up"


class CaptureRefused(Exception):
    def __init__(self, why: Refusal, status: Status | None = None) -> None:
        super().__init__(why.value)
        self.why, self.status = why, status


@dataclass
class MuteState:
    muted: bool = True        # fail closed until the first EVT_MIC_MUTE / GPIO read
    valid: bool = False


@dataclass
class SessionResult:
    session_id: int
    frames: int
    discarded: bool
    end_reason: str
    close_latency_ms: float | None = None
    edge_ms: int | None = None


@dataclass
class _Session:
    sid: int
    mode: MicMode
    queue: asyncio.Queue[AudioChunk | None] = field(default_factory=asyncio.Queue)
    frames: int = 0
    task: asyncio.Task[None] | None = None
    end_reason: str = ""
    discarded: bool = False
    close_latency_ms: float | None = None
    edge_ms: int | None = None


MicEnable = Callable[[bool, int, int, int], Awaitable[Status]]


class PttController:
    def __init__(self, capture: CaptureSource, mic_enable: MicEnable, *, fmt: AudioFormat = AudioFormat(),
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.capture, self.mic_enable, self.fmt, self.clock = capture, mic_enable, fmt, clock
        self.mute = MuteState()
        self._sid = 0
        self._s: _Session | None = None
        self._rail_on = asyncio.Event()
        self._t0 = clock()
        self.frame_counter = 0          # §15 PR2 check: must stay 0 across muted PTT attempts

    def _now_ms(self) -> int:
        return int((self.clock() - self._t0) * 1000)

    @property
    def active(self) -> bool:
        return self._s is not None

    # ---- MCU events (wire to McuLink.on_event) --------------------------------
    async def on_mcu_event(self, m) -> None:
        if m.name == "EVT_MIC_MUTE":
            await self.on_mute(bool(m.fields["muted"]), bool(m.fields["valid"]))
        elif m.name == "EVT_MIC_RAIL":
            if m.fields["on"]:
                if self._s and m.fields["session_id"] == self._s.sid:
                    self._rail_on.set()
            elif self._s and m.fields["session_id"] == self._s.sid:
                await self._abort(f"rail_off:{m.fields['reason']}")

    async def on_mute(self, muted: bool, valid: bool = True) -> None:
        self.mute = MuteState(muted, valid)
        if (muted or not valid) and self._s:
            await self._abort("mute" if muted else "mute_invalid")

    # ---- session API ------------------------------------------------------------
    async def start(self, mode: MicMode = MicMode.HOLD, max_s: int = 0) -> AsyncIterator[AudioChunk]:
        if self._s:
            raise CaptureRefused(Refusal.BUSY)
        if not self.mute.valid:
            raise CaptureRefused(Refusal.MUTE_INVALID)
        if self.mute.muted:
            raise CaptureRefused(Refusal.MUTED)
        self._sid = (self._sid % 0xFFFF) + 1
        s = _Session(self._sid, mode)
        self._s = s
        self._rail_on.clear()
        st = await self._mic(True, s.sid, int(mode), min(max_s or CAPS_S[mode], CAPS_S[mode]))
        if st != Status.OK:
            self._s = None
            raise CaptureRefused({Status.MUTED: Refusal.MUTED, Status.MUTE_INVALID: Refusal.MUTE_INVALID,
                                  Status.NO_PTT: Refusal.NO_PTT}.get(st, Refusal.MCU_DOWN), st)
        try:
            await asyncio.wait_for(self._rail_on.wait(), RAIL_ON_TIMEOUT_S)
        except TimeoutError:
            await self._mic(False, s.sid, int(mode), 0)
            self._s = None
            raise CaptureRefused(Refusal.RAIL_TIMEOUT) from None
        if self._s is not s:                       # aborted (mute) while waiting for the rail
            raise CaptureRefused(Refusal.MUTED)
        await self.capture.open(self.fmt)
        s.task = asyncio.create_task(self._pump(s))
        return self._iter(s)

    async def _mic(self, on: bool, sid: int, mode: int, max_s: int) -> Status:
        try:
            return await self.mic_enable(on, sid, mode, max_s)
        except Exception as e:      # LinkDown etc.
            log.warning("MIC_ENABLE failed: %s", e)
            return Status.CM5_DOWN

    async def _pump(self, s: _Session) -> None:
        seq = 0
        try:
            while True:
                t = self._now_ms()
                pcm = await self.capture.read_frame()
                if self._s is not s:          # edge happened while we were blocked: drop it
                    return
                self.frame_counter += 1
                s.frames += 1
                await s.queue.put(AudioChunk(pcm, seq, t))
                seq += 1
        except (OSError, asyncio.IncompleteReadError):
            if self._s is s:
                await self._abort("capture_error")
        except asyncio.CancelledError:
            pass

    async def _iter(self, s: _Session) -> AsyncIterator[AudioChunk]:
        while True:
            c = await s.queue.get()
            if c is None:
                return
            yield c

    async def stop(self) -> SessionResult | None:
        """Normal release: deliver buffered frames, then is_last."""
        s = self._s
        if not s:
            return None
        self._s = None
        await self._close(s)
        await self._mic(False, s.sid, int(s.mode), 0)
        s.end_reason = "release"
        await s.queue.put(AudioChunk(b"", s.frames, self._now_ms(), True))
        await s.queue.put(None)
        return SessionResult(s.sid, s.frames, False, "release")

    async def _abort(self, reason: str) -> SessionResult:
        """Mute / rail-off edge: close capture first, then discard everything not yet consumed."""
        s = self._s
        assert s is not None
        self._s = None
        t_edge = self.clock()
        s.edge_ms = self._now_ms()
        await self._close(s)
        s.close_latency_ms = (self.clock() - t_edge) * 1000
        while not s.queue.empty():
            s.queue.get_nowait()
        s.discarded = True
        s.end_reason = reason
        await s.queue.put(None)
        await self._mic(False, s.sid, int(s.mode), 0)
        self.last_abort = SessionResult(s.sid, s.frames, True, reason, s.close_latency_ms, s.edge_ms)
        log.info("capture aborted (%s) in %.1f ms; partial buffer discarded", reason, s.close_latency_ms)
        return self.last_abort

    async def _close(self, s: _Session) -> None:
        if s.task:
            s.task.cancel()
            try:
                await s.task
            except asyncio.CancelledError:
                pass
        await self.capture.close()


def link_mic_enable(link) -> MicEnable:
    """Adapter: MIC_ENABLE over an McuLink (pm-power owns the link in production)."""
    from ..mcu.link import Nak
    from ..mcu.messages import msg

    async def _f(on: bool, sid: int, mode: int, max_s: int) -> Status:
        try:
            await link.send(msg("MIC_ENABLE", on=int(on), session_id=sid, mode=mode, max_s=max_s))
        except Nak as e:
            return e.status
        return Status.OK
    return _f


