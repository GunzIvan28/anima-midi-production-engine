"""
ANIMA Solo Performance
Four-bar minor string performance composer:
main hook lead, chord pad, subdivided rhythmic layer, solo staccato phrases,
sub-bass, crying violin lead, and crying violin counter.
"""

import os
import random
import importlib.util

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack


GENERATION_MODE = "simple"

ROOTS = {
    "C": 60, "C#": 61, "Db": 61, "D": 62, "D#": 63, "Eb": 63,
    "E": 64, "F": 65, "F#": 66, "Gb": 66, "G": 67, "G#": 68,
    "Ab": 68, "A": 69, "Bb": 70, "B": 71,
}

MINOR_SCALES = {
    "natural_minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "dorian_minor": [0, 2, 3, 5, 7, 9, 10],
    "phrygian_minor": [0, 1, 3, 5, 7, 8, 10],
    "minor_engine_mixed": [0, 1, 2, 3, 5, 7, 8, 9, 10, 11],
}

SCALE_CHORDS = {
    "natural_minor": {
        "i": [0, 3, 7], "iv": [5, 8, 0], "v": [7, 10, 2],
        "bVI": [8, 0, 3], "bVII": [10, 2, 5], "bIII": [3, 7, 10],
        "ii°": [2, 5, 8],
        "i7": [0, 3, 7, 10], "iv7": [5, 8, 0, 3],
    },
    "harmonic_minor": {
        "i": [0, 3, 7], "iv": [5, 8, 0], "V": [7, 11, 2],
        "VI": [8, 0, 3], "VII": [11, 2, 5], "III": [3, 7, 11],
        "viio": [11, 2, 5], "V7": [7, 11, 2, 5],
        "i7": [0, 3, 7, 11], "iv7": [5, 8, 0, 3],
    },
    "dorian_minor": {
        "i": [0, 3, 7], "IV": [5, 9, 0], "v": [7, 10, 2],
        "bVII": [10, 2, 5], "bIII": [3, 7, 10], "ii": [2, 5, 9],
    },
    "phrygian_minor": {
        "i": [0, 3, 7], "bII": [1, 5, 8], "iv": [5, 8, 0],
        "bVI": [8, 0, 3], "bVII": [10, 1, 5], "bIII": [3, 7, 10],
        "v": [7, 10, 1],
    },
    "minor_engine_mixed": {
        "i": [0, 3, 7], "i7": [0, 3, 7, 10],
        "iio": [2, 5, 8], "ii°": [2, 5, 8],
        "bII": [1, 5, 8],
        "III": [3, 7, 10], "bIII": [3, 7, 10],
        "iv": [5, 8, 0], "IV": [5, 9, 0], "iv7": [5, 8, 0, 3],
        "v": [7, 10, 2], "V": [7, 11, 2], "V7": [7, 11, 2, 5],
        "VI": [8, 0, 3], "bVI": [8, 0, 3], "VI7": [8, 0, 3, 10],
        "VII": [10, 2, 5], "bVII": [10, 2, 5],
        "viio": [11, 2, 5],
    },
}

