# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

root = Path(SPECPATH)
repo = root.parent
version = (repo / "VERSION").read_text(encoding="utf-8").strip()
distribution_name = f"ANIMA-MIDI-Production-Engine-{version}"

datas = [
    (str(root / "qml"), "qml"),
]
for engine_file in (
    "cinematic.py", "major-chord-generatory.py", "minor-chord-generatory.py",
    "solo_performance_major.py", "solo_performance_minor.py", "spanish_family.py",
    "specialist_styles.py", "VVC.py", "world_composer.py",
):
    datas.append((str(repo / "assets" / engine_file), "assets"))
datas += collect_data_files("mido")

a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root), str(repo), str(repo / "assets")],
    binaries=[],
    datas=datas,
    hiddenimports=["mido", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuickControls2"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=distribution_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name=distribution_name,
)
