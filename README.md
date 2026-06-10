# 🌌 ANIMA MIDI Music Production Engine
> **Unified, Mood-Adaptive, Multi-Track MIDI Composition Suite**

```text
+--------------------------------------------------------------+
|                                                              |
|     A N I M A   M I D I   P R O D U C T I O N   S U I T E    |
|          ---  Master Orchestration Workstation  ---          |
|                                                              |
|   Mood-Adaptive  |  Multi-Track  |  Unified Orchestration    |
|                                                              |
+--------------------------------------------------------------+
```

**ANIMA** is a professional-grade command-line MIDI composition suite written in Python. It generates multi-track, humanized MIDI arrangements using pure music theory models, Markov chain voice leading, and mood-adaptive chord progression algorithms. All engines are unified under a single master workstation — `anima-midi-production-engine.py` — accessible from one entry point.

---

## 🌟 Key Features

- **Unified Workstation**: One entry point (`anima-midi-production-engine.py`) boots all composition engines dynamically from one menu.
- **Minor Scale Engine**: 5 emotional families (Sorrowful, Romantic, Yearning, Hopeful, Tragic/Epic), Emotion Fusion Studio for blended moods, Surprise generation, and a Melodic Overlayer.
- **Major Scale Engine**: 4 emotional families (Uplifting/Joyful, Majestic/Heroic, Serene/Ambient, Nostalgic/Bittersweet), Emotion Fusion Studio, Surprise blends, and Melodic Overlayer.
- **VVC String Quartet Engine**: Full 7-track orchestral compositions — String Pad, Violin I, Violin II, Viola, Cello, Unified Ostinato, and Piano Melody. Mood-driven voice leading and humanized CC expression curves.
- **Melodic Overlayer**: Feed any `.mid` file into either chord generator and the suite auto-detects the key/tempo, then composites a lush 7-track string/piano quartet overlay on top.
- **120-Bar Epic Arranger + Choir**: Expand a user-edited 4-bar MIDI source into a full 120-bar cinematic arrangement with dynamic section-aware SATB choir (channels 7–10) covering Intro → Build-up → Main Theme → Development → Climax → Final Chorus → Outro.
- **Modern Cinematic & Ethereal Fantasy Trailer Engine** *(Option 8)*: Professional stem-based cinematic MIDI with a DFS-backtracked melody, 4-part SATB voice-leading choir, sub bass, staccato ostinato, drone, and mood-specific instruments across 3 moods and 12 minor keys.
- **Double-Layer Decoupled Markov Model**: A toggleable generation mode that subdivides bars into half/quarter-note rhythmic grids and performs a second-layer Markov random walk to assign harmonically coherent chords at each subdivision.
- **Emotion Fusion Studio**: Blend any combination of emotional style families to create complex, customized tension arcs and hybrid chord progressions.
- **MIDI CC Humanization**: Automated MIDI CC #11 (Expression) and CC #1 (Modulation) envelope curves on all tracks for realistic sampler response.
- **Spanish Guitar Composer** *(Option 7)*: 4-track nylon guitar engine built from direct MIDI sample analysis. Bajo, Rasgueado arpeggios, Alzapua counter-melody, and Picado lead runs across 7 moods and 7 Spanish scales.

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
    ├── cinematic.py                  ← Cinematic Trailer Engine (Option 8) — SATB Choir, Melody, Brass
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
py assets/minor-chord-generatory.py
py assets/major-chord-generatory.py
py assets/VVC.py
py assets/cinematic.py
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
| `8` | **Modern Cinematic Trailer Engine** | Minor *or* Major tonality — Ethereal Gothic · Epic Heroic · Dark Stealth · Triumphant Ascent · Celestial Wonder · Golden Pastoral — multi-stem MIDI with SATB choir and procedural melody |
| `T` | **Toggle Generation Mode** | Switch between **Simple** (whole notes) and **Double-Layer Decoupled** (subdivided Markov) |
| `0` | **Exit** | — |

---

## 🎬 Option 8 — Modern Cinematic & Ethereal Fantasy Trailer Engine

A dedicated cinematic MIDI composition engine (`assets/cinematic.py`) that generates professional, stem-ready 4-bar arrangements in one of three dramatic moods.

### Moods

