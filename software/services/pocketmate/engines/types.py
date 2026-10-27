"""Engine contracts, verbatim from ARCHITECTURE.md §6.1-§6.8 (field names, defaults, signatures).
Python 3.11 compatible. Additions are marked [impl]."""
from __future__ import annotations

import uuid
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal, Protocol, runtime_checkable

__all__ = [
    "Locality", "RequestContext", "ConsentToken", "EngineInfo", "EngineError", "ConsentRequired",
    "Cancelled", "Engine", "AudioFormat", "AudioChunk", "WordTiming", "TranscriptSegment", "ASREngine",
    "ChatMessage", "GenParams", "TokenDelta", "LLMEngine", "EmbeddingEngine", "ImageRef", "OCRBlock",
    "OCRResult", "OCREngine", "Voice", "TTSEngine", "VisionAnswer", "VisionEngine", "TranslationSegment",
    "TranslationEngine", "new_ctx",
]


class Locality(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"


@dataclass(frozen=True)
class RequestContext:
    request_id: uuid.UUID
    origin: Literal["voice", "ui", "schedule", "system"]
    locale: str = "en-US"
    deadline_ms: int | None = None
    consent_token: ConsentToken | None = None   # required iff backend.locality == CLOUD


@dataclass(frozen=True)
class ConsentToken:
    token_id: uuid.UUID
    scope: Literal["asr", "llm", "ocr", "vision", "tts"]
    request_id: uuid.UUID          # bound to ONE request
    provider: str
    payload_sha256: str            # hash of exactly what the user approved
    expires_at: float              # monotonic deadline, <= 60 s
    signature: bytes               # HMAC by pm-core consent gate key


@dataclass(frozen=True)
class EngineInfo:
    name: str
    version: str
    locality: Locality
    languages: Sequence[str]
    max_input: int | None = None


class EngineError(Exception): ...
class ConsentRequired(EngineError): ...
class Cancelled(EngineError): ...


@runtime_checkable
class Engine(Protocol):
    def info(self) -> EngineInfo: ...
    async def load(self) -> None: ...
    async def unload(self) -> None: ...
    async def health(self) -> bool: ...


# §6.2 ASR
@dataclass(frozen=True)
class AudioFormat:
    sample_rate: int = 16_000
    channels: int = 1
    sample_fmt: Literal["s16le", "f32le"] = "s16le"


@dataclass(frozen=True)
class AudioChunk:
    pcm: bytes
    seq: int
    t_start_ms: int
    is_last: bool = False


@dataclass(frozen=True)
class WordTiming:
    word: str
    start_ms: int
    end_ms: int
    prob: float


@dataclass(frozen=True)
class TranscriptSegment:
    text: str
    start_ms: int
    end_ms: int
    is_final: bool
    confidence: float | None
    language: str | None                     # 'en' | 'hi' | 'hi-en' (code-mixed) | None
    script: Literal["Latn", "Deva", "mixed"] | None = None
    words: Sequence[WordTiming] = ()


@runtime_checkable
class ASREngine(Engine, Protocol):
    def stream(self, ctx: RequestContext, fmt: AudioFormat, audio: AsyncIterator[AudioChunk],
               language_hint: Sequence[str] = ("en", "hi")) -> AsyncIterator[TranscriptSegment]: ...
    async def transcribe(self, ctx: RequestContext, fmt: AudioFormat, pcm: bytes,
                         language_hint: Sequence[str] = ("en", "hi")) -> list[TranscriptSegment]: ...


# §6.3 LLM
@dataclass(frozen=True)
class ChatMessage:
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    source_ids: Sequence[str] = ()


@dataclass(frozen=True)
class GenParams:
    max_tokens: int = 256
    temperature: float = 0.3
    top_p: float = 0.9
    stop: Sequence[str] = ()
    json_schema: dict | None = None
    seed: int | None = None


@dataclass(frozen=True)
class TokenDelta:
    text: str
    finish_reason: Literal["stop", "length", "cancel", None] = None
    usage: dict | None = None


@runtime_checkable
class LLMEngine(Engine, Protocol):
    def generate(self, ctx: RequestContext, messages: Sequence[ChatMessage],
                 params: GenParams) -> AsyncIterator[TokenDelta]: ...
    async def count_tokens(self, text: str) -> int: ...
    @property
    def context_window(self) -> int: ...


@runtime_checkable
class EmbeddingEngine(Engine, Protocol):
    dim: int
    async def embed(self, ctx: RequestContext, texts: Sequence[str]) -> list[list[float]]: ...


# §6.4 OCR
@dataclass(frozen=True)
class ImageRef:
    path: str
    width: int
    height: int
    mime: str = "image/jpeg"
    sha256: str = ""


@dataclass(frozen=True)
class OCRBlock:
    text: str
    bbox: tuple[int, int, int, int]
    confidence: float
    kind: Literal["line", "paragraph", "table_cell", "word"] = "line"
    script: str | None = None
    language: str | None = None


@dataclass(frozen=True)
class OCRResult:
    blocks: Sequence[OCRBlock]
    full_text: str
    language: str | None
    duration_ms: int


@runtime_checkable
class OCREngine(Engine, Protocol):
    async def recognize(self, ctx: RequestContext, image: ImageRef, langs: Sequence[str] = ("en", "hi"),
                        mode: Literal["document", "scene"] = "document") -> OCRResult: ...


# §6.5 TTS and Vision
@dataclass(frozen=True)
class Voice:
    id: str
    language: str
    sample_rate: int


@runtime_checkable
class TTSEngine(Engine, Protocol):
    def voices(self) -> Sequence[Voice]: ...
    def synthesize(self, ctx: RequestContext, text: str, voice: Voice,
                   rate: float = 1.0) -> AsyncIterator[AudioChunk]: ...


@dataclass(frozen=True)
class VisionAnswer:
    text: str
    regions: Sequence[tuple[int, int, int, int]] = ()


@runtime_checkable
class VisionEngine(Engine, Protocol):
    async def describe(self, ctx: RequestContext, image: ImageRef, prompt: str | None = None) -> VisionAnswer: ...


# §6.8 Translation
@dataclass(frozen=True)
class TranslationSegment:
    src_text: str
    tgt_text: str
    src_lang: str
    tgt_lang: str
    bbox: tuple[int, int, int, int] | None = None
    confidence: float | None = None


@runtime_checkable
class TranslationEngine(Engine, Protocol):
    def pairs(self) -> Sequence[tuple[str, str]]: ...
    async def translate(self, ctx: RequestContext, texts: Sequence[str], src_lang: str | None,
                        tgt_lang: str) -> list[TranslationSegment]: ...
    def translate_stream(self, ctx: RequestContext, texts: Sequence[str], src_lang: str | None,
                         tgt_lang: str) -> AsyncIterator[TranslationSegment]: ...


def new_ctx(origin: Literal["voice", "ui", "schedule", "system"] = "ui", **kw: object) -> RequestContext:
    """[impl] Convenience: fresh UUIDv7 request id."""
    from ..util.ids import uuid7
    return RequestContext(uuid7(), origin, **kw)  # type: ignore[arg-type]


_ = field
