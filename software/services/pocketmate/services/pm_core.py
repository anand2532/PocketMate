"""pm-core: orchestrator RPC for pm-ui (prototype stand-in for org.pocketmate.Core on D-Bus).
[impl] In the prototype pm-core hosts MemoryStore and ReminderService in-process (single DB writer)."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict
from pathlib import Path

from .. import config
from ..core.orchestrator import Orchestrator
from ..engines import registry
from ..engines.types import EngineError
from ..ipc.rpc import RpcServer
from ..memory.store import MemoryStore
from ._common import parser, run, sd_notify, setup_logging

log = logging.getLogger("pm.core")


def build_llm(cfg: dict, use_stub: bool):
    try:
        return registry.create("llm", "stub" if use_stub else cfg["llm"]["backend"])
    except (EngineError, KeyError, ImportError) as e:
        log.warning("LLM backend unavailable (%s); extractive answers only", e)
        return None


async def _main(stop: asyncio.Event, args) -> None:
    cfg = config.load(args.settings)
    store = MemoryStore(args.db)
    llm = build_llm(cfg, args.stub_engines)
    if llm is not None:
        try:
            await llm.load()
        except EngineError as e:
            log.warning("LLM load failed: %s", e)
            llm = None
    orch = Orchestrator(store, llm=llm)
    rpc = RpcServer(Path(args.run_dir) / "core.sock")

    @rpc.method("ping")
    def _ping() -> bool:
        return True

    @rpc.method("handle")
    async def _handle(text: str, origin: str = "ui") -> dict:
        return asdict(await orch.handle(text, origin=origin))

    @rpc.method("search")
    def _search(query: str, limit: int = 20) -> list[dict]:
        return [asdict(h) for h in store.search(query, limit=limit)]

    @rpc.method("open_source")
    def _open(chunk_id: int) -> dict | None:
        return store.open_source(chunk_id)

    @rpc.method("list_items")
    def _list(kind: str | None = None, limit: int = 50) -> list[dict]:
        return store.list_items(kind, limit)

    @rpc.method("reminders")
    def _rem() -> list[dict]:
        return orch.reminders.list()

    @rpc.method("confirm_reminder")
    def _confirm(reminder_id: str) -> bool:
        orch.reminders.confirm(reminder_id)
        return True

    @rpc.method("consent_audit")
    def _audit(limit: int = 100) -> list[dict]:
        return store.consent_audit(limit)

    await rpc.start()
    sd_notify("READY=1")
    await stop.wait()
    await rpc.stop()
    store.close()


def main() -> None:
    p = parser("pm-core", __doc__ or "")
    p.add_argument("--db", default=str(config.STATE_DIR / "memory.db"))
    p.add_argument("--settings", default=None)
    p.add_argument("--stub-engines", action="store_true")
    args = p.parse_args()
    setup_logging(args.log_level)
    run(lambda stop: _main(stop, args))
