# PocketMate — Software Architecture (v0.1 draft)

Status: draft for review · Owner: software · Source of truth for requirements: `../PRD.md`
Convention: **[PRD]** = stated in the PRD. **[A-n]** = assumption made by this doc, not a PRD fact; each needs confirmation (see §16).

---

## 0. Scope and design principles

- Target: Raspberry Pi CM5 4 GB [PRD]; CM4 is the alternate [PRD] and must keep working with reduced models (§6.6).
- MVP features [PRD]: push-to-talk assistant with listening/processing indicators; voice and typed notes stored locally; searchable memory with source-linked answers; camera OCR; basic image understanding (local or cloud); reminders, daily tasks, action-item extraction; offline notes, docs, and utilities; configurable local/cloud; physical mic mute; data review/export/edit/delete; battery monitoring; reliable sleep/wake; controlled shutdown.
- Principles:
  1. **Local-first.** Every MVP feature has to work offline. Cloud is an optional adapter used one request at a time with consent.
  2. **No covert capture.** The mic and camera only open on an explicit user action, and the indicator is driven from a hardware-backed path.
  3. **Fast feedback over big models.** The first visual or audio response comes within 300 ms of PTT (§14). Small models are the default.
  4. **Crash isolation.** Each heavy engine runs in its own process. The UI never blocks on inference.
  5. **Recoverable.** A/B rootfs, signed updates, a recovery image, and user data on a separate partition.

---

## 1. System overview

```
 ┌──────────────────────────── CM5 (Linux, aarch64) ─────────────────────────────┐
 │  pm-ui (Qt6/QML, C++)  ◄──── D-Bus (session/system) + Unix socket streams ────┐ │
 │        ▲                                                                       │ │
 │        │ events/state                                                          │ │
 │  pm-core (orchestrator, Python) ── intents, dialog, tools, consent gate ──────┤ │
 │     │        │         │          │           │            │                  │ │
 │  pm-audio  pm-asr   pm-llm     pm-ocr      pm-tts      pm-memory  pm-remind    │ │
 │  (capture, (whisper (llama.cpp (Tesseract/ (Piper)     (SQLite    (scheduler)  │ │
 │   PTT,VAD)  .cpp)    server)    Paddle)                 FTS5+vec)              │ │
 │                                                                               │ │
 │  pm-power (power state machine) ◄── UART ──► Low-power MCU (RP2040 proto)      │ │
 │  pm-cloud (optional, consent-gated egress)   pm-update (A/B, RAUC)             │ │
 └──────────────────────────────────────────────────────────────────────────────┘
        MCU: buttons, PTT, mic-mute sense, LED, fuel gauge, charger, RTC, power rail
```

---

## 2. OS image

| Item | Decision |
|---|---|
| Base | Raspberry Pi OS Lite (Bookworm or newer) 64-bit, built reproducibly with **pi-gen** at first. The plan is to move to **Yocto (meta-raspberrypi + meta-rauc)** before the custom PCB [A-1]. Rationale: pi-gen is the fastest path to a prototype, and Yocto gives a minimal, reproducible, signed product image. |
| Kernel | RPi vendor kernel 6.6+ LTS, arm64, 16K pages default on CM5 (validate llama.cpp/sqlite-vec builds) |
| Init | systemd. Every pm-* service is a unit with `Restart=on-failure`, `MemoryMax=`, `CPUWeight=`, plus sandboxing (`ProtectSystem=strict`, `PrivateNetwork=yes` for all engines except pm-cloud/pm-update) |
| Display stack | Qt6 on **EGLFS/KMS** (no X/Wayland compositor) using the vc4-kms-v3d driver. Fallback: `cage` kiosk Wayland if multi-window is ever needed |
| Audio | PipeWire (or plain ALSA for minimal footprint [A-2]), with ALSA plugin for the I2S mic/amp |
| Camera | libcamera + picamera2 (Python) for capture; IMX708 autofocus module [A-3] |
| Networking | NetworkManager (Wi-Fi/BT). nftables default-deny egress except for the `pm-cloud` and `pm-update` UIDs |
| Users | `pm` (UI), one system user per service, no login shell. SSH disabled in production and enabled only in dev builds |
| Logging | journald with volatile+persistent caps (50 MB). User content (transcripts, text) is **never** logged. Log scrubber unit tests enforce this |
| Time | chrony with the MCU RTC as the fallback source at boot (§11) |

### 2.1 Partition layout (32 GB eMMC [PRD]; microSD in dev)

| # | Name | FS | Size | Mount | Notes |
|---|---|---|---|---|---|
| 1 | boot-A | FAT32 | 256 MB | /boot/firmware | kernel, DTB, overlays, config.txt (slot A) |
| 2 | boot-B | FAT32 | 256 MB | — | slot B |
| 3 | rootfs-A | ext4 (or squashfs+overlay in Yocto) | 3 GB | / (ro) | read-only rootfs |
| 4 | rootfs-B | ext4 | 3 GB | — | |
| 5 | recovery | squashfs | 512 MB | — | minimal recovery and factory-reset UI |
| 6 | models | ext4 (ro, versioned) | 6 GB | /opt/pm/models | model weights updated separately from rootfs (bundle type "models") |
| 7 | data | ext4 on **LUKS2** | rest (~18 GB) | /var/lib/pm | DB, media, settings, logs-persistent |

- `tryboot` / autoboot.txt on CM5 handles A/B bootloader slot selection. The bootloader EEPROM is updated only through signed rpi-eeprom images.
- Data encryption key: LUKS2 keyslot sealed with a device secret. On CM5 this uses the **OTP-backed customer key / rpi-sign-bootconf secure boot** chain [A-4]. An optional user PIN adds a second keyslot. If secure boot isn't provisioned (dev), the key file lives on boot-A. That is acceptable for dev only.

### 2.2 A/B signed updates and recovery

- Tool: **RAUC** (signed bundles with X.509 and CMS, verity format, A/B slot handling, adaptive delta). Alternative considered: SWUpdate. RAUC was picked for its simpler Yocto integration and verity bundles.
- Bundle types: `system` (boot+rootfs), `models`, and `mcu-firmware` (signed UF2/bin flashed by pm-power over SWD/UART bootloader [A-5]).
- Flow: download (pm-update, consented network use) → verify signature → install to the inactive slot → mark the slot "try" → reboot → health check by `pm-health.service`, which requires within 120 s: UI up, pm-core responding, DB open, MCU link OK → `rauc status mark-good`. Otherwise the watchdog or boot counter (3 tries) falls back to the previous slot.
- Updates never run below 30 % battery unless charging, and never during an active recording.
- Recovery partition entry: hold Volume-Down + Power for 5 s at boot (the MCU detects this and sets the boot-mode GPIO/flag over UART) [A-6], or after 3 failed boots on both slots. Recovery offers: reinstall from USB-C mass storage or USB stick, factory reset (cryptographic wipe = destroy LUKS keyslots), export data to USB (requires PIN).
- Signing keys: an offline root CA, plus a separate dev key that production devices reject.

---

## 3. Device tree / config.txt (prototype on CM5 IO Board)

