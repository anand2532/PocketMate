"""pm-remind helper: `next-wake` pushes the next reminder wake time to the MCU via pm-power; `due` lists due."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from .. import config
from ..ipc.rpc import RpcClient
from ..memory.store import MemoryStore
from ..remind.scheduler import ReminderService
from ._common import parser, setup_logging


def main() -> None:
    p = parser("pm-remind", __doc__ or "")
    p.add_argument("--db", default=str(config.STATE_DIR / "memory.db"))
    p.add_argument("cmd", choices=["next-wake", "due", "list"], nargs="?", default="next-wake")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    setup_logging(a.log_level)
    rs = ReminderService(MemoryStore(a.db))
    if a.cmd == "due":
        print(json.dumps([r.__dict__ for r in rs.due()], default=str))
    elif a.cmd == "list":
        print(json.dumps(rs.list(), default=str))
    else:
        nxt = rs.next_wake_ms()
        print(json.dumps({"next_wake_ms": nxt}))
        if nxt and not a.dry_run:
            async def push() -> None:
                c = RpcClient(Path(a.run_dir) / "power.sock")
                await c.connect()
                await c.call("set_wake", epoch_s=nxt // 1000)
                await c.close()
            asyncio.run(push())
