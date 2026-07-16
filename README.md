# ANIMA MIDI Production Engine

ANIMA is a completely offline MIDI composition suite with a command-line source engine and a native PySide6/QML workstation.

Current distribution: **v1.1**. See [CHANGELOG.md](CHANGELOG.md) for release history.

## Source engine

Run from the repository root:

```powershell
python anima-midi-production-engine.py
```

The active engines live in `assets/` and include Major Harmony, Minor Harmony, Solo Major, Solo Minor, Cinematic Major, Cinematic Minor, Spanish Family, World Composer, Flamenco Specialist, and VVC Quartet Overlay.

Generated compositions are saved in `midi_files/`, which is intentionally retained between releases.
Generated MIDI files, local virtual environments, build workspaces, and compiled distributions are excluded from Git. This keeps the remote repository limited to reproducible source code.

## Native workstation

```powershell
cd anima_native_workstation
.\run.ps1
```

The native app is completely offline. Its backend calls the same engine files in `assets/`; it does not duplicate their musical logic.

To create a standalone Windows distribution:

```powershell
cd anima_native_workstation
.\build.ps1
```

The versioned output is written to:

```text
anima_native_workstation/dist/ANIMA-MIDI-Production-Engine-v1.1/
```

The `dist/` directory is intentionally ignored by Git. Zip the versioned distribution and attach it to the matching GitHub Release instead of committing binaries to the source repository.

## Release workflow

Major feature releases use sequential suffixes: `v1.1`, `v1.2`, `v1.3`, and so on.

For every release:

1. Update `VERSION`.
2. Match the semantic version in `anima_native_workstation/pyproject.toml`.
3. Document the changes in `CHANGELOG.md`.
4. Validate the source engines and native catalog.
5. Run `anima_native_workstation/build.ps1` to create the versioned distribution.

## Repository structure

```text
progressions/
├── VERSION
├── CHANGELOG.md
├── README.md
├── anima-midi-production-engine.py
├── assets/                     # Shared MIDI composition engines
├── midi_files/                 # Retained generated compositions
└── anima_native_workstation/   # Offline PySide6/QML application
```
