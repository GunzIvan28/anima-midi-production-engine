"""
ANIMA MIDI MUSIC PRODUCTION ENGINE
— Master Orchestration Workstation —
Unifies the Minor Scale Engine, Major Scale Engine, and VVC Orchestral Arranger
into a single premium composition portal.
"""

import os
import sys
import time
import importlib.util

# ── SYSTEM PATH SETUP ────────────────────────────────────────────────────────
# Append assets folder to system path to ensure clean internal imports.
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

    print("  [LOADING] Initializing Cinematic Engine...")
    cinematic_engine = _load_module('cinematic', 'cinematic.py')

    print("  [SUCCESS] All ANIMA sub-engines loaded successfully.\n")
except Exception as e:
    print(f"\n  [FATAL ERROR] Failed to load engines: {e}")
    sys.exit(1)

def _div(char='-', w=62):
    print(char * w)

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    out_dir = 'midi_files'
    os.makedirs(out_dir, exist_ok=True)
    
    generation_mode = 'simple'

    while True:
        mode_label = "SIMPLE (LEGACY Whole Notes)" if generation_mode == 'simple' else "DOUBLE-LAYER DECOUPLED (Subdivided Halves/Quarters)"
        print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║      A N I M A   M I D I   P R O D U C T I O N   S U I T E  ║
║             —  The Complete Composition Engine  —          ║
║                                                            ║
║    Mood-Adaptive  |  Multi-Track  |  Unified Orchestration ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

   [ ── COMPO COMPANIONS (4-BAR LOOPS) ── ]
     1  →  Minor Scale Engine
           Choose from 5 minor families, blend emotions, or mix surprise minor cocktails.

     2  →  Major Scale Engine
           Choose from 4 major families, blend emotions, or mix surprise major cocktails.

     3  →  VVC String Quartet Engine
           Compose 4-bar orchestral loops in any custom key/scale/tempo and mood.

   [ ── UTILITIES & ARRANGEMENTS ── ]
     4  →  120-Bar Epic Arranger + Choir
           Process a 4-bar MIDI file into a massive 120-bar industrial arrangement 
           with dynamic section-aware SATB choir on channels 7-10.

     5  →  Melodic Overlayer (Quartet Overlay)
           Analyze any MIDI file's key/tempo and build a custom 7-track string/piano overlay.

     6  →  DAW Routing & MIDI Channel Manual
           Detailed information on Spitfire/EastWest DAW track configurations.

     7  →  Spanish Guitar Composer
           Bajo · Rasgueado · Alzapua · Picado — 4-track nylon guitar loops.
           Moods: Duende Oscuro, Alma Flamenca, Noche Española, Serenata + more.

     8  →  Modern Cinematic & Ethereal Fantasy Trailer
           Epic 8-bar procedural arrangements.
           Moods: Ethereal Gothic, Epic Action, Dark Assassin.
  ____________________________________________________________
     T  →  Toggle Generation Mode [Active: {generation_mode.upper()}]
           Switches between Simple Mode and Double-Layer Decoupled
     0  →  Exit
""")
        _div()
        choice = input("  --> ").strip().lower()
        _div('=')

        # Propagate the active generation mode to all loaded modules
        minor_engine.GENERATION_MODE = generation_mode
        major_engine.GENERATION_MODE = generation_mode
        vvc_engine.GENERATION_MODE   = generation_mode
        sg_engine.GENERATION_MODE    = generation_mode

        if choice == '0':
            print("  Exiting ANIMA Workstation. Have a highly creative day!\n")
            break

        elif choice == 't':
            generation_mode = 'decoupled' if generation_mode == 'simple' else 'simple'
            print(f"  [TOGGLE] Switched generation mode to: {generation_mode.upper()}")
            time.sleep(0.8)

        elif choice == '1':
            print("  Opening Minor Scale Engine...")
            time.sleep(0.3)
            try:
                minor_engine.main()
            except Exception as e:
                print(f"  [ERROR] Minor Engine failure: {e}")

        elif choice == '2':
            print("  Opening Major Scale Engine...")
            time.sleep(0.3)
            try:
                major_engine.main()
            except Exception as e:
                print(f"  [ERROR] Major Engine failure: {e}")

        elif choice == '3':
            print("  Opening VVC String Quartet Engine...")
            time.sleep(0.3)
            try:
                vvc_engine.main()
            except Exception as e:
                print(f"  [ERROR] VVC Engine failure: {e}")

        elif choice == '4':
            print("  CREATE 120-BAR EPIC ARRANGEMENT + CHOIR")
            _div()
            print("  Source should be a user-edited 4-bar MIDI with your instrument tracks/channels.")
            filepath = input("  Enter path to 4-bar MIDI file: ").strip().strip('"').strip("'")
            if not os.path.isfile(filepath):
                print(f"  [ERROR] File not found: {filepath}")
            else:
                try:
                    vvc_engine.generate_120bar_arrangement_from_midi(filepath, out_dir)
                except Exception as e:
                    print(f"  [ERROR] Arranger failed: {e}")

        elif choice == '5':
            print("  ANALYZE MIDI FILE & GENERATE STRING QUARTET OVERLAY")
            _div()
            filepath = input("  Enter path to MIDI file: ").strip().strip('"').strip("'")
            if not os.path.isfile(filepath):
                print(f"  [ERROR] File not found: {filepath}")
            else:
                try:
                    vvc_engine.generate_quartet_over_midi(filepath, out_dir)
                except Exception as e:
                    print(f"  [ERROR] Overlayer failed: {e}")

        elif choice == '6':
            try:
                vvc_engine.show_instrument_routing()
            except Exception as e:
                print(f"  [ERROR] Failed to display guide: {e}")
            input("  Press [Enter] to return to Main Menu...")

        elif choice == '7':
            print("  Opening Spanish Guitar Composer...")
            time.sleep(0.3)
            try:
                sg_engine.main(out_dir)
            except Exception as e:
                print(f"  [ERROR] Spanish Guitar Engine failure: {e}")

        elif choice == '8':
            print("  Opening Cinematic Trailer Composer...")
            time.sleep(0.3)
            try:
                cinematic_engine.main(out_dir)
            except Exception as e:
                print(f"  [ERROR] Cinematic Engine failure: {e}")

        else:
            print("  [!] Invalid choice. Enter 1-8, T, or 0.\n")

        _div()
        time.sleep(0.1)

if __name__ == '__main__':
    main()
