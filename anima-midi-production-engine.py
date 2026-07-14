# -*- coding: utf-8 -*-
"""
ANIMA MIDI MUSIC PRODUCTION ENGINE
-- Master Orchestration Workstation --
Unifies the Minor Scale Engine, Major Scale Engine, and VVC Orchestral Arranger
into a single premium composition portal.
"""

import os
import sys
import time
import random
import importlib.util

EXIT_MUSICAL_MESSAGES = [
    "May your next melody arrive before the silence fades.",
    "Keep the rhythm moving, even when the room goes quiet.",
    "Every ending is a dominant chord waiting to resolve.",
    "Let the final note ring. The next song is already listening.",
    "May your chords be rich, your melodies fearless, and your timing human.",
    "The session ends here, but the progression keeps moving.",
    "Leave a little silence between today and your next masterpiece.",
    "May inspiration find you somewhere between the downbeat and the dream.",
    "Keep composing—the world still needs sounds it has never heard.",
    "Until the next measure: stay curious, stay melodic.",
    "May your bass be deep, your harmonies warm, and your crescendos earned.",
    "The orchestra rests. Your imagination does not.",
    "Take the motif with you; it may become a symphony tomorrow.",
    "May every unresolved chord lead you somewhere beautiful.",
    "Fade out gently. Return with thunder.",
    "The MIDI stops here. The music does not.",
]

# ================================================================
# SYSTEM PATH SETUP
# ================================================================
assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets'))
if assets_dir not in sys.path:
    sys.path.append(assets_dir)

def _load_module(module_name, filename):
    filepath = os.path.join(assets_dir, filename)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Missing core asset file: {filename}")
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

try:
    print("  [LOADING] Initializing Minor Scale Engine...")
    minor_engine = _load_module('minor_chord_generatory', 'minor-chord-generatory.py')

    print("  [LOADING] Initializing Major Scale Engine...")
    major_engine = _load_module('major_chord_generatory', 'major-chord-generatory.py')

    print("  [LOADING] Initializing VVC Orchestration Engine...")
    vvc_engine = _load_module('VVC', 'VVC.py')

    print("  [LOADING] Initializing Spanish Guitar Engine...")
    sg_engine = _load_module('spanish_guitar', 'spanish_guitar.py')

    print("  [LOADING] Initializing Spanish Family Engine...")
    sf_engine = _load_module('spanish_family', 'spanish_family.py')

    print("  [LOADING] Initializing World Composer Engine...")
    wc_engine = _load_module('world_composer', 'world_composer.py')

    print("  [LOADING] Initializing Solo Performance Engine...")
    solo_engine = _load_module('solo_performance_minor', 'solo_performance_minor.py')

    print("  [LOADING] Initializing Major Solo Performance Engine...")
    major_solo_engine = _load_module('solo_performance_major', 'solo_performance_major.py')

    print("  [LOADING] Initializing Cinematic Engine...")
    cinematic_engine = _load_module('cinematic', 'cinematic.py')

    print("  [SUCCESS] All ANIMA sub-engines loaded successfully.\n")
except Exception as e:
    print(f"\n  [FATAL ERROR] Failed to load engines: {e}")
    sys.exit(1)


def _div(char='-', w=62):
    print(char * w)


def _pause():
    input("  Press [Enter] to return...")


def _random_exit_message():
    return random.choice(EXIT_MUSICAL_MESSAGES)


def _propagate_generation_mode(generation_mode):
    minor_engine.GENERATION_MODE = generation_mode
    major_engine.GENERATION_MODE = generation_mode
    vvc_engine.GENERATION_MODE = generation_mode
    sg_engine.GENERATION_MODE = generation_mode
    sf_engine.GENERATION_MODE = generation_mode
    wc_engine.GENERATION_MODE = generation_mode
    solo_engine.GENERATION_MODE = generation_mode
    major_solo_engine.GENERATION_MODE = generation_mode


def _prompt_midi_path(prompt="  Enter path to MIDI file: "):
    filepath = input(prompt).strip().strip('"').strip("'")
    if not os.path.isfile(filepath):
        print(f"  [ERROR] File not found: {filepath}")
        return None
    return filepath


