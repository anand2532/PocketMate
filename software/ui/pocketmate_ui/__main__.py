"""pm-ui entry point. On the device: QT_QPA_PLATFORM=eglfs (set in pm-ui.service).
Dev: `python -m pocketmate_ui --demo` (any platform). Screenshots: `python -m pocketmate_ui.shots out/`."""
from __future__ import annotations

import argparse
import sys

from PySide6.QtGui import QGuiApplication


def main() -> int:
    ap = argparse.ArgumentParser(prog="pm-ui")
    ap.add_argument("--run-dir", default="/run/pm")
    ap.add_argument("--demo", action="store_true", help="use built-in demo data instead of pm-core")
    args, qt_args = ap.parse_known_args()
    app = QGuiApplication([sys.argv[0], *qt_args])
    from .app import build
    from .backend import Backend
    backend = Backend(args.run_dir, demo=args.demo)
    engine, errors = build(backend)
    if not engine.rootObjects():
        print("\n".join(errors) or "QML failed to load", file=sys.stderr)
        return 1
    try:
        from pocketmate.services._common import sd_notify
        sd_notify("READY=1")
    except ImportError:
        pass
    rc = app.exec()
    del engine  # tear down QML before the backend it binds to
    return rc


if __name__ == "__main__":
    sys.exit(main())
