import asyncio

import pytest
from conftest import arun

from pocketmate.audio.capture import SimCapture
from pocketmate.audio.ptt import CaptureRefused, PttController, Refusal, link_mic_enable
from pocketmate.mcu.link import McuLink
from pocketmate.mcu.messages import ButtonAction, ButtonId, MicMode
from pocketmate.mcu.simulator import McuSimulator
from pocketmate.mcu.transport import loopback_pair


async def rig(muted=False):
    a, b = loopback_pair()
    sim = McuSimulator(b)
    link = McuLink(a, ack_timeout=0.1, preamble_gap=0)
    cap = SimCapture(pace=True)
    ptt = PttController(cap, link_mic_enable(link))
    link.on_event(ptt.on_mcu_event)
    await sim.start()
    await link.start()
    await sim.set_mute(muted)
    await asyncio.sleep(0.02)
    return sim, link, cap, ptt


async def teardown(sim, link):
    await link.stop()
    await sim.stop()


def test_muted_refuses_and_never_opens_capture():
    async def t():
        sim, link, cap, ptt = await rig(muted=True)
        await sim.press(ButtonId.ACTION, ButtonAction.DOWN)
        for _ in range(100):
            with pytest.raises(CaptureRefused) as e:
                await ptt.start(MicMode.HOLD)
            assert e.value.why == Refusal.MUTED
        assert cap.opens == 0 and ptt.frame_counter == 0 and not sim.priv.mic_pwr_en
        await teardown(sim, link)
    arun(t())


def test_fail_closed_before_first_mute_report():
    async def t():
        cap = SimCapture()

        async def never(*_):
            raise AssertionError("must not call MCU")
        ptt = PttController(cap, never)
        with pytest.raises(CaptureRefused) as e:
            await ptt.start()
        assert e.value.why == Refusal.MUTE_INVALID and cap.opens == 0
    arun(t())


def test_no_ptt_refused_by_mcu():
    async def t():
        sim, link, cap, ptt = await rig()
        with pytest.raises(CaptureRefused) as e:
            await ptt.start(MicMode.HOLD)
        assert e.value.why == Refusal.NO_PTT and cap.opens == 0
        await teardown(sim, link)
    arun(t())


def test_hold_session_streams_and_stops():
    async def t():
        sim, link, cap, ptt = await rig()
        await sim.press(ButtonId.ACTION, ButtonAction.DOWN)
        it = await ptt.start(MicMode.HOLD)
        assert cap.is_open and sim.priv.mic_pwr_en
        await asyncio.sleep(0.15)
        r = await ptt.stop()
        chunks = [c async for c in it]
        assert chunks[-1].is_last and len(chunks) - 1 == r.frames >= 3
        assert all(len(c.pcm) == 640 for c in chunks[:-1])
        await asyncio.sleep(0.02)
        assert not cap.is_open and not sim.priv.mic_pwr_en
        await teardown(sim, link)
    arun(t())


def test_mid_session_mute_closes_fast_and_discards():
    async def t():
        sim, link, cap, ptt = await rig()
        await sim.press(ButtonId.ACTION, ButtonAction.DOWN)
        it = await ptt.start(MicMode.HOLD)
        await asyncio.sleep(0.12)
        await sim.set_mute(True)
        await asyncio.sleep(0.05)
        got = [c async for c in it]
        assert got == [], "partial buffer must be discarded"
        assert ptt.last_abort.discarded and ptt.last_abort.end_reason in ("mute", "rail_off:3")
        assert ptt.last_abort.close_latency_ms < 20
        assert not cap.is_open and not sim.priv.mic_pwr_en
        await teardown(sim, link)
    arun(t())


def test_tap_mode_requires_recent_press():
    async def t():
        sim, link, cap, ptt = await rig()
        await sim.press(ButtonId.ACTION, ButtonAction.DOWN)
        await sim.press(ButtonId.ACTION, ButtonAction.UP)
        it = await ptt.start(MicMode.TAP)
        await ptt.stop()
        _ = [c async for c in it]
        with pytest.raises(CaptureRefused):
            await ptt.start(MicMode.TAP)            # the press was consumed
        await teardown(sim, link)
    arun(t())
