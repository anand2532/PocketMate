"""pm-cloud: the only service with general egress (nftables by UID). Off by default (cloud.enabled=false):
the service then exits immediately. Providers are BYOK stubs with no HTTP transport wired."""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from .. import config
from ..cloud.consent import ConsentGate, load_or_create_key
from ..cloud.providers.sarvam import SarvamProvider
from ..cloud.service import CloudService
from ..ipc.rpc import RpcServer
from ..memory.store import MemoryStore
from ._common import parser, run, sd_notify, setup_logging

log = logging.getLogger("pm.cloud")


async def _main(stop: asyncio.Event, args) -> None:
    cfg = config.load(args.settings)
    if not cfg["cloud"]["enabled"]:
        log.info("cloud.enabled=false: exiting")
        sd_notify("READY=1")
        return
    store = MemoryStore(args.db)
    gate = ConsentGate(load_or_create_key(config.STATE_DIR / "secrets/consent.key"))
    svc = CloudService(store, gate, {"sarvam": SarvamProvider()})
    rpc = RpcServer(Path(args.run_dir) / "cloud.sock")

    @rpc.method("ping")
    def _ping() -> bool:
        return True

    @rpc.method("cloud_log")
    def _log(limit: int = 100) -> list[dict]:
        return svc.cloud_log(limit)

    await rpc.start()
    sd_notify("READY=1")
    while not stop.is_set():
        await svc.process_deletions()
        try:
            await asyncio.wait_for(stop.wait(), 60)
        except TimeoutError:
            pass
    await rpc.stop()


def main() -> None:
    p = parser("pm-cloud", __doc__ or "")
    p.add_argument("--db", default=str(config.STATE_DIR / "memory.db"))
    p.add_argument("--settings", default=None)
    a = p.parse_args()
    setup_logging(a.log_level)
    run(lambda stop: _main(stop, a))