```ini
# /boot/firmware/config.txt (prototype)
arm_64bit=1
dtoverlay=vc4-kms-v3d
# Display: official Raspberry Pi Touch Display 2 (720x1280 portrait, rotated) OR a 4.3" 800x480 DSI panel [A-7]
dtoverlay=vc4-kms-dsi-ili9881-7inch,dsi1   # Touch Display 2 variant; swap for chosen 4.3" panel
# Camera (IMX708 / Camera Module 3, CAM1 port)
camera_auto_detect=0
dtoverlay=imx708,cam1
# I2S audio: mic + amp
dtparam=i2s=on
dtoverlay=googlevoicehat-soundcard          # stand-in for 2x I2S MEMS + MAX98357A; final: custom overlay
# UART to MCU (UART2 on GPIO4/5 → avoid console UART)
dtoverlay=uart2-pi5
# I2C for fuel gauge (if the CM5 reads it directly) / sensors
dtparam=i2c_arm=on
# Wake / power-button line from MCU
dtoverlay=gpio-shutdown,gpio_pin=17,active_low=1
# Hardware watchdog
dtparam=watchdog=on
# RTC: CM5 has an on-board RTC (needs backup battery on VBAT); MCU RTC is secondary
```

Custom overlay `pocketmate-carrier.dtbo` (for the custom PCB) defines: the I2S codec/mic (`simple-audio-card` with 2× MEMS mic, stereo TDM or L/R), amp enable GPIO, MCU UART + `IRQ` GPIO (MCU→CM5 attention), mic-mute sense GPIO (read-only, hardware switch state), indicator LED (owned by the MCU, mirrored), and button GPIOs if not routed through the MCU.

---

## 4. UI — Qt6/QML (800×480 touch)

- **Process**: `pm-ui`, C++ host + QML, EGLFS, runs as the `pm` user. 60 fps target, rendered on the GPU. Startup budget < 3 s after systemd reaches the target (QML precompiled with qmlcachegen / Qt Quick Compiler).
- **Why C++ host**: lower memory and faster startup than PySide. Business logic stays out of the UI. The UI is a thin client of pm-core over D-Bus (QtDBus).
- **Screen map** (800×480, landscape [A-7], 48 px minimum touch targets):
  - *Home*: clock, next reminder, quick-capture tiles (Voice note, Text note, Scan, Ask), status bar (battery %, charging, Wi-Fi, **mic state**, **cloud mode**).
  - *Listening overlay*: full-width colored banner + waveform + elapsed timer while recording, and "Processing…" with a spinner. Cannot be hidden.
  - *Answer view*: response text, **source chips** that open the linked note/transcript/OCR doc at the cited span, and a "Speak" toggle.
  - *Memory*: search box (FTS), filters (type/date/tag), detail view with edit/delete/export.
  - *Scan*: camera preview → capture → OCR result with confidence highlight → save/ask.
  - *Reminders / Today*: list, extracted action items awaiting confirmation.
  - *Settings*: local/cloud mode, retention, consent history (audit log), storage, battery, update, export/backup, factory reset.
  - *Consent dialog*: modal, shows exactly what is sent, where, and why (§8.3).
- **On-screen keyboard**: Qt Virtual Keyboard (multi-language layouts for travelers [PRD user group]).
- **Accessibility**: font scaling, high-contrast theme, TTS readout.

---

## 5. Services and IPC

### 5.1 IPC design
- **Control plane**: **D-Bus system bus** (`org.pocketmate.*`). Typed methods and signals, policy files restrict which UIDs may call what. sd-bus/dbus-next (Python, asyncio) and QtDBus (UI).
- **Data plane (streams)**: Unix domain sockets under `/run/pm/` carrying length-prefixed **msgpack** frames for audio PCM chunks, partial ASR results, and LLM token streams. These avoid D-Bus overhead and the D-Bus message size limit.
- **Large blobs** (images): passed by file path under `/run/pm/blobs/` (tmpfs, mode 0600, per-request ownership). The path is deleted after use.
- Every request carries `request_id` (UUIDv7), `origin` (ui/voice/schedule), and `consent_token` (if cloud).

### 5.2 Service list

| Service | Lang | Responsibilities | Boundary / privileges | Mem budget [A-8] |
|---|---|---|---|---|
| `pm-ui` | C++/QML | Rendering, touch, indicators (mirror), consent dialogs | `pm` user; no network; D-Bus client | 150 MB |
| `pm-core` | Python 3.11 asyncio | Orchestrator: intent routing, dialog state, tool calls (note/search/remind/scan), RAG assembly, action-item extraction, **consent gate**, confirmation of consequential actions | no network; only service allowed to call pm-cloud | 120 MB |
| `pm-audio` | Python + C ext (or C++) | Owns ALSA capture/playback, PTT gating, VAD/endpointing (Silero VAD ONNX or WebRTC VAD), AGC/beamforming lite (2 mics), level meter stream | `audio` group; **only** process that can open capture device (udev ACL); refuses capture if mute switch is on or PTT not held/latched | 60 MB |
| `pm-asr` | Python wrapper over whisper.cpp (C++) | Streaming/segment transcription, language ID | no network, no device access; gets PCM via socket | 250–600 MB |
| `pm-llm` | llama.cpp `llama-server` (C++) + thin Python adapter | Chat/generation, summarization, extraction (JSON-grammar constrained) | no network; models ro | 1.5–2.5 GB |
| `pm-ocr` | Python (Tesseract / PaddleOCR ONNX) | Text detection/recognition, layout blocks | no network | 150–400 MB |
| `pm-vision` | llama.cpp multimodal (mtmd) or ONNX captioner | Basic image understanding (local) | no network; on-demand only | 1–2 GB (exclusive with pm-llm) |
| `pm-tts` | Piper (C++/ONNX) | Speech synthesis, streaming chunks | no network | 80 MB |
| `pm-memory` | Python + SQLite (FTS5, sqlite-vec) | Storage, search, embeddings, retention jobs, export/import | single writer to DB; LUKS data partition | 80 MB |
| `pm-remind` | Python | Reminder/task scheduler, recurrence (RFC 5545 RRULE), hands next wake time to pm-power | | 30 MB |
| `pm-power` | Python | Power state machine, MCU protocol (UART), battery telemetry, inhibitors, watchdog petting | `dialout`; can call logind | 30 MB |
| `pm-cloud` | Python | Optional cloud adapters (LLM/ASR/vision); TLS 1.3, pinned hosts; **validates consent token** before any egress | only service with general egress (nftables by UID) | 50 MB |
| `pm-update` | RAUC + Python agent | Check/download/install bundles | egress to update host only | 30 MB |
| `pm-health` | Python | Boot health check, service liveness, mark-good | | 20 MB |

**Model residency (4 GB RAM)**: ASR and the LLM do not both stay fully resident on CM4 or in vision mode. pm-core runs a **model scheduler**: the LLM is loaded with mmap (stays in page cache). pm-vision runs exclusively, so the LLM is unloaded first. zram swap is 1 GB (lz4). This is a target to measure, not a guarantee [A-8].

### 5.3 Main voice flow (sequence)
1. MCU detects action-button press → `EVT_BUTTON{PTT,down}` → pm-power → D-Bus signal `PttPressed`.
2. pm-audio checks the mute GPIO, then opens capture. **The MCU turns the hardware recording LED on** (the CM5 asks, and the MCU also lights it independently whenever mic-power-enable is asserted, §8.2). The UI shows the Listening overlay.
3. PCM is streamed to pm-asr and partial transcripts are shown live.
4. Button released (hold mode) or VAD end / second press (toggle mode). Capture closes and the LED goes off.
5. pm-core routes the intent. For a question, it runs pm-memory hybrid search → builds a RAG prompt with source ids → pm-llm streams tokens → UI renders them with source chips → optional pm-tts.
6. The transcript, answer, and source links are saved as a `transcript` + `interaction` entry (subject to retention settings).

---

## 6. Modular AI engine interfaces

All engines live in the `pocketmate.engines` package. Backends register through entry points (`pocketmate.engines.asr` etc.) and are selected in `/var/lib/pm/settings.toml`. The core depends only on the Protocols below.

### 6.1 Common types

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Protocol, runtime_checkable, Sequence, Literal
import uuid

