# 🌌 ANIMA MIDI Music Production Engine
> **Unified, Mood-Adaptive, Multi-Track MIDI Composition Suite**

```text
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║      A N I M A   M I D I   P R O D U C T I O N   S U I T E  ║
║             —  The Complete Composition Engine  —          ║
║                                                            ║
║    Mood-Adaptive  |  Multi-Track  |  Unified Orchestration ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

**ANIMA** is a professional-grade command-line MIDI composition suite written in Python. It generates multi-track, humanized MIDI arrangements using pure music theory models, Markov chain voice leading, and mood-adaptive chord progression algorithms. All engines are unified under a single master workstation — `anima-midi-production-engine.py` — accessible from one entry point.

---

## 🌟 Key Features

- **Unified Workstation**: One entry point (`anima-midi-production-engine.py`) boots all three composition engines — Minor Scale, Major Scale, and VVC String Orchestrator — dynamically.
- **Minor Scale Engine**: 5 emotional families (Sorrowful, Romantic, Yearning, Hopeful, Tragic/Epic), Emotion Fusion Studio for blended moods, Surprise generation, and a Melodic Overlayer.
- **Major Scale Engine**: 4 emotional families (Uplifting/Joyful, Majestic/Heroic, Serene/Ambient, Nostalgic/Bittersweet), Emotion Fusion Studio, Surprise blends, and Melodic Overlayer.
- **VVC String Quartet Engine**: Full 7-track orchestral compositions — String Pad, Violin I, Violin II, Viola, Cello, Unified Ostinato, and Piano Melody. Mood-driven voice leading and humanized CC expression curves.
- **Melodic Overlayer**: Feed any `.mid` file into either chord generator and the suite auto-detects the key/tempo, then composites a lush 7-track string/piano quartet overlay on top.
- **120-Bar Epic Arranger + Choir**: Expand a user-edited 4-bar MIDI source into a full 120-bar cinematic arrangement with dynamic section-aware SATB choir (channels 7–10) covering Intro → Build-up → Main Theme → Development → Climax → Final Chorus → Outro.
- **Double-Layer Decoupled Markov Model**: A toggleable generation mode that subdivides bars into half/quarter-note rhythmic grids and performs a second-layer Markov random walk to assign harmonically coherent chords at each subdivision — producing varied, emotionally catchy progressions that go far beyond monotonous whole-note loops.
- **Emotion Fusion Studio**: Blend any combination of emotional style families to create complex, customized tension arcs and hybrid chord progressions.
- **MIDI CC Humanization**: Automated MIDI CC #11 (Expression) and CC #1 (Modulation) envelope curves on all tracks for realistic sampler response.
- **Spanish Guitar Composer** *(Option 7)*: 4-track nylon guitar engine built from direct MIDI sample analysis. Bajo, Rasgueado arpeggios, Alzapua counter-melody, and Picado lead runs across 7 moods and 7 Spanish scales (Harmonic Minor, Phrygian Dominant, Phrygian, Dorian, Natural Minor, Ionian, Mixolydian).

---

## 📂 Project Architecture

```
progressions/
├── anima-midi-production-engine.py   ← Master unified workstation (START HERE)
├── README.md
├── midi_files/                       ← Auto-created; all generated MIDI output lands here
├── samples/                          ← Optional; place reference MIDI files here
└── assets/                           ← All composition sub-engines
    ├── minor-chord-generatory.py     ← Minor Scale Engine (Aeolian, Phrygian, Dorian, etc.)
    ├── major-chord-generatory.py     ← Major Scale Engine (Ionian, Lydian, Mixolydian, etc.)
    ├── VVC.py                        ← VVC String Orchestration Engine (Quartet + Choir + Arranger)
    ├── specialist_styles.py          ← Shared orchestration backend (CC curves, percussion grids)
    └── __init__.py
```

> **Note:** The `assets/` scripts can also be run standalone, but using the unified master entry point is strongly recommended for seamless cross-engine access and toggle functionality.

---

## ⚙️ Environment Setup & Installation

### 1. Navigate to the project directory
```powershell
cd c:\Users\Administrator.DESKTOP-7PUVTGC\Desktop\progressions
```

### 2. Configure the Python Virtual Environment
```powershell
# Create virtual environment
py -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1
```

### 3. Install Required Dependencies
```powershell
pip install mido
```

### 4. Launch the Unified Workstation
```powershell
# Recommended — launches all engines from one menu
py anima-midi-production-engine.py
```

Or launch individual engines directly:
```powershell
# Minor Scale Engine only
py assets/minor-chord-generatory.py