| # | Mood | Instruments | Character |
| :---: | :--- | :--- | :--- |
| `1` | **Ethereal Gothic Fantasy** | SATB Choir × 4, Harp, Piano, Sub Bass, Drone, Staccato Strings, Melody | Touching, celestial, dark fantasy |
| `2` | **Epic Heroic Action** | SATB Choir × 4, Heavy Brass, Sub Bass, Drone, Staccato Strings, Melody | Intense, cinematic, battle-ready |
| `3` | **Dark Assassin Stealth** | Nylon Guitars, Sparse Piano, Sub Bass, Drone, Staccato Strings, Melody | Brooding, mysterious, tension-driven |

### Foundation Tracks (All Moods)

| Track | GM Program | Role |
| :--- | :---: | :--- |
| Sub Bass | 43 (Contrabass) | Deep root anchor plucks on the beat |
| High Drone | 48 (String Ensemble) | Sustained atmospheric pad |
| Staccato Strings | 48 | Rhythmic staccato ostinato off-beats |
| Melody | 40 (Violin) | Procedural 4-bar motif — singable, unique every run |

### SATB Choir Engine (Mood 1 & 2)

The choir uses a dynamic **nearest-pitch voice-leading algorithm** — each voice resolves to the closest chord tone of the next bar, minimizing interval size to create smooth, human-sounding progressions. Notes are humanized with random attack stagger (0–18 ticks) and breath-release space (35–80 ticks before bar end).

| Track | GM Program | MIDI Range | Role |
| :--- | :---: | :---: | :--- |
| Choir - Bass | 52 (Choir Aahs) | 43–55 (G2–G3) | Root foundation, always locks to chord root |
| Choir - Tenor | 52 | 53–65 (F3–F4) | Smooth voice-led chord tones |
| Choir - Alto | 52 | 59–71 (B3–B4) | Smooth voice-led chord tones |
| Choir - Soprano | 52 | 65–77 (F4–F5) | Smooth voice-led chord tones |

### Major Moods (new)

| # | Mood | Instruments | Character | Tracks |
| :---: | :--- | :--- | :--- | :---: |
| `1` | **Triumphant Ascent** | Brass Fanfare, SATB Choir × 4, Piano, Sub Bass, Drone, Staccato Strings, Melody | Heroic, victorious, soaring | 10 |
| `2` | **Celestial Wonder** | Celesta Arps, SATB Choir × 4, Sub Bass, Drone, Staccato Strings, Melody | Floating, Lydian, magical | 9 |
| `3` | **Golden Pastoral** | Pastoral Harp, Woodwind Lead, Sub Bass, Drone, Staccato Strings, Melody | Warm, Mixolydian, anthemic | 6 |

### Major Scales Used

| Scale | Degrees | Film Character |
| :--- | :--- | :--- |
| **Ionian** (Natural Major) | `0 2 4 5 7 9 11` | Triumphant, resolved, victory fanfares |
| **Lydian** | `0 2 4 6 7 9 11` | Floating wonder — John Williams, Interstellar |
| **Mixolydian** | `0 2 4 5 7 9 10` | Anthemic rock-epic — Game of Thrones style |
| **Melodic Major** | `0 2 4 5 7 8 10` | Bittersweet, nostalgic, poignant endings |

### Major Chord Pool (14 chords)

Includes Lydian `II`, borrowed `bVII`, `bVI`, `bIII`, minor `iv` (Melodic Major), and all diatonic major chords.

### Major Chord Progressions Pool (24 progressions)

| Category | Sample Progressions |
| :--- | :--- |
| Triumphant / Heroic | `I – bVII – IV – I`, `I – V – vi – IV`, `I – bIII – bVII – IV` |
| Lydian Wonder | `I – II – I – V`, `Imaj7 – II – IVmaj7 – I`, `I – II – V – I` |
| Mixolydian Anthem | `I – bVII – I – IV`, `I – IV – bVII – I`, `I – V – bVII – IV` |
| Bittersweet / Nostalgic | `I – vi – IV – V`, `I – iv – I – V`, `I – bVI – bIII – bVII` |

### New Major-Specific Generators

| Generator | GM Program | Role |
| :--- | :---: | :--- |
| `generate_brass_fanfare` | 61 (Brass) | Dotted-quarter + 8th fanfare hits on root/3rd/5th, beats 1 & 3 |
| `generate_celesta_arpeggios` | 8 (Celesta) | Soft ascending 16th-note shimmer in MIDI 72–90 |
| `generate_woodwind_lead` | 73 (Flute) | Stepwise lyrical line in MIDI 65–79, two notes per bar |

