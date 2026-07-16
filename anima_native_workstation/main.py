"""Application entry point for the completely offline ANIMA workstation."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QFontDatabase
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from app_backend import AppBackend


def main() -> int:
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
    # QFileDialog and the other native desktop dialogs are QWidget-based and
    # therefore require QApplication. QApplication still provides the complete
    # QGuiApplication API used by the QML scene.
    app = QApplication(sys.argv)
    app.setApplicationName("ANIMA MIDI Production Engine")
    app.setOrganizationName("ANIMA")

    root = Path(__file__).resolve().parent
    font = root / "resources" / "fonts" / "Inter-Regular.ttf"
    if font.exists():
        QFontDatabase.addApplicationFont(str(font))

    backend = AppBackend()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", backend)
    engine.load(QUrl.fromLocalFile(str(root / "qml" / "Main.qml")))
    if not engine.rootObjects():
        return 1
    backend.initialize()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