def _select_cinematic_key(is_major):
    available_keys = sorted(list(cinematic_engine.ROOTS.keys()))
    tonality_label = "Major" if is_major else "Minor"
    enharmonics = {
        'Db': 'C#', 'D#': 'Eb', 'Gb': 'F#', 'A#': 'Bb', 'Ab': 'G#',
    }

    print(f"\n  Select {tonality_label} Key (Available: {', '.join(available_keys)}):")
    root_name_raw = input("  --> ").strip()
    if len(root_name_raw) >= 1:
        root_name = root_name_raw[0].upper() + root_name_raw[1:]
    else:
        root_name = 'C' if is_major else 'D'

    root_name = enharmonics.get(root_name, root_name)
    if root_name not in cinematic_engine.ROOTS:
        root_name = 'C' if is_major else 'D'
    return root_name, cinematic_engine.ROOTS[root_name]


def _select_cinematic_bpm(is_major):
    print("\n  Select Tempo (BPM) [e.g. 100, 120, 140]:")
    bpm_str = input("  --> ").strip()
    try:
        return int(bpm_str)
    except ValueError:
        return 120 if is_major else 110


def _save_cinematic_mid(mid, out_dir, mood_name, root_name, tonality_label, bpm, prog_label):
    adjectives = [
        "Apex", "Infinite", "Midnight", "Titan", "Solar", "Gothic", "Ethereal", "Grim",
        "Silent", "Shadow", "Crimson", "Nebula", "Spectral", "Cosmic", "Lost", "Fallen",
        "Eternal", "Frozen", "Abyssal", "Radiant", "Iron", "Storm", "Phoenix", "Astral",
        "Mystic", "Ancient", "Vortex", "Golden", "Obsidian", "Celestial", "Wounded",
    ]
    nouns = [
        "Ascent", "Requiem", "Odyssey", "Eclipse", "Horizon", "Empire", "Sanctuary",
        "Vanguard", "Echo", "Whisper", "Rift", "Conquest", "Genesis", "Destiny", "Void",
        "Valhalla", "Covenant", "Chronicle", "Legacy", "Bastion", "Rebirth", "Summit",
        "Oracle", "Wasteland", "Mirage", "Lament", "Citadel", "Overture", "Pilgrimage",
    ]
    project_title = f"{random.choice(adjectives)}_{random.choice(nouns)}"
    fname = (
        f"{project_title}__Cinematic_{mood_name.replace(' ', '_')}__{root_name}"
        f"_{tonality_label}__{bpm}BPM__{prog_label}"
    )
    fpath = os.path.join(out_dir, fname + ".mid")
    idx = 1
    while os.path.exists(fpath):
        fpath = os.path.join(out_dir, f"{fname}_v{idx}.mid")
        idx += 1
    mid.save(fpath)
    print(f"\n  [SAVED]  {os.path.basename(fpath)}")
    print(f"  [PATH ]  {fpath}\n")


def _run_cinematic_direct(out_dir, is_major=None):
    if is_major is None:
        is_major = random.choice([True, False])
        print(f"  Surprise tonality: {'Major' if is_major else 'Minor'}")

    if is_major:
        print("\n  Select Major Cinematic Mood:")
        print("    1 -> Triumphant Ascent")
        print("    2 -> Celestial Wonder")
        print("    3 -> Golden Pastoral")
    else:
        print("\n  Select Minor Cinematic Mood:")
        print("    1 -> Ethereal Gothic Fantasy")
        print("    2 -> Epic Heroic Action")
        print("    3 -> Dark Assassin Stealth")

    mood_str = input("  --> ").strip()
    mood_id = int(mood_str) if mood_str in ('1', '2', '3') else random.randint(1, 3)
    root_name, root_val = _select_cinematic_key(is_major)
    bpm = _select_cinematic_bpm(is_major)

    print("\n  [GENERATING] Composing cinematic arrangement...")
    if is_major:
        mid, mood_name, prog_label = cinematic_engine.compose_cinematic_major_track(mood_id, bpm, root_name, root_val)
        tonality_label = "Major"
    else:
        mid, mood_name, prog_label = cinematic_engine.compose_cinematic_track(mood_id, bpm, root_name, root_val)
        tonality_label = "Minor"

    _save_cinematic_mid(mid, out_dir, mood_name, root_name, tonality_label, bpm, prog_label)


def _run_generate_new_midi(out_dir):
    while True:
        print("""
GENERATE NEW MIDI

  1 -> Minor Scale Engine
  2 -> Major Scale Engine
  3 -> VVC String Quartet Engine
  4 -> Surprise Me
  B -> Back
""")
        _div()
        choice = input("  --> ").strip().lower()
        _div('=')

        if choice == 'b':
            return
        try:
            if choice == '1':
                print("  Opening Minor Scale Engine...")
                minor_engine.main(out_dir)
            elif choice == '2':
                print("  Opening Major Scale Engine...")
                major_engine.main(out_dir)
            elif choice == '3':
                print("  Opening VVC String Quartet Engine...")
                vvc_engine.main(out_dir)
            elif choice == '4':
                selected_engine = random.choice(['minor', 'major', 'vvc'])
                if selected_engine == 'minor':
                    minor_engine.main(out_dir)
                elif selected_engine == 'major':
                    major_engine.main(out_dir)
                else:
                    vvc_engine.main(out_dir)
            else:
                print("  [!] Invalid choice. Enter 1-4 or B.\n")
        except Exception as e:
            print(f"  [ERROR] Engine failure: {e}")


