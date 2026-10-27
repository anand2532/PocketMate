"""Piper TTS backend (§6.5): runs the `piper` binary with --output-raw and streams PCM.
Voices from /opt/pm/models/tts/*.onnx (+ .onnx.json). Not exercised on x86 CI."""
from __future__ import annotations

import asyncio
import json
import shutil
from collections.abc import AsyncIterator
from pathlib import Path

from ..types import AudioChunk, EngineError, EngineInfo, Locality, RequestContext, Voice


class PiperTTS:
    def __init__(self, voice_dir: str = "/opt/pm/models/tts", default_voice: str | None = None, **_: object) -> None:
        self.voice_dir = Path(voice_dir)
        self.default_voice = default_voice
        self._bin: str | None = None

    def info(self) -> EngineInfo:
        return EngineInfo("piper", "cli", Locality.LOCAL, tuple(sorted({v.language for v in self.voices()})))

    async def load(self) -> None:
        self._bin = shutil.which("piper")
        if not self._bin:
            raise EngineError("piper binary not found")

    async def unload(self) -> None:
        pass

    async def health(self) -> bool:
        return self._bin is not None

    def voices(self) -> list[Voice]:
        out = []
        for cfg in sorted(self.voice_dir.glob("*.onnx.json")):
            try:
                j = json.loads(cfg.read_text())
                lang = j.get("language", {}).get("code", "en")
                sr = j.get("audio", {}).get("sample_rate", 22050)
            except (OSError, ValueError):
                continue
            out.append(Voice(cfg.name.removesuffix(".onnx.json"), lang, sr))
        return out

    async def synthesize(self, ctx: RequestContext, text: str, voice: Voice,
                         rate: float = 1.0) -> AsyncIterator[AudioChunk]:
        """Sentence-chunked: one piper run per call; PCM s16le at voice.sample_rate."""
        if not self._bin:
            raise EngineError("not loaded")
        v = voice.id
        proc = await asyncio.create_subprocess_exec(
            self._bin, "--model", str(self.voice_dir / f"{v}.onnx"), "--output-raw",
            "--length_scale", f"{1.0 / max(rate, 0.1):.2f}",
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
        assert proc.stdin and proc.stdout
        proc.stdin.write(text.encode() + b"\n")
        await proc.stdin.drain()
        proc.stdin.close()
        seq, t_ms = 0, 0
        while chunk := await proc.stdout.read(4096):
            yield AudioChunk(chunk, seq, t_ms)
            seq += 1
            t_ms += len(chunk) * 1000 // (2 * voice.sample_rate)
        await proc.wait()
        yield AudioChunk(b"", seq, t_ms, True)
