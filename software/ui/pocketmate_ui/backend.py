"""QML-facing backend. Talks to pm-core (core.sock) and pm-power (power.sock) over the Unix-socket RPC on
a background asyncio thread; falls back to demo data with --demo or when the sockets are absent."""
from __future__ import annotations

import asyncio
import threading
import time
from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

DEMO_TASKS = [
    {"title": "Call the electrician", "due": "Today 18:00", "done": False},
    {"title": "Pay electricity bill", "due": "Tomorrow", "done": False},
    {"title": "Buy notebook for Riya", "due": "Sat", "done": True},
]
DEMO_HITS = [
    {"text": "Parking: level B2, pillar 14", "source": "Voice note · Mon 09:12"},
    {"text": "Wi-Fi password at office is on the fridge note", "source": "Photo · 21 Oct"},
]


def _label(src: dict) -> str:
    """Source chip text from a pm-core source/SearchHit dict: kind · title · date (created_at is ms)."""
    parts = [str(src.get("kind", "")).replace("_", " ").capitalize()]
    if src.get("title"):
        parts.append(str(src["title"]))
    if src.get("created_at"):
        parts.append(time.strftime("%d %b %H:%M", time.localtime(int(src["created_at"]) / 1000)))
    return " · ".join(p for p in parts if p)


class Backend(QObject):
    changed = Signal()
    screenChanged = Signal()
    resultsChanged = Signal()
    answerChanged = Signal()

    def __init__(self, run_dir: str | Path = "/run/pm", demo: bool = False) -> None:
        super().__init__()
        self._run = Path(run_dir)
        self._demo = demo or not (self._run / "core.sock").exists()
        self._screen = "home"
        self._mic = "ready"          # ready | rec | muted
        self._cloud = False
        self._battery = 78
        self._charging = False
        self._lte = "off" if self._demo else "unknown"
        self._answer = ""
        self._sources: list[str] = []
        self._results: list[dict] = []
        self._tasks: list[dict] = list(DEMO_TASKS) if self._demo else []
        self._loop: asyncio.AbstractEventLoop | None = None
        self._core = self._power = None
        if not self._demo:
            self._start_rpc()
        self._clock = QTimer(self)
        self._clock.timeout.connect(self.changed)
        self._clock.start(10_000)

    # --- RPC thread ---------------------------------------------------------------------------
    def _start_rpc(self) -> None:
        from pocketmate.ipc.rpc import RpcClient

        def run() -> None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._core = RpcClient(self._run / "core.sock")
            self._power = RpcClient(self._run / "power.sock")

            async def connect() -> None:
                for c in (self._core, self._power):
                    try:
                        await c.connect()
                    except OSError:
                        pass
                self._power.on_signal(self._on_power_signal)
            self._loop.run_until_complete(connect())
            self._loop.run_forever()
        threading.Thread(target=run, name="pm-ui-rpc", daemon=True).start()

    def close(self) -> None:
        """Stop the RPC thread (tests / clean exit)."""
        if self._loop is not None:
            async def _shut() -> None:
                for c in (self._core, self._power):
                    if c is not None and hasattr(c, "close"):
                        await c.close()
            asyncio.run_coroutine_threadsafe(_shut(), self._loop).result(2)
            self._loop.call_soon_threadsafe(self._loop.stop)

    def _call(self, client_attr: str, method: str, cb, **params: Any) -> None:
        client = getattr(self, client_attr)
        if self._loop is None or client is None:
            return
        fut = asyncio.run_coroutine_threadsafe(client.call(method, **params), self._loop)
        fut.add_done_callback(lambda f: cb(None if f.exception() else f.result()))

    def _on_power_signal(self, name: str, args: dict) -> None:
        if name == "MicMute":
            self._mic = "muted" if args.get("muted") else "ready"
        elif name == "MicRail":
            self._mic = "rec" if args.get("on") else ("muted" if self._mic == "muted" else "ready")
        elif name == "Battery":
            self._battery, self._charging = int(args.get("soc", self._battery)), bool(args.get("charging"))
        elif name == "LteGovernor":
            self._lte = args.get("tx", "unknown")
        self.changed.emit()

    # --- properties ---------------------------------------------------------------------------
    def _get(name):
        return lambda self: getattr(self, name)

    clock = Property(str, lambda self: time.strftime("%H:%M"), notify=changed)
    mic = Property(str, _get("_mic"), notify=changed)
    cloud = Property(bool, _get("_cloud"), notify=changed)
    battery = Property(int, _get("_battery"), notify=changed)
    charging = Property(bool, _get("_charging"), notify=changed)
    lte = Property(str, _get("_lte"), notify=changed)
    demo = Property(bool, _get("_demo"), constant=True)
    screen = Property(str, _get("_screen"), notify=screenChanged)
    answer = Property(str, _get("_answer"), notify=answerChanged)
    sources = Property("QVariantList", _get("_sources"), notify=answerChanged)
    results = Property("QVariantList", _get("_results"), notify=resultsChanged)
    tasks = Property("QVariantList", _get("_tasks"), notify=resultsChanged)

    # --- actions ------------------------------------------------------------------------------
    @Slot(str)
    def go(self, screen: str) -> None:
        self._screen = screen
        self.screenChanged.emit()
        if screen == "tasks" and not self._demo:
            self._call("_core", "reminders", self._set_tasks)

    @Slot(str)
    def ask(self, text: str) -> None:
        self.go("processing")
        if self._demo:
            QTimer.singleShot(600, lambda: self._set_answer({"text": f"(demo) You asked: {text}", "sources": []}))
            return
        self._call("_core", "handle", self._set_answer, text=text)

    @Slot(str)
    def search(self, q: str) -> None:
        if self._demo:
            self._results = [h for h in DEMO_HITS if any(w in h["text"].lower() for w in q.lower().split())] or DEMO_HITS
            self.resultsChanged.emit()
            return
        self._call("_core", "search", self._set_results, query=q)

    @Slot(str)
    def setMic(self, state: str) -> None:
        self._mic = state
        self.changed.emit()

    # --- callbacks (RPC thread -> Qt via signals) ---------------------------------------------
    def _set_answer(self, r: dict | None) -> None:
        r = r or {"text": "Couldn't reach pm-core. Try again.", "sources": []}
        self._answer = r.get("text", "")
        self._sources = [_label(s) for s in r.get("sources", [])] or ([r["source_label"]] if r.get("source_label") else [])
        self._screen = "response"
        self.answerChanged.emit()
        self.screenChanged.emit()

    def _set_results(self, r: list | None) -> None:
        self._results = [{"text": h.get("snippet", ""), "source": _label(h)} for h in (r or [])]
        self.resultsChanged.emit()

    def _set_tasks(self, r: list | None) -> None:
        self._tasks = [{"title": t.get("title", t.get("text", "")), "due": str(t.get("due", "")),
                        "done": bool(t.get("done"))} for t in (r or [])]
        self.resultsChanged.emit()
