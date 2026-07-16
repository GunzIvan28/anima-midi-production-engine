"""Qt-facing backend for the offline ANIMA native workstation."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, QSettings, QThread, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog

from engine_adapter import EngineAdapter, GenerationRequest


class GenerationThread(QThread):
    completed = Signal(dict)
    failed = Signal(str)

    def __init__(self, adapter: EngineAdapter, request: GenerationRequest) -> None:
        super().__init__()
        self.adapter = adapter
        self.request = request

    def run(self) -> None:
        try:
            self.completed.emit(self.adapter.generate(self.request).to_dict())
        except Exception as exc:  # UI receives a stable, readable error.
            self.failed.emit(str(exc))


class AppBackend(QObject):
    catalogChanged = Signal()
    libraryChanged = Signal()
    outputDirectoryChanged = Signal()
    busyChanged = Signal()
    progressChanged = Signal()
    inputFileChanged = Signal()
    compositionChanged = Signal()
    generationCompleted = Signal(dict)
    generationFailed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._adapter = EngineAdapter()
        self._catalog: list[dict[str, Any]] = []
        self._library: list[dict[str, Any]] = []
        self._busy = False
        self._progress = "Ready"
        self._thread: GenerationThread | None = None
        self._input_file = ""
        self._composition: dict[str, Any] = {}
        self._settings = QSettings("ANIMA", "MIDI Production Engine")
        default_output = Path(__file__).resolve().parent / "user_data" / "midi_files"
        self._output_directory = str(
            Path(self._settings.value("outputDirectory", str(default_output))).resolve()
        )
        Path(self._output_directory).mkdir(parents=True, exist_ok=True)

    @Property("QVariantList", notify=catalogChanged)
    def engineCatalog(self):
        return self._catalog

    @Property("QVariantList", notify=libraryChanged)
    def library(self):
        return self._library

    @Property(str, notify=outputDirectoryChanged)
    def outputDirectory(self) -> str:
        return self._output_directory

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, notify=progressChanged)
    def progressText(self) -> str:
        return self._progress

    @Property(str, notify=inputFileChanged)
    def inputFile(self) -> str:
        return self._input_file

    @Property("QVariantMap", notify=compositionChanged)
    def composition(self):
        return self._composition

    @Property(bool, constant=True)
    def playbackAvailable(self) -> bool:
        return False

    @Slot()
    def initialize(self) -> None:
        try:
            self._catalog = self._adapter.catalog()
            self.catalogChanged.emit()
            self.refreshLibrary()
        except Exception as exc:
            self.generationFailed.emit(
                f"Backend initialization failed: {exc}. Install dependencies from requirements.txt."
            )

    @Slot(result=int)
    def createSeed(self) -> int:
        return random.SystemRandom().randint(10000, 999999)

    @Slot()
    def chooseOutputDirectory(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            None, "Choose ANIMA MIDI output folder", self._output_directory
        )
        if selected:
            self._output_directory = str(Path(selected).resolve())
            self._settings.setValue("outputDirectory", self._output_directory)
            self.outputDirectoryChanged.emit()
            self.refreshLibrary()

    @Slot()
    def chooseInputMidi(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            None, "Import MIDI for orchestration", str(Path.home()), "MIDI files (*.mid *.midi)"
        )
        if selected:
            self._input_file = str(Path(selected).resolve())
            self.inputFileChanged.emit()

    @Slot()
    def openOutputDirectory(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(self._output_directory))

    @Slot(str)
    def revealFile(self, file_path: str) -> None:
        path = Path(file_path)
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))

    @Slot()
    def refreshLibrary(self) -> None:
        root = Path(self._output_directory)
        rows = []
        for path in sorted(root.glob("*.mid"), key=lambda item: item.stat().st_mtime, reverse=True):
            parts = path.stem.split("__")
            rows.append({
                "title": parts[0].replace("_", " "),
                "details": "  •  ".join(part.replace("_", " ") for part in parts[1:4]),
                "filename": path.name,
                "file": str(path.resolve()),
                "size": f"{max(1, path.stat().st_size // 1024)} KB",
            })
        self._library = rows
        self.libraryChanged.emit()

    @Slot("QVariantMap")
    def generate(self, payload) -> None:
        if self._busy:
            return
        try:
            request = GenerationRequest(
                engine=str(payload["engine"]),
                mood=str(payload["mood"]),
                key=str(payload["key"]),
                bpm=int(payload["bpm"]),
                instrument=str(payload["instrument"]),
                seed=int(payload["seed"]),
                output_directory=self._output_directory,
                bars=int(payload.get("bars", 4)),
                input_file=str(payload.get("inputFile", self._input_file)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            self.generationFailed.emit(f"Invalid generation settings: {exc}")
            return

        self._set_busy(True, "Composing with the selected ANIMA engine…")
        self._thread = GenerationThread(self._adapter, request)
        self._thread.completed.connect(self._generation_complete)
        self._thread.failed.connect(self._generation_failed)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _set_busy(self, value: bool, text: str) -> None:
        self._busy = value
        self._progress = text
        self.busyChanged.emit()
        self.progressChanged.emit()

    @Slot(dict)
    def _generation_complete(self, result: dict) -> None:
        self._set_busy(False, f"Created {result['filename']}")
        self._composition = result
        self.compositionChanged.emit()
        self.refreshLibrary()
        self.generationCompleted.emit(result)
        self._thread = None

    @Slot(str)
    def _generation_failed(self, message: str) -> None:
        self._set_busy(False, "Generation failed")
        self.generationFailed.emit(message)
        self._thread = None
