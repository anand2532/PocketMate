"""Deterministic stub engines: tests, UI demo, and the 'engine missing' fallback.
They never touch the network or hardware."""
from __future__ import annotations

import asyncio
import hashlib
import math
from collections.abc import AsyncIterator, Sequence

from ..types import (
    AudioChunk,
    AudioFormat,
    ChatMessage,
    EngineInfo,
    GenParams,
    ImageRef,
    Locality,
    OCRBlock,
    OCRResult,
    RequestContext,
    TokenDelta,
    TranscriptSegment,
    TranslationSegment,
    VisionAnswer,
    Voice,
)


class _Base:
    NAME = "stub"

    def __init__(self, **_: object) -> None:
        self.loaded = False

    async def load(self) -> None:
        self.loaded = True

    async def unload(self) -> None:
        self.loaded = False

    async def health(self) -> bool:
        return True

    def info(self) -> EngineInfo:
        return EngineInfo(self.NAME, "0", Locality.LOCAL, ("en", "hi", "hi-en"), None)


class StubASR(_Base):
    """Returns `script` as the transcript once the audio stream ends."""
    NAME = "stub-asr"

    def __init__(self, script: str = "remind me to call mom kal subah 9 baje", **kw: object) -> None:
        super().__init__(**kw)
        self.script = script

    async def stream(self, ctx: RequestContext, fmt: AudioFormat, audio: AsyncIterator[AudioChunk],
                     language_hint: Sequence[str] = ("en", "hi")) -> AsyncIterator[TranscriptSegment]:
        n, last_ms = 0, 0
        words = self.script.split()
        async for ch in audio:
            n += 1
            last_ms = ch.t_start_ms + len(ch.pcm) * 1000 // (2 * fmt.sample_rate)
            if n % 10 == 0:
                yield TranscriptSegment(" ".join(words[: n // 10]), 0, last_ms, False, 0.5, "hi-en", "Latn")
            if ch.is_last:
                break
        yield TranscriptSegment(self.script, 0, last_ms, True, 0.9, "hi-en", "Latn")

    async def transcribe(self, ctx: RequestContext, fmt: AudioFormat, pcm: bytes,
                         language_hint: Sequence[str] = ("en", "hi")) -> list[TranscriptSegment]:
        dur = len(pcm) * 1000 // (2 * fmt.sample_rate)
        return [TranscriptSegment(self.script, 0, dur, True, 0.9, "hi-en", "Latn")]


class StubLLM(_Base):
    NAME = "stub-llm"

    def __init__(self, reply: str | None = None, **kw: object) -> None:
        super().__init__(**kw)
        self.reply = reply

    async def generate(self, ctx: RequestContext, messages: Sequence[ChatMessage],
                       params: GenParams = GenParams()) -> AsyncIterator[TokenDelta]:
        text = self.reply if self.reply is not None else f"(stub) {messages[-1].content[:120] if messages else ''}"
        words = text.split(" ")[: params.max_tokens]
        for i, w in enumerate(words):
            await asyncio.sleep(0)
            yield TokenDelta(w + ("" if i == len(words) - 1 else " "))
        yield TokenDelta("", "stop", {"prompt_tokens": sum(len(m.content) // 4 for m in messages),
                                      "completion_tokens": len(words)})

    async def count_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    @property
    def context_window(self) -> int:
        return 4096


class StubEmbedding(_Base):
    NAME = "stub-embed"
    dim = 32

    async def embed(self, ctx: RequestContext, texts: Sequence[str]) -> list[list[float]]:
        out = []
        for t in texts:
            h = hashlib.sha256(t.encode()).digest()
            v = [(h[i % 32] - 128) / 128 for i in range(self.dim)]
            n = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / n for x in v])
        return out


class StubOCR(_Base):
    NAME = "stub-ocr"

    def __init__(self, text: str = "Paracetamol 500 mg\nदिन में दो बार", **kw: object) -> None:
        super().__init__(**kw)
        self.text = text

    async def recognize(self, ctx: RequestContext, image: ImageRef, langs: Sequence[str] = ("en", "hi"),
                        mode: str = "document") -> OCRResult:
        blocks = tuple(OCRBlock(line, (0, 40 * i, image.width, 40 * i + 36), 0.9,
                                script="Deva" if any("\u0900" <= c <= "\u097f" for c in line) else "Latn")
                       for i, line in enumerate(self.text.splitlines()))
        return OCRResult(blocks, self.text, "hi", 5)


class StubTTS(_Base):
    NAME = "stub-tts"

    def voices(self) -> Sequence[Voice]:
        return [Voice("stub-en", "en", 22050), Voice("stub-hi", "hi", 22050)]

    async def synthesize(self, ctx: RequestContext, text: str, voice: Voice,
                         rate: float = 1.0) -> AsyncIterator[AudioChunk]:
        t = 0
        for seq, sentence in enumerate(s for s in text.replace("।", ".").split(".") if s.strip()):
            ms = int(60 * len(sentence) / rate)
            yield AudioChunk(b"\x00\x00" * (voice.sample_rate * ms // 1000), seq, t)
            t += ms
        yield AudioChunk(b"", 10_000, t, True)


class StubVision(_Base):
    NAME = "stub-vision"

    async def describe(self, ctx: RequestContext, image: ImageRef, prompt: str | None = None) -> VisionAnswer:
        return VisionAnswer(f"(stub) an image {image.width}x{image.height}")


class StubTranslate(_Base):
    NAME = "stub-translate"

    def pairs(self) -> Sequence[tuple[str, str]]:
        return [("hi", "en"), ("en", "hi")]

    async def translate(self, ctx: RequestContext, texts: Sequence[str], src_lang: str | None,
                        tgt_lang: str) -> list[TranslationSegment]:
        return [TranslationSegment(t, f"[{tgt_lang}] {t}", src_lang or "hi", tgt_lang, None, 0.5) for t in texts]

    async def translate_stream(self, ctx: RequestContext, texts: Sequence[str], src_lang: str | None,
                               tgt_lang: str) -> AsyncIterator[TranslationSegment]:
        for seg in await self.translate(ctx, texts, src_lang, tgt_lang):
            yield seg
