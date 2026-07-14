"""Four-bar Major Solo Performance, isolated from the minor solo engine."""

import importlib.util
import os
import random


def _load(name, filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load the proven performance rules into a private module namespace. Changing
# these globals cannot alter the separately loaded minor Solo Performance.
_core = _load("major_solo_private_core", "solo_performance_minor.py")
_major = _load("major_solo_harmony_source", "major-chord-generatory.py")

SCALE_NAME = "Natural Major"
MAJOR_CHORDS = {
    symbol: list(definition[0])
    for symbol, definition in _major.roman_numerals.items()
}
_core.MINOR_SCALES = {SCALE_NAME: list(_major.SCALE_IONIAN)}
_core.SCALE_CHORDS = {SCALE_NAME: MAJOR_CHORDS}


def _major_bars_data(progression, _scale_name):
    """Give the private violin engine the scale color assigned to each chord."""
    return [
        (MAJOR_CHORDS[symbol], list(_major.roman_numerals[symbol][1]))
        for symbol in progression
    ]


_core._solo_bars_data = _major_bars_data

ROOTS = dict(_core.ROOTS)
INSTRUMENTS = _core.INSTRUMENTS


def _entries(items):
    return [(label, SCALE_NAME, list(chords)) for label, chords in items]


MOOD_POOLS = {
    "Uplifting & Hopeful": _entries([
        ("Promise in Motion", ("I", "V", "vi", "IV")),
        ("Optimistic Leap", ("I", "IV", "vi", "V")),
        ("Openhearted Rise", ("I", "vi", "IV", "V")),
        ("Sunlit Cadence", ("I", "IV", "V", "I")),
        ("Gentle Ascent", ("I", "iii", "IV", "V")),
        ("Homeward Light", ("I", "V", "IV", "I")),
        ("Bright Morning", ("I", "V", "I", "IV")),
        ("Faithful Steps", ("I", "IV", "I", "V")),
        ("Hopeful Circle", ("I", "vi", "ii", "V")),
        ("New Horizon", ("IV", "I", "V", "vi")),
        ("Rising Again", ("vi", "IV", "I", "V")),
        ("Forward Together", ("I", "ii", "IV", "V")),
    ]),
    "Romantic & Heartfelt": _entries([
        ("Wistful Devotion", ("I", "iii", "vi", "IV")),
        ("Classic Romance", ("I", "vi", "ii", "V")),
        ("Endless Affection", ("I", "vi", "IV", "V")),
        ("Velvet Promise", ("Imaj7", "vi", "IVmaj7", "V")),
        ("Candlelit Cadence", ("Imaj7", "IVmaj7", "ii7", "V7")),
        ("Close to You", ("I", "IVmaj7", "iii", "vi")),
        ("Love Returns", ("vi", "IV", "I", "V")),
        ("Unspoken Words", ("I", "V", "vi", "iii")),
        ("Tender Vow", ("Imaj7", "iii", "IVmaj7", "V")),
        ("Heart at Dusk", ("I", "iii", "IV", "iv")),
        ("Always Near", ("I", "vi", "IVmaj7", "V")),
        ("Celestial Embrace", ("Imaj7", "IVmaj7", "Imaj7", "IVmaj7")),
    ]),
    "Tender Hope": _entries([
        ("Fragile Sunrise", ("Imaj7", "V", "vi", "IVmaj7")),
        ("Quiet Reassurance", ("I", "IVmaj7", "vi", "V")),
        ("Held by Grace", ("I", "iii", "IVmaj7", "I")),
        ("Patient Heart", ("I", "vi", "ii7", "V")),
        ("Small Mercies", ("I", "IV", "I", "V")),
        ("Ambient Horizon", ("Imaj7", "II", "IVmaj7", "I")),
        ("Soft Recovery", ("vi", "IVmaj7", "I", "V")),
        ("Safe Return", ("I", "V", "IVmaj7", "I")),
        ("Gentle Promise", ("Imaj7", "vi", "ii", "IV")),
        ("First Light", ("I", "ii", "vi", "IVmaj7")),
        ("Open Arms", ("IVmaj7", "I", "V", "vi")),
        ("Quiet Bloom", ("I", "IVmaj7", "ii7", "I")),
    ]),
    "Quiet Triumph": _entries([
        ("Steady Victory", ("I", "bVII", "IV", "I")),
        ("Ascent to Grace", ("I", "IV", "bVII", "I")),
        ("Lydian Rising", ("I", "II", "IV", "I")),
        ("Triumphant Call", ("I", "V", "IV", "I")),
        ("Earned Arrival", ("IV", "I", "V", "I")),
        ("Distant Summit", ("I", "bVI", "bVII", "I")),
        ("Inner Strength", ("I", "IV", "vi", "I")),
        ("Rise with Courage", ("vi", "IV", "I", "V")),
        ("Unbroken Hope", ("I", "V", "vi", "IV")),
        ("Royal Restraint", ("I", "bVII", "I", "IV")),
        ("Laurel at Dawn", ("IV", "V", "I", "Imaj7")),
        ("Brave Horizon", ("I", "II", "V", "I")),
    ]),
    "Tears of Joy": _entries([
        ("Tears of Joy", ("I", "IV", "iv", "I")),
        ("Bittersweet Epilogue", ("I", "V", "vi", "iv")),
        ("Joy through Tears", ("I", "vi", "IV", "iv")),
        ("Beautiful Goodbye", ("Imaj7", "IVmaj7", "iv", "I")),
        ("Love Remembers", ("I", "iii", "IV", "iv")),
        ("Solitary Path", ("I", "bVI", "IV", "I")),
        ("Warmest Memory", ("Imaj7", "IV", "iv", "I")),
        ("Coming Home", ("vi", "IV", "iv", "I")),
        ("One Last Look", ("I", "V", "iv", "I")),
        ("Tender Release", ("I", "IVmaj7", "iv", "Imaj7")),
        ("Grateful Heart", ("I", "vi", "iv", "I")),
        ("Light after Rain", ("I", "bVI", "iv", "I")),
    ]),
    "Pain / Heartbreak": _entries([
        ("The Love We Lost", ("I", "V", "vi", "iv")),
        ("Falling out of Forever", ("I", "iii", "vi", "iv")),
        ("Warmth Turning Cold", ("I", "vi", "IV", "iv")),
        ("A Promise Unkept", ("I", "iii", "IV", "iv")),
        ("Beautiful Absence", ("Imaj7", "IVmaj7", "iv", "I")),
        ("Your Empty Chair", ("Imaj7", "iii", "iv", "I")),
        ("The Final Goodbye", ("I", "V", "iv", "I")),
        ("Still Coming Home", ("vi", "IV", "iv", "I")),
        ("Weight of Memory", ("I", "bVI", "IV", "iv")),
        ("No Road Back", ("I", "bVI", "bIII", "bVII")),
        ("Sorrow in Daylight", ("I", "iv", "I", "iv")),
        ("Photograph of You", ("Imaj7", "IVmaj7", "iv", "Imaj7")),
        ("After You Left", ("I", "vi", "iv", "I")),
        ("Everything We Were", ("I", "iii", "vi", "bVI")),
        ("Last Tenderness", ("Imaj7", "vi", "IV", "iv")),
        ("Breaking Quietly", ("vi", "iii", "IV", "iv")),
        ("Ache beneath the Light", ("I", "bVI", "iv", "I")),
        ("Love without Resolution", ("IVmaj7", "iv", "I", "vi")),
    ]),
}

ALL_PROGRESSIONS = [entry for pool in MOOD_POOLS.values() for entry in pool]


def _validate_library():
    for mood, pool in MOOD_POOLS.items():
        if len(pool) < 8:
            raise ValueError(f"Major Solo mood needs a wide progression pool: {mood}")
        for label, scale_name, chords in pool:
            if scale_name != SCALE_NAME or len(chords) != 4:
                raise ValueError(f"Major Solo progression must be four bars: {label}")
            unknown = [symbol for symbol in chords if symbol not in MAJOR_CHORDS]
            if unknown:
                raise ValueError(f"Unsupported chord(s) in {label}: {unknown}")


_validate_library()


def compose_major_solo_performance(out_dir, key_name, root_val, bpm,
                                   instrument_key="1", progression_pool=None,
                                   mood_name="Surprise Me"):
    tpb = 480
    label, scale_name, progression = random.choice(progression_pool or ALL_PROGRESSIONS)
    instrument = INSTRUMENTS.get(instrument_key, random.choice(list(INSTRUMENTS.values())))
    plan = _core._build_harmonic_plan(root_val, progression, scale_name)
    violin_lead, violin_counter, _lead_data, _counter_data = \
        _core._generate_crying_violin_parts(root_val, progression, scale_name, tpb)

    tracks = [
        _core._generate_main_hook_lead(root_val, plan, scale_name, tpb),
        _core._generate_pad(plan, tpb),
        _core._generate_rhythmic_layer(plan, tpb, bpm),
        _core._generate_staccato(root_val, progression, scale_name, tpb, bpm, instrument),
        _core._generate_sub_bass(root_val, progression, scale_name, tpb, bpm),
        violin_lead,
        violin_counter,
    ]
    names = [
        "Main Hook Lead - Major Opening Theme",
        "Chord Pad - Four Bar Major String Bed",
        "Rhythmic Layer - Continuous Major Chord Pulse",
        f"{instrument['name']} Staccato Phrases - Major Solo Performance",
        "Sub-Bass - Major Progression Root Support",
        "Crying Violin Lead Melody - Major",
        "Crying Violin Counter - Major",
    ]
    loop_end = 16 * tpb
    mid = _core._events_to_mid(tracks, names, bpm, tpb, loop_end)
    fname = (
        f"{_core._title()}__Major_Solo_Performance__{_core._slug(mood_name)}__"
        f"{instrument['name']}__{_core._slug(label)}__{key_name}_Major__"
        f"{bpm}BPM__{'-'.join(progression)}"
    )
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, fname + ".mid")
    version = 1
    while os.path.exists(path):
        path = os.path.join(out_dir, f"{fname}_v{version}.mid")
        version += 1
    mid.save(path)
    print(f"\n  [SAVED]  {os.path.basename(path)}")
    print(f"  [PATH ]  {path}")
    print(f"  [STYLE]  Major Solo Performance - {instrument['name']}")
    print(f"  [MOOD ]  {mood_name}")
    print(f"  [PROG ]  {'-'.join(progression)}\n")
    return path, progression


