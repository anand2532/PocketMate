import asyncio

from conftest import arun

from pocketmate.ipc.rpc import RpcClient, RpcServer
from pocketmate.lte.controller import THROTTLE_RATE, LteController
from pocketmate.lte.quectel import AIRPLANE_OFF, AIRPLANE_ON, RAT_CMD


def test_allow_then_idempotent():
    c = LteController()
    a = c.apply({"tx": "allow", "rat": "lte", "throttled": False})
    assert ("at", AIRPLANE_OFF) in a and ("at", RAT_CMD["lte"]) in a and ("shape", None) in a
    assert c.apply({"tx": "allow", "rat": "lte"}) == []


def test_block_airplane_and_back():
    c = LteController()
    c.apply({"tx": "allow", "rat": "lte"})
    assert c.apply({"tx": "block", "rat": "lte"}) == [("at", AIRPLANE_ON)]
    assert c.apply({"tx": "allow", "rat": "lte"}) == [("at", AIRPLANE_OFF)]


def test_throttle_shapes_and_releases():
    c = LteController()
    c.apply({"tx": "allow", "rat": "lte"})
    assert c.apply({"tx": "throttle", "rat": "lte"}) == [("shape", THROTTLE_RATE)]
    assert c.apply({"tx": "allow", "rat": "lte"}) == [("shape", None)]


def test_shutdown_powers_off_once_and_reinits():
    c = LteController()
    c.apply({"tx": "allow", "rat": "lte"})
    assert c.apply({"tx": "shutdown"}) == [("power", "off")]
    assert c.apply({"tx": "shutdown"}) == []
    a = c.apply({"tx": "allow", "rat": "lte"})
    assert a[:2] == [("power", "on"), ("init",)] and ("at", AIRPLANE_OFF) in a


def test_rat_change_to_2g_and_missing_fields_fail_safe():
    c = LteController()
    c.apply({"tx": "allow", "rat": "lte"})
    assert c.apply({"tx": "allow", "rat": "lte+gsm"}) == [("at", RAT_CMD["lte+gsm"])]
    assert c.apply({}) == [("at", AIRPLANE_ON)]        # no tx -> block


def test_pm_power_rpc_lte_governor_roundtrip(tmp_path):
    from pocketmate.mcu.link import McuLink
    from pocketmate.mcu.simulator import McuSimulator
    from pocketmate.mcu.transport import loopback_pair
    from pocketmate.power.actuators import Sysfs
    from pocketmate.services.pm_power import PowerService

    async def t():
        a, b = loopback_pair()
        sim = McuSimulator(b)
        link = McuLink(a, ack_timeout=0.1, preamble_gap=0)
        svc = PowerService(link, Sysfs(tmp_path))
        rpc = RpcServer(tmp_path / "power.sock")
        svc.register(rpc)
        await rpc.start(); await sim.start(); await link.start()
        cli = RpcClient(tmp_path / "power.sock"); await cli.connect()
        assert (await cli.call("lte_governor"))["tx"] == "block"       # no telemetry yet
        await sim.battery(3900, -800)
        await asyncio.sleep(0.05)
        assert (await cli.call("lte_governor"))["tx"] == "allow"
        assert await cli.call("lte_present", present=False) == 0
        assert sim.lte_present is False
        await cli.close(); await rpc.stop(); await link.stop(); await sim.stop()
    arun(t())
