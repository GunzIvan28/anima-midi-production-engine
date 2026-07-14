# ANIMA MIDI Workstation

ANIMA is a Windows MIDI composition workstation with two entry points:

- `ANIMA-Workstation.exe` - the Windows GUI workstation.
- `ANIMA-MIDI-Engine.exe` - the original command-line engine used by the GUI.

The GUI preserves the command-line workflow, but adds buttons, file pickers, output-folder controls, and a live command log. The workstation uses a glassy purple Windows theme with lavender panels and bright accent controls.

## Run The Compiled App

Open the compiled workstation from:

```powershell
dist\ANIMA-Workstation.exe
```

Keep these two files together in the same folder:

```text
dist\ANIMA-Workstation.exe
dist\ANIMA-MIDI-Engine.exe
```

The workstation launches `ANIMA-MIDI-Engine.exe` behind the scenes. The engine is still a console program, so it is normal for it to open as a command-line app when run directly.

## Use The Workstation

1. Open `dist\ANIMA-Workstation.exe`.
2. Click `Start Engine`.
3. Wait for the ANIMA menu to appear in the command log.
4. Use the right-side buttons to send menu choices.
5. Use the manual input box for any prompt that needs custom text.
6. Use `Choose MIDI File` when the engine asks for an existing MIDI path.
7. Use `Choose Output Folder` and `Send Output Folder` when changing output location.

Generated MIDI files are saved to the selected output folder. The default is `midi_files`.

## Main Workflows

The engine supports these top-level workflows:

```text
1 -> Generate New MIDI
2 -> Work With Existing MIDI
3 -> Cinematic Trailer Engine
4 -> Guitar & Specialist Styles
5 -> Routing / Help
6 -> Settings
0 -> Exit
```

The GUI includes shortcut tabs for:

- Generate
- Existing MIDI
- Cinematic
- Help
- Settings

Option `4 -> Guitar & Specialist Styles` currently includes:

- Spanish Guitar Composer
- Spanish Family Composer
- World Composer, a minor-scale Spanish / Asian / Oriental trap MIDI specialist
- Solo Performance (Minor), provided by `assets/solo_performance_minor.py`
- Solo Performance (Major), provided by `assets/solo_performance_major.py`

## Solo Performance Engines

Both Solo Performance engines create strict four-bar MIDI compositions with seven isolated tracks:

1. Main Hook Lead - MIDI channel 7
2. Chord Pad - MIDI channel 1
3. Rhythmic Layer - MIDI channel 6
4. Staccato Phrases - MIDI channel 2
5. Sub-Bass - MIDI channel 3
6. Crying Violin Lead - MIDI channel 4
7. Crying Violin Counter - MIDI channel 5

The chord pad is present from bar one. The rhythmic layer also spans all four bars and randomly chooses sustained, simple, moderate, active, or turnaround chord divisions. Its chord segments remain connected, so rhythmic re-articulation does not create unwanted gaps. The main hook lead is deliberately sparse, uses sustained notes, and selects its pitches from the active chord-pad voicing.

### Solo Performance (Minor)

The minor engine retains its native minor progression library and adopted Minor Scale Engine mood groups. It supports natural minor, harmonic minor, Dorian, and Phrygian colors.

`Pain / Heartbreak` includes 18 dedicated four-bar progressions built around minor-key lament movement, unresolved dominants, `iv`, `v`, `bVI`, `bVII`, and Phrygian `bII` colors.

### Solo Performance (Major)

The major engine is separate from the minor module and borrows its chord vocabulary from `assets/major-chord-generatory.py`. All progressions contain exactly four chords, with one chord assigned to each bar. It supports Ionian, Lydian, Mixolydian, major-seventh harmony, and borrowed major-key colors such as minor `iv`, `bVI`, and `bVII`.

Available major moods are:

- Uplifting & Hopeful - 12 progressions
- Romantic & Heartfelt - 12 progressions
- Tender Hope - 12 progressions
- Quiet Triumph - 12 progressions
- Tears of Joy - 12 progressions
- Pain / Heartbreak - 18 progressions

