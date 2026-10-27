"""pm-memory maintenance (timer): retention sweep + orphan check; `export`/`verify-chain` CLIs."""
from __future__ import annotations

import json

from .. import config
from ..memory.store import MemoryStore
from ._common import parser, setup_logging


def main() -> None:
    p = parser("pm-memory", __doc__ or "")
    p.add_argument("--db", default=str(config.STATE_DIR / "memory.db"))
    p.add_argument("cmd", choices=["sweep", "verify-chain", "export", "orphans"], nargs="?", default="sweep")
    p.add_argument("--out", default="pocketmate-export.zip")
    a = p.parse_args()
    setup_logging(a.log_level)
    s = MemoryStore(a.db)
    if a.cmd == "sweep":
        print(json.dumps({"swept": s.retention_sweep(), "orphans": s.orphan_counts()}))
    elif a.cmd == "verify-chain":
        ok, bad = s.verify_consent_chain()
        print(json.dumps({"ok": ok, "first_bad_id": bad}))
        raise SystemExit(0 if ok else 1)
    elif a.cmd == "export":
        print(s.export_zip(a.out))
    else:
        print(json.dumps(s.orphan_counts()))
