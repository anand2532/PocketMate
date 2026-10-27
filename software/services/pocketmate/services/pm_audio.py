"""pm-audio: the only process allowed to open capture. PTT sessions are started by pm-core
(RPC start_capture) and gated by the MCU via pm-power (mic_enable). PCM goes out on the
data-plane stream socket /run/pm/audio.stream as msgpack frames {seq,t,pcm,last}."""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from ..audio.capture import AlsaCapture, SimCapture
from ..audio.ptt import CaptureRefused, PttController
from ..ipc.framing import write_frame
from ..ipc.rpc import RpcClient, RpcServer
from ..mcu.messages import MicMode, Status
from ._common import parser, run, sd_notify, setup_logging

log = logging.getLogger("pm.audio")


async def _main(stop: asyncio.Event, args) -> None:
    run_dir = Path(args.run_dir)
    power = RpcClient(run_dir / "power.sock")
    await power.connect()

    async def mic_enable(on: bool, sid: int, mode: int, max_s: int) -> Status:
        return Status(await power.call("mic_enable", on=on, session_id=sid, mode=mode, max_s=max_s))

    ptt = PttController(SimCapture(args.sim_wav) if args.sim else AlsaCapture(args.device), mic_enable)

    class _M:  # adapt pm-power signals to the McuLink event shape
        def __init__(self, name: str, fields: dict) -> None:
            self.name, self.fields = name, fields

    async def on_sig(name: str, a: dict) -> None:
        if name == "MicMute":
            await ptt.on_mute(bool(a["muted"]), bool(a["valid"]))
        elif name == "MicRail":
            await ptt.on_mcu_event(_M("EVT_MIC_RAIL", a))
    power.on_signal(on_sig)

    subscribers: set[asyncio.StreamWriter] = set()

    async def stream_client(_r: asyncio.StreamReader, w: asyncio.StreamWriter) -> None:
        subscribers.add(w)

    stream = await asyncio.start_unix_server(stream_client, str(run_dir / "audio.stream"))
    rpc = RpcServer(run_dir / "audio.sock")

    @rpc.method("ping")
    def _ping() -> bool:
        return True

    @rpc.method("start_capture")
    async def _start(mode: int = int(MicMode.HOLD), max_s: int = 0) -> dict:
        try:
            it = await ptt.start(MicMode(mode), max_s)
        except CaptureRefused as e:
            return {"ok": False, "reason": e.why.name, "message": str(e)}

        async def pump() -> None:
            async for c in it:
                for w in list(subscribers):
                    try:
                        await write_frame(w, {"seq": c.seq, "t": c.t_start_ms, "pcm": c.pcm, "last": c.is_last})
                    except (ConnectionError, RuntimeError):
                        subscribers.discard(w)
        asyncio.create_task(pump())
        return {"ok": True}

    @rpc.method("stop_capture")
    async def _stop() -> dict:
        r = await ptt.stop()
        return {"frames": r.frames} if r else {}

    @rpc.method("status")
    def _status() -> dict:
        return {"active": ptt.active, "muted": ptt.mute.muted, "mute_valid": ptt.mute.valid,
                "frame_counter": ptt.frame_counter}

    await rpc.start()
    sd_notify("READY=1")
    await stop.wait()
    await ptt.stop()
    await rpc.stop()
    stream.close()
    await power.close()


def main() -> None:
    p = parser("pm-audio", __doc__ or "")
    p.add_argument("--device", default="plughw:CARD=pocketmate,DEV=0")
    p.add_argument("--sim", action="store_true")
    p.add_argument("--sim-wav", default=None)
    args = p.parse_args()
    setup_logging(args.log_level)
    run(lambda stop: _main(stop, args))