The SATB choir, sub bass, drone, staccato ostinato, and DFS melody engine are **fully reused** — the major chord tones (`[0,4,7]` etc.) automatically produce a brighter harmonic output without any separate code.

### Updated Filename Format

The tonality (`Minor` or `Major`) is now encoded in every filename:

```
Radiant_Ascent__Cinematic_Triumphant_Ascent__C_Major__120BPM__I-bVII-IV-I.mid
Spectral_Bastion__Cinematic_Ethereal_Gothic_Fantasy__D_Minor__110BPM__i-III-VI-VII.mid
```


The melody is generated by a **DFS backtracking algorithm** that enforces cinematic phrasing rules on every run:

- **A-A-B-A' phrase structure** across 4 bars (13 notes total)
- **Exactly one defining leap** — Perfect 4th, 5th, minor 6th, or octave (5, 7, 8, or 12 semitones)
- **Stepwise motion everywhere else** — all other intervals ≤ 4 semitones
- **Single unique climax note** placed in Bar 3 or Bar 4
- **Range constraint** — entire melody stays within one octave
- **Chord-tone density** — at least 9 of 13 notes are chord tones of the active bar
- **Candidate shuffling** ensures a different melody on every generation

### Chord Progressions Pool (24 progressions)

The engine randomly selects from 24 progressions grouped into four style categories:

| Category | Examples | Feel |
| :--- | :--- | :--- |
| Epic / Touching | `i – III – VI – VII`, `i – VI – III – VII` | Orchestral, emotional |
| Heroic / Action | `VI – VII – i – v`, `VI – III – iv – i` | Driving, powerful |
| Ethereal / Gothic | `i – VII – VI – V`, `i – iv – III – VII` | Floating, dark, haunting |
| Dorian & Phrygian | `i – IV – VI – VII`, `i – II – VI – VII` | Exotic, soaring, ancient |

### Supported Minor Keys

All 12 chromatic minor keys are supported. The CLI lists all available options and auto-resolves enharmonic equivalents:

```
A  Bb  B  C  C#  D  Eb  E  F  F#  G  G#
```

| Input | Resolves to |
| :--- | :---: |
| `Db` or `db` | `C#` |
| `D#` | `Eb` |
| `Gb` or `gb` | `F#` |
| `Ab` | `G#` |
| `A#` | `Bb` |

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

### Option 8 — Cinematic Engine (Mood 1: Ethereal Gothic Fantasy — 10 Tracks)
| Track | Role | GM Program | Recommended Patch |
| :---: | :--- | :---: | :--- |
| Sub Bass | Deep root anchor | 43 | Kontakt Contrabass, Spitfire LABS Strings |
| High Drone | Atmospheric pad | 48 | EastWest Hollywood Strings Sustain |
| Staccato Strings | Rhythmic ostinato | 48 | Spitfire Chamber Strings Staccato |
| Melody | Procedural violin motif | 40 | Spitfire Symphonic Strings Violin Solo |
| Choir - Bass | SATB bass line | 52 | EastWest Symphonic Choirs Bass |
| Choir - Tenor | SATB tenor | 52 | EastWest Symphonic Choirs Tenor |
| Choir - Alto | SATB alto | 52 | Spitfire Albion Tundra Alto |
| Choir - Soprano | SATB soprano | 52 | Spitfire Albion Tundra Soprano |
| Harp / Nylon Arps | Arpeggio decoration | 46 | Native Instruments Harp, Ample Guitar N |
| Piano Melody | High register melody | 0 | Native Instruments The Grandeur |

### Option 8 — Cinematic Engine (Mood 2: Epic Heroic Action — 8 Tracks)
| Track | Role | GM Program | Recommended Patch |
| :---: | :--- | :---: | :--- |
| Sub Bass | Deep root anchor | 43 | Kontakt Contrabass |
| High Drone | Atmospheric pad | 48 | Spitfire Albion ONE Pad |
| Staccato Strings | Rhythmic ostinato | 48 | EastWest Hollywood Strings Staccato |
| Melody | Procedural violin motif | 40 | Spitfire Symphonic Strings Violin Solo |
| Heavy Brass | Epic unison brass | 61 | Spitfire BBC Symphony Brass |
| Choir - Bass | SATB bass line | 52 | EastWest Symphonic Choirs Bass |
| Choir - Tenor | SATB tenor | 52 | EastWest Symphonic Choirs Tenor |
| Choir - Alto | SATB alto | 52 | Spitfire Albion Tundra Alto |
| Choir - Soprano | SATB soprano | 52 | Spitfire Albion Tundra Soprano |

