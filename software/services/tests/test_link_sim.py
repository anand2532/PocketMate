import asyncio

import pytest
from conftest import arun

from pocketmate.mcu.link import LinkDown, McuLink, Nak
from pocketmate.mcu.messages import PROTO_VER, ButtonAction, ButtonId, MicMode, Status, msg
from pocketmate.mcu.simulator import McuSimulator
from pocketmate.mcu.transport import loopback_pair


async def _pair():
    a, b = loopback_pair()
    sim = McuSimulator(b)
    link = McuLink(a, ack_timeout=0.1, preamble_gap=0)
    events = []
    link.on_event(lambda m: events.append(m))
    await sim.start()
    await link.start()
    return link, sim, events, a


def test_hello_and_hello_ack():
    async def t():
        link, sim, ev, _ = await _pair()
        await link.send(msg("HELLO", proto_ver=PROTO_VER, cm5_fw_ver=1))
        await asyncio.sleep(0.05)
        assert any(e.name == "HELLO_ACK" for e in ev)
        with pytest.raises(Nak) as ei:
            await link.send(msg("HELLO", proto_ver=99, cm5_fw_ver=1))
        assert ei.value.status == Status.BAD_VERSION
        await link.stop(); await sim.stop()
    arun(t())


def test_retry_then_linkdown():
    async def t():
        link, sim, _, _ = await _pair()
        sim.ignore_next = 1
        await link.send(msg("HEARTBEAT", uptime_s=1, cm5_state=0))
        assert link.stats["retries"] == 1
        sim.ignore_next = 10
        with pytest.raises(LinkDown):
            await link.send(msg("HEARTBEAT", uptime_s=2, cm5_state=0))
        assert not link.up
        await link.stop(); await sim.stop()
    arun(t())


def test_time_get_set():
    async def t():
        link, sim, _, _ = await _pair()
        await link.send(msg("TIME", tail=(1_800_000_000).to_bytes(4, "little")))
        ack = await link.send(msg("TIME"))
        assert int.from_bytes(ack.tail, "little") == 1_800_000_000
        await link.stop(); await sim.stop()
    arun(t())


def test_mic_enable_requires_ptt_and_unmuted():
    async def t():
        link, sim, ev, _ = await _pair()
        with pytest.raises(Nak) as e1:
            await link.send(msg("MIC_ENABLE", on=1, session_id=1, mode=int(MicMode.HOLD), max_s=0))
        assert e1.value.status == Status.NO_PTT
        await sim.press(ButtonId.ACTION, ButtonAction.DOWN)
        await link.send(msg("MIC_ENABLE", on=1, session_id=2, mode=int(MicMode.HOLD), max_s=0))
        await asyncio.sleep(0.05)
        assert any(e.name == "EVT_MIC_RAIL" and e.fields["on"] == 1 for e in ev)
        await sim.set_mute(True)
        await asyncio.sleep(0.05)
        assert any(e.name == "EVT_MIC_RAIL" and e.fields["on"] == 0 for e in ev)
        with pytest.raises(Nak) as e2:
            await link.send(msg("MIC_ENABLE", on=1, session_id=3, mode=int(MicMode.HOLD), max_s=0))
        assert e2.value.status == Status.MUTED
        await link.stop(); await sim.stop()
    arun(t())


def test_events_are_acked_and_deduped():
    async def t():
        link, sim, ev, _ = await _pair()
        await sim.thermal(350)
        await asyncio.sleep(0.05)
        n = len([e for e in ev if e.name == "EVT_THERMAL"])
        assert n == 1
        await link.stop(); await sim.stop()
    arun(t())
