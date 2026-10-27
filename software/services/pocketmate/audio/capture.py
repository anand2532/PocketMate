"""Capture sources. SimCapture runs anywhere; AlsaCapture needs the real codec (hardware-only)."""
from __future__ import annotations

import asyncio
import math
import shutil
import struct
import wave
from pathlib import Path
from typing import Protocol

from ..engines.types import AudioFormat

FRAME_MS = 20


def frame_bytes(fmt: AudioFormat, ms: int = FRAME_MS) -> int:
    bps = 2 if fmt.sample_fmt == "s16le" else 4
    return fmt.sample_rate * ms // 1000 * bps * fmt.channels


class CaptureSource(Protocol):
    is_open: bool
    async def open(self, fmt: AudioFormat) -> None: ...
    async def read_frame(self) -> bytes: ...
    async def close(self) -> None: ...


class SimCapture:
    """20 ms frames from a WAV file (16 kHz mono s16le) or a 440 Hz tone, paced in real time (pace=False: fast)."""

    def __init__(self, wav: str | Path | None = None, *, pace: bool = True) -> None:
        self.wav, self.pace = wav, pace
        self.is_open = False
        self.opens = 0
        self._pcm = b""
        self._pos = 0
        self._fb = 640

    async def open(self, fmt: AudioFormat) -> None:
        self._fb = frame_bytes(fmt)
        if self.wav:
            with wave.open(str(self.wav)) as w:
                self._pcm = w.readframes(w.getnframes())
        else:
            n = fmt.sample_rate
            self._pcm = b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / n)))
                                 for i in range(n))
        self._pos = 0
        self.is_open = True
        self.opens += 1

    async def read_frame(self) -> bytes:
        if not self.is_open:
            raise OSError("capture closed")
        if self.pace:
            await asyncio.sleep(FRAME_MS / 1000)
        else:
            await asyncio.sleep(0)
        chunk = self._pcm[self._pos:self._pos + self._fb]
        self._pos = (self._pos + self._fb) % max(len(self._pcm), 1)
        return chunk.ljust(self._fb, b"\x00")

    async def close(self) -> None:
        self.is_open = False


class AlsaCapture:
    """arecord-based capture of the PCM card (HARDWARE-ONLY; card name per cm5-config / dts overlay - VERIFY).
    Killing the process closes the ALSA PCM immediately, which is what the 20 ms mute-close budget relies on."""

    def __init__(self, device: str = "plughw:CARD=pocketmate,DEV=0") -> None:
        self.device = device
        self.is_open = False
        self._proc: asyncio.subprocess.Process | None = None
        self._fb = 640

    async def open(self, fmt: AudioFormat) -> None:
        exe = shutil.which("arecord")
        if not exe:
            raise OSError("arecord not installed (alsa-utils)")
        self._fb = frame_bytes(fmt)
        self._proc = await asyncio.create_subprocess_exec(
            exe, "-q", "-D", self.device, "-f", "S16_LE" if fmt.sample_fmt == "s16le" else "FLOAT_LE",
            "-r", str(fmt.sample_rate), "-c", str(fmt.channels), "-t", "raw", "--buffer-time=20000",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        self.is_open = True

    async def read_frame(self) -> bytes:
        if not self._proc or not self._proc.stdout:
            raise OSError("capture closed")
        return await self._proc.stdout.readexactly(self._fb)

    async def close(self) -> None:
        if self._proc and self._proc.returncode is None:
            self._proc.kill()
            await self._proc.wait()
        self._proc = None
        self.is_open = False
