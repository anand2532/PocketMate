import asyncio
import struct

import pytest
from conftest import arun

from pocketmate import config
from pocketmate.core.orchestrator import NO_SOURCES, Orchestrator
from pocketmate.engines.backends.stub import StubLLM
from pocketmate.ipc import framing
from pocketmate.ipc.rpc import RpcClient, RpcError, RpcServer


def test_framing_codecs():
    for pref in (True, False):
        b = framing.encode({"a": 1, "pcm": "x"}, prefer_msgpack=pref)
        (n,) = struct.unpack("<I", b[:4])
        assert n == len(b) - 4
        assert framing.decode_body(b[4], b[5:]) == {"a": 1, "pcm": "x"}
    with pytest.raises(framing.FrameError):
        framing.decode_body(9, b"")


def test_rpc_roundtrip_errors_and_signals(tmp_path):
    async def t():
        srv = RpcServer(tmp_path / "s.sock")

        @srv.method("add")
        async def add(a, b):
            return a + b

        @srv.method("boom")
        def boom():
            raise ValueError("nope")
        await srv.start()
        c = RpcClient(tmp_path / "s.sock")
        sigs = []
        c.on_signal(lambda n, a: sigs.append((n, a)))
        await c.connect()
        assert await c.call("add", a=2, b=3) == 5
        with pytest.raises(RpcError, match="ValueError"):
            await c.call("boom")
        with pytest.raises(RpcError, match="NoSuchMethod"):
            await c.call("nothing")
        await srv.emit("Thermal", stage=2)
        await asyncio.sleep(0.05)
        assert sigs == [("Thermal", {"stage": 2})]
        await c.close()
        await srv.stop()
    arun(t())


def test_orchestrator_routes(store):
    o = Orchestrator(store, llm=StubLLM(reply="You met Ravi [1]."))

    async def t():
        a = await o.handle("note: Ravi ka number 98xxxx")
        assert a.kind == "note_saved" and store.get_item(a.item_id)
        b = await o.handle("remind me to call mom kal subah 9 baje")
        assert b.kind == "reminder_suggested" and b.needs_confirmation
        c = await o.handle("Who is Ravi?")
        assert c.kind == "answer" and c.sources and c.source_label is None
        d = await o.handle("What is the capital of France?")
        assert d.kind == "answer" and d.sources == [] and d.source_label == NO_SOURCES
        e = await o.handle("search Ravi")
        assert e.kind == "search" and e.sources
    arun(t())


def test_orchestrator_without_llm_is_extractive(store):
    store.add_note("wifi password is on the fridge")
    a = arun(Orchestrator(store).handle("where is the wifi password"))
    assert "fridge" in a.text and a.sources


def test_config_defaults_and_roundtrip(tmp_path):
    p = tmp_path / "s.toml"
    p.write_text('[cloud]\nenabled = true\n[asr]\nmodel = "x.bin"\n')
    c = config.load(p)
    assert c["cloud"]["enabled"] and c["asr"]["model"] == "x.bin" and c["asr"]["partials"] == "vosk"
    assert config.load(tmp_path / "missing.toml")["llm"]["model"] == "llama-3.2-1b-instruct-q4_k_m.gguf"
    assert config.load(tmp_path / "missing.toml")["cloud"]["enabled"] is False
    config.save(c, tmp_path / "o.toml")
    assert config.load(tmp_path / "o.toml") == c
