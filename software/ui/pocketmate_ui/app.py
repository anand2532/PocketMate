"""Builds the QML engine. Shared by __main__ (device/dev) and the offscreen screenshot tool/tests."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine

from .backend import Backend

QML_DIR = Path(__file__).parent / "qml"
WIDTH, HEIGHT = 800, 480


def build(backend: Backend) -> tuple[QQmlApplicationEngine, list[str]]:
    engine = QQmlApplicationEngine()
    errors: list[str] = []
    engine.warnings.connect(lambda ws: errors.extend(w.toString() for w in ws))
    engine.addImportPath(str(QML_DIR))
    engine.rootContext().setContextProperty("pm", backend)
    engine.load(QUrl.fromLocalFile(str(QML_DIR / "Main.qml")))
    return engine, errors