PROGRESSIONS = [
    ("Bounty Root Spell", "natural_minor", ["i", "i", "v", "i"]),
    ("Dynasty Descent", "natural_minor", ["bIII", "v", "i", "i"]),
    ("Samurai Return", "natural_minor", ["i", "v", "i", "iv"]),
    ("Shanghai Lantern", "natural_minor", ["i", "i", "iv", "v"]),
    ("Soprano Cry", "natural_minor", ["v", "i", "bIII", "v"]),
    ("Sweet Low Memory", "natural_minor", ["bVI", "iv", "bVI", "iv"]),
    ("Taipei Night Loop", "natural_minor", ["v", "bIII", "i", "i"]),
    ("Yakuza Minor Walk", "natural_minor", ["bIII", "i", "v", "i"]),
    ("Familia Longing", "natural_minor", ["i", "bIII", "bVII", "bIII"]),
    ("Rojo Suspense", "natural_minor", ["bIII", "ii°", "v", "v"]),
    ("Mercado Shadows", "natural_minor", ["bVII", "bVII", "bVI", "iv"]),
    ("Venezuela Pulse", "natural_minor", ["i", "v", "i", "v"]),
    ("Andalusian Lament", "harmonic_minor", ["i", "VII", "VI", "V"]),
    ("Granada Shadow", "harmonic_minor", ["i", "iv", "V", "i"]),
    ("Night Descent", "harmonic_minor", ["i", "VI", "III", "V"]),
    ("Saeta Resolve", "harmonic_minor", ["i", "VI", "iv", "V"]),
    ("Dorian Road", "dorian_minor", ["i", "bVII", "IV", "i"]),
    ("Old Photograph", "dorian_minor", ["i", "bIII", "bVII", "i"]),
    ("Phrygian Cry", "phrygian_minor", ["i", "bII", "bVII", "i"]),
    ("Shadow Road", "phrygian_minor", ["i", "bVI", "bIII", "bVII"]),
    ("Hopeful Grief", "natural_minor", ["i", "bVI", "bIII", "bVII"]),
    ("Austere Church", "natural_minor", ["i", "iv", "v", "i"]),
    ("Circular Grief", "natural_minor", ["i", "bVI", "bVII", "i"]),
    ("Fado", "natural_minor", ["i", "iv", "bVII", "bIII"]),
    ("Deceptive Resolution", "natural_minor", ["bVI", "bVII", "i", "i"]),
    ("Triumphant Minor", "natural_minor", ["i", "v", "bVI", "bVII"]),
    ("Descending Heroic", "natural_minor", ["i", "bVII", "bVI", "v"]),
    ("Battle March", "natural_minor", ["i", "iv", "bVI", "bVII"]),
    ("Inception Style", "natural_minor", ["i", "bIII", "bVII", "bVI"]),
    ("Hero Journey", "natural_minor", ["i", "bVI", "bVII", "bIII"]),
    ("Fate And Struggle", "natural_minor", ["i", "v", "bVII", "iv"]),
    ("Dark Triumph", "natural_minor", ["i", "bVII", "bIII", "bVI"]),
    ("Warrior Ballad", "natural_minor", ["i", "bVI", "v", "bVII"]),
    ("Cavalry Charge", "natural_minor", ["i", "iv", "bVII", "bVI"]),
    ("Gladiator Ostinato", "natural_minor", ["i", "v", "i", "bVII"]),
    ("Rising From Ashes", "natural_minor", ["bVI", "bIII", "bVII", "i"]),
    ("Hopeful Minor", "natural_minor", ["i", "bIII", "bVI", "bVII"]),
    ("Wistful", "natural_minor", ["i", "bVII", "bIII", "bVI"]),
    ("Reflective", "natural_minor", ["bVI", "bVII", "i", "v"]),
    ("Memory Lane", "natural_minor", ["i", "bVI", "bIII", "iv"]),
    ("Tender Regret", "natural_minor", ["i", "bIII", "iv", "bVI"]),
    ("Faded Summer", "natural_minor", ["bIII", "bVII", "i", "bVI"]),
    ("Childhood Echo", "natural_minor", ["i", "iv", "bIII", "bVII"]),
    ("Film Nostalgia", "natural_minor", ["bVI", "bIII", "i", "bVII"]),
    ("Soft Longing", "natural_minor", ["i", "bVI", "bVII", "bIII"]),
    ("Classical Sorrow", "harmonic_minor", ["i", "VI", "iv", "V"]),
    ("Neapolitan Grief", "phrygian_minor", ["i", "bVI", "bII", "v"]),
    ("Baroque Descent", "harmonic_minor", ["i", "viio", "V", "i"]),
    ("Gothic Thriller", "phrygian_minor", ["i", "iv", "bII", "v"]),
    ("Ominous Buildup", "harmonic_minor", ["i", "iv", "V", "i"]),
    ("Horror Cadence", "harmonic_minor", ["i", "viio", "i", "V7"]),
    ("Sacrifice Theme", "harmonic_minor", ["i", "VII", "iv", "V"]),
    ("Tragic Climax", "harmonic_minor", ["i", "V", "iv", "V"]),
    ("Jazz Noir", "harmonic_minor", ["i7", "iv7", "V7", "i"]),
    ("Spanish Flamenco", "phrygian_minor", ["i", "bII", "bVII", "i"]),
    ("Templar Phrygian", "phrygian_minor", ["i", "bII", "i", "bVII"]),
    ("Dark Descent", "phrygian_minor", ["i", "bVI", "bII", "i"]),
    ("Assassin Theme", "phrygian_minor", ["i", "bII", "bVII", "i"]),
    ("Black Mass", "phrygian_minor", ["i", "iv", "v", "bII"]),
    ("Gregorian Doom", "phrygian_minor", ["bII", "i", "bII", "bVII"]),
    ("Venetian Darkness", "phrygian_minor", ["i", "bVII", "bII", "i"]),
    ("Inquisition", "phrygian_minor", ["i", "v", "bII", "bVII"]),
    ("Lovecraftian Dread", "phrygian_minor", ["i", "bVI", "v", "bII"]),
    ("Nostalgic Lift", "dorian_minor", ["i", "bVII", "bIII", "IV"]),
    ("Dorian Yearning", "dorian_minor", ["i", "IV", "v", "i"]),
    ("Moonlit Dorian", "dorian_minor", ["i", "bIII", "IV", "bVII"]),
    ("River Resolve", "dorian_minor", ["i", "ii", "bVII", "i"]),
    ("Bittersweet Optimism", "natural_minor", ["i", "bIII", "bVI", "iv"]),
    ("Tender Hope", "natural_minor", ["i", "bIII", "iv", "bVII"]),
    ("Morning Light", "natural_minor", ["bIII", "i", "bVI", "bVII"]),
    ("Renewal", "natural_minor", ["bVI", "bIII", "i", "bVII"]),
    ("Anthem Hope", "natural_minor", ["bIII", "bVII", "bVI", "i"]),
    ("Determined Spirit", "natural_minor", ["i", "v", "bIII", "bVII"]),
    ("Victorious Resolve", "natural_minor", ["bVI", "bIII", "bVII", "i"]),
    ("Doomed Hero", "phrygian_minor", ["i", "bII", "v", "i"]),
    ("Last Stand", "natural_minor", ["bVI", "i", "v", "bVII"]),
    ("Unresolved Anguish", "natural_minor", ["i", "iv", "v", "bVI"]),
    ("Warm Resolution", "natural_minor", ["bVI", "bIII", "iv", "i"]),
    ("Heart Swell", "natural_minor", ["i", "bIII", "iv", "bVII"]),
    ("Quiet Devotion", "natural_minor", ["i", "iv", "bIII", "v"]),
    ("Twilight Echo", "natural_minor", ["bVI", "i", "v", "bVII"]),
    ("Lost Paradise", "natural_minor", ["i", "bIII", "bVII", "iv"]),
    ("Soft Reverie", "natural_minor", ["i", "bVII", "iv", "bVI"]),
]

PAIN_HEARTBREAK_PROGRESSIONS = [
    ("Heartbreak - Unanswered Goodbye", "natural_minor", ["i", "iv", "v", "bVI"]),
    ("Heartbreak - Memory of Us", "natural_minor", ["i", "bVI", "bIII", "iv"]),
    ("Heartbreak - Tender Regret", "natural_minor", ["i", "bIII", "iv", "bVI"]),
    ("Heartbreak - Lost Paradise", "natural_minor", ["i", "bIII", "bVII", "iv"]),
    ("Heartbreak - Cannot Stay", "natural_minor", ["bVI", "bVII", "i", "v"]),
    ("Heartbreak - Fado Letter", "natural_minor", ["i", "iv", "bVII", "bIII"]),
    ("Heartbreak - Quiet Devotion", "natural_minor", ["i", "iv", "bIII", "v"]),
    ("Heartbreak - Twilight Separation", "natural_minor", ["bVI", "i", "v", "bVII"]),
    ("Heartbreak - Soft Collapse", "natural_minor", ["i", "bVII", "iv", "bVI"]),
    ("Heartbreak - Empty Room", "natural_minor", ["i", "bVI", "iv", "v"]),
    ("Heartbreak - Words Unsaid", "natural_minor", ["i", "iv", "bVI", "v"]),
    ("Heartbreak - Love in Reverse", "natural_minor", ["bVI", "iv", "i", "v"]),
    ("Heartbreak - Last Embrace", "natural_minor", ["i", "bIII", "v", "iv"]),
    ("Heartbreak - Wound Reopens", "natural_minor", ["i", "v", "bVI", "iv"]),
    ("Heartbreak - Classical Farewell", "harmonic_minor", ["i", "VI", "iv", "V"]),
    ("Heartbreak - Unresolved Cry", "harmonic_minor", ["i", "V", "iv", "V"]),
    ("Heartbreak - Neapolitan Grief", "phrygian_minor", ["i", "bVI", "bII", "v"]),
    ("Heartbreak - Phrygian Goodbye", "phrygian_minor", ["i", "bII", "bVII", "i"]),
]

PROGRESSIONS.extend(PAIN_HEARTBREAK_PROGRESSIONS)


def _adopt_minor_engine_progressions():
    import sys as _sys
    minor_path = os.path.join(os.path.dirname(__file__), "chord_generatory_minor.py")
    if not os.path.exists(minor_path):
        return
    # Pre-register before exec to block any re-entrant call during the load itself.
    # We do NOT check for "minor_chord_generatory" here — that would incorrectly
    # block callers like cinematic.py who load us independently.
    if "solo_minor_engine_reference" in _sys.modules:
        return
    try:
        spec = importlib.util.spec_from_file_location("solo_minor_engine_reference", minor_path)
        minor_engine = importlib.util.module_from_spec(spec)
        _sys.modules["solo_minor_engine_reference"] = minor_engine
        spec.loader.exec_module(minor_engine)
    except Exception:
        _sys.modules.pop("solo_minor_engine_reference", None)
        return

    seen = {label for label, _scale, _prog in PROGRESSIONS}
    for cluster in getattr(minor_engine, "STYLE_CLUSTERS", {}).values():
        mood = " / ".join(name.title() for name in cluster.get("names", []))
        for entry in cluster.get("progressions", []):
            label = f"Minor Engine {mood} - {entry['label']}"
            if label in seen:
                continue
            progression = list(entry["chords"])
            if all(symbol in SCALE_CHORDS["minor_engine_mixed"] for symbol in progression):
                PROGRESSIONS.append((label, "minor_engine_mixed", progression))
                seen.add(label)


