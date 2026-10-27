import asyncio

from conftest import arun

from pocketmate.mcu.link import McuLink
from pocketmate.mcu.simulator import McuSimulator
from pocketmate.mcu.transport import loopback_pair
from pocketmate.power.actuators import Sysfs
from pocketmate.power.governor import CPU_UI_KHZ
from pocketmate.services.pm_power import PowerService


async def _svc(tmp_path):
    for n in range(4):
        (tmp_path / f"sys/devices/system/cpu/cpu{n}/cpufreq").mkdir(parents=True)
    a, b = loopback_pair()
    sim = McuSimulator(b)
    link = McuLink(a, ack_timeout=0.1, preamble_gap=0)
    svc = PowerService(link, Sysfs(tmp_path))
    signals = []

    async def emit(name, **kw):
        signals.append((name, kw))
    svc._emit = emit
    await sim.start()
    await link.start()
    return svc, sim, link, signals


def test_battery_events_drive_lte_governor_and_cpu_cap(tmp_path):
    async def t():
        svc, sim, link, sig = await _svc(tmp_path)
        await sim.battery(3900, -1000)
        await asyncio.sleep(0.05)
        assert svc.lte_decision.tx.value == "allow"
        await svc.lte_update(100.0, 3900, 6000)
        await svc.lte_update(101.0, 3900, 6000)
        assert svc.lte_decision.throttled
        cap = (tmp_path / "sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq")
        assert cap.exists() and int(cap.read_text()) <= CPU_UI_KHZ
        assert any(n == "LteGovernor" and k["tx"] == "throttle" for n, k in sig)
        await sim.overcurrent(6000)
        await sim.battery(3500, -500)
        await asyncio.sleep(0.05)
        assert svc.lte_decision.tx.value == "block"
        await link.stop(); await sim.stop()
    arun(t())


def test_lte_present_sends_cfg_to_mcu(tmp_path):
    async def t():
        svc, sim, link, _ = await _svc(tmp_path)
        from pocketmate.mcu.messages import msg
        await link.send(msg("LTE_CFG", present=0, vreg_max_mV=4240))
        assert sim.lte_present is False and sim.vreg_max_mV == 4240
        from pocketmate.mcu.link import Nak
        try:
            await link.send(msg("LTE_CFG", present=1, vreg_max_mV=4300))
            raise AssertionError("expected RANGE")
        except Nak:
            pass
        await link.stop(); await sim.stop()
    arun(t())


def test_lte_config_from_settings():
    from pocketmate.services.pm_power import lte_config
    assert lte_config({}).throttle_on_mA == 5500 and not lte_config({}).allow_2g
    c = lte_config({"cell": "prototype", "allow_2g": True})
    assert c.throttle_on_mA == 2500 and c.allow_2g