# Major Scale Engine only
py assets/major-chord-generatory.py

# VVC String Orchestrator only
py assets/VVC.py
```

---

## 🎛️ Master Workstation — Menu Overview

When you run `anima-midi-production-engine.py`, the following options are available:

| Option | Label | Description |
| :---: | :--- | :--- |
| `1` | **Minor Scale Engine** | 5 minor emotional families, Fusion Studio, Surprise mode, Melodic Overlayer |
| `2` | **Major Scale Engine** | 4 major emotional families, Fusion Studio, Surprise blends, Melodic Overlayer |
| `3` | **VVC String Quartet Engine** | Compose 4-bar orchestral loops in any key, scale, tempo, and mood |
| `4` | **120-Bar Epic Arranger + Choir** | Expand a 4-bar MIDI into a full cinematic 120-bar song arc with SATB choir |
| `5` | **Melodic Overlayer** | Analyze any MIDI file and add a 7-track string/piano quartet overlay |
| `6` | **DAW Routing & MIDI Channel Manual** | View track/channel assignments for sampler configuration |
| `7` | **Spanish Guitar Composer** | Bajo · Rasgueado · Alzapua · Picado — 4-track nylon guitar loops across 7 Spanish moods |
| `T` | **Toggle Generation Mode** | Switch between **Simple** (whole notes) and **Double-Layer Decoupled** (subdivided Markov) |
| `0` | **Exit** | — |

---

## 🎭 Generation Modes

### Simple Mode (Default)
Each chord in the progression receives a full 4-beat whole note. Clean, predictable, and great for structured reference loops.

### Double-Layer Decoupled Markov Mode (Toggle with `T`)
A two-layer stochastic model that generates far more dynamic and varied compositions:

- **Layer 1 — Rhythm Grid Selection**: Based on the current mood's tension value, one of several bar subdivision templates is randomly chosen (e.g. `[4.0]`, `[2.0, 2.0]`, `[2.0, 1.0, 1.0]`, `[1.0, 1.0, 1.0, 1.0]`).
- **Layer 2 — Harmonic Random Walk**: A second Markov chain performs a voice-led walk through the current scale's transition matrix, assigning harmonically coherent chord symbols to each subdivision slot.

All melody generators, counter-melody, cello, viola, and piano parts are **subdivision-aware**: they query the active chord and scale at each beat position rather than at the bar level, producing tight voice leading over complex rhythmic shapes.

> Enable Decoupled Mode in the master workstation with `T` before entering any engine. The mode persists across all subsequent generations until toggled again.

---

## 🎼 Emotional Style Families

### Minor Scale Engine
| Key | Family | Tension | Character |
| :---: | :--- | :---: | :--- |
| A | Sorrowful / Melancholic / Dark | 60% | Deep grief, tragedy, loss |
| B | Romantic / Passionate / Intense | 55% | Love, longing, drama |
| C | Yearning / Nostalgic / Bittersweet | 45% | Wistfulness, memory, sweet sadness |
| D | Hopeful / Resolute / Determined | 40% | Rising spirit, courage, resolve |
| E | Tragic-Epic / Cinematic / Majestic | 75% | Grand darkness, film score tension |

### Major Scale Engine
| Key | Family | Tension | Character |
| :---: | :--- | :---: | :--- |
| A | Uplifting / Joyful / Bright | 35% | Sunny energy, happiness, optimism |
| B | Majestic / Triumphant / Heroic | 65% | Glory, victory, epic power |
| C | Serene / Dreamy / Ambient | 25% | Calm, floating, celestial peace |
| D | Nostalgic / Bittersweet / Reflective | 45% | Warm memories, gentle sadness |

---

## 🎚️ DAW Instrument Routing Table

All engines produce standard multi-track MIDI files to `midi_files/`. Assign channels to your sampler patches as follows:

### Spanish Guitar Composer Output (4 Tracks — GM 24 Nylon Guitar)
| Track | Channel | Register | Role | Technique |
| :---: | :---: | :--- | :--- | :--- |
| Track 0 | Ch 0 | E2–F#3 (MIDI 40–54) | Bajo — Bass | Root + 5th anchor plucks |
| Track 1 | Ch 1 | G2–F#4 (MIDI 43–66) | Rasgueado — Chord Arpeggio | Single-note ascending/descending chord outlines |
| Track 2 | Ch 2 | G3–C5 (MIDI 55–72) | Alzapua — Counter-Melody | Sparse inner voice, stepwise voice-led |
| Track 3 | Ch 3 | D4–A5 (MIDI 62–81) | Picado — Lead Melody | 16th-note ornamental runs + sustained phrases |

> **DAW tip**: Route all 4 channels to the **same nylon guitar patch** (e.g. Ample Guitar N, Orange Tree Samples Evolution Nylon), panned slightly centre. Use velocity sensitivity and round-robin articulations for realism.

### VVC String Quartet Output (7 Tracks)
| Track | Channel | GM Program | Target Instrument / Patch | Recommended Libraries |
| :---: | :---: | :---: | :--- | :--- |
| Track 0 | Ch 0 | 48 | String Ensemble Pad | Spitfire Chamber Strings, BBCSO |
| Track 1 | Ch 1 | 40 | Violin I — Lead Melody | Spitfire Symphonic Strings |
| Track 2 | Ch 2 | 40 | Violin II — Counter-melody | EastWest Hollywood Strings |
| Track 3 | Ch 3 | 41 | Viola — Harmonic Support | Orchestral Tools Berlin Strings |
| Track 4 | Ch 4 | 42 | Cello — Bass Pedal Line | Cinesamples CineStrings |
| Track 5 | Ch 5 | 49 | Unified Ostinato (Pizzicato/Arco) | Spitfire Albion ONE |
| Track 6 | Ch 6 | 0  | Piano Melody — High Decoration | Native Instruments The Grandeur |

### 120-Bar Arrangement — Additional Choir Tracks
| Track | Channel | Role | Voice | Recommended Libraries |
| :---: | :---: | :--- | :--- | :--- |
| Track 7 | Ch 7 | SATB Choir | Soprano | EastWest Symphonic Choirs |
| Track 8 | Ch 8 | SATB Choir | Alto | EastWest Symphonic Choirs |
| Track 9 | Ch 9 | SATB Choir | Tenor | Spitfire Albion Tundra |
| Track 10 | Ch 10 | SATB Choir | Bass | Spitfire Albion Tundra |

### Minor / Major Scale Engine Loop Output (3 Tracks)
| Track | Channel | Target Instrument / Patch | Recommended Libraries |
| :---: | :---: | :--- | :--- |
| Track 0 | Ch 0 | Chord Voicings (Strings/Piano) | Spitfire Labs, Keyscape |
| Track 1 | Ch 1 | Lead Melody | Violin Solo / Synth Lead |
| Track 2 | Ch 2 | Counter-Melody | Viola / Cello / Synth Pad |

> **Tip:** For the most realistic playback, ensure all sampler patches respond to **MIDI CC #11 (Expression)** and **MIDI CC #1 (Modulation)**. The ANIMA engine generates automated dynamic envelope curves on every track.

---

## 📁 Output File Naming Convention

Generated MIDI files are automatically saved to `midi_files/` with descriptive names encoding key musical parameters:

```
VVC_String_Quartet_4Bar_Sorrowful__Dark_Lament__A_Minor__90BPM.mid
Mood__Uplifting_Joyful_Bright__Pop-Punk_Anthem__C_Major.mid
Blend__Nostalgic+Uplifting__Wistful_Reflection__G_Major.mid
```

If a filename already exists, a `_v2`, `_v3`, etc. suffix is appended automatically.

---

## 🔧 Technical Notes

- **Python**: `py` (Windows launcher) or `python3` on macOS/Linux.
- **Dependencies**: Only `mido` is required. No external audio libraries.
- **Module loading**: The master workstation uses `importlib.util` to dynamically load each sub-engine from `assets/`, injecting the `GENERATION_MODE` state at runtime.
- **Ticks per beat**: All engines use `tpb = 480` for high DAW compatibility.
- **No static templates**: All chord voicings, rhythms, and melodies are procedurally generated on every run — no two outputs are identical.