_adopt_minor_engine_progressions()


def _solo_native_mood(label, scale_name):
    text = label.lower()
    if "heartbreak" in text or any(word in text for word in ("goodbye", "separation", "farewell")):
        return "Pain / Heartbreak"
    if scale_name in ("phrygian_minor", "harmonic_minor") or any(word in text for word in ("gothic", "horror", "dark", "shadow", "assassin", "inquisition", "doom")):
        return "Dark / Phrygian / Gothic"
    if any(word in text for word in ("hope", "hero", "triumph", "victorious", "renewal", "rising", "morning", "spirit", "stand")):
        return "Hopeful / Heroic"
    if any(word in text for word in ("romance", "heart", "tender", "warm", "devotion", "love")):
        return "Romantic / Emotional"
    if any(word in text for word in ("nostalg", "memory", "wistful", "reflect", "faded", "childhood", "twilight", "lost", "reverie")):
        return "Yearning / Nostalgic"
    return "Sorrowful / Sad"


def _progression_mood_groups():
    groups = {}
    for item in PROGRESSIONS:
        label, scale_name, _prog = item
        if label.startswith("Minor Engine "):
            rest = label[len("Minor Engine "):]
            mood = rest.split(" - ", 1)[0]
            group_name = f"Minor Engine - {mood}"
        else:
            group_name = f"Solo Native - {_solo_native_mood(label, scale_name)}"
        groups.setdefault(group_name, []).append(item)
    return dict(sorted(groups.items(), key=lambda pair: pair[0]))


INSTRUMENTS = {
    "1": {"name": "Violin", "program": 40, "range": (55, 88), "prefer": 74},
    "2": {"name": "Viola", "program": 41, "range": (48, 79), "prefer": 67},
    "3": {"name": "Cello", "program": 42, "range": (36, 72), "prefer": 55},
}

NAME_WORDS = (
    [
        "Lonely", "Velvet", "Midnight", "Faded", "Silver", "Wounded",
        "Autumn", "Glass", "Hidden", "Distant", "Burning", "Hollow",
        "Ashen", "Moonlit", "Trembling", "Buried", "Frozen", "Restless",
        "Crimson", "Pale", "Withered", "Sacred", "Mourning", "Stormlit",
        "Shattered", "Golden", "Nocturnal", "Bruised", "Ancient", "Weeping",
        "Desolate", "Tender", "Haunted", "Dusky", "Fevered", "Quiet",
        "Forgotten", "Cathedral", "Soft", "Broken", "Radiant", "Drifting",
    ],
    [
        "Soliloquy", "Lament", "Pulse", "Elegy", "Memory", "Ostinato",
        "Letter", "Prayer", "Echo", "Fugitive", "Romance", "Nocturne",
        "Requiem", "Confession", "Whisper", "Sorrow", "Waltz", "Dirge",
        "Vigil", "Adagio", "Farewell", "Shadow", "Tear", "Hymn",
        "Serenade", "Ashes", "Cathedral", "Mirage", "Remembrance", "Oath",
        "Prelude", "Afterglow", "Grief", "Candle", "Rain", "Dawn",
        "Crescendo", "Undertow", "Devotion", "Fable", "Threnody", "Dream",
    ],
)


def _div(c="-", w=62):
    print(c * w)


def _slug(value):
    keep = []
    for ch in str(value):
        if ch.isalnum() or ch in ("#", "b"):
            keep.append(ch)
        elif ch in (" ", "-", "_", "/", "°"):
            keep.append("_")
    text = "".join(keep).strip("_")
    while "__" in text:
        text = text.replace("__", "_")
    return text or "Solo"


def _scale_pitches(root_val, scale, lo, hi):
    pcs = {(root_val + interval) % 12 for interval in scale}
    return [pitch for pitch in range(lo, hi + 1) if pitch % 12 in pcs]


def _chord_pitches(root_val, chord, lo, hi):
    pcs = {(root_val + interval) % 12 for interval in chord}
    return [pitch for pitch in range(lo, hi + 1) if pitch % 12 in pcs]


def _nearest(candidates, target):
    if not candidates:
        return target
    return min(candidates, key=lambda pitch: (abs(pitch - target), pitch))


def _emit(events, tick, kind, val1, val2, channel):
    events.append((max(0, int(tick)), kind, int(val1), int(val2), channel))


def _add_note(events, tick, pitch, dur_ticks, velocity, channel, humanize=True):
    start = int(tick)
    end = int(tick + dur_ticks)
    if humanize:
        start += random.randint(-5, 5)
        end += random.randint(-3, 3)
    start = max(0, start)
    end = max(start + 16, end)
    _emit(events, start, "on", pitch, max(1, min(127, velocity)), channel)
    _emit(events, end, "off", pitch, 0, channel)


def _cc_curve(events, channel, control, start_tick, duration, start_val, end_val, steps=8):
    for step in range(steps + 1):
        pct = step / float(max(1, steps))
        tick = start_tick + int(duration * pct)
        val = int(start_val + (end_val - start_val) * pct)
        _emit(events, tick, "cc", control, max(0, min(127, val)), channel)


def _voicing(root_val, chord, scale, previous=None):
    scale_pcs = {(root_val + interval) % 12 for interval in scale}
    pcs = [(root_val + interval) % 12 for interval in chord]
    pcs = [pc for pc in pcs if pc in scale_pcs] or pcs
    notes = []
    targets = [48, 55, 60, 67, 72]
    for idx, pc in enumerate((pcs + pcs[:2])[:5]):
        candidates = [p for p in range(43, 77) if p % 12 == pc]
        notes.append(_nearest(candidates, targets[idx]))
    notes = sorted(set(notes))
    if previous:
        notes = sorted(notes, key=lambda n: min(abs(n - p) for p in previous))[:4]
        return sorted(notes)
    return notes[:4]


def _compact_chord(root_val, chord, scale, lo, hi, center):
    chord_notes = _chord_pitches(root_val, chord, lo, hi)
    if not chord_notes:
        chord_notes = _scale_pitches(root_val, scale, lo, hi)
    near = [p for p in chord_notes if abs(p - center) <= 9]
    pool = near or chord_notes
    return sorted(pool, key=lambda pitch: (abs(pitch - center), pitch))[:4]


