# ANIMA MIDI Production Engine changelog

## v1.1 — 2026-07-16

- Consolidated the project around the Python source engines and native PySide6/QML workstation.
- Removed the discontinued Spanish Guitar engine while retaining Spanish Family and Flamenco.
- Added the redesigned native full-suite engine catalog, workspace, transport presentation, and performance mixer presentation.
- Added functional offline MIDI import handling and standalone Windows packaging.
- Reworked Spanish Family into six curated four-bar moods with expanded progression libraries.
- Improved Spanish Family trumpet and violin phrasing with chord-tone harmony, sustains, staccatos, and accents.
- Added Major and Minor Solo Performance mood libraries and memorable lead/rhythmic-layer behavior.
- Reworked Cinematic Major to use Major Solo mood progressions.
- Reworked Cinematic Minor to use five Minor Engine mood groups with 14 progressions each.
- Cleaned obsolete prototypes, legacy build systems, caches, test fixtures, and repair utilities from the repository.

## Release convention

Every major feature release increments the minor version: `v1.2`, `v1.3`, and so on. For each release:

1. Update `VERSION`.
2. Update the project version in `anima_native_workstation/pyproject.toml`.
3. Add a dated section to this changelog.
4. Run `anima_native_workstation/build.ps1`.

The build is created as `ANIMA-MIDI-Production-Engine-vX.Y`, allowing releases to coexist without overwriting one another.
