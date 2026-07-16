# ANIMA MIDI Production Engine — Native Workstation

This directory contains a completely offline native desktop redesign of ANIMA. It is isolated from the existing command-line, Tkinter, and Tauri projects.

## Architecture

```text
QML native workstation UI
        ↓
PySide6 controllers and background worker
        ↓
engine_adapter.py
        ↓
existing ANIMA Python composition engines
        ↓
local .mid files
```

There is no browser, localhost server, account system, telemetry, cloud storage, or online API. After dependencies are installed, generation is entirely offline.

## Full suite workflow

1. **Create** — choose an engine family, emotional direction, key, tempo,
   supported length, instrument, and deterministic seed.
2. **Generate** — the selected engine runs on a background thread and writes a
   local MIDI file without terminal prompts.
3. **Workspace** — inspect the actual tracks, channels, note activity, chord
   progression, key, tempo, and length returned by the generated MIDI.
4. **Library** — browse, reveal, and manage output from the persistent local
   MIDI directory.
5. **Import & Orchestrate** — choose an existing MIDI file and pass it to the
   VVC expressive quartet analyzer/overlay workflow.

## Integrated engines

- Major Chord Engine
- Minor Chord Engine
- Solo Performance Major
- Solo Performance Minor
- Cinematic Major
- Cinematic Minor
- Spanish Family
- World Composer
- Specialist Flamenco
- VVC Quartet Overlay for imported MIDI

Every integration calls composition functions directly. The adapter never
automates console menus, and it does not modify established generator behavior.

### Spanish Family moods

Spanish Family provides six minor-centered Spanish/English mood groups:
Lamento Andaluz [Andalusian Lament], Nostalgia Gitana [Gypsy Nostalgia],
Esperanza Renacida [Renewed Hope], Romance Apasionado [Passionate Romance],
Tristeza del Alma [Sorrow of the Soul], and Dolor de un Corazón Roto
[Pain of a Broken Heart]. Each group contains 20 curated four-bar progression
arcs. Output is strictly limited to four bars while retaining the existing
five-channel Spanish Family performance rules.

## Included native features

- Engine and mood browser
- Key, BPM, instrument, seed, and output controls
- Non-blocking generation worker
- Generated-project timeline populated from real MIDI tracks
- Performance mixer project controls populated from real MIDI tracks
- Imported-MIDI orchestration workflow
- Persistent output-folder setting
- Offline generated-MIDI library
- Reveal-in-folder action
- Deterministic generation seeds
- Native error dialogs

The transport is intentionally capability-gated in this version: Play and Stop
remain disabled until a licensed local SoundFont/software-synth module is
installed. Generation and MIDI export do not require that audio module.

## Directory isolation

All new application files and dependencies live here:

```text
anima_native_workstation/
├── .venv/                 # created locally; ignored by Git
├── qml/                   # native Qt Quick interface
├── user_data/midi_files/  # default generated output
├── app_backend.py
├── engine_adapter.py
├── main.py
├── requirements.txt
├── pyproject.toml
├── run.ps1
├── build.ps1
└── anima_native.spec
```

The source adapter reads the established generators from the repository's
`assets` directory without changing them. Packaged builds copy the attached
suite engine files into the application bundle.

## Run from source

From this directory:

```powershell
.\run.ps1
```

On first run, the script creates `.venv` inside this directory and installs PySide6, mido, and PyInstaller there. Later launches remain offline unless dependencies need updating.

Manual setup is also supported:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Build the offline application

After the isolated environment exists:

```powershell
.\build.ps1
```

The application is produced in:

```text
dist/ANIMA-MIDI-Production-Engine-v1.1/
```

The initial build uses PyInstaller's one-folder format because dependency and Qt plugin problems are easier to diagnose there. An installer and code signing can be added after the application is stable.

## Adding another engine

Add its metadata and direct compose call in `engine_adapter.py`. The QML interface builds engine and mood controls from the returned catalog, so it does not need terminal-menu numbers or prompt parsing.
