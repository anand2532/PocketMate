"""pm-power: owns the MCU link (/dev/ttyAMA0), thermal governor, power cap, radio leases; serves
mic_enable for pm-audio and forwards MCU events as signals. `--sim` uses the in-process MCU simulator."""
from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path

from .. import config
from ..ipc.rpc import RpcServer
from ..lte.governor import LteGovConfig, LteGovernor, LteInputs, Tx, gauge_to_discharge_mA
from ..mcu.link import LinkDown, McuLink, Nak
from ..mcu.messages import PROTO_VER, LightCase, Status, ThermalStage, msg
from ..power.actuators import Backlight, CpuControl, Rfkill, Sysfs
from ..power.governor import CPU_UI_KHZ, Governor, ThermalInputs
from ..power.radio import RadioLeaseManager
from ._common import parser, run, sd_notify, setup_logging

log = logging.getLogger("pm.power")


def lte_config(sec: dict) -> LteGovConfig:
    """settings.toml [lte]: cell = "production" (5.5 A) | "prototype" (Akyga 2.5 A cap); allow_2g opt-in."""
    base = LteGovConfig.prototype_akyga() if sec.get("cell") == "prototype" else LteGovConfig()
    import dataclasses
    return dataclasses.replace(base, allow_2g=bool(sec.get("allow_2g", False)))


class PowerService:
    def __init__(self, link: McuLink, fs: Sysfs, lte_cfg: LteGovConfig | None = None) -> None:
        self.link, self.fs = link, fs
        self.gov = Governor()
        self.cpu, self.bl = CpuControl(fs), Backlight(fs)
        self.radios = RadioLeaseManager(Rfkill(fs).set_blocked, time.monotonic)
        self.last: dict[str, dict] = {}
        self.case = LightCase.HELD
        self.rpc: RpcServer | None = None
        self.lte_gov = LteGovernor(lte_cfg or LteGovConfig())
        self.lte_decision = None
        self._ocp_pending = False
        self._thermal_khz: int | None = None
        link.on_event(self.on_event)

    def soc_c(self) -> float:
        try:
            return int(self.fs.read("sys/class/thermal/thermal_zone0/temp", "45000")) / 1000
        except ValueError:
            return 45.0

    async def on_event(self, m) -> None:
        self.last[m.name] = dict(m.fields)
        if m.name == "EVT_THERMAL":
            f = m.fields
            a = self.gov.update(ThermalInputs(time.monotonic(), None if f["adc_fault"] else f["case_ntc_dC"] / 10,
                                              self.soc_c(), 0.0, case=self.case))
            self._thermal_khz = a.cpu_max_khz
            self._apply_cpu()
            await self._emit("Thermal", stage=int(a.stage), allow_local_ai=a.allow_new_local_ai,
                             offer_cloud=a.offer_cloud)
        elif m.name == "EVT_LIGHT":
            self.case = LightCase(m.fields["case"])
        elif m.name == "EVT_BUTTON":
            await self._emit("Button", **m.fields)
        elif m.name == "EVT_MIC_MUTE":
            await self._emit("MicMute", muted=m.fields["muted"], valid=m.fields["valid"])
        elif m.name == "EVT_MIC_RAIL":
            await self._emit("MicRail", **m.fields)
        elif m.name == "EVT_SHUTDOWN_REQ":
            await self._emit("ShutdownRequested", **m.fields)
        elif m.name == "EVT_OVERCURRENT":
            self._ocp_pending = True
        elif m.name == "EVT_BATTERY":
            await self._emit("Battery", soc=m.fields["soc"], charging=bool(m.fields["chg"]))
            await self.lte_update(time.monotonic(), m.fields["mV"], gauge_to_discharge_mA(m.fields["mA"]))

    def _apply_cpu(self) -> None:
        khz = self._thermal_khz
        if self.lte_decision is not None and self.lte_decision.throttled:
            khz = min(khz or CPU_UI_KHZ, CPU_UI_KHZ)       # power-config.md: cap cpufreq while over 5.5 A
        if khz is not None:
            self.cpu.set_max_khz(khz)

    async def lte_update(self, t: float, cell_mV: int, discharge_mA: int) -> None:
        """LTE governor step (§19.5). Light = thermal governor allows new local AI and no cap active."""
        light = self.gov.stage == ThermalStage.NORMAL
        d = self.lte_gov.update(LteInputs(t, cell_mV, discharge_mA, light, self._ocp_pending))
        self._ocp_pending = False
        changed = self.lte_decision is None or (d.tx, d.rat, d.throttled) != (
            self.lte_decision.tx, self.lte_decision.rat, self.lte_decision.throttled)
        self.lte_decision = d
        if changed:
            log.info("LTE governor: tx=%s rat=%s reasons=%s", d.tx.value, d.rat.value, ",".join(d.reasons))
            self._apply_cpu()
            await self._emit("LteGovernor", tx=d.tx.value, rat=d.rat.value, throttled=d.throttled,
                             reasons=list(d.reasons))

    async def _emit(self, sig: str, **kw) -> None:
        if self.rpc:
            await self.rpc.emit(sig, **kw)

    async def hello(self) -> dict:
        await self.link.send(msg("HELLO", proto_ver=PROTO_VER, cm5_fw_ver=0x000400))
        await asyncio.sleep(0.1)
        return self.last.get("HELLO_ACK", {})

    def register(self, rpc: RpcServer) -> None:
        self.rpc = rpc

        @rpc.method("ping")
        def _ping() -> bool:
            return self.link.up

        @rpc.method("mic_enable")
        async def _mic(on: bool, session_id: int, mode: int, max_s: int) -> int:
            try:
                await self.link.send(msg("MIC_ENABLE", on=int(on), session_id=session_id, mode=mode, max_s=max_s))
            except Nak as e:
                return int(e.status)
            except LinkDown:
                return int(Status.CM5_DOWN)
            return int(Status.OK)

        @rpc.method("set_wake")
        async def _wake(epoch_s: int) -> bool:
            await self.link.send(msg("SET_WAKE", epoch_s=epoch_s))
            return True

        @rpc.method("status")
        def _status() -> dict:
            return {"link_up": self.link.up, "stage": int(self.gov.stage), "stats": self.link.stats,
                    "last": self.last}

        @rpc.method("lte_governor")
        def _lte_gov() -> dict:
            d = self.lte_decision
            if d is None:                      # no battery telemetry yet: fail safe, LTE TX blocked
                return {"tx": Tx.BLOCK.value, "rat": "lte", "throttled": False, "reasons": ["no_telemetry"]}
            return {"tx": d.tx.value, "rat": d.rat.value, "throttled": d.throttled, "reasons": list(d.reasons)}

        @rpc.method("lte_present")
        async def _lte_present(present: bool) -> int:
            """pm-lte reports whether the LTE board answered. MCU clamps VREG <= 4.24 V while present."""
            try:
                await self.link.send(msg("LTE_CFG", present=int(present), vreg_max_mV=4240))
            except Nak as e:
                return int(e.status)
            except LinkDown:
                return int(Status.CM5_DOWN)
            return int(Status.OK)

        @rpc.method("radio_acquire")
        def _acq(radio: str, purpose: str, timeout_s: float = 60.0) -> int:
            return self.radios.acquire(radio, purpose, timeout_s).id

        @rpc.method("radio_release")
        def _rel(lease_id: int) -> bool:
            ls = self.radios.leases.get(lease_id)
            if ls:
                self.radios.release(ls)
            return ls is not None


