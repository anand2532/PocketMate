"""pm-lte: LTE board bring-up and policy executor (§19). Powers the module with pm-lte-power, runs the
Quectel init profile (LTE-only, RX diversity off on EC25, GNSS on), tells pm-power the board is present
(MCU clamps VREG <= 4.24 V), then follows pm-power's `lte_governor` decision every 2 s.
Data connection: systemd-networkd (.network files in lte/network); APN from settings.toml [lte] apn."""
from __future__ import annotations

import asyncio
import logging
import os
import subprocess
from pathlib import Path

from .. import config
from ..ipc.rpc import RpcClient
from ..lte.at import AtClient, apply_profile
from ..lte.controller import LteController
from ..lte.quectel import by_usb_id
from ._common import parser, run, sd_notify, setup_logging

log = logging.getLogger("pm.lte")
POWER_TOOL = os.environ.get("PM_LTE_POWER", "/usr/lib/pocketmate/pm-lte-power")
AT_PORT = os.environ.get("PM_LTE_AT", "/dev/pm-lte-at")
WWAN_IF = os.environ.get("PM_LTE_IF", "wwan0")


def _usb_id() -> tuple[int, int] | None:
    for d in Path("/sys/bus/usb/devices").glob("*"):
        try:
            if (d / "idVendor").read_text().strip() == "2c7c":
                return 0x2C7C, int((d / "idProduct").read_text().strip(), 16)
        except OSError:
            continue
    return None


class SerialPort:
    """Raw tty without pyserial (stdlib termios)."""
    def __init__(self, path: str) -> None:
        import termios
        import tty
        self.fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        tty.setraw(self.fd)
        attrs = termios.tcgetattr(self.fd)
        attrs[6][termios.VMIN], attrs[6][termios.VTIME] = 0, 1
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
        os.set_blocking(self.fd, True)

    def write(self, data: bytes) -> int:
        return os.write(self.fd, data)

    def read(self, n: int) -> bytes:
        return os.read(self.fd, n)

    def close(self) -> None:
        os.close(self.fd)


def _shape(rate: str | None) -> None:
    cmd = (["tc", "qdisc", "replace", "dev", WWAN_IF, "root", "tbf", "rate", rate, "burst", "32kbit", "latency", "400ms"]
           if rate else ["tc", "qdisc", "del", "dev", WWAN_IF, "root"])
    subprocess.run(cmd, check=False, capture_output=True)


async def _main(stop: asyncio.Event, args) -> None:
    sec = config.load().get("lte", {})
    power = RpcClient(Path(args.run_dir) / "power.sock")
    await power.connect()
    if sec.get("enabled") is False:
        await power.call("lte_present", present=False)
        subprocess.run([POWER_TOOL, "off"], check=False)
        log.info("LTE disabled in settings; module held off")
        sd_notify("READY=1")
        await stop.wait()
        return
    rc = subprocess.run([POWER_TOOL, "on"], check=False).returncode
    await power.call("lte_present", present=True)     # fitted (rc!=0 still means LTE_VBAT is connected)
    ids = _usb_id()
    prof = by_usb_id(*ids) if ids else None
    if rc != 0 or prof is None:
        log.error("LTE module did not enumerate (rc=%s, usb=%s); see pm-lte-power status", rc, ids)
    ctl = LteController()
    at: AtClient | None = None
    if prof is not None and Path(AT_PORT).exists():
        port = SerialPort(AT_PORT)
        at = AtClient(port)
        res = await asyncio.to_thread(apply_profile, at, prof)
        log.info("LTE %s init: %s", prof.name, ", ".join(f"{k.split('=')[0]}={v}" for k, v in res.items()))
    sd_notify("READY=1")
    while not stop.is_set():
        try:
            d = await power.call("lte_governor")
        except Exception as e:  # noqa: BLE001 - pm-power restart: fail safe to airplane mode
            log.warning("pm-power unavailable (%s): airplane mode", type(e).__name__)
            d = {"tx": "block", "rat": "lte"}
        for act in ctl.apply(d):
            if act[0] == "power":
                await asyncio.to_thread(subprocess.run, [POWER_TOOL, act[1]], check=False)
            elif act[0] == "init" and at is not None and prof is not None:
                await asyncio.to_thread(apply_profile, at, prof)
            elif act[0] == "at" and at is not None:
                r = await asyncio.to_thread(at.cmd, act[1], 5.0)
                log.info("LTE %s -> %s", act[1].split("=")[0], "ok" if r.ok else "error")
            elif act[0] == "shape":
                await asyncio.to_thread(_shape, act[1])
        try:
            await asyncio.wait_for(stop.wait(), 2.0)
        except TimeoutError:
            pass
    await power.close()


def main() -> None:
    p = parser("pm-lte", __doc__ or "")
    args = p.parse_args()
    setup_logging(args.log_level)
    run(lambda stop: _main(stop, args))
