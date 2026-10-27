"""pm-health: post-boot checks within 120 s, then `rauc status mark-good` (or mark-bad)."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from .. import config
from ..health import db_opens, mark, rpc_ping, run_checks, unit_active
from ._common import parser, setup_logging


def main() -> None:
    p = parser("pm-health", __doc__ or "")
    p.add_argument("--db", default=str(config.STATE_DIR / "memory.db"))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--deadline", type=float, default=120.0)
    a = p.parse_args()
    setup_logging(a.log_level)
    run_dir = Path(a.run_dir)
    checks = {"ui": unit_active("pm-ui.service"), "core": rpc_ping(run_dir / "core.sock"),
              "db": db_opens(a.db), "mcu_link": rpc_ping(run_dir / "power.sock")}
    rep = asyncio.run(run_checks(checks, deadline_s=a.deadline))
    cmd = mark(rep.ok, dry_run=a.dry_run)
    print(json.dumps({"ok": rep.ok, "results": rep.results, "elapsed_s": round(rep.elapsed_s, 1),
                      "action": " ".join(cmd)}))
    raise SystemExit(0 if rep.ok else 1)
