"""settings.toml (§6.6) with SKU-profile defaults (§6.11). Missing keys fall back to DEFAULTS."""
from __future__ import annotations

import copy
import os
import tomllib
from pathlib import Path
from typing import Any

SETTINGS_PATH = Path(os.environ.get("PM_SETTINGS", "/var/lib/pm/settings.toml"))
STATE_DIR = Path(os.environ.get("PM_STATE_DIR", "/var/lib/pm"))
RUN_DIR = Path(os.environ.get("PM_RUN_DIR", "/run/pm"))

DEFAULTS: dict[str, Any] = {
    "profile": {"sku": "auto", "mode": "local", "primary_language": "hinglish"},
    "asr": {"backend": "whispercpp", "model": "hinglish-small-q5_0.bin", "partials": "vosk",
            "partial_models": ["en-in-small", "hi-small"]},
    "llm": {"backend": "llamacpp", "model": "llama-3.2-1b-instruct-q4_k_m.gguf", "ctx": 4096},
    "ocr": {"backend": "paddleocr", "doc_langs": ["en", "hi"], "scene_backend": "indicphotoocr"},
    "translate": {"backend": "indictrans2-dist-ct2", "pairs": ["hi-en", "en-hi", "indic-en"]},
    "tts": {"backend": "piper", "voices": {"en": "en_US-lessac-medium", "hi": "hi_IN-pratham-medium"}},
    "vision": {"backend": "llamacpp-mtmd", "model": "smolvlm-500m"},
    "embed": {"backend": "llamacpp", "model": "multilingual-e5-small-q8_0.gguf", "enabled": True},
    "summary": {"enabled": False, "time": "20:30"},
    "cloud": {"enabled": False},
    # LTE board (§19). Governor thresholds: see pocketmate/lte/governor.py. allow_2g is opt-in.
    "lte": {"enabled": "auto", "allow_2g": False, "cell": "production", "apn": ""},
}


def _merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load(path: str | Path | None = None) -> dict[str, Any]:
    p = Path(path) if path else SETTINGS_PATH
    user = tomllib.loads(p.read_text()) if p.exists() else {}
    return _merge(DEFAULTS, user)


def _toml_value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, list):
        return "[" + ", ".join(_toml_value(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {_toml_value(x)}" for k, x in v.items()) + " }"
    raise TypeError(type(v))


def dump(cfg: dict[str, Any]) -> str:
    lines = ["# PocketMate settings (§6.6). Written by pm-core; safe to hand-edit while services are stopped."]
    for sec, kv in cfg.items():
        lines.append(f"\n[{sec}]")
        lines += [f"{k} = {_toml_value(v)}" for k, v in kv.items()]
    return "\n".join(lines) + "\n"


def save(cfg: dict[str, Any], path: str | Path | None = None) -> None:
    p = Path(path) if path else SETTINGS_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(dump(cfg))
    os.replace(tmp, p)