class Locality(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"

@dataclass(frozen=True)
class RequestContext:
    request_id: uuid.UUID
    origin: Literal["voice", "ui", "schedule", "system"]
    locale: str = "en-US"
    deadline_ms: int | None = None
    consent_token: "ConsentToken | None" = None   # required iff backend.locality == CLOUD

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
    name: str; version: str; locality: Locality
    languages: Sequence[str]; max_input: int | None = None

class EngineError(Exception): ...
class ConsentRequired(EngineError): ...
class Cancelled(EngineError): ...

class Engine(Protocol):
    def info(self) -> EngineInfo: ...
    async def load(self) -> None: ...
    async def unload(self) -> None: ...
    async def health(self) -> bool: ...
```

### 6.2 ASR

```python
@dataclass(frozen=True)
class AudioFormat:
    sample_rate: int = 16_000; channels: int = 1; sample_fmt: Literal["s16le", "f32le"] = "s16le"

@dataclass(frozen=True)
class AudioChunk:
    pcm: bytes; seq: int; t_start_ms: int; is_last: bool = False

@dataclass(frozen=True)
class WordTiming:
    word: str; start_ms: int; end_ms: int; prob: float

@dataclass(frozen=True)
class TranscriptSegment:
    text: str; start_ms: int; end_ms: int
    is_final: bool; confidence: float | None
    language: str | None; words: Sequence[WordTiming] = ()

@runtime_checkable
class ASREngine(Engine, Protocol):
    def stream(self, ctx: RequestContext, fmt: AudioFormat,
               audio: AsyncIterator[AudioChunk]) -> AsyncIterator[TranscriptSegment]:
        """Yields partial (is_final=False) and final segments. Must honour cancellation."""
    async def transcribe(self, ctx: RequestContext, fmt: AudioFormat, pcm: bytes) -> list[TranscriptSegment]: ...
```

Local backends (realistic on CM5, 4× A76 @2.4 GHz):
- **Default: whisper.cpp `base.en` / `base` (multilingual) Q5_1**, NEON, 4 threads. Pseudo-streaming: re-decode a sliding 5–10 s window with VAD segmentation for partials, plus final decode on endpoint. Expected RTF ≈ 0.3–0.6 for base on CM5 [A-9, measure]. `small` is an option for accuracy ("accurate mode").
- **Low-latency/CM4 fallback: Vosk** (Kaldi, small en/multi models ~50 MB) gives true streaming partials. It is also usable as an instant partial display while whisper produces the final [A-10].
- Optional: faster-whisper (CTranslate2 int8) for benchmark comparison.

### 6.3 LLM

```python
@dataclass(frozen=True)
class ChatMessage:
    role: Literal["system", "user", "assistant", "tool"]; content: str
    source_ids: Sequence[str] = ()          # memory items cited/injected

@dataclass(frozen=True)
class GenParams:
    max_tokens: int = 256; temperature: float = 0.3; top_p: float = 0.9
    stop: Sequence[str] = (); json_schema: dict | None = None   # → GBNF grammar locally
    seed: int | None = None

@dataclass(frozen=True)
class TokenDelta:
    text: str; finish_reason: Literal["stop", "length", "cancel", None] = None
    usage: dict | None = None               # prompt/completion tokens, t/s

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
```

Local backends: **llama.cpp `llama-server`** (OpenAI-compatible HTTP over a Unix socket; streaming SSE), GGUF Q4_K_M:
- Default candidates [A-11, benchmark in M3]: **Qwen2.5-1.5B-Instruct** or **Llama-3.2-1B/3B-Instruct**, Gemma-2/3 2B-class. Expected ~8–15 tok/s for 1–1.5B Q4 on CM5, ~3–6 tok/s for 3B [measure].
- CM4: 0.5–1B class only (e.g., Qwen2.5-0.5B), ~3–6 tok/s.
- Context: 4k, prompt cache enabled (`--cache-reuse`), system prompt KV pre-warmed at boot.
- Structured extraction (action items, reminder parse) uses a JSON schema → GBNF grammar, so the output is always parseable.
- Embeddings: **bge-small-en-v1.5 / multilingual-e5-small** (384-d) via llama.cpp `--embedding` or ONNX Runtime. Runs in background batches while charging/idle.

### 6.4 OCR

```python
@dataclass(frozen=True)
class ImageRef:
    path: str; width: int; height: int; mime: str = "image/jpeg"; sha256: str = ""

@dataclass(frozen=True)
class OCRBlock:
    text: str; bbox: tuple[int, int, int, int]; confidence: float
    kind: Literal["line", "paragraph", "table_cell"] = "line"

@dataclass(frozen=True)
class OCRResult:
    blocks: Sequence[OCRBlock]; full_text: str; language: str | None; duration_ms: int

@runtime_checkable
class OCREngine(Engine, Protocol):
    async def recognize(self, ctx: RequestContext, image: ImageRef,
                        langs: Sequence[str] = ("eng",)) -> OCRResult: ...
```
- Preprocessing (OpenCV): autofocus capture at 12 MP → document detection/deskew → downscale to ~2–3 MP → adaptive threshold.
- **Default: Tesseract 5 (LSTM, `tessdata_fast`)**: light and many languages. **Alternative: PaddleOCR PP-OCRv4 mobile (ONNX Runtime)** gives better results on photos/scene text. Pick per benchmark [A-12]. Target < 3 s per page.

### 6.5 TTS and Vision

```python
@dataclass(frozen=True)
class Voice:
    id: str; language: str; sample_rate: int

@runtime_checkable
class TTSEngine(Engine, Protocol):
    def voices(self) -> Sequence[Voice]: ...
    def synthesize(self, ctx: RequestContext, text: str, voice: Voice,
                   rate: float = 1.0) -> AsyncIterator[AudioChunk]: ...  # sentence-chunked

@dataclass(frozen=True)
class VisionAnswer:
    text: str; regions: Sequence[tuple[int, int, int, int]] = ()

@runtime_checkable
class VisionEngine(Engine, Protocol):
    async def describe(self, ctx: RequestContext, image: ImageRef,
                       prompt: str | None = None) -> VisionAnswer: ...
```
- **TTS default: Piper** (VITS ONNX, `medium`/`low` voices, ~22 kHz). Faster than real time on CM5. Synthesis is sentence-streamed so the first audio arrives < 500 ms after the first sentence.
- **Vision local**: llama.cpp multimodal with a small VLM (e.g., SmolVLM-256M/500M, Moondream2, or Qwen2-VL-2B Q4) [A-13]. Expect 5–30 s per image on CM5, so it's labeled "basic" per PRD. Cloud vision is the higher-quality option, gated by consent.

### 6.6 Backend registry and profiles

```toml
# /var/lib/pm/settings.toml
[profile]               # "cm5" | "cm4" auto-detected from /proc/device-tree/model
mode = "local"          # "local" | "ask_each_time" | (never "cloud_always" in MVP)
[asr]    backend = "whispercpp"; model = "ggml-base-q5_1.bin"; partials = "vosk"
[llm]    backend = "llamacpp";   model = "qwen2.5-1.5b-instruct-q4_k_m.gguf"; ctx = 4096
[ocr]    backend = "tesseract";  langs = ["eng"]
[tts]    backend = "piper";      voice = "en_US-lessac-medium"
[vision] backend = "llamacpp-mtmd"; model = "smolvlm-500m"
[embed]  backend = "llamacpp";   model = "bge-small-en-v1.5-q8_0.gguf"; enabled = true
[cloud]  enabled = false; provider = ""  # adapters: openai-compatible, etc. [A-14]
```

### 6.7 Cloud adapter (optional)

- `CloudLLMEngine`, `CloudASREngine`, and `CloudVisionEngine` implement the same Protocols with `locality = CLOUD` and run **inside pm-cloud only**.
- **Hard gate**: pm-cloud rejects any call without a valid `ConsentToken` whose `request_id` matches, `payload_sha256` matches the exact bytes being sent, scope matches, and that hasn't expired. A token is single-use and is stored in the consent log.
- The cloud is never used as a silent fallback. If the local engine fails, the UI offers "Try with cloud?" and the consent dialog opens.
- API keys are stored in the LUKS data partition (or kernel keyring), entered by the user, and never logged.

---

## 7. Memory — SQLite FTS5 schema

DB: `/var/lib/pm/memory.db`, WAL mode, `PRAGMA foreign_keys=ON`, `secure_delete=ON` (so deleted data is overwritten), single writer (pm-memory). Media files live under `/var/lib/pm/media/<yyyy>/<mm>/<uuid>.<ext>`.

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA secure_delete = ON;

-- Common item table: every memorable thing has a row here (source-link target).
CREATE TABLE items (
  id            TEXT PRIMARY KEY,            -- UUIDv7
  kind          TEXT NOT NULL CHECK (kind IN ('note','transcript','ocr_doc','image','interaction','task')),
  title         TEXT,
  created_at    INTEGER NOT NULL,            -- unix ms UTC
  updated_at    INTEGER NOT NULL,
  source        TEXT NOT NULL CHECK (source IN ('voice','typed','camera','import','assistant')),
  locality      TEXT NOT NULL DEFAULT 'local' CHECK (locality IN ('local','cloud')), -- was cloud used to produce it
  retention     TEXT NOT NULL DEFAULT 'default', -- 'default' | 'keep' | ISO duration e.g. 'P30D'
  expires_at    INTEGER,                     -- computed from retention; NULL = keep
  pinned        INTEGER NOT NULL DEFAULT 0,
  deleted_at    INTEGER                      -- soft delete (trash, 7 days) before purge
);
CREATE INDEX items_kind_created ON items(kind, created_at DESC);
CREATE INDEX items_expires ON items(expires_at) WHERE expires_at IS NOT NULL;

CREATE TABLE tags (item_id TEXT REFERENCES items(id) ON DELETE CASCADE, tag TEXT NOT NULL,
                   PRIMARY KEY (item_id, tag));

CREATE TABLE notes (
  item_id   TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  body      TEXT NOT NULL,                   -- markdown
  origin_transcript_id TEXT REFERENCES items(id) ON DELETE SET NULL
);

CREATE TABLE transcripts (
  item_id     TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  text        TEXT NOT NULL,
  language    TEXT,
  duration_ms INTEGER,
  audio_path  TEXT,                          -- NULL unless user chose "keep audio" (default: discard audio)
  engine      TEXT NOT NULL                  -- e.g. 'whispercpp:base-q5_1'
);
CREATE TABLE transcript_segments (
  item_id  TEXT REFERENCES items(id) ON DELETE CASCADE,
  seq      INTEGER, start_ms INTEGER, end_ms INTEGER, text TEXT,
  PRIMARY KEY (item_id, seq)
);

CREATE TABLE ocr_docs (
  item_id     TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  image_path  TEXT NOT NULL,
  full_text   TEXT NOT NULL,
  language    TEXT,
  blocks_json TEXT,                          -- [{text,bbox,conf}]
  engine      TEXT NOT NULL,
  mean_conf   REAL
);

CREATE TABLE interactions (                  -- Q&A history with citations
  item_id   TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  question  TEXT NOT NULL, answer TEXT NOT NULL, engine TEXT NOT NULL
);
CREATE TABLE citations (
  interaction_id TEXT REFERENCES items(id) ON DELETE CASCADE,
  cited_item_id  TEXT REFERENCES items(id) ON DELETE CASCADE,
  span_start INTEGER, span_end INTEGER,      -- char offsets in cited text (or ms for transcript)
  PRIMARY KEY (interaction_id, cited_item_id, span_start)
);

CREATE TABLE reminders (
  id           TEXT PRIMARY KEY,
  item_id      TEXT REFERENCES items(id) ON DELETE SET NULL,   -- originating note/transcript
  title        TEXT NOT NULL,
  due_at       INTEGER,                      -- unix ms UTC; NULL = undated task
  tz           TEXT NOT NULL DEFAULT 'Asia/Kolkata',  -- [A-15] device tz from settings
  rrule        TEXT,                         -- RFC 5545, e.g. 'FREQ=DAILY;BYHOUR=9'
  status       TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('suggested','pending','done','dismissed','snoozed')),
  snooze_until INTEGER,
  is_task      INTEGER NOT NULL DEFAULT 0,   -- daily task vs timed reminder
  created_at   INTEGER NOT NULL, completed_at INTEGER
);
CREATE INDEX reminders_due ON reminders(status, due_at);

CREATE TABLE consent_log (                   -- append-only audit log
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  ts           INTEGER NOT NULL,
  event        TEXT NOT NULL CHECK (event IN ('cloud_granted','cloud_denied','cloud_sent','cloud_error',
                                              'mic_open','mic_close','camera_capture','export','delete',
                                              'retention_change','setting_change','factory_reset')),
  scope        TEXT,                         -- asr/llm/ocr/vision
  provider     TEXT,
  request_id   TEXT,
  payload_sha256 TEXT,
  bytes_sent   INTEGER,
  detail       TEXT,                         -- JSON, no user content
  prev_hash    TEXT NOT NULL,                -- hash chain for tamper evidence
  row_hash     TEXT NOT NULL
);
CREATE TRIGGER consent_log_no_update BEFORE UPDATE ON consent_log
BEGIN SELECT RAISE(ABORT, 'consent_log is append-only'); END;
CREATE TRIGGER consent_log_no_delete BEFORE DELETE ON consent_log
WHEN (SELECT value FROM meta WHERE key='factory_reset_in_progress') IS NOT '1'
BEGIN SELECT RAISE(ABORT, 'consent_log is append-only'); END;

CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);  -- schema_version, etc.

-- Full-text index over all searchable text (external-content style, one row per chunk).
CREATE TABLE chunks (
  id       INTEGER PRIMARY KEY,
  item_id  TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  seq      INTEGER NOT NULL,
  text     TEXT NOT NULL,                    -- ~300-500 tokens, overlap 50
  span_start INTEGER, span_end INTEGER,      -- offsets back into source text (source links)
  UNIQUE(item_id, seq)
);
CREATE VIRTUAL TABLE chunks_fts USING fts5(
  text, title UNINDEXED, kind UNINDEXED,
  content='', contentless_delete=1,          -- SQLite >= 3.43
  tokenize = 'unicode61 remove_diacritics 2'
);
-- pm-memory writes chunks_fts(rowid=chunks.id, ...) in the same transaction as chunks.
-- Optional: second index with tokenize='trigram' for substring/OCR-noise tolerant search.

-- Optional semantic retrieval (sqlite-vec extension)
-- .load vec0
CREATE VIRTUAL TABLE chunk_vec USING vec0(
  chunk_id INTEGER PRIMARY KEY,
  embedding float[384]                       -- bge-small / e5-small
);
CREATE TABLE embedding_meta (chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
                             model TEXT NOT NULL, created_at INTEGER NOT NULL);
```

> Note: chunk/FTS/vec rows are deleted by pm-memory in the same transaction as the item (vec0 and contentless FTS don't honor FK cascades). A test asserts zero orphans after delete.

### 7.1 Example queries

```sql
-- 1. Keyword search with ranking + snippet, newest-weighted, excluding trash
SELECT i.id, i.kind, i.title, i.created_at,
       snippet(chunks_fts, 0, '[', ']', '…', 12) AS snip,
       c.span_start, c.span_end,
       bm25(chunks_fts) AS score
FROM chunks_fts
JOIN chunks c ON c.id = chunks_fts.rowid
JOIN items  i ON i.id = c.item_id
WHERE chunks_fts MATCH :q            -- e.g. 'wifi NEAR(password, 5)' or 'invoice*'
  AND i.deleted_at IS NULL
ORDER BY score + (strftime('%s','now')*1000 - i.created_at) / 8.64e10 * 0.05
LIMIT 20;

-- 2. Semantic top-k (sqlite-vec) then hybrid merge (Reciprocal Rank Fusion) in Python
SELECT chunk_id, distance FROM chunk_vec
WHERE embedding MATCH :qvec AND k = 20 ORDER BY distance;

-- 3. Source link: open the exact cited span
SELECT i.kind, c.text, c.span_start, c.span_end FROM citations ct
JOIN chunks c ON c.item_id = ct.cited_item_id
JOIN items i ON i.id = ct.cited_item_id
WHERE ct.interaction_id = :iid;

-- 4. Today's agenda
SELECT id, title, due_at, is_task FROM reminders
WHERE status IN ('pending','snoozed')
  AND (due_at < :end_of_day_ms OR (is_task = 1 AND due_at IS NULL))
ORDER BY due_at NULLS LAST;

-- 5. Next wake time to hand to MCU
SELECT MIN(COALESCE(snooze_until, due_at)) FROM reminders
WHERE status IN ('pending','snoozed') AND COALESCE(snooze_until, due_at) > :now_ms;

-- 6. Retention sweep (run daily + on boot)
UPDATE items SET deleted_at = :now WHERE expires_at < :now AND pinned = 0 AND deleted_at IS NULL;
-- purge after 7-day trash: DELETE items + chunks + chunks_fts + chunk_vec + media files

-- 7. Consent audit for UI
SELECT ts, event, scope, provider, bytes_sent FROM consent_log ORDER BY id DESC LIMIT 100;
```

**Export**: a ZIP containing `items.jsonl`, markdown notes, media, and `consent_log.csv`, optionally encrypted with an age passphrase. **Import** restores from the same format. That gives the documented backup/recovery the PRD requires.

---

## 8. Consent and privacy model

### 8.1 Rules (enforced, tested)
| # | Rule | Enforcement |
|---|---|---|
| P1 | **Push-to-talk only.** No wake word, no continuous or background recording in MVP | pm-audio opens capture only during a PTT session. There's no API for unattended capture. Code review gate + test that capture fails without a PTT event |
| P2 | **Visible recording indicator** whenever the mic is live | Hardware LED controlled by the MCU and tied to mic power/enable (§8.2), plus a UI overlay. The UI can't dismiss it |
| P3 | **Physical mic mute** | Hardware switch cuts mic power/clock (on custom PCB) [A-16]. The state is readable by GPIO, and the UI shows "Mic off (hardware)" |
| P4 | **No covert camera** | Camera opens only from the Scan screen with a visible preview. The shutter is a user action. The LED blinks on capture |
| P5 | **Max session length** | PTT session auto-stops at 120 s (configurable up to 10 min for dictation) with a visible countdown |
| P6 | **Audio not retained by default** | PCM lives in RAM and is dropped after transcription unless "Keep audio" is enabled per note |
| P7 | **Cloud off by default.** Per-request explicit consent | §8.3. Modes: *Local only* (default) / *Ask each time*. There's no "always cloud" in MVP [A-17] |
| P8 | **Confirm consequential actions** | Deleting, bulk export, factory reset, sending anything off-device, and creating reminders from AI extraction (shown as `suggested` until confirmed) |
| P9 | **Retention control** | Per-kind defaults (e.g., transcripts 90 days, interactions 30 days, notes keep) [A-18], per-item override, trash for 7 days, `secure_delete` |
| P10 | **Secure storage and comms** | LUKS2 data partition, TLS 1.3 + cert pinning for cloud/update, nftables egress by UID |
| P11 | **Audit log** | `consent_log`, hash-chained and append-only. Viewable in Settings and included in export |
| P12 | **Source links** | Every assistant answer that uses memory stores citations. If nothing was retrieved, the UI labels the answer "No sources: general knowledge" |

### 8.2 Recording indicator integrity
- The mic enable/power rail is driven by the **MCU**, and the MCU lights the red LED whenever that rail is on. That means CM5 software can't record without the LED lighting. The CM5 *requests* mic-on over UART while PTT is active.
- Prototype limitation: with a USB/I2S mic on the IO board, the mic is always powered, so the guarantee is software-only. It becomes hardware-enforced on the custom PCB [A-16].

### 8.3 Cloud consent flow
1. pm-core decides the cloud would help (or the user picks "Use cloud").
2. The consent dialog shows the provider, the data category, an **exact preview** (text, or a thumbnail for an image), size, and the retention policy of the provider (as configured). Buttons: *Send once* / *Cancel*. The default focus is Cancel.
3. On *Send once*, pm-core mints a single-use `ConsentToken` bound to the request and the payload hash. The log records `cloud_granted`.
4. pm-cloud verifies the token, sends, and logs `cloud_sent` with bytes. The resulting item has `locality='cloud'`, and the UI shows a cloud badge.
5. No implicit retries to other providers. Cancel logs `cloud_denied` and falls back to the local engine.

---

## 9. Reminders, tasks, action items

- Creation: voice or typed natural language → LLM with a JSON-schema grammar → `{title, due_at_local, rrule?, is_task}` → deterministic date parsing check (`dateparser`) → shown as a **suggested** reminder → the user confirms.
- Action-item extraction: after a voice note or transcript is saved, pm-core runs an extraction prompt and lists the candidate tasks as `suggested`. Nothing is auto-scheduled.
- Scheduling: pm-remind keeps an in-memory heap of upcoming occurrences, recomputed on change, RRULE via `dateutil.rrule`.
- Delivery: in Active/Idle, a UI banner + chime. In Display-off/Suspend, pm-remind gives pm-power the **next due time**, pm-power programs the MCU RTC alarm (`CMD_SET_WAKE`) and the CM5 RTC wakealarm, and on wake the MCU pulses the vibration/LED [A-19] while the CM5 shows the reminder.
- Missed reminders (device was MCU-held off) are shown on next boot as "missed".
- Time zone changes are handled by storing UTC + tz.

---

## 10. Power states

| State | CM5 | Display | MCU | Entry | Exit / wake |
|---|---|---|---|---|---|
| **S0 Active** | running, governor `schedutil` | on, backlight per ALS/user | awake | any input | idle timer |
| **S1 Idle** | running, inference unloaded after 5 min, governor `powersave` | dimmed 30 % | awake | 30 s no input [A-20] | touch/button |
| **S2 Display-off** | running (background jobs, reminders, embedding batch if charging) | off (DPMS), touch IRQ disabled except power/action | awake | 60 s idle or short power press | power/action button, reminder |
| **S3 Suspend** | `systemctl suspend` (s2idle) **if supported on CM5 kernel** [A-21]; otherwise fall through to S4 with a fast boot path | off | low-power, RTC running | 10 min in S2 and not charging, no inhibitors | button, RTC alarm, USB-C plug, low battery |
| **S4 MCU-held off** | **CM5 rails off** (PMIC off via MCU-controlled enable / `GLOBAL_EN`) | off | RP2040 dormant, RTC alarm armed | long idle (e.g., 2 h) [A-20], long-press power → "Power off", critical battery | power button, RTC alarm (reminder), charger plug (optional) |
| **S5 Controlled shutdown** (transient) | sync, close DB (WAL checkpoint), unmount, `poweroff` | "Shutting down" | waits for `EVT_HALTED` / CM5 3V3 drop, then cuts power | user, battery ≤ 3 %, thermal critical, update | → S4 |

Notes:
- **Realistic CM5 behavior**: Linux suspend-to-RAM on CM5 is not a mature feature. The validated low-power path is the BCM2712 PMIC "off" state (`POWER_OFF_ON_HALT=1` in EEPROM, ~0.01 W class) or the MCU cutting the input rail. So "sleep" in MVP is likely **S2 (display off, CPU idle) for short gaps, and S4 + fast boot for long gaps**. Boot-time optimization (target < 12 s to usable UI) therefore matters [A-21].
- **Inhibitors**: active PTT session, OCR/LLM job, update install, export. These are held through `systemd-inhibit` / pm-power's API.
- **Battery thresholds** [A-22]: 15 % warning, 5 % force S2 + warning, 3 % controlled shutdown, and the MCU hard-cuts at the pack UVLO / 3.0 V cell if the CM5 doesn't respond within 30 s.
- **Thermal**: > 80 °C throttles LLM threads (4→2), > 85 °C pauses inference, at critical temperature runs a controlled shutdown.

Transition diagram:
```
 S0 ──30s──► S1 ──60s──► S2 ──10m, !charging──► S3/S4
  ▲  input    ▲  input    │ button/reminder        │ button / RTC alarm / USB-C
  └───────────┴───────────┘◄───────────────────────┘ (S4 → boot → S0)
 any ──(long-press+confirm | batt≤3% | thermal | update)──► S5 ──► S4
```

---

## 11. CM5 ↔ MCU protocol

**Physical**: UART at 115200 8N1 (CM5 UART2 ↔ RP2040 UART0) plus an `MCU_IRQ` GPIO (MCU→CM5 attention, also a wake source) and the CM5 `RUN`/`GLOBAL_EN` line controlled by the MCU. I2C is kept as an alternative (the MCU as an I2C slave at 0x42) [A-23]. UART is preferred because it allows asynchronous events and a simple bootloader path. The fuel gauge stays on the **MCU's** I2C bus so it's monitored while the CM5 is off.

**Framing** (COBS-encoded, `0x00` delimiter):
```
| ver(1) | type(1) | seq(1) | len(1) | payload(len ≤ 64) | crc16-CCITT(2) |
```
Every command gets `ACK{seq,status}` within 50 ms. Otherwise the sender retries ×3, and after that the link is marked down.

| Type | Dir | Name | Payload |
|---|---|---|---|
| 0x01 | CM5→MCU | `HELLO` | proto_ver, cm5_fw_ver |
| 0x02 | MCU→CM5 | `HELLO_ACK` | mcu_fw_ver, boot_reason (button/rtc/usb/wdt/brownout), flags |
| 0x10 | CM5→MCU | `SET_STATE` | target state (S0..S5) |
| 0x11 | CM5→MCU | `HEARTBEAT` | uptime_s, cm5_state |
| 0x12 | CM5→MCU | `SET_WAKE` | epoch_s (UTC) of next RTC alarm; 0 = clear |
| 0x13 | CM5→MCU | `SET_TIME` / `GET_TIME` | epoch_s |
| 0x14 | CM5→MCU | `MIC_ENABLE` | on/off (MCU drives mic power + REC LED) |
| 0x15 | CM5→MCU | `LED` | pattern id (charging, notify, rec, error), brightness |
| 0x16 | CM5→MCU | `HAPTIC` | pattern [A-19] |
| 0x17 | CM5→MCU | `SHUTDOWN_READY` | — (MCU starts power-cut timer after CM5 halts) |
| 0x18 | CM5→MCU | `BOOT_MODE` | normal / recovery (for next boot) |
| 0x19 | CM5→MCU | `WDT_CFG` | timeout_s (default 30) |
| 0x1A | CM5→MCU | `FW_UPDATE_BEGIN/CHUNK/END` | signed image chunks |
| 0x20 | MCU→CM5 | `EVT_BUTTON` | id (POWER, ACTION/PTT, VOL+, VOL−), action (down/up/short/long/double) |
| 0x21 | MCU→CM5 | `EVT_BATTERY` | soc_%, mV, mA (signed), temp_dC, charging state, every 30 s or on change > 1 % |
| 0x22 | MCU→CM5 | `EVT_POWER_SRC` | usb_attached, charger status/fault |
| 0x23 | MCU→CM5 | `EVT_MIC_MUTE` | hw switch state |
| 0x24 | MCU→CM5 | `EVT_RTC_ALARM` | epoch_s |
| 0x25 | MCU→CM5 | `EVT_SHUTDOWN_REQ` | reason (long-press, critical battery, thermal) and deadline_s |
| 0x2F | MCU→CM5 | `EVT_FAULT` | code |

**Wake sources** (S3/S4 → on): POWER button, ACTION button (configurable), RTC alarm (reminder), USB-C attach (configurable: boot to "charging" screen or stay off and show the charge LED), critical events.

**Watchdog**: two layers. (1) The BCM2712 hardware watchdog is fed by systemd (`RuntimeWatchdogSec=15`). (2) The MCU watchdog expects a `HEARTBEAT` every 5 s in S0–S2. If it misses for 30 s, the MCU toggles `RUN` to reset the CM5 (logged as `boot_reason=wdt`). After 3 WDT resets in 10 min, it requests `BOOT_MODE=recovery`. The MCU itself runs its own hardware WDT.

**RTC**: CM5 has an on-board RTC (needs VBAT backup cell or supercap). The MCU also keeps time (RP2040 RTC, or an external RV-3028 on the custom PCB for ~45 nA [A-24]) so RTC alarms work while CM5 rails are fully off. The CM5 syncs MCU time after NTP and pulls MCU time at boot before chrony sync.

---

## 12. Low-power MCU firmware outline

- **Target**: RP2040 on the prototype (Pico). Production candidate: a lower-quiescent part (e.g., STM32U0/L0, nRF52, or RP2350 in dormant mode) [A-25]. Firmware is written in C on a portable HAL (Pico SDK at first, behind a thin HAL so it can be ported). Zephyr is an option.
- **Modules**:
  - `hal_*`: GPIO, UART, I2C, ADC, timers, flash, WDT.
  - `link`: COBS/CRC framing, seq/ack, retry, command dispatch.
  - `buttons`: debounce (5 ms), short/long (≥ 800 ms)/very-long (≥ 8 s = hard power-off without the CM5), double-press, boot combos.
  - `power_fsm`: S0–S5 state machine (mirror of §10), CM5 rail/`RUN` control, power-cut timer after `SHUTDOWN_READY` (cuts after CM5 3V3 drops or a 10 s timeout).
  - `battery`: fuel gauge driver (e.g., MAX17048 / BQ27441 [A-26]), charger status (e.g., BQ25895/BQ24074), thresholds and UVLO policy, charge-LED patterns. Works even when the CM5 is off.
  - `rtc_alarm`: time keeping and alarm → wake CM5.
  - `privacy`: mic power enable + REC LED interlock (LED := mic_power), mute switch sense. This module is tiny and reviewed separately.
  - `wdt_supervisor`: CM5 heartbeat monitor and reset policy.
  - `bootloader`: A/B MCU image with signature check (ed25519), updated through `FW_UPDATE_*` messages. Fallback: RP2040 BOOTSEL USB.
  - `log`: ring buffer of events (boot reasons, faults) readable from the CM5.
- **Main loop**: event-driven. Sleep (`__wfi`, or dormant in S4 with wake on GPIO/RTC). Target average current in S4 < 1 mA on the prototype Pico (realistically a few mA with Pico regulators [A-27]) and < 50 µA on the custom PCB.
- **Safety invariants** (unit-tested on the host): the REC LED is never off while mic power is on; power is never cut while the CM5 is running unless very-long press / UVLO; a critical battery event always forces S5→S4.

---

## 13. Logging, telemetry, and diagnostics
- journald with no user content. A structured `pm.log` JSON with event codes.
- No remote telemetry in MVP. A "Diagnostics bundle" export (logs, versions, MCU log, no user content) is user-initiated.
- Crash dumps: `systemd-coredump` limited to engine binaries, stored on the data partition, deleted after 7 days.

## 14. Performance targets (to validate in prototype) [A-28]
| Metric | Target CM5 |
|---|---|
| PTT press → listening indicator | < 150 ms (MCU LED immediate, UI < 150 ms) |
| End of speech → final transcript (10 s utterance) | < 2.5 s |
| Question → first LLM token (with RAG) | < 2.5 s |
| LLM stream | ≥ 8 tok/s (1.5B Q4) |
| FTS search over 50k chunks | < 50 ms |
| OCR one page | < 3 s |
| Cold boot → usable UI | < 15 s (stretch < 10 s) |
| S2 → S0 wake | < 300 ms |

## 15. Repo layout and dev workflow
```
PocketMate/
  software/
    ARCHITECTURE.md
    os/         pi-gen stage + (later) yocto layer meta-pocketmate, rauc config, dts overlays
    ui/         Qt6/QML app (CMake)
    services/   python package `pocketmate` (core, audio, asr, llm, ocr, tts, memory, remind, power, cloud)
      pocketmate/engines/  protocols.py, backends/*
    mcu/        firmware (CMake, Pico SDK), host-side tests
    tools/      benchmarks, protocol fuzzer, flashing scripts
    tests/      pytest (unit), integration (on-device, HIL with MCU)
```
CI: lint (ruff, mypy --strict for protocols), unit tests, cross-builds (aarch64) of llama.cpp/whisper.cpp, MCU firmware build + host unit tests, image build nightly. Git flow per PRD: issue → branch → PR → merge as anand2532.

---

# Part B — Prototype plan (off-the-shelf CM5 IO Board)

## B1. Goals
Validate on existing hardware before the custom PCB [PRD strategy]: capture/search/OCR/reminders working end-to-end; measure performance, privacy behavior, battery life, and thermals; freeze the MCU protocol and power behavior; derive the custom carrier requirements.

## B2. BOM (prototype, ~1–2 units) [prices are rough estimates, A-29]

| # | Item | Purpose | Qty | Est. USD |
|---|---|---|---|---|
| 1 | Raspberry Pi CM5, 4 GB RAM, 32 GB eMMC, wireless (CM5104032) | compute [PRD] | 1 | 90 |
| 2 | Raspberry Pi CM5 IO Board | carrier | 1 | 25 |
| 3 | CM5 active cooler (official) | thermals | 1 | 10 |
| 4 | Antenna kit for CM5 (if using external antenna) | Wi-Fi/BT | 1 | 5 |
| 5 | Display: Raspberry Pi Touch Display 2 (7", 720×1280 DSI) **or** Waveshare 4.3" DSI capacitive 800×480 | UI; the 4.3" matches PRD size | 1 | 40–60 |
| 6 | Raspberry Pi Camera Module 3 (IMX708, autofocus) + CM-length FFC (22-pin) | OCR [PRD CSI AF] | 1 | 25 |
| 7 | 2× I2S MEMS mic breakout (INMP441 or Adafruit SPH0645/ICS-43434) | stereo mic [PRD 2 mics] | 2 | 10 |
| 7b | Alt: USB mic (e.g., ReSpeaker USB / mini USB mic) | quick-start fallback | 1 | 10–60 |
| 8 | MAX98357A I2S class-D amp breakout + 8 Ω 1–2 W mini speaker (e.g., 28–40 mm) | audio out | 1 | 10 |
| 9 | Raspberry Pi Pico (RP2040) or Pico 2 | MCU stand-in | 2 | 10 |
| 10 | Battery/UPS: e.g., a Li-ion UPS board with I2C fuel gauge (Waveshare UPS HAT/Module (C/D) or PiSugar-class), or discrete: Adafruit BQ24074 charger + MAX17048 fuel gauge + 5 V boost (≥ 3 A, e.g., TPS61088/ MT3608-class is too weak) | power path + battery [PRD] | 1 | 25–40 |
| 11 | Li-ion/LiPo cell(s), protected, 3000–5000 mAh [A-30] | battery | 1–2 | 15 |
| 12 | USB-C PD/5 V 5 A supply (official 27 W) | bench power | 1 | 12 |
| 13 | INA219/INA226 breakout or USB power meter | power measurement | 1 | 10 |
| 14 | Tactile buttons (large action button, power, vol±), slide switch (mic mute), RGB/red LED, resistors, P-MOSFET/load switch (e.g., TPS22918) for mic power | controls, privacy interlock | kit | 10 |
| 15 | Dupont/JST wiring, breadboard, standoffs, 3D-printed test frame | assembly | kit | 15 |
| 16 | USB-UART adapter (3.3 V), Raspberry Pi Debug Probe (SWD) | debug | 1 | 15 |
| | **Total (approx.)** | | | **~$330–400** |

## B3. Wiring (prototype)

| From (CM5 IO Board 40-pin header, GPIO#) | To | Notes |
|---|---|---|
| GPIO18 (PCM_CLK/BCLK) | Mic1 SCK, Mic2 SCK, MAX98357A BCLK | shared I2S bus |
| GPIO19 (PCM_FS/LRCLK) | Mic1 WS, Mic2 WS, MAX98357A LRC | |
| GPIO20 (PCM_DIN) | Mic1 SD + Mic2 SD | mic L/R select: Mic1 L/R→GND (left), Mic2 L/R→3V3 (right) |
| GPIO21 (PCM_DOUT) | MAX98357A DIN | amp GAIN default; SD pin→GPIO16 (amp enable) |
| 3V3 via load switch (Pico-controlled) | Mic1/Mic2 VDD | **mic power interlock**: Pico GP10 → load switch EN; same net → REC LED (via transistor) |
| GPIO4 (UART2 TX) | Pico GP1 (UART0 RX) | 3.3 V logic |
| GPIO5 (UART2 RX) | Pico GP0 (UART0 TX) | |
| GPIO17 (in) | Pico GP2 (`MCU_IRQ` / shutdown request) | gpio-shutdown overlay for fallback |
| GPIO22 (in) | Mute switch (also to Pico GP11) | sense only |
| IO Board power button / `PWR_BUT` and `RUN`/`GLOBAL_EN` test points (J2 / headers) | Pico GP3 (open-drain via NPN/MOSFET) | lets the MCU press power / hold off the CM5 [A-31: confirm IO board headers] |
| GND | common ground | single-point star near the UPS |
| Pico GP4/GP5 (I2C0 SDA/SCL) | fuel gauge (MAX17048) + charger status | MCU owns battery telemetry |
| Pico GP6–GP9 | Buttons: ACTION/PTT, POWER, VOL+, VOL− (to GND, internal pull-ups) | |
| Pico GP12/13 | status RGB LED / haptic driver (optional) | |
| Pico VSYS | battery/UPS always-on rail (3.3–5 V) | MCU stays powered when the CM5 is off |
| UPS 5 V out | CM5 IO Board power input (barrel/USB-C, via load switch controlled by Pico GP14 for "MCU-held off") | ≥ 3 A @ 5 V; note the IO Board 12 V barrel is regulated down, so feed 5 V via the USB-C path [A-31] |
| CAM1 FFC | Camera Module 3 | |
| DSI1 FFC | Display | touch over DSI I2C |

## B4. Milestones

| M | Duration [A-32] | Deliverables | Exit criteria |
|---|---|---|---|
| **M0 Bring-up** | 1 wk | pi-gen image, overlays, display/touch/camera/I2S mic/amp working, Qt EGLFS hello | All peripherals enumerate; `arecord`/`aplay` stereo OK; camera AF still capture |
| **M1 Skeleton** | 2 wk | D-Bus services skeleton, pm-ui shell screens, pm-memory schema + migrations, typed notes, FTS search | Create/search/edit/delete notes; unit tests ≥ 80 % for memory |
| **M2 Voice** | 2 wk | pm-audio PTT, whisper.cpp + Vosk partials, Piper, listening/processing indicators, voice notes | Voice note end-to-end; indicator acceptance tests pass |
| **M3 Assistant + RAG** | 2 wk | llama.cpp service, model benchmark (≥ 3 models), hybrid retrieval, source chips, action-item extraction | Answers cite sources; latency targets §14 measured |
| **M4 OCR + Vision** | 1.5 wk | Scan flow, Tesseract vs PaddleOCR benchmark, local VLM trial | OCR doc searchable; accuracy report |
| **M5 Reminders + Power + MCU** | 2.5 wk | pm-remind, pm-power, Pico firmware v0 (protocol, buttons, battery, RTC alarm, WDT, mic interlock), S0–S5 | Reminder fires from S4 via RTC wake; controlled shutdown on low battery |
| **M6 Cloud adapter + privacy hardening** | 1.5 wk | pm-cloud, consent dialog/token, nftables egress, LUKS data, audit log, export/import | Privacy test suite passes; zero egress in local mode (pcap) |
| **M7 Updates + recovery** | 1.5 wk | RAUC A/B, signed bundles, health check, recovery partition, MCU FW update | Pull-power-during-update test passes 20/20 |
| **M8 Validation** | 2 wk | Battery/thermal/perf soak, 1-week dogfooding, custom PCB requirements doc | Report + go/no-go for custom carrier |

## B5. Test and acceptance criteria

**Functional**
- F1: Voice note: PTT → transcript saved and searchable within 5 s of release (10 s utterance), ≥ 90 % word accuracy on a quiet-room English test set [A-33].
- F2: Q&A over memory returns at least one correct source chip for ≥ 80 % of a 50-question gold set. Tapping the chip opens the exact span.
- F3: OCR of printed A4 page: ≥ 95 % character accuracy (CER ≤ 5 %) at good lighting.
- F4: Reminders fire within ±60 s of due time from S0, S2, and S4 (RTC wake). Missed reminders are shown after off-periods.
- F5: Export → factory reset → import restores all items, tags, reminders, and the consent log (hash chain verifies).
- F6: All features in §0 work with Wi-Fi disabled.

**Privacy (must pass, release-blocking)**
- PR1: Capture is impossible without a PTT event (fuzz pm-audio D-Bus API, attempt direct ALSA open from other service UIDs → EACCES).
- PR2: The REC LED is on 100 % of the time the mic is powered (logic analyzer on mic VDD vs LED, 1,000 PTT cycles).
- PR3: With the mute switch on, the PTT session refuses and the UI shows "Mic off (hardware)".
- PR4: In Local mode, zero packets leave the device from any pm-* UID except update checks (when enabled) over a 24 h pcap.
- PR5: Cloud requests without a valid token are rejected. Tokens can't be reused, the payload hash mismatch test passes, and every send has a `consent_log` row.
- PR6: Delete → item absent from FTS, vec, media, and page-level DB scan (`secure_delete`).
- PR7: No user content in journald (grep a test corpus of canary strings).

**Power / reliability**
- PW1: Measured current and battery life per state (S0 talk, S1, S2, S4). Report runtime with the chosen cell. Target set after M5 [A-34].
- PW2: 500 S2↔S0 cycles and 200 S4→boot cycles without failure. Boot < 15 s.
- PW3: Battery at 3 % → controlled shutdown completes, no DB corruption (`PRAGMA integrity_check` ok) over 50 runs.
- PW4: Kill pm-core / hang the CM5 → the MCU WDT resets within 35 s, boot_reason=wdt logged.
- PW5: Update power-pull test (random power cuts during install) leaves a bootable slot 20/20.

**Performance / thermal**
- PT1: §14 targets met or documented with a gap analysis.
- PT2: 30-min continuous Q&A loop in a 25 °C ambient, enclosed in a printed mock enclosure: no throttling above 80 °C with the active cooler. Report the passive-only result to guide the enclosure design.

---

## 16. Assumptions and open questions

| ID | Assumption / question |
|---|---|
| A-1 | pi-gen for the prototype, Yocto for the product. Confirm the build system preference. |
| A-2 | PipeWire vs plain ALSA. Decide after latency/memory measurement. |
| A-3 | IMX708 (Camera Module 3) as the CSI autofocus camera. The PRD only says "CSI autofocus". |
| A-4 | Secure boot / OTP key provisioning is used for the production LUKS key. Needs a manufacturing flow. |
| A-5 | The MCU firmware is updated from the CM5 (UART bootloader or SWD). |
| A-6 | Recovery button combo (Vol− + Power). |
| A-7 | Landscape 800×480 4.3" DSI. The PRD says "~800x480+", so the panel and orientation aren't chosen yet. |
| A-8 | Memory budgets are estimates to be measured. |
| A-9..A-13 | Model choices and performance numbers are expectations to benchmark, not facts. |
| A-14 | No cloud provider chosen. The adapter is OpenAI-compatible-API shaped. |
| A-15 | Default tz is the device setting. Asia/Kolkata is shown only as an example default. |
| A-16 | Hardware mic power cut + LED interlock on the custom PCB. On the prototype it's emulated via a load switch. |
| A-17 | MVP excludes "always use cloud" mode. Needs product confirmation. |
| A-18 | Default retention periods. |
| A-19 | Haptic motor. The PRD doesn't list one. |
| A-20 | Idle/off timeouts. |
| A-21 | CM5 suspend-to-RAM support is uncertain, so S3 may collapse into S4 + fast boot. |
| A-22 | Battery thresholds. |
| A-23 | UART is the primary link and I2C the alternate. |
| A-24 | External low-power RTC on the custom PCB. |
| A-25 | Production MCU part. The PRD says "low-power MCU if needed". |
| A-26 | Fuel gauge/charger part numbers are candidates. |
| A-27 | Pico board quiescent current isn't representative of the product. |
| A-28 | Performance targets are proposed, not from the PRD. |
| A-29 | BOM prices are rough. |
| A-30 | Battery capacity isn't specified in the PRD. It's constrained by the 125×75×18–24 mm, 200–300 g ID. |
| A-31 | Exact CM5 IO Board power/RUN header pinout must be verified against the official IO Board datasheet before wiring. |
| A-32 | Milestone durations assume one software engineer plus agent help. |
| A-33 | Test-set definitions (languages, noise conditions). |
| A-34 | The battery-life target isn't in the PRD. It needs a product target (e.g., "full day of typical use"). |

**Open questions for PM/hardware**
1. Display: a 4.3" 800×480 panel vs a higher-res panel. Is landscape the main orientation?
2. Battery capacity/runtime target, and is S4 + fast boot acceptable as "sleep" if CM5 suspend is not viable?
3. Is a dedicated low-power MCU confirmed (the architecture assumes yes, for privacy LED interlock, RTC wake, and battery supervision with the CM5 off)?
4. Languages required at launch (affects ASR/TTS/OCR models and storage).
5. Cloud provider(s), and is "ask each time" the only cloud mode for MVP?
6. Haptics: in or out?
7. Default retention policy, and is keeping raw audio ever the default?
8. Update delivery: who hosts update bundles and signing keys?