Major Solo Performance currently contains 78 strict four-bar progressions. Its `Pain / Heartbreak` group uses borrowed minor harmony, `vi`, `iii`, major sevenths, and modal mixture to create bittersweet major-key compositions.

## Post-Generation Controls

Generation modules now share the same repeat workflow after saving a MIDI:

```text
G -> Generate again
B -> Back
Q -> Quit the current module
```

Use `G` to stay inside the current composer and quickly create another variation. Use `B` to return to that module's previous menu, or `Q` to leave the current composer and return toward the ANIMA workstation menu.

## Run From Source

Use this if you want to run the Python source instead of the compiled EXE.

```powershell
cd "C:\Users\Administrator.DESKTOP-7PUVTGC\Desktop\progressions"
py anima-midi-production-engine.py
```

To run the GUI from source:

```powershell
py anima_gui_workstation.py
```

The source engine requires `mido`.

## Build The Windows EXEs

Use the included build script:

```powershell
cd "C:\Users\Administrator.DESKTOP-7PUVTGC\Desktop\progressions"
.\build_windows_exes.bat
```

The script will:

1. Create a local `.venv` if needed.
2. Ensure `pip` is available.
3. Install `pyinstaller` and `mido` into the local environment.
4. Build `dist\ANIMA-MIDI-Engine.exe`.
5. Build `dist\ANIMA-Workstation.exe`.

Do not install PyInstaller into the global `uv`-managed Python. The build script uses the local virtual environment on purpose.

## Tauri Suite Prototype

The project also includes a next-generation Direction 2 interface:

```text
anima_tauri_suite/
```

This is a glassy purple Tauri-style suite that mirrors the command-line engine workflow with a modern HTML/CSS frontend and a Rust backend bridge. It launches `ANIMA-MIDI-Engine.exe`, streams engine output into the session log, and sends the same menu choices or prompt responses that the command-line engine expects.

To build it, install Node.js LTS and Rust/Cargo first. If `npm` is not recognized, install Node.js:

```powershell
winget install OpenJS.NodeJS.LTS
```

Then install Rust:

```powershell
winget install Rustlang.Rustup
```

Close and reopen PowerShell, then verify:

```powershell
node --version
npm --version
cargo --version
```

If `npm` is still not recognized, check the standard Windows install path:

```powershell
Test-Path "C:\Program Files\nodejs\npm.cmd"
```

If it returns `True`, add Node.js to your user PATH:

```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Program Files\nodejs",
  "User"
)
```

Close and reopen PowerShell again, then run:

```powershell
npm --version
```

After that, run:

```powershell
cd anima_tauri_suite
npm install
npm run dev
```

For production:

```powershell
npm run build
```

The compiled Tauri app must stay in the same folder as:

```text
ANIMA-MIDI-Engine.exe
```

## Project Structure

```text
progressions/
├── anima-midi-production-engine.py   # Original command-line engine
├── anima_gui_workstation.py          # Windows GUI wrapper
├── anima_tauri_suite/                # Direction 2 Tauri suite source
├── build_windows_exes.bat            # Rebuilds both EXEs
├── README.md
├── assets/                           # Required engine modules
│   ├── solo_performance_minor.py     # Four-bar minor Solo Performance
│   └── solo_performance_major.py     # Four-bar major Solo Performance
├── dist/
│   ├── ANIMA-MIDI-Engine.exe         # Backend console engine
│   └── ANIMA-Workstation.exe         # GUI workstation
└── midi_files/                       # Generated MIDI output
```

## Notes

- `ANIMA-MIDI-Engine.exe` must remain beside `ANIMA-Workstation.exe`.
- The GUI is a hybrid wrapper. It sends the same menu choices you would type manually in the console.
- If the GUI cannot find the engine, confirm both EXEs are in the same folder.
- If the engine reports a missing Python module after rebuild, add that module to `build_windows_exes.bat` in the dependency install line and as a PyInstaller hidden import if needed.
