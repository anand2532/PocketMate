"""Offscreen QML checks: loads with zero QML warnings, renders every screen at 800x480, and the backend
talks to a fake pm-core / pm-power over the real Unix-socket RPC."""
from __future__ import annotations

import asyncio
import os
import threading
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pocketmate_ui import shots
from pocketmate_ui.app import build
from pocketmate_ui.backend import Backend
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickWindow  # noqa: F401


@pytest.fixture(scope="module")
def app():
    return QGuiApplication.instance() or QGuiApplication(["test"])


def test_loads_without_warnings(app):
    be = Backend("/nonexistent", demo=True)
    engine, errors = build(be)
    win = engine.rootObjects()[0]
    assert (win.width(), win.height()) == (800, 480)
    for s in ["home", "listening", "processing", "response", "memory", "tasks", "battery"]:
        be.go(s)
        QCoreApplication.processEvents()
    assert errors == []
    del win, engine


def test_screenshots(app, tmp_path):
    assert shots.main(str(tmp_path)) == 0
    pngs = sorted(p.name for p in tmp_path.glob("*.png"))
    assert len(pngs) == 8 and "home.png" in pngs
    from PySide6.QtGui import QImage
    img = QImage(str(tmp_path / "home.png"))
    assert (img.width(), img.height()) == (800, 480)
    assert img.pixelColor(400, 450).name() == "#000000"          # hint bar chrome
    assert img.pixelColor(100, 160).name().lower() == "#4c8dff"  # primary "Ask" tile = accent


def _wait(pred, timeout=5.0):
    end = time.time() + timeout
    while time.time() < end:
        QCoreApplication.processEvents()
        if pred():
            return True
        time.sleep(0.02)
    return False


def test_rpc_roundtrip(app, tmp_path):
    from pocketmate.ipc.rpc import RpcServer
    loop = asyncio.new_event_loop()
    core, power = RpcServer(tmp_path / "core.sock"), RpcServer(tmp_path / "power.sock")

    @core.method("handle")
    def _h(text: str, origin: str = "ui") -> dict:
        return {"kind": "answer", "text": "B2 pillar 14",
                "sources": [{"kind": "voice_note", "title": "Parking", "created_at": 0}]}

    @core.method("search")
    def _s(query: str, limit: int = 20) -> list:
        return [{"kind": "note", "title": "Parking", "snippet": "level B2", "created_at": 0}]

    loop.run_until_complete(core.start())
    loop.run_until_complete(power.start())
    t = threading.Thread(target=loop.run_forever, daemon=True)
    t.start()
    be = Backend(tmp_path)
    assert not be.demo
    assert _wait(lambda: be._loop is not None and be._power is not None)
    time.sleep(0.2)
    be.ask("where did I park")
    assert _wait(lambda: be.screen == "response")
    assert be.answer == "B2 pillar 14" and be.sources == ["Voice note · Parking"]
    be.search("park")
    assert _wait(lambda: be.results and be.results[0]["text"] == "level B2")
    asyncio.run_coroutine_threadsafe(power.emit("Battery", soc=15, charging=True), loop).result(2)
    assert _wait(lambda: be.battery == 15 and be.charging)
    asyncio.run_coroutine_threadsafe(power.emit("MicMute", muted=1, valid=1), loop).result(2)
    assert _wait(lambda: be.mic == "muted")
    asyncio.run_coroutine_threadsafe(power.emit("LteGovernor", tx="throttle", rat="lte", throttled=True,
                                                reasons=[]), loop).result(2)
    assert _wait(lambda: be.lte == "throttle")
    be.close()
    for srv in (core, power):
        asyncio.run_coroutine_threadsafe(srv.stop(), loop).result(2)
    loop.call_soon_threadsafe(loop.stop)
    t.join(2)
