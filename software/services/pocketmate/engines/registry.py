"""Backend registry. Backends are selected by settings.toml (§6.9) and resolved through the
`pocketmate.engines.<kind>` entry points, with a built-in table so it works uninstalled too.
Local backends import their heavy dependencies lazily: a missing wheel raises EngineError at
load(), never at import time."""
from __future__ import annotations

import importlib
from importlib import metadata

_BUILTIN = {
    "asr": {"stub": "pocketmate.engines.backends.stub:StubASR",
            "whispercpp": "pocketmate.engines.backends.whispercpp:WhisperCppASR"},
    "llm": {"stub": "pocketmate.engines.backends.stub:StubLLM",
            "llamacpp": "pocketmate.engines.backends.llamacpp:LlamaCppLLM"},
    "embed": {"stub": "pocketmate.engines.backends.stub:StubEmbedding",
              "llamacpp": "pocketmate.engines.backends.llamacpp:LlamaCppEmbedding"},
    "ocr": {"stub": "pocketmate.engines.backends.stub:StubOCR",
            "paddleocr": "pocketmate.engines.backends.paddleocr:PaddleOCR"},
    "tts": {"stub": "pocketmate.engines.backends.stub:StubTTS",
            "piper": "pocketmate.engines.backends.piper:PiperTTS"},
    "translate": {"stub": "pocketmate.engines.backends.stub:StubTranslate"},
    "vision": {"stub": "pocketmate.engines.backends.stub:StubVision"},
}


def _load(spec: str):
    mod, _, attr = spec.partition(":")
    return getattr(importlib.import_module(mod), attr)


def available(kind: str) -> list[str]:
    names = set(_BUILTIN.get(kind, {}))
    try:
        names |= {ep.name for ep in metadata.entry_points(group=f"pocketmate.engines.{kind}")}
    except Exception:  # pragma: no cover
        pass
    return sorted(names)


def create(kind: str, name: str, **kwargs):
    try:
        eps = {ep.name: ep for ep in metadata.entry_points(group=f"pocketmate.engines.{kind}")}
    except Exception:  # pragma: no cover
        eps = {}
    if name in eps:
        cls = eps[name].load()
    elif name in _BUILTIN.get(kind, {}):
        cls = _load(_BUILTIN[kind][name])
    else:
        raise KeyError(f"no {kind} backend {name!r}; available: {available(kind)}")
    return cls(**kwargs)