def _tempo_settings(bpm):
    if bpm < 95:
        return {
            "density": (2, 3),
            "grid": [0.0, 0.75, 1.0, 1.5, 2.0, 2.5, 2.75, 3.25],
            "dur": (0.34, 0.72),
            "pickup_chance": 0.28,
            "rest_chance": 0.22,
        }
    if bpm < 125:
        return {
            "density": (3, 5),
            "grid": [0.0, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 2.75, 3.0, 3.5],
            "dur": (0.22, 0.48),
            "pickup_chance": 0.42,
            "rest_chance": 0.14,
        }
    return {
        "density": (4, 7),
        "grid": [0.0, 0.33, 0.5, 0.67, 0.75, 1.0, 1.5, 2.0, 2.33, 2.5, 2.67, 3.0, 3.25, 3.5, 3.67],
        "dur": (0.12, 0.32),
        "pickup_chance": 0.58,
        "rest_chance": 0.08,
    }


def _chord_role(symbol):
    if symbol in ("i", "I"):
        return "home"
    if symbol in ("V", "V7", "v", "VII", "bVII", "viio"):
        return "tension"
    if symbol in ("iv", "IV", "ii", "ii°", "iio", "bII"):
        return "motion"
    return "color"


def _pick_bar_beats(settings, role, bar_index):
    min_notes, max_notes = settings["density"]
    density = random.randint(min_notes, max_notes)
    if role == "home":
        density = max(min_notes, density - random.choice([0, 1]))
    elif role == "tension":
        density = min(max_notes, density + random.choice([0, 1]))
    if bar_index == 3 and random.random() < 0.55:
        density = max(min_notes, density - 1)

    beats = []
    anchors = {
        "home": [0.0, 2.0],
        "tension": [0.0, 1.5, 3.0],
        "motion": [0.75, 2.0],
        "color": [0.0, 2.5],
    }[role]
    for beat in anchors:
        if beat in settings["grid"] and random.random() > settings["rest_chance"]:
            beats.append(beat)

    pool = [beat for beat in settings["grid"] if beat not in beats]
    random.shuffle(pool)
    for beat in pool:
        if len(beats) >= density:
            break
        if beat >= 3.25 and random.random() > settings["pickup_chance"]:
            continue
        if beats and min(abs(beat - old) for old in beats) < 0.24:
            continue
        beats.append(beat)
    return sorted(beats)


def _choose_phrase_pitch(root_val, chord, scale, lo, hi, current, role, note_index, direction):
    chord_notes = _chord_pitches(root_val, chord, lo, hi)
    scale_notes = _scale_pitches(root_val, scale, lo, hi)
    if not chord_notes:
        chord_notes = scale_notes

    if note_index == 0 or role in ("home", "tension"):
        pool = chord_notes
    elif random.random() < 0.72:
        pool = chord_notes
    else:
        pool = scale_notes

    if current is not None:
        leap = 7 if role != "tension" else 9
        directional = [p for p in pool if abs(p - current) <= leap and (p - current) * direction >= 0]
        near = [p for p in pool if abs(p - current) <= leap]
        pool = directional or near or pool
        target = current + direction * random.choice([2, 3, 5, 7])
    else:
        target = (lo + hi) // 2
    pitch = _nearest(pool, target)
    if current is not None and abs(pitch - current) == 1:
        alternatives = [p for p in pool if abs(p - current) not in (0, 1)]
        pitch = _nearest(alternatives or pool, target)
    return pitch


def _phrase_duration(settings, beat, next_beat, role):
    low, high = settings["dur"]
    gap = max(0.12, next_beat - beat - 0.06)
    dur = random.uniform(low, high)
    if role == "home" and random.random() < 0.35:
        dur *= 1.35
    if beat >= 3.25:
        dur *= 0.72
    return max(0.08, min(gap, dur))


TEST_MIDI_STACCATO_CELLS = [
    # Kit2 strings: alternating long-short staccato drive across the bar.
    [(0.0, 0.67), (0.67, 0.33), (1.0, 0.33), (1.33, 0.67), (2.0, 0.67), (2.67, 0.33), (3.0, 0.33), (3.33, 0.67)],
    # Kit1 strings: fast opening six-note burst.
    [(0.0, 0.33), (0.33, 0.33), (0.67, 0.33), (1.0, 0.33), (1.33, 0.33), (1.67, 0.33)],
    # Kit2 harp/sustain-derived late answer.
    [(2.0, 0.67), (2.67, 0.67), (3.33, 0.67)],
    # Kit2 early answering cell.
    [(0.0, 0.67), (0.67, 0.67), (1.33, 0.67)],
    # Reduced cells shaped from the common bar anchors in the reference pack.
    [(0.0, 0.5), (1.5, 0.34), (2.0, 0.5), (3.5, 0.22)],
    [(0.75, 0.42), (1.5, 0.34), (2.5, 0.42), (3.25, 0.22)],
]


def _reference_staccato_cell(settings, bpm, role, bar_index, instrument):
    if bpm < 95:
        candidates = [TEST_MIDI_STACCATO_CELLS[i] for i in (2, 3, 4, 5)]
    elif bpm < 125:
        candidates = [TEST_MIDI_STACCATO_CELLS[i] for i in (0, 2, 3, 4, 5)]
    else:
        candidates = [TEST_MIDI_STACCATO_CELLS[i] for i in (0, 1, 4, 5)]

    if role == "home" and random.random() < 0.65:
        candidates = [TEST_MIDI_STACCATO_CELLS[i] for i in (2, 3, 4)]
    elif role == "tension" and random.random() < 0.72:
        candidates = [TEST_MIDI_STACCATO_CELLS[i] for i in (0, 1, 5)]

    cell = [tuple(item) for item in random.choice(candidates)]
    if bar_index in (1, 3) and random.random() < 0.45:
        shift = random.choice([0.5, 0.75, 1.0])
        cell = [((beat + shift) % 4.0, dur) for beat, dur in cell]

    min_notes, max_notes = settings["density"]
    if instrument["name"] == "Cello":
        max_notes = max(min_notes, max_notes - 1)
    elif instrument["name"] == "Violin" and bpm >= 125:
        max_notes += 1

    if len(cell) > max_notes:
        keep = set(random.sample(range(len(cell)), max_notes))
        keep.add(0)
        if role == "tension":
            keep.add(len(cell) - 1)
        cell = [item for idx, item in enumerate(cell) if idx in keep]
    while len(cell) < min_notes and random.random() < 0.75:
        extra = random.choice(settings["grid"])
        if all(abs(extra - beat) >= 0.24 for beat, _dur in cell):
            cell.append((extra, random.uniform(*settings["dur"])))

    if role == "home" and bar_index == 3 and random.random() < 0.55:
        cell = [item for item in cell if item[0] <= 2.75] or cell[:1]
    if role in ("motion", "tension") and random.random() < settings["pickup_chance"]:
        pickup = random.choice([3.0, 3.25, 3.33, 3.5])
        if all(abs(pickup - beat) >= 0.18 for beat, _dur in cell):
            cell.append((pickup, random.choice([0.16, 0.2, 0.24])))

    return sorted((round(beat, 2), max(0.08, min(0.72, dur))) for beat, dur in cell if 0 <= beat < 4.0)