def _run_existing_midi_menu(out_dir):
    while True:
        print("""
WORK WITH EXISTING MIDI

  1 -> Add String Quartet Overlay
  2 -> Expand 4-Bar MIDI to 120-Bar Arrangement
  3 -> Add Choir to Existing MIDI
  4 -> Analyze MIDI Key / Tempo
  B -> Back
""")
        _div()
        choice = input("  --> ").strip().lower()
        _div('=')

        if choice == 'b':
            return
        if choice not in ('1', '2', '3', '4'):
            print("  [!] Invalid choice. Enter 1-4 or B.\n")
            continue

        filepath = _prompt_midi_path()
        if not filepath:
            continue

        try:
            if choice == '1':
                vvc_engine.generate_quartet_over_midi(filepath, out_dir)
            elif choice == '2':
                vvc_engine.generate_120bar_arrangement_from_midi(filepath, out_dir)
            elif choice == '3':
                vvc_engine.generate_choir_over_midi(filepath, out_dir)
            elif choice == '4':
                chord_groups, _ = vvc_engine.parse_midi_chords(filepath)
                if not chord_groups:
                    print("  [ERROR] No chord groups detected.")
                else:
                    root_name, _, _, scale_name, is_minor = vvc_engine.detect_key(chord_groups)
                    bpm = vvc_engine.detect_tempo(filepath)
                    print(f"\n  Key      : {root_name} {scale_name}")
                    print(f"  Tonality : {'Minor' if is_minor else 'Major'}")
                    print(f"  BPM      : {bpm}\n")
        except Exception as e:
            print(f"  [ERROR] Existing-MIDI task failed: {e}")


def _run_cinematic_menu(out_dir):
    while True:
        print("""
CINEMATIC TRAILER ENGINE

  1 -> Minor Cinematic Cue
  2 -> Major Cinematic Cue
  3 -> Surprise Cinematic Cue
  B -> Back
""")
        _div()
        choice = input("  --> ").strip().lower()
        _div('=')

        try:
            if choice == 'b':
                return
            elif choice == '1':
                while True:
                    _run_cinematic_direct(out_dir, is_major=False)
                    print("  [G] Generate again  [B] Back  [Q] Quit")
                    sub = input("  --> ").strip().lower()
                    if sub == 'g':
                        continue
                    if sub == 'q':
                        return
                    if sub == 'b':
                        break
            elif choice == '2':
                while True:
                    _run_cinematic_direct(out_dir, is_major=True)
                    print("  [G] Generate again  [B] Back  [Q] Quit")
                    sub = input("  --> ").strip().lower()
                    if sub == 'g':
                        continue
                    if sub == 'q':
                        return
                    if sub == 'b':
                        break
            elif choice == '3':
                while True:
                    _run_cinematic_direct(out_dir, is_major=None)
                    print("  [G] Generate again  [B] Back  [Q] Quit")
                    sub = input("  --> ").strip().lower()
                    if sub == 'g':
                        continue
                    if sub == 'q':
                        return
                    if sub == 'b':
                        break
            else:
                print("  [!] Invalid choice. Enter 1-3 or B.\n")
        except Exception as e:
            print(f"  [ERROR] Cinematic Engine failure: {e}")


def _run_guitar_specialist_menu(out_dir):
    while True:
        print("""
GUITAR & SPECIALIST STYLES

  1 -> Spanish Guitar Composer
  2 -> Spanish Family Composer
  3 -> World Composer
  4 -> Solo Performance (Minor)
  5 -> Solo Performance (Major)
  B -> Back
""")
        _div()
        choice = input("  --> ").strip().lower()
        _div('=')

        if choice == 'b':
            return
        elif choice == '1':
            try:
                sg_engine.main(out_dir)
            except Exception as e:
                print(f"  [ERROR] Spanish Guitar Engine failure: {e}")
        elif choice == '2':
            try:
                sf_engine.main(out_dir)
            except Exception as e:
                print(f"  [ERROR] Spanish Family Engine failure: {e}")
        elif choice == '3':
            try:
                wc_engine.main(out_dir)
            except Exception as e:
                print(f"  [ERROR] World Composer Engine failure: {e}")
        elif choice == '4':
            try:
                solo_engine.main(out_dir)
            except Exception as e:
                print(f"  [ERROR] Solo Performance Engine failure: {e}")
        elif choice == '5':
            try:
                major_solo_engine.main(out_dir)
            except Exception as e:
                print(f"  [ERROR] Major Solo Performance Engine failure: {e}")
        else:
            print("  [!] Invalid choice. Enter 1, 2, 3, 4, 5 or B.\n")


