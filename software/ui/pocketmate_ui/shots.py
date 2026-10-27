"""Offscreen screenshots of each screen at 800x480: python -m pocketmate_ui.shots <outdir>."""
from __future__ import annotations

import os
import sys
from pathlib import Path

SCREENS = [("home", None), ("listening", "rec"), ("processing", None), ("response", None),
           ("memory", None), ("tasks", None), ("battery", None), ("home", "muted")]


def main(out: str) -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQuick import QQuickWindow  # noqa: F401 - registers the QQuickWindow wrapper

    from .app import HEIGHT, WIDTH, build
    from .backend import Backend
    _app = QGuiApplication.instance() or QGuiApplication([sys.argv[0]])  # must stay referenced
    be = Backend("/nonexistent", demo=True)
    be._answer, be._sources = "Your car is on level B2, near pillar 14.", ["Voice note · Mon 09:12"]
    be.search("parking")
    engine, errors = build(be)
    if not engine.rootObjects():
        print("\n".join(errors), file=sys.stderr)
        return 1
    win = engine.rootObjects()[0]
    Path(out).mkdir(parents=True, exist_ok=True)

    def pump(ms: int = 150) -> None:
        loop = QEventLoop(); QTimer.singleShot(ms, loop.quit); loop.exec()
        QCoreApplication.processEvents()
    for name, mic in SCREENS:
        be.setMic(mic or "ready")
        be.go(name)
        pump()
        img = win.grabWindow()
        assert img.width() == WIDTH and img.height() == HEIGHT, (img.width(), img.height())
        img.save(str(Path(out) / f"{name}{'-' + mic if mic and name == 'home' else ''}.png"))
    rc = 0
    if errors:
        print("\n".join(errors), file=sys.stderr)
        rc = 2
    del win
    del engine  # before the backend, so bindings don't see a null context property
    print(f"wrote {len(SCREENS)} screenshots to {out}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "shots"))