def _solo_string_cell_pool(bpm, role):
    if bpm < 95:
        cells = [
            [(0.0, 0.75, "root", "marcato"), (0.75, 0.25, "third", "spiccato")],
            [(0.0, 0.50, "root", "staccato"), (0.5, 0.50, "fifth", "staccato")],
            [(0.0, 0.50, "root", "staccato"), (0.5, 0.25, "third", "spiccato"), (0.75, 0.25, "fifth", "spiccato")],
        ]
    elif bpm < 125:
        cells = [
            [(0.0, 0.50, "root", "staccato"), (0.5, 0.25, "fifth", "spiccato"), (0.75, 0.25, "third", "spiccato")],
            [(0.0, 0.25, "root", "spiccato"), (0.25, 0.25, "third", "spiccato"), (0.5, 0.50, "fifth", "staccato")],
            [(0.0, 0.50, "root", "staccato"), (0.5, 0.50, "root", "staccato")],
            [(0.0, 0.50, "third", "staccato"), (0.5, 0.25, "fifth", "spiccato"), (0.75, 0.25, "root", "spiccato")],
        ]
    else:
        cells = [
            [(0.0, 0.50, "root", "staccato"), (0.5, 0.50, "fifth", "staccato")],
            [(0.0, 0.25, "root", "spiccato"), (0.25, 0.25, "fifth", "spiccato"), (0.5, 0.50, "root", "staccato")],
            [(0.0, 0.25, "root", "spiccato"), (0.25, 0.25, "third", "spiccato"), (0.5, 0.25, "fifth", "spiccato"), (0.75, 0.25, "root", "spiccato")],
        ]

    if role == "tension":
        cells.append([(0.0, 0.25, "root", "spiccato"), (0.25, 0.25, "fifth", "spiccato"), (0.5, 0.25, "octave", "spiccato"), (0.75, 0.25, "fifth", "spiccato")])
    elif role == "home":
        cells.append([(0.0, 0.50, "root", "staccato")])
    return cells


def _role_pitch(root_val, chord, scale, lo, hi, role, previous, center):
    index = {
        "root": 0,
        "third": 1,
        "fifth": 2,
        "color": -1,
        "octave": 0,
    }.get(role, 0)
    interval = chord[index % len(chord)]
    pc = (root_val + interval) % 12
    candidates = [pitch for pitch in range(lo, hi + 1) if pitch % 12 == pc]
    if not candidates:
        candidates = _scale_pitches(root_val, scale, lo, hi)
    target = previous if previous is not None else center
    pitch = _nearest(candidates, target)
    if previous is not None and abs(pitch - previous) > 7:
        close = [p for p in candidates if abs(p - previous) <= 7]
        pitch = _nearest(close or candidates, previous)
    if role == "octave" and previous is not None:
        higher = [p for p in candidates if p >= previous]
        pitch = _nearest(higher or candidates, previous + 7)
    return pitch


def _contour_chord_pitch(chord_pool, current, center, shift):
    if not chord_pool:
        return current
    target = center if current is None else current + shift
    if current is None or shift == 0:
        return _nearest(chord_pool, target)

    direction = 1 if shift > 0 else -1
    directional = [
        pitch for pitch in chord_pool
        if (pitch - current) * direction > 0 and abs(pitch - current) <= 10
    ]
    near = [pitch for pitch in chord_pool if abs(pitch - current) <= 10]
    return _nearest(directional or near or chord_pool, target)


CRY_VIOLIN_RANGE = (58, 76)
CRY_VIOLIN_CENTER = 67
CRY_RHYTHM_LYRICAL = [0.5, 1.0, 1.0, 1.5, 2.0, 2.0, 3.0, 4.0]
CRY_RHYTHM_SUSTAIN = [1.0, 2.0, 2.0, 3.0, 4.0]


def _weighted_rhythm(pool, beats_left, tension):
    choices = [dur for dur in pool if dur <= beats_left + 1e-6]
    if not choices:
        return beats_left
    if tension > 0.65:
        weights = [1.0 / dur for dur in choices]
    else:
        weights = [dur for dur in choices]
    return random.choices(choices, weights=weights, k=1)[0]


def _cry_violin_pitch(root_val, offset, center=CRY_VIOLIN_CENTER):
    pc = (root_val + offset) % 12
    lo, hi = CRY_VIOLIN_RANGE
    candidates = [pitch for pitch in range(lo, hi + 1) if pitch % 12 == pc]
    return _nearest(candidates, center)


def _cry_sounding_note_at_beat(events, target_beat):
    elapsed = 0.0
    for note, duration in events or []:
        if elapsed <= target_beat < elapsed + duration - 1e-9:
            return note
        elapsed += duration
    return None


