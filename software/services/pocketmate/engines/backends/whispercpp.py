"""whisper.cpp ASR backend (§6.2). Uses the `pywhispercpp` binding if present; otherwise falls
back to the `whisper-cli` binary. Model path from settings: /opt/pm/models/asr/<model>.bin.
Not exercised on x86 CI (models are not in the repo); verify on CM5 (latency targets §4)."""
from __future__ import annotations

import asyncio
import shutil
import tempfile
import wave
from collections.abc import AsyncIterator, Sequence

from ..types import (
    AudioChunk,
    AudioFormat,
    EngineError,
    EngineInfo,
    Locality,
    RequestContext,
    TranscriptSegment,
)


class WhisperCppASR:
    def __init__(self, model_path: str = "/opt/pm/models/asr/ggml-small-q5_1.bin", threads: int = 4,
                 language: str = "auto", **_: object) -> None:
        self.model_path, self.threads, self.language = model_path, threads, language
        self._model = None
        self._cli: str | None = None

    def info(self) -> EngineInfo:
        return EngineInfo("whisper.cpp", "binding" if self._model else "cli", Locality.LOCAL, ("en", "hi"), 30_000)

    async def load(self) -> None:
        try:
            from pywhispercpp.model import Model  # type: ignore[import-not-found]
            self._model = await asyncio.to_thread(Model, self.model_path, n_threads=self.threads)
            return
        except ImportError:
            pass
        self._cli = shutil.which("whisper-cli") or shutil.which("whisper-cpp")
        if not self._cli:
            raise EngineError("whisper.cpp not installed (pywhispercpp or whisper-cli)")

    async def unload(self) -> None:
        self._model = None

    async def health(self) -> bool:
        return self._model is not None or self._cli is not None

    async def transcribe(self, ctx: RequestContext, fmt: AudioFormat, pcm: bytes,
                         language_hint: Sequence[str] = ("en", "hi")) -> list[TranscriptSegment]:
        lang = self.language if len(language_hint) != 1 else language_hint[0]
        if self._model is not None:
            import numpy as np  # type: ignore[import-not-found]
            audio = np.frombuffer(pcm, dtype=np.int16).astype("float32") / 32768.0
            segs = await asyncio.to_thread(self._model.transcribe, audio, language=lang)
            return [TranscriptSegment(s.text.strip(), int(s.t0 * 10), int(s.t1 * 10), True, 0.8, lang)
                    for s in segs]
        if self._cli is None:
            raise EngineError("not loaded")
        with tempfile.NamedTemporaryFile(suffix=".wav", dir="/run/pm" if _isdir("/run/pm") else None) as f:
            with wave.open(f.name, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(fmt.sample_rate)
                w.writeframes(pcm)
            proc = await asyncio.create_subprocess_exec(
                self._cli, "-m", self.model_path, "-t", str(self.threads), "-l", lang, "-nt", "-f", f.name,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
            out, _ = await proc.communicate()
            # audio file is deleted on context exit (P6: audio is never persisted)
        if proc.returncode:
            raise EngineError(f"whisper-cli exit {proc.returncode}")
        dur = len(pcm) * 1000 // (2 * fmt.sample_rate)
        return [TranscriptSegment(out.decode().strip(), 0, dur, True, 0.8, lang)]

    async def stream(self, ctx: RequestContext, fmt: AudioFormat, audio: AsyncIterator[AudioChunk],
                     language_hint: Sequence[str] = ("en", "hi")) -> AsyncIterator[TranscriptSegment]:
        # MVP: buffer the PTT utterance (<=120 s) in RAM, transcribe on release. Partial
        # hypotheses (streaming whisper with VAD windows) are a TODO.
        buf = bytearray()
        async for ch in audio:
            buf += ch.pcm
            if ch.is_last:
                break
        for seg in await self.transcribe(ctx, fmt, bytes(buf), language_hint):
            yield seg
        buf[:] = b"\x00" * len(buf)


def _isdir(p: str) -> bool:
    import os
    return os.path.isdir(p)