### Option 8 — Cinematic Engine (Mood 3: Dark Assassin Stealth — 6 Tracks)
| Track | Role | GM Program | Recommended Patch |
| :---: | :--- | :---: | :--- |
| Sub Bass | Deep root anchor | 43 | Kontakt Contrabass |
| High Drone | Atmospheric pad | 48 | Spitfire LABS Frozen Strings |
| Staccato Strings | Rhythmic ostinato | 48 | EastWest Hollywood Strings Staccato |
| Melody | Procedural violin motif | 40 | Cinesamples CineStrings Solo Violin |
| Nylon Guitars | Harp-style arpeggios | 24 | Ample Guitar N, Orange Tree Nylon |
| Dark Piano | Sparse high-register touches | 0 | Keyscape, The Grandeur |

### Spanish Guitar Composer Output (4 Tracks — GM 24 Nylon Guitar)
| Track | Channel | Register | Role | Technique |
| :---: | :---: | :--- | :--- | :--- |
| Track 0 | Ch 0 | E2–F#3 (MIDI 40–54) | Bajo — Bass | Root + 5th anchor plucks |
| Track 1 | Ch 1 | G2–F#4 (MIDI 43–66) | Rasgueado — Chord Arpeggio | Single-note ascending/descending chord outlines |
| Track 2 | Ch 2 | G3–C5 (MIDI 55–72) | Alzapua — Counter-Melody | Sparse inner voice, stepwise voice-led |
| Track 3 | Ch 3 | D4–A5 (MIDI 62–81) | Picado — Lead Melody | 16th-note ornamental runs + sustained phrases |

> **DAW tip**: Route all 4 channels to the **same nylon guitar patch** (e.g. Ample Guitar N, Orange Tree Evolution Nylon), panned slightly centre.

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

Generated MIDI files are automatically saved to `midi_files/` with descriptive names encoding key musical parameters.

### Cinematic Engine (Option 8)
Files are prefixed with a procedurally generated cinematic project title drawn from pools of **27 adjectives × 25 nouns (675 unique combinations)**:

```
Spectral_Bastion__Cinematic_Epic_Heroic_Action__D_Minor__110BPM__VI-VII-i-v.mid
Midnight_Covenant__Cinematic_Ethereal_Gothic_Fantasy__F#_Minor__120BPM__i-VII-VI-V.mid
Crimson_Valhalla__Cinematic_Dark_Assassin_Stealth__G#_Minor__100BPM__VI-III-iv-i.mid
```

**Format**: `{Project_Title}__Cinematic_{Mood}__{Key}_Minor__{BPM}BPM__{Progression}.mid`

### Other Engines
```
Silver_Oracle__VVC_String_Quartet_4Bar_Sorrowful__Dark_Lament__A_Minor__90BPM__i-VI-III-VII.mid
Golden_Harbor__Major_Engine_Uplifting_Joyful_Bright__Pop-Punk_Anthem__C_Major__126BPM__I-V-vi-IV.mid
Obsidian_Lament__Minor_Engine_Blend_Romantic+Tragic__Doomed_Lovers__A_Minor__138BPM__i-VI-bII-V7.mid
```

If a filename already exists, a `_v2`, `_v3`, etc. suffix is appended automatically.

---

## 🔧 Technical Notes

- **Python**: `py` (Windows launcher) or `python3` on macOS/Linux.
- **Dependencies**: Only `mido` is required. No external audio libraries.
- **Module loading**: The master workstation uses `importlib.util` to dynamically load each sub-engine from `assets/`, injecting the `GENERATION_MODE` state at runtime.
- **Ticks per beat**: All engines use `tpb = 480` for high DAW compatibility.
- **No static templates**: All chord voicings, rhythms, and melodies are procedurally generated on every run — no two outputs are identical.
- **Cinematic Melody DFS**: The melody generator uses a Depth-First Search backtracking algorithm with 6 fallback levels and candidate shuffling to guarantee a valid, singable, unique motif every generation.
- **SATB Voice Leading**: The cinematic choir uses nearest-pitch resolution — each voice selects the chord tone requiring the smallest interval move from its previous pitch, replicating natural human vocal behaviour.