def _run_help_menu():
    while True:
        print("""
ROUTING / HELP

  1 -> DAW Channel Routing Guide
  2 -> Engine Track Layouts
  3 -> Filename Naming Guide
  4 -> Recommended Instrument Patches
  B -> Back
""")
        _div()
        choice = input("  --> ").strip().lower()
        _div('=')

        if choice == 'b':
            return
        elif choice in ('1', '2', '4'):
            vvc_engine.show_instrument_routing()
            _pause()
        elif choice == '3':
            print("""
FILENAME NAMING GUIDE

  Cinematic:
    Project_Title__Cinematic_Mood__Key_Tonality__BPM__Progression.mid

  Major / Minor scale engines:
    Project_Title__Major_Engine_Mood__Style__Key_Major__BPM__Progression.mid
    Project_Title__Minor_Engine_Mood__Style__Key_Minor__BPM__Progression.mid

  VVC:
    Project_Title__VVC_Engine_Mood__Style__Key_Tonality__BPM__Progression.mid
""")
            _pause()
        else:
            print("  [!] Invalid choice. Enter 1-4 or B.\n")


def _run_settings_menu(generation_mode, out_dir):
    while True:
        mode_label = (
            "SIMPLE (Whole Notes)"
            if generation_mode == 'simple'
            else "DOUBLE-LAYER DECOUPLED (Subdivided Halves/Quarters)"
        )
        print(f"""
SETTINGS

  1 -> Toggle Generation Mode  [Active: {mode_label}]
  2 -> Output Folder           [Active: {out_dir}]
  B -> Back
""")
        _div()
        choice = input("  --> ").strip().lower()
        _div('=')

        if choice == 'b':
            return generation_mode, out_dir
        elif choice == '1':
            generation_mode = 'decoupled' if generation_mode == 'simple' else 'simple'
            _propagate_generation_mode(generation_mode)
            print(f"  [TOGGLE] Generation mode -> {generation_mode.upper()}")
        elif choice == '2':
            new_out = input("  Output folder: ").strip().strip('"').strip("'")
            if new_out:
                out_dir = new_out
                os.makedirs(out_dir, exist_ok=True)
                print(f"  [OUTPUT] {out_dir}")
        else:
            print("  [!] Invalid choice. Enter 1-2 or B.\n")


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    out_dir = 'midi_files'
    os.makedirs(out_dir, exist_ok=True)

    generation_mode = 'simple'
    _propagate_generation_mode(generation_mode)

    while True:
        print(f"""
+--------------------------------------------------------------+
|                                                              |
|     A N I M A   M I D I   P R O D U C T I O N   S U I T E    |
|          ---  Master Orchestration Workstation  ---          |
|                                                              |
|   Mood-Adaptive  |  Multi-Track  |  Unified Orchestration    |
|                                                              |
+--------------------------------------------------------------+

  1 -> Generate New MIDI
  2 -> Work With Existing MIDI
  3 -> Cinematic Trailer Engine
  4 -> Guitar & Specialist Styles
  5 -> Routing / Help
  6 -> Settings
  0 -> Exit
""")
        _div()
        choice = input("  --> ").strip().lower()
        _div('=')

        _propagate_generation_mode(generation_mode)

        if choice == '0':
            print(f"\n  ♪ {_random_exit_message()} ♪")
            print("  Exiting ANIMA Workstation.\n")
            break

        elif choice == '1':
            _run_generate_new_midi(out_dir)

        elif choice == '2':
            _run_existing_midi_menu(out_dir)

        elif choice == '3':
            _run_cinematic_menu(out_dir)

        elif choice == '4':
            _run_guitar_specialist_menu(out_dir)

        elif choice == '5':
            _run_help_menu()

        elif choice == '6':
            generation_mode, out_dir = _run_settings_menu(generation_mode, out_dir)

        else:
            print("  [!] Invalid choice. Enter 1-6 or 0.\n")

        _div()
        time.sleep(0.1)


if __name__ == '__main__':
    main()
