"""Software MCU for development and tests: speaks the §11 protocol over any Transport and runs
the privacy interlock model. `pm-mcu-sim --pty` exposes it on a pseudo-terminal so pm-power can
open it like /dev/ttyAMA0."""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import time

from .frame import Deframer, Frame
from .messages import (
    PROTO_VER,
    BootReason,
    ButtonAction,
    ButtonId,
    Message,
    MicRailReason,
    Status,
    msg,
)
from .privacy_model import PrivacyInterlock
from .transport import Transport

log = logging.getLogger("pm.mcu.sim")
MCU_FW_VER = (0 << 16) | (1 << 8) | 0


class McuSimulator:
    def __init__(self, transport: Transport, *, auto_ack_events: bool = True) -> None:
        self.t = transport
        self.deframer = Deframer()
        self.priv = PrivacyInterlock()
        self.priv.boot()
        self.priv.power_good = True
        self.priv.muted_pin = False
        self.priv.events.clear()
        self.rx_log: list[Message] = []
        self.ignore_next = 0                 # test hook: swallow N commands without ACK
        self._seq = 0x80
        self._time_epoch = int(time.time())
        self.wake_epoch = 0
        self.lte_present, self.vreg_max_mV = True, 4240   # fail-safe default (LTE_CFG)
        self.state = 0
        self._task: asyncio.Task[None] | None = None
        self._t0 = time.monotonic()
        self.auto_ack_events = auto_ack_events

    def now_ms(self) -> int:
        return int((time.monotonic() - self._t0) * 1000)

    async def start(self) -> None:
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _send(self, m: Message) -> None:
        self._seq = (self._seq + 1) & 0xFF
        await self.t.write(b"\x00" + Frame.from_message(m, self._seq).encode())

    async def _ack(self, seq: int, status: Status, data: bytes = b"") -> None:
        await self.t.write(Frame.from_message(msg("ACK", tail=data, acked_seq=seq, status=int(status)),
                                              seq).encode())

    async def _flush_rail_events(self) -> None:
        evs, self.priv.events = self.priv.events, []
        for on, reason, sid in evs:
            await self._send(msg("EVT_MIC_RAIL", on=int(on), reason=int(reason), session_id=sid))

    # ---- operator / test actions --------------------------------------------
    async def press(self, button: ButtonId, action: ButtonAction) -> None:
        if button == ButtonId.ACTION and action in (ButtonAction.DOWN, ButtonAction.UP):
            self.priv.now_ms = self.now_ms()
            self.priv.on_action(action == ButtonAction.DOWN)
        await self._send(msg("EVT_BUTTON", id=int(button), action=int(action), t_ms=self.now_ms(), woke=0))
        await self._flush_rail_events()

    async def set_mute(self, muted: bool) -> None:
        self.priv.now_ms = self.now_ms()
        self.priv.on_mute_pin(muted)
        await self._flush_rail_events()
        await self._send(msg("EVT_MIC_MUTE", muted=int(muted), valid=int(self.priv.mute_valid),
                             t_ms=self.now_ms()))

    async def thermal(self, case_dC: int, stage: int = 0, lux: int = 100, fault: int = 0) -> None:
        await self._send(msg("EVT_THERMAL", case_ntc_dC=case_dC, cell_dC=case_dC, ambient_dC_est=300,
                             stage=stage, adc_fault=fault, lux=lux))

    async def battery(self, mV: int, mA: int, soc: int = 50, temp_dC: int = 300, chg: int = 0) -> None:
        """mA uses the MAX17055 sign: negative = discharge."""
        await self._send(msg("EVT_BATTERY", soc=soc, mV=mV, mA=mA, temp_dC=temp_dC, chg=chg))

    async def overcurrent(self, cell_mA: int, duration_ms: int = 1000, action: int = 0) -> None:
        await self._send(msg("EVT_OVERCURRENT", cell_mA=cell_mA, duration_ms=duration_ms, action=action))

    async def tick(self) -> None:
        self.priv.tick(self.now_ms())
        await self._flush_rail_events()

    # ---- command handling ---------------------------------------------------
    async def _loop(self) -> None:
        while True:
            data = await self.t.read()
            for f in self.deframer.feed(data):
                try:
                    m = f.message()
                except (KeyError, ValueError):
                    await self._ack(f.seq, Status.BAD_LEN)
                    continue
                if m.name == "ACK":
                    continue
                if self.ignore_next:
                    self.ignore_next -= 1
                    continue
                self.rx_log.append(m)
                self.priv.now_ms = self.now_ms()
                self.priv.on_frame_rx()
                st, data_out = self._handle(m)
                await self._ack(f.seq, st, data_out)
                if m.name == "HELLO" and st == Status.OK:
                    await self._send(msg("HELLO_ACK", proto_ver=PROTO_VER, mcu_fw_ver=MCU_FW_VER,
                                         boot_reason=int(BootReason.PWR_BUTTON),
                                         flags=(int(self.priv.muted_pin) << 1) | (int(self.priv.mute_valid) << 2),
                                         e_used_J=0))
                await self._flush_rail_events()

    def _handle(self, m: Message) -> tuple[Status, bytes]:
        f = m.fields
        if m.name == "HELLO":
            if f["proto_ver"] != PROTO_VER:
                return Status.BAD_VERSION, b""
            return Status.OK, b""
        if m.name == "HEARTBEAT":
            self.priv.on_heartbeat()
            return Status.OK, b""
        if m.name == "MIC_ENABLE":
            return self.priv.mic_enable(bool(f["on"]), f["session_id"], f["mode"], f["max_s"]), b""
        if m.name == "SHUTDOWN_READY":
            self.priv.on_shutdown_ready()
            return Status.OK, b""
        if m.name == "SET_STATE":
            if f["state"] > 6:
                return Status.RANGE, b""
            self.state = f["state"]
            return Status.OK, b""
        if m.name == "SET_WAKE":
            self.wake_epoch = f["epoch_s"]
            return Status.OK, b""
        if m.name == "LTE_CFG":
            if f["vreg_max_mV"] > 4240 or f["vreg_max_mV"] < 3840:
                return Status.RANGE, b""
            self.lte_present, self.vreg_max_mV = bool(f["present"]), f["vreg_max_mV"]
            return Status.OK, b""
        if m.name == "TIME":
            import struct
            if len(m.tail) == 4:
                (self._time_epoch,) = struct.unpack("<I", m.tail)
                return Status.OK, b""
            if not m.tail:
                return Status.OK, struct.pack("<I", self._time_epoch)
            return Status.BAD_LEN, b""
        return Status.OK, b""


async def _run_pty() -> None:  # pragma: no cover - interactive dev helper
    import pty
    import tty

    master, slave = pty.openpty()
    tty.setraw(slave)
    print(f"MCU simulator on {os.ttyname(slave)} (115200 8N1); Ctrl-C to stop", flush=True)
    loop = asyncio.get_running_loop()
    q: asyncio.Queue[bytes] = asyncio.Queue()
    loop.add_reader(master, lambda: q.put_nowait(os.read(master, 256)))

    class PtyT:
        async def write(self, data: bytes) -> None:
            os.write(master, data)

        async def read(self) -> bytes:
            return await q.get()

        async def close(self) -> None:
            os.close(master)

    sim = McuSimulator(PtyT())
    await sim.start()
    while True:
        await asyncio.sleep(0.1)
        await sim.tick()


def main() -> None:  # pragma: no cover
    ap = argparse.ArgumentParser(description="PocketMate MCU simulator")
    ap.add_argument("--pty", action="store_true", help="serve on a pseudo-terminal")
    ap.parse_args()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(_run_pty())


__all__ = ["McuSimulator", "MicRailReason"]
