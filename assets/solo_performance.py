"""
ANIMA Solo Performance
Four-bar minor string performance composer:
chord pad, solo staccato phrases, and sub-bass.
"""

import os
import random

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
    if symbol in ("V", "v", "VII", "bVII"):
        return "tension"
    if symbol in ("iv", "IV", "ii", "ii°", "bII"):
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


def _generate_pad(root_val, progression, scale_name, tpb):
    scale = MINOR_SCALES[scale_name]
    chords = SCALE_CHORDS[scale_name]
    events = [(0, "program", 48, 0, 0)]
    previous = None
    for bar, symbol in enumerate(progression):
        start = bar * 4 * tpb
        notes = _voicing(root_val, chords[symbol], scale, previous)
        previous = notes
        for idx, note in enumerate(notes):
            _add_note(events, start + idx * 5, note, 4 * tpb - 34, 50 + idx * 3, 0)
        _cc_curve(events, 0, 11, start, 4 * tpb, 42, 88, steps=7)
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


def _generate_crying_violin(root_val, progression, scale_name, tpb, bpm):
    scale = MINOR_SCALES[scale_name]
    chords = SCALE_CHORDS[scale_name]
    lo, hi = 60, 88
    events = [(0, "program", 40, 0, 3)]
    current = _nearest(_chord_pitches(root_val, chords[progression[0]], lo, hi), 76)
    contour = random.choice([
        [-5, 4, -4, 2],
        [4, -5, 3, -4],
        [-3, -2, 5, -5],
        [3, 4, -6, -2],
        [0, -4, 5, -3],
        [-4, 6, -3, -2],
    ])
    phrase_arcs = random.choice([
        [0.70, 0.88, 1.05, 0.82],
        [0.78, 0.96, 0.86, 1.10],
        [0.72, 0.82, 1.08, 0.92],
    ])
    last_sustain_delta = 0

    for bar, symbol in enumerate(progression):
        start = bar * 4 * tpb
        chord = chords[symbol]
        role = _chord_role(symbol)
        energy = phrase_arcs[bar % len(phrase_arcs)]
        chord_pool = _chord_pitches(root_val, chord, lo, hi)
        scale_pool = _scale_pitches(root_val, scale, lo, hi)
        if not chord_pool:
            chord_pool = scale_pool

        if role == "tension":
            tone_role = random.choice(["third", "fifth", "color"])
        elif role == "motion":
            tone_role = random.choice(["third", "fifth", "root"])
        else:
            tone_role = random.choice(["root", "third", "fifth"])

        role_pitch = _role_pitch(root_val, chord, scale, lo, hi, tone_role, current, 76)
        target_pool = [p for p in chord_pool if p % 12 == role_pitch % 12] or chord_pool
        target = _contour_chord_pitch(target_pool, current, 76, contour[bar % len(contour)])
        if abs(target - current) > 10:
            target = _nearest([p for p in chord_pool if abs(p - current) <= 10] or chord_pool, current)
        if current is not None and ((last_sustain_delta > 0 and target >= current) or (bar == 3 and target > current)):
            lower = [p for p in chord_pool if p < current and abs(p - current) <= 10]
            if lower:
                target = _nearest(lower, current - random.choice([2, 3, 5]))

        entry = random.choice([0.0, 0.0, 0.25, 0.5]) if bar else 0.0
        if role == "tension" and random.random() < 0.45:
            entry = random.choice([0.0, 0.5])
        release = random.choice([3.05, 3.35, 3.65, 3.85])
        if bar == 3:
            release = random.choice([3.55, 3.75, 3.9])
        dur_beats = max(1.4, release - entry)
        velocity = max(48, min(96, int(58 + 26 * energy) + random.randint(-4, 5)))
        _add_note(events, start + int(entry * tpb), target, int(dur_beats * tpb), velocity, 3, humanize=False)
        _cc_curve(events, 3, 11, start + int(entry * tpb), int(dur_beats * tpb), 38, 96 if energy > 0.95 else 82, steps=6)

        if random.random() < (0.50 if bpm < 120 else 0.38):
            sob_delay = random.choice([0.5, 0.75, 1.0, 1.5])
            sob_candidates = [p for p in chord_pool if 1 <= abs(p - target) <= 5]
            if not sob_candidates and random.random() < 0.25:
                sob_candidates = [p for p in scale_pool if 1 <= abs(p - target) <= 3]
            sob_direction = -1 if contour[bar % len(contour)] >= 0 else 1
            sob = _nearest(sob_candidates or chord_pool, target + sob_direction * random.choice([2, 3, 5]))
            sob_dur = random.choice([0.18, 0.24, 0.32])
            _add_note(events, start + int(sob_delay * tpb), sob, int(sob_dur * tpb), max(38, velocity - 18), 3, humanize=False)

        if random.random() < (0.34 if role in ("motion", "tension") else 0.18):
            answer_beat = random.choice([2.5, 2.75, 3.0])
            answer_role = random.choice(["root", "third", "fifth"])
            answer_shift = -contour[bar % len(contour)] if contour[bar % len(contour)] else random.choice([-4, 4])
            answer_pool = _chord_pitches(root_val, chord, lo, hi)
            answer_role_pitch = _role_pitch(root_val, chord, scale, lo, hi, answer_role, target, 76)
            answer_pool = [p for p in answer_pool if p % 12 == answer_role_pitch % 12] or chord_pool
            answer = _contour_chord_pitch(answer_pool, target, 76, answer_shift)
            if abs(answer - target) > 5:
                answer = _nearest([p for p in chord_pool if abs(p - target) <= 5] or chord_pool, target)
            _add_note(events, start + int(answer_beat * tpb), answer, int(random.choice([0.25, 0.33, 0.42]) * tpb), max(42, velocity - 12), 3, humanize=False)

        last_sustain_delta = target - current
        current = target
    return events


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
        for tick, kind, val1, val2, ch in sorted(events, key=lambda ev: (ev[0], 0 if ev[1] in ("program", "cc") else 1)):
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


def compose_solo_performance(out_dir, key_name, root_val, bpm, instrument_key="1"):
    tpb = 480
    label, scale_name, progression = random.choice(PROGRESSIONS)
    instrument = INSTRUMENTS.get(instrument_key, random.choice(list(INSTRUMENTS.values())))
    tracks = [
        _generate_pad(root_val, progression, scale_name, tpb),
        _generate_staccato(root_val, progression, scale_name, tpb, bpm, instrument),
        _generate_sub_bass(root_val, progression, scale_name, tpb, bpm),
        _generate_crying_violin(root_val, progression, scale_name, tpb, bpm),
    ]
    names = [
        "Chord Pad - Four Bar Minor String Bed",
        f"{instrument['name']} Staccato Phrases - Solo Performance",
        "Sub-Bass - Progression Root Support",
        "Crying Violin - Sustained Sorrow Lead",
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


def main(out_dir="midi_files"):
    print("""
SOLO PERFORMANCE

  Four-bar freestyle minor string performance.
  Tracks: chord pad, staccato phrases, sub-bass.
""")
    _div()
    key_name, root_val = _select_key()
    bpm = _select_bpm()
    instrument_key = _select_instrument()
    print("\n  [GENERATING] Writing Solo Performance MIDI...")
    compose_solo_performance(out_dir, key_name, root_val, bpm, instrument_key)


if __name__ == "__main__":
    main()