def _cry_lead_bar_directions(melody, num_bars):
    directions = [0] * num_bars
    elapsed = 0.0
    last_by_bar = [[] for _ in range(num_bars)]
    for note, dur in melody:
        bar = min(num_bars - 1, int(elapsed // 4))
        if note is not None:
            last_by_bar[bar].append(note)
        elapsed += dur
    for idx, notes in enumerate(last_by_bar):
        if len(notes) >= 2:
            directions[idx] = notes[-1] - notes[0]
    return directions


def _choose_cry_counter_pitch(root_val, chord_tones, scale, lead_pitch, previous_pitch,
                              lead_direction=0, strong=False):
    source = chord_tones if strong else list(dict.fromkeys(chord_tones + scale))
    candidates = [_cry_violin_pitch(root_val, tone, previous_pitch) for tone in source]
    consonances = {3, 4, 5, 7, 8, 9}

    def score(pitch):
        value = 7.0 if (pitch - root_val) % 12 in {tone % 12 for tone in chord_tones} else 0.0
        value -= abs(pitch - previous_pitch) * 0.8
        if lead_pitch is not None:
            interval = abs(pitch - lead_pitch)
            value += 13.0 if interval in consonances else -18.0
            if interval == 0:
                value -= 25.0
            value += 2.5 if pitch < lead_pitch else -1.0
        motion = pitch - previous_pitch
        if lead_direction > 0 and motion < 0:
            value += 3.0
        elif lead_direction < 0 and motion > 0:
            value += 3.0
        elif lead_direction and motion * lead_direction > 0:
            value -= 2.0
        return value + random.random() * 0.75

    return max(candidates, key=score)


def _solo_bars_data(progression, scale_name):
    scale = MINOR_SCALES[scale_name]
    chords = SCALE_CHORDS[scale_name]
    if scale_name == "minor_engine_mixed":
        return [(chords[symbol], chords[symbol]) for symbol in progression]
    return [(chords[symbol], scale) for symbol in progression]


def _generate_crying_violin_lead_data(root_val, bars_data, tension):
    melody = []
    cur = 0
    motif_rhythm = None
    for bar_idx, (ct, sc) in enumerate(bars_data):
        if motif_rhythm is None or tension > 0.65:
            beats_left = 4.0
            bar_rhythm = []
            while beats_left > 0.01:
                dur = _weighted_rhythm(CRY_RHYTHM_LYRICAL, beats_left, tension * 0.7)
                bar_rhythm.append(dur)
                beats_left -= dur
            if motif_rhythm is None:
                motif_rhythm = bar_rhythm
        else:
            bar_rhythm = motif_rhythm

        beat_pos = 0.0
        for dur in bar_rhythm:
            strong = (beat_pos % 2.0 < 0.01)
            if strong or random.random() < 0.9:
                off = random.choice(ct)
            else:
                scale_options = [tone for tone in sc if tone not in ct]
                off = random.choice(scale_options or sc)
            pitch = _cry_violin_pitch(root_val, off)
            melody.append((pitch, dur))
            cur = off
            beat_pos += dur
    return melody


def _generate_crying_violin_counter_data(root_val, bars_data, tension, lead_melody):
    counter = []
    previous_pitch = _cry_violin_pitch(root_val, 7)
    lead_dirs = _cry_lead_bar_directions(lead_melody, len(bars_data))
    for bar_idx, (ct, sc) in enumerate(bars_data):
        beats_left = 4.0
        beat_pos = 0.0
        while beats_left > 0.01:
            dur = _weighted_rhythm(CRY_RHYTHM_SUSTAIN, beats_left, tension * 0.4)
            absolute_beat = bar_idx * 4.0 + beat_pos
            lead_pitch = _cry_sounding_note_at_beat(lead_melody, absolute_beat)
            pitch = _choose_cry_counter_pitch(
                root_val, ct, sc, lead_pitch, previous_pitch,
                lead_dirs[bar_idx], strong=(beat_pos % 2.0 < 0.01)
            )
            counter.append((pitch, dur))
            previous_pitch = pitch
            beats_left -= dur
            beat_pos += dur
    return counter


def _violin_data_to_events(data, channel, velocity, tpb, program=40, expression=True):
    events = [(0, "program", program, 0, channel)]
    tick = 0
    for pitch, dur_beats in data:
        dur_ticks = max(24, int(dur_beats * tpb))
        if pitch is not None:
            _add_note(events, tick, pitch, dur_ticks, velocity + random.randint(-5, 5), channel, humanize=False)
            if expression and dur_beats >= 1.0:
                _cc_curve(events, channel, 11, tick, dur_ticks, 42, random.choice([78, 86, 94]), steps=5)
        tick += dur_ticks
    return events


def _build_harmonic_plan(root_val, progression, scale_name):
    scale = MINOR_SCALES[scale_name]
    chords = SCALE_CHORDS[scale_name]
    plan = []
    previous = None
    for symbol in progression:
        notes = _voicing(root_val, chords[symbol], scale, previous)
        plan.append({"symbol": symbol, "notes": notes})
        previous = notes
    return plan


def _generate_pad(harmonic_plan, tpb):
    events = [(0, "program", 48, 0, 0)]
    for bar, harmony in enumerate(harmonic_plan):
        start = bar * 4 * tpb
        for idx, note in enumerate(harmony["notes"]):
            _add_note(events, start + idx * 5, note, 4 * tpb - 34, 50 + idx * 3, 0)
        _cc_curve(events, 0, 11, start, 4 * tpb, 42, 88, steps=7)
    return events


def _generate_rhythmic_layer(harmonic_plan, tpb, bpm):
    """Give each bar its own density while sustaining between every attack."""
    patterns = {
        "sustain": [[0.0]],
        "simple": [
            [0.0, 1.0], [0.0, 1.5], [0.0, 2.0], [0.0, 2.5], [0.0, 3.0],
        ],
        "moderate": [
            [0.0, 0.75, 2.0], [0.0, 1.5, 2.5], [0.0, 1.0, 2.75],
            [0.0, 0.75, 1.75, 3.0], [0.0, 1.25, 2.0, 3.5],
        ],
        "active": [
            [0.0, 0.75, 1.0, 2.0, 2.75, 3.5],
            [0.0, 0.5, 1.5, 2.25, 3.0, 3.75],
            [0.0, 0.75, 1.5, 2.0, 3.0, 3.5],
        ],
        "turnaround": [
            [0.0, 2.0, 3.0, 3.5], [0.0, 1.5, 2.75, 3.25, 3.75],
            [0.0, 2.5, 3.0, 3.5, 3.75],
        ],
    }

    role_weights = [42, 34, 18, 6] if bpm >= 132 else [28, 34, 27, 11]
    role_names = ["sustain", "simple", "moderate", "active"]
    bar_roles = random.choices(role_names, weights=role_weights, k=len(harmonic_plan))

    # Make space an intentional part of every performance and prevent a run of
    # busy bars. A turnaround is optional rather than automatic.
    if bar_roles and not any(role in ("sustain", "simple") for role in bar_roles):
        bar_roles[random.randrange(len(bar_roles))] = random.choice(["sustain", "simple"])
    busy_indices = [idx for idx, role in enumerate(bar_roles) if role == "active"]
    for idx in busy_indices[1:]:
        bar_roles[idx] = random.choice(["simple", "moderate"])
    if bar_roles and random.random() < (0.22 if bpm >= 132 else 0.38):
        last = len(bar_roles) - 1
        if any(role in ("sustain", "simple") for role in bar_roles[:last]):
            bar_roles[last] = "turnaround"

    events = [(0, "program", 48, 0, 5)]
    base_velocity = random.randint(57, 70)

    for bar, (harmony, role) in enumerate(zip(harmonic_plan, bar_roles)):
        hits = random.choice(patterns[role])
        notes = list(harmony["notes"])
        if len(notes) > 3 and role in ("moderate", "active", "turnaround") and random.random() < 0.55:
            # Preserve the voicing's harmonic identity while leaving mix space.
            notes = [notes[0], notes[len(notes) // 2], notes[-1]]

        for hit_index, beat in enumerate(hits):
            start = bar * 4 * tpb + int(beat * tpb)
            next_beat = hits[hit_index + 1] if hit_index + 1 < len(hits) else 4.0
            available = next_beat - beat
            # Each attack lasts exactly to the next attack (or bar line). The
            # accents create rhythm while the chord remains a continuous bed.
            duration = max(24, int(available * tpb))
            accent = 1.10 if hit_index == 0 else random.choice([0.72, 0.80, 0.88, 0.96])
            if available <= 0.5:
                accent += 0.06
            velocity = max(42, min(100, int(base_velocity * accent) + random.randint(-3, 3)))
            for note_index, note in enumerate(notes):
                _add_note(
                    events, start + note_index * 2, note,
                    duration, velocity + min(5, note_index * 2), 5, humanize=False
                )

    return events


def _generate_main_hook_lead(root_val, harmonic_plan, scale_name, tpb):
    """Write a repeatable hook entirely from the pad progression's chord tones."""
    register_center = random.choice([72, 74, 76, 77])
    opening_pool = sorted({
        shifted for note in harmonic_plan[0]["notes"]
        for shifted in (note, note + 12, note + 24) if 65 <= shifted <= 86
    })
    anchor = _nearest(opening_pool, register_center)
    signature_leap = random.choice([5, 7, -5])
    contour = random.choice([
        [0, 2, 1, 4, 2],
        [0, 3, 2, 5, 3],
        [0, 2, 4, 1, 3],
        [0, -2, 1, 4, 2],
    ])
    contour[random.choice([1, 2])] += signature_leap

    hook_rhythms = [
        [(0.0, 1.25), (1.5, 0.50), (2.25, 1.50)],
        [(0.0, 0.75), (1.0, 1.50), (3.0, 1.00)],
        [(0.0, 1.50), (2.0, 0.50), (2.75, 1.25)],
        [(0.5, 1.00), (1.75, 0.75), (2.75, 1.25)],
    ]
    answer_rhythms = [
        [(0.5, 1.25), (2.0, 1.75)],
        [(0.0, 1.50), (2.0, 0.75), (3.0, 1.00)],
        [(0.75, 0.75), (1.75, 2.00)],
    ]
    hook = random.choice(hook_rhythms)
    answer = random.choice(answer_rhythms)
    events = [(0, "program", 80, 0, 6)]
    previous = anchor

    for bar, harmony in enumerate(harmonic_plan):
        if bar % 4 in (0, 1):
            rhythm = hook
        elif bar % 4 == 2:
            rhythm = answer
        else:
            # Recall the opening rhythm so the phrase remains memorable.
            rhythm = hook

        chord_pool = sorted({
            shifted for note in harmony["notes"] for shifted in (note, note + 12, note + 24)
            if 65 <= shifted <= 86
        })

        for idx, (beat, duration_beats) in enumerate(rhythm):
            contour_idx = min(idx, len(contour) - 1)
            target = anchor + contour[contour_idx]
            if bar % 4 == 1 and idx >= len(rhythm) - 2:
                target += random.choice([-2, 2])
            elif bar % 4 == 2:
                target += random.choice([-3, 3])

            # Every hook note comes from the chord currently voiced by the pad.
            # Rhythm and contour provide movement without introducing a
            # merely-in-scale note that may rub against the active harmony.
            pitch = _nearest(chord_pool, target)
            if previous is not None and abs(pitch - previous) > 9:
                pitch = _nearest(chord_pool, previous + (5 if pitch > previous else -5))

            # Resolve the recalled phrase toward the final chord's stable tones.
            if bar == len(harmonic_plan) - 1 and idx == len(rhythm) - 1:
                pitch = _nearest(chord_pool, anchor)
                duration_beats = min(1.2, 4.0 - beat)

            velocity = random.randint(82, 91)
            if idx == 0:
                velocity += 8
            tick = bar * 4 * tpb + int(beat * tpb)
            duration = max(36, int(duration_beats * tpb))
            _add_note(events, tick, pitch, duration, min(112, velocity), 6, humanize=False)
            previous = pitch

    return events


def _generate_staccato(root_val, progression, scale_name, tpb, bpm, instrument):
    scale = MINOR_SCALES[scale_name]
    chords = SCALE_CHORDS[scale_name]
    lo, hi = instrument["range"]
    events = [(0, "program", instrument["program"], 0, 1)]
    current = None
    phrase_arcs = random.choice([
        [0.72, 0.88, 1.06, 0.82],
        [0.66, 0.92, 0.96, 1.10],
        [0.78, 0.84, 1.12, 0.74],
        [0.82, 1.04, 0.86, 1.12],
    ])
    register_center = max(lo, min(hi, instrument["prefer"] + random.choice([-3, 0, 0, 2, 5])))
    motif_cache = {}
    for bar, symbol in enumerate(progression):
        start = bar * 4 * tpb
        chord = chords[symbol]
        role = _chord_role(symbol)
        energy = phrase_arcs[bar % len(phrase_arcs)]
        cell_pool = _solo_string_cell_pool(bpm, role)
        motif_cache.setdefault(role, [random.choice(cell_pool) for _ in range(4)])
        motif = motif_cache[role]

        for beat in range(4):
            if beat == 0:
                cell = motif[0]
            elif beat == 3 and role == "home" and energy < 0.9:
                cell = [(0.0, 0.50, "root", "staccato")]
            elif beat == 2 and energy > 1.0:
                cell = random.choice(cell_pool)
            else:
                cell = random.choice([motif[beat % 4], random.choice(cell_pool)])

            if instrument["name"] == "Cello" and bpm >= 125 and len(cell) > 2:
                cell = [item for idx, item in enumerate(cell) if idx in (0, len(cell) - 1)]
            if energy < 0.78 and beat in (1, 3) and random.random() < 0.35:
                continue

            for step_idx, (offset, dur, tone_role, articulation) in enumerate(cell):
                pitch = _role_pitch(root_val, chord, scale, lo, hi, tone_role, current, register_center)
                tick = start + beat * tpb + int(offset * tpb)

                gate = {"spiccato": 0.42, "staccato": 0.58, "marcato": 0.76}.get(articulation, 0.52)
                dur_ticks = max(18, int(dur * tpb * gate) - random.randint(0, 6))
                velocity = int(68 + 28 * energy)
                if beat in (0, 2) and offset == 0.0:
                    velocity += 12
                elif offset == 0.0:
                    velocity += 5
                else:
                    velocity -= 5
                if role == "tension":
                    velocity += 5
                velocity = max(45, min(118, velocity + random.randint(-4, 4)))
                _add_note(events, tick, pitch, dur_ticks, velocity, 1, humanize=False)
                current = pitch
    return events


def _generate_sub_bass(root_val, progression, scale_name, tpb, bpm):
    chords = SCALE_CHORDS[scale_name]
    events = [(0, "program", 38, 0, 2)]
    previous = 40
    for bar, symbol in enumerate(progression):
        start = bar * 4 * tpb
        chord = chords[symbol]
        root_pc = (root_val + chord[0]) % 12
        fifth_pc = (root_val + chord[-1]) % 12
        root = _nearest([p for p in range(31, 49) if p % 12 == root_pc], previous)
        fifth = _nearest([p for p in range(34, 52) if p % 12 == fifth_pc], root + 7)
        _add_note(events, start, root, int((3.6 if bpm < 120 else 2.8) * tpb), 72, 2)
        if bpm >= 100 and bar % 2 == 1:
            _add_note(events, start + int(3.5 * tpb), fifth, int(0.42 * tpb), 54, 2)
            previous = fifth
        else:
            previous = root
    return events


def _generate_crying_violin_parts(root_val, progression, scale_name, tpb):
    bars_data = _solo_bars_data(progression, scale_name)
    tension = 0.58
    lead_data = _generate_crying_violin_lead_data(root_val, bars_data, tension)
    counter_data = _generate_crying_violin_counter_data(root_val, bars_data, tension, lead_data)
    lead_events = _violin_data_to_events(lead_data, 3, 78, tpb)
    counter_events = _violin_data_to_events(counter_data, 4, 58, tpb)
    return lead_events, counter_events, lead_data, counter_data


def _events_to_mid(tracks, names, bpm, tpb, loop_end_tick):
    mid = MidiFile()
    mid.ticks_per_beat = tpb
    for idx, events in enumerate(tracks):
        track = MidiTrack()
        track.name = names[idx]
        mid.tracks.append(track)
        track.append(MetaMessage("track_name", name=names[idx], time=0))
        if idx == 0:
            track.append(MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
            track.append(MetaMessage("time_signature", numerator=4, denominator=4, time=0))
        last = 0
        event_priority = {"program": 0, "cc": 0, "off": 1, "on": 2}
        for tick, kind, val1, val2, ch in sorted(events, key=lambda ev: (ev[0], event_priority[ev[1]])):
            tick = min(max(0, tick), loop_end_tick)
            delta = max(0, tick - last)
            last = tick
            if kind == "program":
                track.append(Message("program_change", program=val1, channel=ch, time=delta))
            elif kind == "cc":
                track.append(Message("control_change", control=val1, value=val2, channel=ch, time=delta))
            elif kind == "on":
                track.append(Message("note_on", note=val1, velocity=val2, channel=ch, time=delta))
            elif kind == "off":
                track.append(Message("note_off", note=val1, velocity=0, channel=ch, time=delta))
        track.append(MetaMessage("end_of_track", time=max(0, loop_end_tick - last)))
    return mid


def _title():
    adjectives, nouns = NAME_WORDS
    return f"{random.choice(adjectives)}_{random.choice(nouns)}"


def compose_solo_performance(out_dir, key_name, root_val, bpm, instrument_key="1", progression_pool=None, mood_name="Surprise"):
    tpb = 480
    pool = progression_pool or PROGRESSIONS
    label, scale_name, progression = random.choice(pool)
    instrument = INSTRUMENTS.get(instrument_key, random.choice(list(INSTRUMENTS.values())))
    harmonic_plan = _build_harmonic_plan(root_val, progression, scale_name)
    cry_lead, cry_counter, _lead_data, _counter_data = _generate_crying_violin_parts(root_val, progression, scale_name, tpb)
    # The pad must state every chord from bar one; the hook leads by musical
    # prominence and track order, not by removing the progression underneath it.
    pad = _generate_pad(harmonic_plan, tpb)
    rhythmic = _generate_rhythmic_layer(harmonic_plan, tpb, bpm)
    sub_bass = _generate_sub_bass(root_val, progression, scale_name, tpb, bpm)
    staccato = _generate_staccato(root_val, progression, scale_name, tpb, bpm, instrument)
    tracks = [
        _generate_main_hook_lead(root_val, harmonic_plan, scale_name, tpb),
        pad,
        rhythmic,
        staccato,
        sub_bass,
        cry_lead,
        cry_counter,
    ]
    names = [
        "Main Hook Lead - Opening Theme",
        "Chord Pad - Four Bar Minor String Bed",
        "Rhythmic Layer - Continuous Chord Pulse",
        f"{instrument['name']} Staccato Phrases - Solo Performance",
        "Sub-Bass - Progression Root Support",
        "Crying Violin Lead Melody",
        "Crying Violin Counter",
    ]
    loop_end = 4 * 4 * tpb
    mid = _events_to_mid(tracks, names, bpm, tpb, loop_end)
    fname = (
        f"{_title()}__Solo_Performance__{instrument['name']}__"
        f"{_slug(label)}__{key_name}_{_slug(scale_name.title())}__"
        f"{bpm}BPM__{'-'.join(progression)}"
    )
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, fname + ".mid")
    idx = 1
    while os.path.exists(path):
        path = os.path.join(out_dir, f"{fname}_v{idx}.mid")
        idx += 1
    mid.save(path)
    print(f"\n  [SAVED]  {os.path.basename(path)}")
    print(f"  [PATH ]  {path}")
    print(f"  [STYLE]  Solo Performance - {instrument['name']}")
    print(f"  [MOOD ]  {mood_name}")
    print(f"  [PROG ]  {'-'.join(progression)}\n")
    return path, progression


def _select_key():
    keys = sorted(ROOTS.keys())
    print(f"\n  Select Minor Root Key (Available: {', '.join(keys)})")
    key = input("  --> ").strip()
    if key:
        key = key[0].upper() + key[1:]
    if key not in ROOTS:
        key = random.choice(keys)
        print(f"  [RANDOM KEY] {key}")
    return key, ROOTS[key]


def _select_bpm():
    print("\n  Tempo BPM [70-156, Enter=random]:")
    raw = input("  --> ").strip()
    try:
        bpm = int(raw)
    except ValueError:
        bpm = random.choice([80, 84, 91, 96, 111, 116, 118, 120, 123, 132, 140, 156])
    return max(70, min(156, bpm))


def _select_instrument():
    print("""
  Select Solo Instrument:
    1 -> Violin
    2 -> Viola
    3 -> Cello
    R -> Random
""")
    choice = input("  --> ").strip().lower()
    if choice in INSTRUMENTS:
        return choice
    return random.choice(list(INSTRUMENTS.keys()))


def _select_mood_pool():
    groups = _progression_mood_groups()
    names = list(groups.keys())
    print("\n  Select Solo Performance Mood:")
    print("    S -> Surprise Me (all Solo + Minor Engine moods)")
    for idx, name in enumerate(names, 1):
        print(f"    {idx:>2} -> {name} ({len(groups[name])} progressions)")
    print("    B -> Back")
    choice = input("  --> ").strip().lower()
    if choice == "b":
        return None, None
    if choice == "s" or not choice:
        return "Surprise Me", PROGRESSIONS
    if choice.isdigit() and 1 <= int(choice) <= len(names):
        name = names[int(choice) - 1]
        return name, groups[name]
    print("  [RANDOM MOOD] Surprise Me")
    return "Surprise Me", PROGRESSIONS


def main(out_dir="midi_files"):
    os.makedirs(out_dir, exist_ok=True)
    print("""
SOLO PERFORMANCE

  Four-bar freestyle minor string performance.
  Tracks: main hook lead, chord pad, rhythmic layer, staccato phrases, sub-bass,
          crying violin lead, crying violin counter.
""")
    while True:
        _div()
        mood_name, progression_pool = _select_mood_pool()
        if progression_pool is None:
            return
        key_name, root_val = _select_key()
        bpm = _select_bpm()
        instrument_key = _select_instrument()
        print("\n  [GENERATING] Writing Solo Performance MIDI...")
        compose_solo_performance(out_dir, key_name, root_val, bpm, instrument_key, progression_pool, mood_name)

        print("  [G] Generate again  [B] Back  [Q] Quit")
        sub = input("  --> ").strip().lower()
        if sub in ("b", "q"):
            return


if __name__ == "__main__":
    main()
