"""pm-profile (oneshot, before pm-core): writes /run/pm/profile.toml (§6.11)."""
from __future__ import annotations

from pathlib import Path

from ..profile import build, to_toml
from ._common import parser, setup_logging


def main() -> None:
    p = parser("pm-profile", __doc__ or "")
    p.add_argument("--root", default="/")
    p.add_argument("--manifest", default="/opt/pm/models/manifest.json")
    p.add_argument("--allow-unsupported", action="store_true")
    a = p.parse_args()
    setup_logging(a.log_level)
    prof = build(a.root, a.manifest, a.allow_unsupported)
    out = Path(a.run_dir) / "profile.toml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_toml(prof))
    print(out.read_text(), end="")
    raise SystemExit(0 if prof.supported else 3)    # 3 -> diagnostics-only mode
