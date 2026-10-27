import hashlib
import json

from conftest import arun

from pocketmate.engines import registry
from pocketmate.engines.backends.stub import StubASR, StubLLM, StubOCR, StubTranslate, StubTTS
from pocketmate.engines.types import (
    ASREngine,
    AudioChunk,
    AudioFormat,
    ChatMessage,
    GenParams,
    ImageRef,
    LLMEngine,
    OCREngine,
    TranslationEngine,
    TTSEngine,
    new_ctx,
)
from pocketmate.health import HealthReport, mark, run_checks
from pocketmate.profile import build, to_toml


def _root(tmp_path, model, mem_kb):
    dt = tmp_path / "proc/device-tree"
    dt.mkdir(parents=True)
    (dt / "model").write_bytes(model.encode() + b"\x00")
    (tmp_path / "proc/meminfo").write_text(f"MemTotal:       {mem_kb} kB\n")
    return tmp_path


def test_profile_detection_and_manifest(tmp_path):
    r = _root(tmp_path, "Raspberry Pi Compute Module 5 Rev 1.0", 4_000_000)
    md = tmp_path / "models"
    md.mkdir()
    (md / "a.bin").write_bytes(b"asr")
    man = {"models": [{"role": "asr", "file": "a.bin", "sha256": hashlib.sha256(b"asr").hexdigest(),
                       "skus": ["cm5-4g"]},
                      {"role": "llm", "file": "l.gguf", "sha256": "0", "skus": ["cm5-4g"]}]}
    (md / "manifest.json").write_text(json.dumps(man))
    p = build(r, md / "manifest.json")
    assert p.sku == "cm5-4g" and p.supported and "asr" in p.models and "llm" in p.missing
    assert 'sku = "cm5-4g"' in to_toml(p)


def test_profile_2g_unsupported(tmp_path):
    p = build(_root(tmp_path, "Raspberry Pi Compute Module 5", 2_000_000), tmp_path / "none.json")
    assert p.sku == "cm5-2g" and not p.supported


def test_health_checks():
    async def ok():
        return True
    calls = {"n": 0}

    async def flaky():
        calls["n"] += 1
        return calls["n"] >= 2
    rep = arun(run_checks({"a": ok, "b": flaky}, deadline_s=5, retry_s=0.01))
    assert rep.ok
    async def bad():
        return False
    assert not arun(run_checks({"a": bad}, deadline_s=0.05, retry_s=0.01)).ok
    assert mark(True, dry_run=True) == ["rauc", "status", "mark-good"]
    assert not HealthReport().ok


def test_stubs_satisfy_protocols():
    assert isinstance(StubASR(), ASREngine) and isinstance(StubLLM(), LLMEngine)
    assert isinstance(StubOCR(), OCREngine) and isinstance(StubTTS(), TTSEngine)
    assert isinstance(StubTranslate(), TranslationEngine)


def test_stub_engines_run():
    async def t():
        ctx = new_ctx("voice")

        async def audio():
            for i in range(20):
                yield AudioChunk(b"\0" * 640, i, i * 20, i == 19)
        segs = [s async for s in StubASR(script="hello duniya").stream(ctx, AudioFormat(), audio())]
        assert segs[-1].is_final and segs[-1].text == "hello duniya"
        toks = [d async for d in StubLLM(reply="a b c").generate(ctx, [ChatMessage("user", "x")], GenParams())]
        assert "".join(d.text for d in toks) == "a b c" and toks[-1].finish_reason == "stop"
        assert await StubLLM().count_tokens("abcdefgh") == 2 and StubLLM().context_window == 4096
        r = await StubOCR().recognize(ctx, ImageRef("x.jpg", 100, 100))
        assert r.blocks[1].script == "Deva"
        tts = StubTTS()
        chunks = [c async for c in tts.synthesize(ctx, "Hello. Namaste.", tts.voices()[0])]
        assert chunks[-1].is_last
        tr = await StubTranslate().translate(ctx, ["namaste"], None, "en")
        assert tr[0].tgt_lang == "en"
    arun(t())


def test_registry_lists_and_creates():
    assert "stub" in registry.available("llm")
    assert isinstance(registry.create("asr", "stub"), StubASR)