def _select_mood_pool():
    names = list(MOOD_POOLS)
    print("\n  Select Major Solo Performance Mood:")
    print(f"    S -> Surprise Me ({len(ALL_PROGRESSIONS)} progressions)")
    for index, name in enumerate(names, 1):
        print(f"    {index} -> {name} ({len(MOOD_POOLS[name])} progressions)")
    print("    B -> Back")
    choice = input("  --> ").strip().lower()
    if choice == "b":
        return None, None
    if choice in ("", "s"):
        return "Surprise Me", ALL_PROGRESSIONS
    if choice.isdigit() and 1 <= int(choice) <= len(names):
        name = names[int(choice) - 1]
        return name, MOOD_POOLS[name]
    print("  [RANDOM MOOD] Surprise Me")
    return "Surprise Me", ALL_PROGRESSIONS


def _select_key():
    keys = sorted(ROOTS)
    print(f"\n  Select Major Root Key (Available: {', '.join(keys)})")
    key = input("  --> ").strip()
    if key:
        key = key[0].upper() + key[1:]
    if key not in ROOTS:
        key = random.choice(keys)
        print(f"  [RANDOM KEY] {key}")
    return key, ROOTS[key]


def main(out_dir="midi_files"):
    os.makedirs(out_dir, exist_ok=True)
    print("""
MAJOR SOLO PERFORMANCE

  Strict four-bar, heart-touching major performance.
  Tracks: main hook lead, chord pad, rhythmic layer, staccato phrases, sub-bass,
          crying violin lead, crying violin counter.
""")
    while True:
        _core._div()
        mood_name, pool = _select_mood_pool()
        if pool is None:
            return
        key_name, root_val = _select_key()
        bpm = _core._select_bpm()
        instrument_key = _core._select_instrument()
        print("\n  [GENERATING] Writing Major Solo Performance MIDI...")
        compose_major_solo_performance(
            out_dir, key_name, root_val, bpm, instrument_key, pool, mood_name
        )
        print("  [G] Generate again  [B] Back  [Q] Quit")
        if input("  --> ").strip().lower() in ("b", "q"):
            return


if __name__ == "__main__":
    main()