async def _main(stop: asyncio.Event, args) -> None:
    if args.sim:
        from ..mcu.simulator import McuSimulator
        from ..mcu.transport import loopback_pair
        a, b = loopback_pair()
        sim = McuSimulator(b)
        await sim.start()
        link = McuLink(a)
    else:
        from ..mcu.transport import SerialTransport
        link = McuLink(SerialTransport(args.port))
    await link.start()
    svc = PowerService(link, Sysfs(args.sysfs_root), lte_config(config.load().get("lte", {})))
    rpc = RpcServer(Path(args.run_dir) / "power.sock")
    svc.register(rpc)
    await rpc.start()
    try:
        log.info("HELLO_ACK %s", await svc.hello())
    except (LinkDown, Nak) as e:
        log.error("MCU HELLO failed: %s", e)
    link.start_heartbeat()
    sd_notify("READY=1")
    while not stop.is_set():
        svc.radios.tick()
        try:
            await asyncio.wait_for(stop.wait(), 1.0)
        except TimeoutError:
            pass
    await rpc.stop()
    await link.stop()


def main() -> None:
    p = parser("pm-power", __doc__ or "")
    p.add_argument("--port", default="/dev/ttyAMA0")
    p.add_argument("--sysfs-root", default="/")
    p.add_argument("--sim", action="store_true")
    args = p.parse_args()
    setup_logging(args.log_level)
    run(lambda stop: _main(stop, args))
