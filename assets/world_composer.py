"""
ANIMA World Composer
Minor-scale regional MIDI composer for Spanish, Asian, Oriental, and
world-trap/drill melodic material.
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

WORLD_SCALES = {
    "natural_minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "dorian_minor": [0, 2, 3, 5, 7, 9, 10],
    "minor_pentatonic": [0, 3, 5, 7, 10],
    "japanese_in_minor": [0, 1, 5, 7, 8],
    "chinese_minor_pentatonic": [0, 3, 5, 7, 10],
    "arabic_minor": [0, 1, 3, 5, 7, 8, 11],
}

SCALE_CHORDS = {
    "natural_minor": {
        "i": [0, 3, 7], "iv": [5, 8, 0], "v": [7, 10, 2],
        "bVI": [8, 0, 3], "bVII": [10, 2, 5], "bIII": [3, 7, 10],
        "ii°": [2, 5, 8], "iadd4": [0, 3, 5], "vadd4": [7, 10, 0],
        "ivadd2": [5, 7, 0], "bVIadd2": [8, 10, 3],
    },
    "harmonic_minor": {
        "i": [0, 3, 7], "iv": [5, 8, 0], "V": [7, 11, 2],
        "VI": [8, 0, 3], "VII": [11, 2, 5], "III": [3, 7, 11],
    },
    "phrygian": {
        "i": [0, 3, 7], "bII": [1, 5, 8], "iv": [5, 8, 0],
        "bVI": [8, 0, 3], "bVII": [10, 1, 5], "bIII": [3, 7, 10],
    },
    "dorian_minor": {
        "i": [0, 3, 7], "IV": [5, 9, 0], "v": [7, 10, 2],
        "bVII": [10, 2, 5], "bIII": [3, 7, 10], "ii": [2, 5, 9],
    },
    "minor_pentatonic": {
        "i": [0, 3, 7], "iv": [5, 10, 0], "bVII": [10, 3, 5],
        "bIII": [3, 7, 10],
    },
    "japanese_in_minor": {
        "i": [0, 7, 12], "iadd4": [0, 5, 7], "iaddb2": [0, 1, 7],
        "bII": [1, 5, 8], "bIIsus": [1, 8, 13],
        "iv": [5, 8, 0], "ivadd2": [5, 7, 0],
        "bVI": [8, 0, 5], "bVIaddb2": [8, 0, 1],
    },
    "chinese_minor_pentatonic": {
        "i": [0, 3, 7], "iv": [5, 10, 0], "bVII": [10, 3, 5],
        "bIII": [3, 7, 10],
    },
    "arabic_minor": {
        "i": [0, 3, 7], "bII": [1, 5, 8], "iv": [5, 8, 0],
        "V": [7, 11, 1], "bVI": [8, 0, 3], "bIII": [3, 7, 11],
        "VII": [11, 3, 5], "iaddb2": [0, 1, 7], "bIIadd6": [1, 5, 8, 11],
    },
}

WORLD_PRESETS = {
    "1": {
        "region": "Andalusian Drill",
        "desc": "Spanish/Arabic minor tension with drill-ready spacing",
        "scale": "harmonic_minor",
        "profile": "andalusian",
        "bpm_range": (118, 145),
        "tension": 0.76,
        "lead_program": 24,
        "pluck_program": 104,
        "pad_program": 89,
        "progressions": [
            ("Desert Cadence", ["i", "VII", "VI", "V"]),
            ("Granada Shadow", ["i", "iv", "V", "i"]),
            ("Night Descent", ["i", "VI", "III", "V"]),
            ("Lamento Andaluz", ["i", "iv", "VII", "III", "VI", "iv", "V", "i"]),
            ("Saeta Resolve", ["i", "VI", "iv", "V", "i", "VII", "VI", "V"]),
            ("Alhambra Tears", ["i", "III", "VI", "V", "iv", "i", "VII", "i"]),
            ("Moorish Descent", ["i", "VII", "VI", "iv", "i", "VI", "V", "i"]),
            ("Midnight Solea", ["i", "iv", "i", "V", "VI", "III", "VII", "i"]),
            ("Cante Jondo", ["i", "VI", "VII", "i", "iv", "III", "V", "i"]),
        ],
        "name_words": (
            [
                "Andaluz", "Granada", "Caliente", "Sombra", "Rojo", "Gitano",
                "Alhambra", "Saeta", "Solea", "Jondo", "Morisco", "Azahar",
                "Carmesi", "Lloroso", "Nocturno", "Duende", "Serrano", "Herido",
            ],
            [
                "Mercado", "Lamento", "Fuego", "Callejon", "Noche", "Patio",
                "Candela", "Llanto", "Falseta", "Procesion", "Ermita", "Barrio",
                "Romance", "Taconeo", "Madrugada", "Catedral", "Sierra", "Ceniza",
            ],
        ),
    },
    "2": {
        "region": "Tokyo Koto Trap",
        "desc": "Sparse Japanese plucks, high hooks, and dark minor roots",
        "scale": "natural_minor",
        "profile": "tokyo",
        "bpm_range": (112, 132),
        "tension": 0.58,
        "lead_program": 77,
        "pluck_program": 107,
        "pad_program": 90,
        "progressions": [
            ("Bounty Root Spell", ["i", "i", "i", "i", "v", "i", "v", "i"]),
            ("Dynasty Descent", ["bIII", "v", "i", "i", "bIII", "v", "iv", "bIII"]),
            ("Samurai Return", ["i", "v", "i", "i", "bVII", "iv", "v", "iv"]),
            ("Shanghai Lantern", ["i", "i", "iv", "v", "i", "i", "iv", "i"]),
            ("Soprano Cry", ["v", "i", "bIII", "v", "v", "i", "bIII", "v"]),
            ("Sweet Low Memory", ["bVI", "iv", "bVI", "iv", "i", "v", "bVI", "iv"]),
            ("Taipei Night Loop", ["v", "bIII", "i", "i", "v", "bIII", "i", "i"]),
            ("Yakuza Minor Walk", ["bIII", "i", "v", "i", "bIII", "ii°", "v", "i"]),
            ("Familia Longing", ["i", "bIII", "bVII", "bIII", "bVI", "v", "i", "bIII"]),
            ("Rojo Suspense", ["bIII", "vadd4", "v", "v", "bIII", "vadd4", "v", "i"]),
            ("Unicorn Drone", ["i", "iadd4", "v", "iv", "i", "iadd4", "v", "i"]),
            ("Mercado Shadows", ["bVII", "bVII", "bVI", "bVI", "iv", "iv", "i", "i"]),
        ],
        "name_words": (
            [
                "Tokyo", "Kyoto", "Samurai", "Neon", "Yakuza", "Shibuya",
                "Akihabara", "Sakura", "Ronin", "Midnight", "Violet",
                "Rainlit", "Hollow", "Torii", "Kitsune", "Moonlit",
            ],
            [
                "Temple", "Rain", "Lantern", "Blade", "Garden", "Shrine",
                "Afterglow", "Last_Train", "Koto_Dream", "Night_Market",
                "Paper_Moon", "Glass_Pond", "Silent_Roof", "Fog_Path",
                "Electric_Petal", "Bamboo_Court",
            ],
        ),
    },
    "3": {
        "region": "Shanghai Night Drill",
        "desc": "Oriental phrygian color with hollow fifths and bell hooks",
        "scale": "natural_minor",
        "profile": "shanghai",
        "bpm_range": (110, 124),
        "tension": 0.66,
        "lead_program": 110,
        "pluck_program": 107,
        "pad_program": 92,
        "progressions": [
            ("Shanghai Lantern", ["i", "i", "iv", "v", "i", "i", "iv", "i"]),
            ("Taipei Rain Cycle", ["v", "bIII", "i", "i", "v", "bIII", "i", "i"]),
            ("Dynasty River", ["bIII", "v", "i", "i", "bIII", "v", "iv", "bIII"]),
            ("Jade Descent", ["i", "bIII", "bVII", "i", "bIII", "v", "iv", "i"]),
            ("Red Lantern Memory", ["i", "iv", "v", "i", "bVI", "iv", "v", "i"]),
            ("Harbor Root Spell", ["i", "iadd4", "i", "v", "iv", "i", "v", "i"]),
            ("Moon Gate Resolve", ["bVI", "bVII", "i", "v", "bIII", "ivadd2", "v", "i"]),
            ("Dragon Alley Cry", ["i", "v", "bIII", "iv", "i", "bVII", "v", "i"]),
        ],
        "name_words": (
            ["Shanghai", "Taipei", "Jade", "Dragon", "Lantern", "Harbor", "Moonlit", "Dynasty", "Red", "Pearl"],
            ["Harbor", "Dynasty", "Alley", "Market", "Moon", "River", "Gate", "Rain", "Pagoda", "Memory"],
        ),
    },
    "4": {
        "region": "Arabian Trap",
        "desc": "Desert harmonic minor phrases with oud-like ornaments",
        "scale": "arabic_minor",
        "profile": "arabian",
        "bpm_range": (92, 122),
        "tension": 0.62,
        "lead_program": 72,
        "pluck_program": 104,
        "pad_program": 89,
        "progressions": [
            ("Oasis Lament", ["i", "iv", "bVI", "V"]),
            ("Desert Crown", ["i", "bII", "bVI", "i"]),
            ("Mirage Resolve", ["i", "bVI", "iv", "V"]),
            ("Ney Over Dunes", ["i", "bII", "i", "V", "bVI", "iv", "V", "i"]),
            ("Qanun Tears", ["iaddb2", "bVI", "bII", "V", "i", "iv", "bIIadd6", "i"]),
            ("Cairo Night Prayer", ["i", "bIII", "bVI", "V", "i", "bII", "V", "i"]),
            ("Amber Caravan", ["i", "iv", "bII", "i", "bVI", "bIII", "V", "i"]),
            ("Sahara Descent", ["i", "VII", "bVI", "V", "i", "bII", "iv", "V"]),
            ("Mirage Longing", ["bVI", "V", "i", "bII", "iv", "bVI", "V", "i"]),
        ],
        "name_words": (
            ["Sahara", "Mirage", "Oasis", "Cairo", "Amber", "Ney", "Qanun", "Desert", "Dusk", "Saffron"],
            ["Dune", "Crown", "Caravan", "Moon", "Prayer", "Minaret", "Tears", "Sands", "Night", "Lament"],
        ),
    },
    "5": {
        "region": "Latin Minor Trap",
        "desc": "Slow emotional minor guitar and bell hooks for trap beats",
        "scale": "natural_minor",
        "profile": "latin",
        "bpm_range": (80, 116),
        "tension": 0.48,
        "lead_program": 24,
        "pluck_program": 12,
        "pad_program": 88,
        "progressions": [
            ("Venezuela Tears", ["i", "bVI", "bIII", "bVII"]),
            ("Sweet Minor", ["i", "iv", "bVII", "bVI"]),
            ("Familia Memory", ["i", "bIII", "bVII", "iv"]),
            ("Venezuela Pulse", ["i", "v", "i", "v", "bVI", "iv", "i", "v"]),
            ("Sweet Low Memory", ["bVI", "iv", "bVI", "iv", "i", "v", "bVI", "iv"]),
            ("Familia Longing", ["i", "bIII", "bVII", "bIII", "bVI", "v", "i", "bIII"]),
            ("Mercado Evening", ["bVII", "bVII", "bVI", "bVI", "iv", "iv", "i", "i"]),
            ("Caliente Resolve", ["i", "bVI", "iv", "v", "bIII", "bVII", "iv", "i"]),
            ("Balcony Sorrow", ["i", "iv", "i", "v", "bVI", "bIII", "bVII", "i"]),
            ("Dulce Descent", ["bIII", "bVII", "i", "bVI", "bIII", "v", "iv", "i"]),
        ],
        "name_words": (
            ["Venezuela", "Familia", "Dulce", "Caracas", "Caliente", "Mercado", "Nocturno", "Tierno", "Corazon", "Balcony"],
            ["Tears", "Sweet", "Balcony", "Memory", "Serenade", "Evening", "Promise", "Calle", "Romance", "Sombra"],
        ),
    },
    "6": {
        "region": "Balkan Drill",
        "desc": "Fast minor hooks with asymmetric-feeling ornaments",
        "scale": "dorian_minor",
        "profile": "balkan",
        "bpm_range": (124, 156),
        "tension": 0.82,
        "lead_program": 71,
        "pluck_program": 21,
        "pad_program": 89,
        "progressions": [
            ("Gypsy Sprint", ["i", "IV", "bVII", "i"]),
            ("Night Caravan", ["i", "ii", "bVII", "i"]),
            ("Folk Drill", ["i", "bIII", "IV", "bVII"]),
            ("Danube Fire", ["i", "ii", "i", "bVII", "i", "IV", "v", "i"]),
            ("Clarinet Descent", ["bIII", "bVII", "i", "i", "bIII", "IV", "v", "i"]),
            ("Aksak Lament", ["i", "v", "bVII", "IV", "i", "ii", "v", "i"]),
            ("Midnight Circle", ["i", "bIII", "bVII", "i", "ii", "IV", "bVII", "i"]),
            ("Caravan Resolve", ["i", "IV", "ii", "v", "i", "bVII", "IV", "i"]),
            ("Folk Cry", ["bIII", "ii", "i", "bVII", "i", "v", "ii", "i"]),
        ],
        "name_words": (
            ["Balkan", "Gypsy", "Folk", "Danube", "Midnight", "Aksak", "Clarinet", "River", "Ember", "Wild"],
            ["Caravan", "Sprint", "Circle", "Market", "Dance", "Lament", "Wedding", "Fire", "Road", "Echo"],
        ),
    },
}

GM_BASS = 32
GM_BELL = 14
GUITAR_LOW = 40
GUITAR_HIGH = 88
GUITAR_RASGUEO_LOW = 43
GUITAR_RASGUEO_HIGH = 66
GUITAR_PICADO_LOW = 62
GUITAR_PICADO_HIGH = 81
GUITAR_ALZAPUA_LOW = 55
GUITAR_ALZAPUA_HIGH = 72
KOTO_LOW = 48
KOTO_HIGH = 76
KOTO_HOOK_LOW = 55
KOTO_HOOK_HIGH = 74
SHAKUHACHI_LOW = 62
SHAKUHACHI_HIGH = 84

STYLE_PROFILES = {
    "andalusian": {
        "programs": [32, 24, 24, 89, 40, 0],
        "names": [
            "808 Bajo / Andalusian Root",
            "Cante Falseta Lead (Nylon Guitar)",
            "Rasgueado Compas Guitar",
            "Moorish Minor Drone Pad",
            "Violin Cry / Saeta Answer",
            "Palmas, Golpe and Cajon Pulse",
        ],
        "pluck_grid": [[0.0, 0.33, 0.67, 1.5, 2.0, 2.33, 2.67, 3.5], [0.0, 0.5, 1.0, 1.5, 2.0, 2.75, 3.5]],
        "lead_grid": [0.5, 2.5],
        "percussion": "palmas",
        "bass": "root_fifth",
        "emotion": "cry",
        "lead_bars": {2, 3, 6, 7, 10, 11, 14, 15},
    },
    "tokyo": {
        "programs": [33, 77, 107, 90, 14, 0],
        "names": [
            "Sub Bass / Silent Temple Root",
            "Shakuhachi Breath Lead",
            "Koto Harmonic Plucks",
            "Neon Shrine Air Pad",
            "Glass Bell Counter Motif",
            "Taiko Shadow Pulse",
        ],
        "pluck_grid": [[0.0, 0.75, 1.5, 3.0], [0.0, 1.0, 1.25, 2.5, 3.5]],
        "lead_grid": [0.0, 1.5, 2.0, 3.25],
        "percussion": "taiko",
        "bass": "sparse",
        "emotion": "space",
    },
    "shanghai": {
        "programs": [33, 110, 107, 92, 15, 0],
        "names": [
            "Drill Bass / Harbor Root",
            "Erhu Lament Lead",
            "Guzheng Rolling Plucks",
            "Red Lantern Atmosphere",
            "Yangqin Bell Reply",
            "Gong and Hat Drill Pulse",
        ],
        "pluck_grid": [[0.0, 0.25, 0.5, 1.5, 2.0, 2.25, 2.5, 3.5], [0.0, 0.5, 1.0, 2.0, 2.5, 3.0]],
        "lead_grid": [0.0, 0.5, 1.75, 2.0, 3.0],
        "percussion": "gong_drill",
        "bass": "slide",
        "emotion": "bend",
    },
    "arabian": {
        "programs": [32, 72, 104, 89, 69, 0],
        "names": [
            "Deep Desert 808",
            "Ney / Oud Taqsim Lead",
            "Oud Tremolo Ostinato",
            "Dune Choir Drone",
            "Qanun Answer Phrase",
            "Darbuka Trap Pulse",
        ],
        "pluck_grid": [[0.0, 0.5, 0.75, 1.5, 2.0, 2.5, 2.75, 3.5], [0.0, 0.33, 0.67, 1.5, 2.0, 3.0]],
        "lead_grid": [0.0, 0.25, 0.75, 1.5, 2.5, 3.25],
        "percussion": "darbuka",
        "bass": "pedal",
        "emotion": "maqam",
    },
    "latin": {
        "programs": [32, 24, 12, 88, 108, 0],
        "names": [
            "Warm 808 Bass",
            "Nylon Requinto Lead",
            "Marimba / Bell Tresillo",
            "Soft Latin Minor Pad",
            "Kalimba Sweet Counter",
            "Reggaeton Ghost Percussion",
        ],
        "pluck_grid": [[0.0, 0.75, 1.5, 2.5, 3.0], [0.0, 0.5, 1.5, 2.0, 2.75, 3.5]],
        "lead_grid": [0.0, 1.0, 1.5, 2.5, 3.0],
        "percussion": "tresillo",
        "bass": "tresillo",
        "emotion": "sweet",
    },
    "balkan": {
        "programs": [33, 71, 21, 89, 22, 0],
        "names": [
            "Drill Bass / Aksak Root",
            "Balkan Clarinet Fire Lead",
            "Accordion Offbeat Stabs",
            "Dark Folk Drone",
            "Reed Counter Dance",
            "Aksak Hand Drum Pulse",
        ],
        "pluck_grid": [[0.0, 0.75, 1.5, 2.5, 3.25], [0.0, 0.5, 1.25, 2.0, 2.75, 3.5]],
        "lead_grid": [0.0, 0.25, 0.75, 1.5, 2.25, 2.5, 3.25],
        "percussion": "aksak",
        "bass": "aksak",
        "emotion": "fire",
    },
}


def _div(c="-", w=62):
    print(c * w)


def _slug(value):
    keep = []
    for ch in str(value):
        if ch.isalnum() or ch in ("#", "b"):
            keep.append(ch)
        elif ch in (" ", "-", "_", "/"):
            keep.append("_")
    text = "".join(keep).strip("_")
    while "__" in text:
        text = text.replace("__", "_")
    return text or "World"


def _pitch_for_pc(pc, lo, hi, prefer=None):
    candidates = [p for p in range(lo, hi + 1) if p % 12 == pc % 12]
    if not candidates:
        return max(lo, min(hi, pc))
    if prefer is None:
        return random.choice(candidates)
    return min(candidates, key=lambda p: abs(p - prefer))


def _scale_pitches(root_val, scale, lo, hi):
    pcs = {(root_val + interval) % 12 for interval in scale}
    return [pitch for pitch in range(lo, hi + 1) if pitch % 12 in pcs]


def _chord_pitches(root_val, chord_offsets, lo, hi):
    pcs = {(root_val + interval) % 12 for interval in chord_offsets}
    return [pitch for pitch in range(lo, hi + 1) if pitch % 12 in pcs]


def _nearest_pitch(candidates, target):
    if not candidates:
        return target
    return min(candidates, key=lambda pitch: (abs(pitch - target), pitch))


def _nearest_chord_tone(root_val, chord_offsets, lo, hi, target):
    return _nearest_pitch(_chord_pitches(root_val, chord_offsets, lo, hi), target)


def _nearest_scale_tone(root_val, scale, lo, hi, target):
    return _nearest_pitch(_scale_pitches(root_val, scale, lo, hi), target)


def _constrain_leap(candidates, current, max_leap=7):
    near = [pitch for pitch in candidates if abs(pitch - current) <= max_leap]
    return near or candidates


def _neighbor_tone(root_val, scale, lo, hi, anchor, direction=None):
    scale_notes = _scale_pitches(root_val, scale, lo, hi)
    if not scale_notes:
        return anchor
    if direction is None:
        direction = random.choice([-1, 1])
    candidates = [pitch for pitch in scale_notes if 0 < direction * (pitch - anchor) <= 3]
    if not candidates:
        candidates = [pitch for pitch in scale_notes if 0 < abs(pitch - anchor) <= 3]
    return _nearest_pitch(candidates or scale_notes, anchor + direction * 2)


def _voicing(root_val, chord_offsets, lo=48, hi=84):
    notes = []
    for idx, offset in enumerate(chord_offsets):
        pc = (root_val + offset) % 12
        prefer = 48 + idx * 5
        notes.append(_pitch_for_pc(pc, lo, hi, prefer))
    root_pc = (root_val + chord_offsets[0]) % 12
    notes.append(_pitch_for_pc(root_pc, lo, hi, 72))
    fifth_pc = (root_val + chord_offsets[-1]) % 12
    notes.append(_pitch_for_pc(fifth_pc, lo, hi, 79))
    return sorted(set(notes))


def _guitar_chord_voicing(root_val, chord_offsets, scale):
    scale_pcs = {(root_val + interval) % 12 for interval in scale}
    chord_pcs = [(root_val + interval) % 12 for interval in chord_offsets]
    chord_pcs = [pc for pc in chord_pcs if pc in scale_pcs] or chord_pcs
    root_pc = chord_pcs[0]
    third_pc = chord_pcs[1] if len(chord_pcs) > 1 else root_pc
    fifth_pc = chord_pcs[2] if len(chord_pcs) > 2 else root_pc

    bass = _pitch_for_pc(root_pc, 40, 52, 43)
    voicing = [bass]
    for pc, minimum in [
        (third_pc, bass + 3),
        (fifth_pc, bass + 7),
        (root_pc, bass + 12),
        (third_pc, bass + 15),
    ]:
        pitch = pc
        while pitch < minimum:
            pitch += 12
        while pitch in voicing:
            pitch += 12
        if GUITAR_LOW <= pitch <= 84:
            voicing.append(pitch)
    return sorted(set(voicing))


def _emit(events, tick, kind, val1, val2, channel):
    events.append((max(0, int(tick)), kind, int(val1), int(val2), channel))


def _add_note(events, tick, pitch, dur_ticks, velocity, channel):
    pitch = max(0, min(127, int(pitch)))
    velocity = max(1, min(127, int(velocity)))
    start = max(0, int(tick) + random.randint(-5, 5))
    end = max(start + 12, int(tick + dur_ticks) + random.randint(-3, 3))
    _emit(events, start, "on", pitch, velocity, channel)
    _emit(events, end, "off", pitch, 0, channel)


def _add_tremolo_note(events, tick, pitch, dur_ticks, velocity, channel, repeats_per_beat=5):
    repeats = max(1, int((dur_ticks / 480.0) * repeats_per_beat))
    repeat_ticks = max(45, dur_ticks // repeats)
    for rep in range(repeats):
        rep_tick = tick + rep * repeat_ticks
        progress = rep / float(max(1, repeats - 1))
        vel = int((velocity - 18) + progress * 28) + random.randint(-5, 5)
        vel = max(24, min(118, vel))
        start = max(0, rep_tick + random.randint(-5, 5))
        end = min(tick + dur_ticks - 8, start + max(30, repeat_ticks - 12))
        if end > start:
            _emit(events, start, "on", pitch, vel, channel)
            _emit(events, end, "off", pitch, 0, channel)


def _add_koto_tremolo(events, tick, pitch, dur_ticks, velocity, channel):
    repeat_ticks = random.choice([108, 120, 132])
    repeats = max(3, dur_ticks // repeat_ticks)
    for rep in range(repeats):
        start = tick + rep * repeat_ticks + random.randint(-3, 3)
        end = min(tick + dur_ticks - 6, start + random.choice([46, 54, 62]))
        if end > start:
            vel = velocity + random.choice([-7, -3, 0, 4])
            _emit(events, start, "on", pitch, max(30, min(112, vel)), channel)
            _emit(events, end, "off", pitch, 0, channel)


def _notes_from_events(events, channel):
    active = {}
    notes = []
    for tick, etype, pitch, vel, ch in sorted(events, key=lambda ev: (ev[0], ev[1])):
        if ch != channel:
            continue
        if etype == "on" and vel > 0:
            active.setdefault(pitch, []).append((tick, vel))
        elif etype == "off" and active.get(pitch):
            start, start_vel = active[pitch].pop(0)
            notes.append((start, tick, pitch, start_vel))
    return notes


def _active_notes_in_span(notes, tick, dur_ticks, pad_ticks=90):
    span_end = tick + dur_ticks
    return [
        pitch for start, end, pitch, _vel in notes
        if tick - pad_ticks < end and start < span_end + pad_ticks
    ]


def _attack_near(events, tick, channel, window=90):
    for ev_tick, etype, _pitch, vel, ch in events:
        if ch == channel and etype == "on" and vel > 0 and abs(ev_tick - tick) <= window:
            return True
    return False


def _choose_against_events(candidates, avoid_notes, tick, dur_ticks, previous=None):
    if not candidates:
        return None
    bad_intervals = {0, 1, 2, 6, 10, 11}
    good_intervals = {3, 4, 7, 8, 9}
    scored = []
    active = _active_notes_in_span(avoid_notes, tick, dur_ticks)
    for pitch in candidates:
        score = 0
        if previous is not None:
            score += abs(pitch - previous) * 0.6
        for other in active:
            interval = abs(pitch - other) % 12
            if interval in bad_intervals:
                score += 900
            elif interval in good_intervals:
                score -= 30
            score += max(0, 5 - abs(pitch - other)) * 35
        scored.append((score + random.random() * 2, pitch))
    clean = [item for item in scored if item[0] < 600]
    return min(clean or scored)[1]


def _sanitize_track_to_scale(events, root_val, scale, channel_ranges):
    scale_pcs = {(root_val + interval) % 12 for interval in scale}
    sanitized = []
    for tick, etype, val1, val2, channel in events:
        if etype in ("on", "off") and channel in channel_ranges:
            low, high = channel_ranges[channel]
            if val1 % 12 not in scale_pcs or not (low <= val1 <= high):
                candidates = [p for p in range(low, high + 1) if p % 12 in scale_pcs]
                if candidates:
                    val1 = _nearest_pitch(candidates, val1)
                else:
                    val1 = max(low, min(high, val1))
        sanitized.append((tick, etype, val1, val2, channel))
    return sanitized


def _trim_halfstep_overlaps(events, channel):
    notes = _notes_from_events(events, channel)
    adjusted = [
        {"start": start, "end": end, "pitch": pitch, "vel": vel}
        for start, end, pitch, vel in notes
    ]
    for idx, note in enumerate(adjusted):
        for other in adjusted:
            if other is note:
                continue
            if note["start"] < other["end"] and other["start"] < note["end"]:
                interval = abs(note["pitch"] - other["pitch"]) % 12
                if interval in {1, 11} and note["start"] <= other["start"]:
                    note["end"] = max(note["start"] + 24, min(note["end"], other["start"] - 8))

    rebuilt = [
        ev for ev in events
        if not (ev[4] == channel and ev[1] in ("on", "off"))
    ]
    for note in adjusted:
        if note["end"] > note["start"]:
            rebuilt.append((note["start"], "on", note["pitch"], note["vel"], channel))
            rebuilt.append((note["end"], "off", note["pitch"], 0, channel))
    return sorted(rebuilt, key=lambda ev: (ev[0], 0 if ev[1] == "off" else 1))


def _cc_curve(events, channel, control, start_tick, duration, start_val, end_val, steps=8):
    for step in range(steps + 1):
        pct = step / float(max(1, steps))
        tick = start_tick + int(duration * pct)
        val = int(start_val + (end_val - start_val) * pct)
        _emit(events, tick, "cc", control, max(0, min(127, val)), channel)


def _build_progression(preset, bars):
    label, base = random.choice(preset["progressions"])
    if GENERATION_MODE == "decoupled":
        chords = list(SCALE_CHORDS[preset["scale"]].keys())
        result = []
        cur = "i"
        for bar in range(bars):
            result.append(cur)
            if bar % 4 == 3:
                cur = random.choice(["i", base[0]])
            else:
                cur = random.choice(chords)
        return label, result
    if len(base) >= bars:
        return label, base[:bars]
    return label, [base[i % len(base)] for i in range(bars)]


def _generate_bass(root_val, progression, scale_chords, tpb, tension, program, profile):
    events = [(0, "program", program, 0, 0)]
    previous = 40
    for bar, symbol in enumerate(progression):
        start = bar * 4 * tpb
        chord = scale_chords[symbol]
        root_pc = (root_val + chord[0]) % 12
        fifth_pc = (root_val + chord[-1]) % 12
        root = _pitch_for_pc(root_pc, 33, 52, previous)
        fifth = _pitch_for_pc(fifth_pc, 36, 55, root + 7)
        if abs(root - previous) > 12:
            root = _pitch_for_pc(root_pc, 33, 52, previous + (12 if root < previous else -12))
        if abs(fifth - root) > 12:
            fifth = _pitch_for_pc(fifth_pc, 36, 55, root)
        vel = 70 + int(tension * 22)
        bass_style = profile["bass"]
        if bass_style == "sparse":
            _add_note(events, start, root, 3 * tpb - 30, vel - 8, 0)
            if bar % 4 == 3:
                _add_note(events, start + int(3.5 * tpb), fifth, int(0.45 * tpb), vel - 18, 0)
                previous = fifth
            else:
                previous = root
        elif bass_style == "tresillo":
            for beat, pitch, dur in [(0.0, root, 0.7), (0.75, root, 0.55), (1.5, fifth, 0.65), (2.5, root, 1.2)]:
                _add_note(events, start + int(beat * tpb), pitch, int(dur * tpb), vel - (4 if beat else 0), 0)
            previous = root
        elif bass_style == "aksak":
            for beat, pitch, dur in [(0.0, root, 0.65), (0.75, fifth, 0.55), (1.5, root, 0.8), (2.5, fifth, 0.55), (3.25, root, 0.55)]:
                _add_note(events, start + int(beat * tpb), pitch, int(dur * tpb), vel, 0)
            previous = root
        elif bass_style == "pedal":
            _add_note(events, start, root, 4 * tpb - 30, vel, 0)
            if bar % 2 == 1:
                _add_note(events, start + int(3.5 * tpb), _pitch_for_pc((root_pc - 1) % 12, 33, 52, root), int(0.35 * tpb), vel - 16, 0)
            previous = root
        else:
            _add_note(events, start, root, 2 * tpb - 20, vel, 0)
            _add_note(events, start + 2 * tpb, fifth, 2 * tpb - 20, vel - 8, 0)
            previous = fifth
    return events


def _generate_pad(root_val, progression, scale_chords, tpb, tension, program):
    events = [(0, "program", program, 0, 3)]
    prev = None
    for bar, symbol in enumerate(progression):
        start = bar * 4 * tpb
        chord = scale_chords[symbol]
        notes = _voicing(root_val, chord, 48, 78)
        if prev:
            notes = sorted(notes, key=lambda n: min(abs(n - p) for p in prev))[:4]
        prev = notes
        for note in sorted(notes)[:4]:
            _add_note(events, start, note, 4 * tpb - 32, 48 + int(tension * 18), 3)
        _cc_curve(events, 3, 11, start, 4 * tpb, 54, 88, steps=6)
    return events


def _tokyo_hook_pitch(root_val, chord, scale, previous, role, phrase_floor):
    chord_notes = _chord_pitches(root_val, chord, SHAKUHACHI_LOW, SHAKUHACHI_HIGH)
    scale_notes = _scale_pitches(root_val, scale, SHAKUHACHI_LOW, SHAKUHACHI_HIGH)
    if not chord_notes:
        chord_notes = scale_notes
    if previous is None:
        previous = _nearest_chord_tone(root_val, chord, SHAKUHACHI_LOW, SHAKUHACHI_HIGH, phrase_floor)

    near_chord = sorted(_constrain_leap(chord_notes, previous, max_leap=8))
    near_scale = sorted(_constrain_leap(scale_notes, previous, max_leap=5))

    if role == "root":
        root_pc = (root_val + chord[0]) % 12
        pool = [p for p in chord_notes if p % 12 == root_pc] or near_chord
        pitch = _nearest_pitch(pool, previous)
    elif role == "upper":
        above = [p for p in near_chord if p > previous]
        pitch = _nearest_pitch(above or near_chord, previous + 5)
    elif role == "lower":
        below = [p for p in near_chord if p < previous]
        pitch = _nearest_pitch(below or near_chord, previous - 5)
    elif role == "neighbor_up":
        pitch = _neighbor_tone(root_val, scale, SHAKUHACHI_LOW, SHAKUHACHI_HIGH, previous, direction=1)
    elif role == "neighbor_down":
        pitch = _neighbor_tone(root_val, scale, SHAKUHACHI_LOW, SHAKUHACHI_HIGH, previous, direction=-1)
    else:
        pitch = _nearest_pitch(near_chord or chord_notes, previous + random.choice([-5, 5]))

    if pitch == previous and len(near_chord) > 1:
        alternatives = [p for p in near_chord if p != previous]
        pitch = _nearest_pitch(alternatives, previous + random.choice([-5, 5]))
    if abs(pitch - previous) > 8:
        pitch = _nearest_pitch(near_scale or scale_notes, previous)
    return pitch


def _generate_tokyo_lead(root_val, progression, scale_chords, scale, tpb, tension, program, avoid_events=None, avoid_channel=2):
    events = [(0, "program", program, 0, 1)]
    avoid_notes = _notes_from_events(avoid_events or [], avoid_channel)
    phrase_templates = [
        [
            [(0.0, "root", 1.65), (3.5, "upper", 0.35)],
            [(0.0, "root", 1.1), (2.0, "lower", 0.9)],
            [(0.0, "upper", 1.35), (2.0, "root", 0.8)],
            [(0.5, "lower", 0.8), (2.0, "root", 1.25)],
        ],
        [
            [(0.0, "upper", 1.45)],
            [(0.0, "root", 1.1), (3.0, "neighbor_down", 0.38)],
            [(0.0, "lower", 1.25), (2.0, "root", 0.75)],
            [(0.0, "root", 1.75), (3.5, "upper", 0.32)],
        ],
        [
            [(0.0, "root", 1.2), (2.0, "upper", 0.7)],
            [(0.5, "lower", 1.0)],
            [(0.0, "root", 1.5), (3.0, "neighbor_up", 0.35)],
            [(0.0, "upper", 0.9), (2.0, "root", 1.0)],
        ],
    ]
    phrase_floor = root_val + 12
    current = None
    phrase_template = random.choice(phrase_templates)

    for bar, symbol in enumerate(progression):
        start = bar * 4 * tpb
        chord = scale_chords[symbol]
        if bar % 4 == 0 and bar:
            phrase_template = random.choice(phrase_templates)
        phrase = sorted(phrase_template[bar % 4])
        if bar % 4 == 2 and random.random() < 0.35:
            phrase = [(beat, "root" if role.startswith("neighbor") else role, dur) for beat, role, dur in phrase]

        for idx, (beat, role, dur_beats) in enumerate(phrase):
            tick = start + int(beat * tpb)
            dur_ticks = int(dur_beats * tpb)
            pitch = _tokyo_hook_pitch(root_val, chord, scale, current, role, phrase_floor)
            chord_notes = _chord_pitches(root_val, chord, SHAKUHACHI_LOW, SHAKUHACHI_HIGH)
            if idx in (0, len(phrase) - 1):
                pitch = _choose_against_events(
                    _constrain_leap(chord_notes or [pitch], current or pitch, max_leap=8),
                    avoid_notes, tick, dur_ticks, current,
                ) or pitch
            elif _attack_near(avoid_events or [], tick, avoid_channel, window=80):
                tick += int(0.18 * tpb)
                dur_ticks = max(int(0.22 * tpb), dur_ticks - int(0.18 * tpb))

            _add_note(events, tick, pitch, dur_ticks, 74 + int(tension * 23), 1)
            if dur_beats >= 0.72:
                _cc_curve(events, 1, 11, tick, dur_ticks, 46, 94, steps=5)
            current = pitch

        if bar % 4 == 3:
            current = _nearest_chord_tone(
                root_val, chord, SHAKUHACHI_LOW, SHAKUHACHI_HIGH,
                current if current is not None else phrase_floor,
            )

    return events


def _generate_tokyo_koto(root_val, progression, scale_chords, scale, tpb, tension, program):
    events = [(0, "program", program, 0, 2)]
    phrase_templates = [
        [
            [(0.0, 0, "pick"), (2.0, 1, "pick")],
            [(0.0, 0, "pick"), (3.5, 1, "pickup")],
            [(0.0, 2, "tremolo"), (2.0, 1, "pick")],
            [(0.0, 0, "pick"), (1.5, 1, "pick"), (3.0, 0, "pick")],
        ],
        [
            [(0.0, 0, "pick"), (0.5, 1, "pickup"), (2.0, 0, "pick")],
            [(0.0, 1, "pick"), (2.0, 2, "pick")],
            [(0.0, 0, "pick"), (3.0, 1, "pickup"), (3.5, 0, "pickup")],
            [(0.0, 0, "tremolo"), (2.0, 1, "pick")],
        ],
        [
            [(0.0, 1, "pick"), (2.0, 0, "pick")],
            [(0.0, 0, "pick"), (1.5, 1, "pick"), (3.5, 0, "pickup")],
            [(0.0, 2, "pick"), (2.0, 1, "pick")],
            [(0.0, 0, "pick"), (2.5, 1, "tremolo")],
        ],
        [
            [(0.0, 0, "pick")],
            [(0.0, 1, "pick"), (2.0, 0, "pick")],
            [(0.0, 2, "pick"), (1.0, 1, "pickup"), (2.0, 0, "pick")],
            [(0.0, 0, "pick"), (3.0, 1, "pickup"), (3.5, 0, "pickup")],
        ],
    ]
    previous = None
    phrase_template = random.choice(phrase_templates)
    motif_rotation = random.choice([0, 0, 1, -1])
    for bar, symbol in enumerate(progression):
        start = bar * 4 * tpb
        chord = scale_chords[symbol]
        chord_notes = _chord_pitches(root_val, chord, KOTO_HOOK_LOW, KOTO_HOOK_HIGH)
        scale_notes = _scale_pitches(root_val, scale, KOTO_HOOK_LOW, KOTO_HOOK_HIGH)
        if not chord_notes:
            chord_notes = scale_notes
        center = previous if previous is not None else root_val + 7
        anchor = _nearest_chord_tone(root_val, chord, KOTO_HOOK_LOW, KOTO_HOOK_HIGH, center)
        compact = sorted(_constrain_leap(chord_notes, anchor, max_leap=7))
        if len(compact) < 3:
            compact = sorted(_constrain_leap(chord_notes, anchor, max_leap=12))
        if not compact:
            compact = [anchor]
        compact = sorted(compact, key=lambda pitch: (abs(pitch - anchor), pitch))[:4]
        compact = sorted(compact)
        pattern = phrase_template[bar % 4]
        if bar % 4 == 2 and random.random() < 0.45:
            pattern = [(beat, (degree + motif_rotation) % max(1, len(compact)), gesture) for beat, degree, gesture in pattern]

        for idx, (beat, degree, gesture) in enumerate(pattern):
            if gesture == "tremolo" and not (bar % 4 in (2, 3) and random.random() < 0.55):
                gesture = "pick"
            degree = degree % len(compact)
            pitch = compact[degree]
            if previous is not None:
                close_pool = [p for p in compact if abs(p - previous) <= 7 and abs(p - previous) != 1]
                pitch = _nearest_pitch(close_pool or compact, pitch)

            if previous is not None and abs(pitch - previous) > 7:
                pitch = _nearest_pitch(_constrain_leap(compact, previous, max_leap=7) or compact, previous)
            if previous is not None and abs(pitch - previous) == 1:
                alternatives = [p for p in chord_notes if abs(p - previous) not in (0, 1)]
                pitch = _nearest_pitch(alternatives or chord_notes, previous)
            if gesture == "pick" and idx == 1 and random.random() < 0.10:
                neighbor = _neighbor_tone(root_val, scale, KOTO_HOOK_LOW, KOTO_HOOK_HIGH, pitch)
                if (
                    neighbor in scale_notes
                    and abs(neighbor - pitch) <= 5
                    and (previous is None or abs(neighbor - previous) not in (1, 11))
                    and neighbor % 12 in {(root_val + offset) % 12 for offset in chord}
                ):
                    pitch = neighbor

            dur_beats = random.choice([0.28, 0.34, 0.42])
            if gesture == "tremolo":
                dur_beats = random.choice([0.58, 0.68, 0.78])
            elif gesture == "pickup":
                dur_beats = random.choice([0.16, 0.22, 0.28])
            elif idx == 0:
                dur_beats = random.choice([0.5, 0.65])
            vel = 61 + int(tension * 25) - (3 if idx in (1, 3) else 0)
            tick = start + int(beat * tpb)
            if gesture == "tremolo":
                _add_koto_tremolo(events, tick, pitch, int(dur_beats * tpb), vel - 4, 2)
            else:
                _add_note(events, tick, pitch, int(dur_beats * tpb), vel, 2)
            previous = pitch

    return _trim_halfstep_overlaps(events, 2)


def _compact_chord_notes(root_val, chord, scale, lo, hi, center, max_leap=8):
    chord_notes = _chord_pitches(root_val, chord, lo, hi)
    scale_notes = _scale_pitches(root_val, scale, lo, hi)
    if not chord_notes:
        chord_notes = scale_notes
    anchor = _nearest_chord_tone(root_val, chord, lo, hi, center)
    compact = sorted(_constrain_leap(chord_notes, anchor, max_leap=max_leap))
    if len(compact) < 2:
        compact = sorted(_constrain_leap(chord_notes, anchor, max_leap=max_leap + 5))
    compact = sorted(compact or [anchor], key=lambda pitch: (abs(pitch - anchor), pitch))[:4]
    return sorted(compact), scale_notes


def _emit_regional_gesture(events, tick, pitch, dur_ticks, velocity, channel, gesture):
    if gesture in ("tremolo", "roll"):
        _add_koto_tremolo(events, tick, pitch, dur_ticks, velocity, channel)
    elif gesture == "grace":
        grace = pitch - 1 if pitch > 0 else pitch
        _add_note(events, tick, grace, max(28, dur_ticks // 4), max(32, velocity - 18), channel)
        _add_note(events, tick + max(36, dur_ticks // 5), pitch, max(40, dur_ticks - max(36, dur_ticks // 5)), velocity, channel)
    else:
        _add_note(events, tick, pitch, dur_ticks, velocity, channel)


def _generate_regional_ostinato(root_val, progression, scale_chords, scale, tpb, tension, program, profile):
    events = [(0, "program", program, 0, 2)]
    emotion = profile["emotion"]
    settings = {
        "bend": {
            "range": (55, 78),
            "templates": [
                [[(0.0, 0, "pick"), (0.5, 1, "pick"), (2.0, 0, "roll")],
                 [(0.0, 0, "pick"), (1.5, 1, "pick"), (3.5, 0, "pickup")],
                 [(0.0, 2, "pick"), (2.0, 1, "roll")],
                 [(0.0, 0, "pick"), (3.0, 1, "pickup"), (3.5, 0, "pickup")]],
                [[(0.0, 0, "roll"), (2.0, 1, "pick")],
                 [(0.0, 1, "pick"), (2.0, 0, "pick")],
                 [(0.0, 0, "pick"), (1.0, 2, "pickup"), (2.0, 1, "pick")],
                 [(0.0, 0, "pick"), (2.5, 1, "roll")]],
            ],
        },
        "maqam": {
            "range": (50, 73),
            "templates": [
                [[(0.0, 0, "tremolo"), (2.0, 1, "pick")],
                 [(0.0, 0, "pick"), (1.5, 1, "grace"), (3.0, 0, "pick")],
                 [(0.0, 2, "pick"), (2.0, 1, "tremolo")],
                 [(0.0, 0, "pick"), (3.5, 1, "pickup")]],
                [[(0.0, 0, "pick"), (0.75, 1, "grace"), (2.0, 0, "pick")],
                 [(0.0, 1, "tremolo"), (2.5, 0, "pick")],
                 [(0.0, 0, "pick"), (1.5, 2, "pick"), (3.0, 1, "pickup")],
                 [(0.0, 0, "tremolo"), (2.0, 1, "pick")]],
            ],
        },
        "sweet": {
            "range": (55, 76),
            "templates": [
                [[(0.0, 0, "pick"), (0.75, 1, "pick"), (1.5, 0, "pick"), (2.75, 1, "pick")],
                 [(0.0, 0, "pick"), (1.5, 1, "pick"), (2.75, 0, "pick")],
                 [(0.0, 2, "pick"), (0.75, 1, "pick"), (2.0, 0, "pick")],
                 [(0.0, 0, "pick"), (2.5, 1, "pick"), (3.5, 0, "pickup")]],
                [[(0.0, 0, "pick"), (1.5, 1, "pick"), (2.5, 0, "pick")],
                 [(0.0, 1, "pick"), (0.75, 0, "pick"), (2.75, 2, "pick")],
                 [(0.0, 0, "pick"), (2.0, 1, "pick")],
                 [(0.0, 0, "pick"), (1.5, 2, "pick"), (2.75, 1, "pick")]],
            ],
        },
        "fire": {
            "range": (53, 76),
            "templates": [
                [[(0.0, 0, "stab"), (1.5, 1, "stab"), (2.5, 0, "stab")],
                 [(0.0, 0, "stab"), (0.75, 1, "pickup"), (2.0, 2, "stab")],
                 [(0.0, 1, "stab"), (1.25, 0, "pickup"), (2.5, 1, "stab"), (3.25, 0, "pickup")],
                 [(0.0, 0, "stab"), (1.5, 2, "stab"), (3.0, 1, "pickup")]],
                [[(0.0, 0, "stab"), (0.5, 1, "pickup"), (1.5, 0, "stab"), (2.75, 2, "pickup")],
                 [(0.0, 1, "stab"), (2.0, 0, "stab")],
                 [(0.0, 2, "stab"), (1.5, 1, "pickup"), (2.5, 0, "stab")],
                 [(0.0, 0, "stab"), (2.0, 1, "stab"), (3.25, 0, "pickup")]],
            ],
        },
    }[emotion]
    lo, hi = settings["range"]
    template = random.choice(settings["templates"])
    rotation = random.choice([0, 0, 1, -1])
    previous = None
    for bar, symbol in enumerate(progression):
        start = bar * 4 * tpb
        chord = scale_chords[symbol]
        center = previous if previous is not None else lo + 12
        compact, scale_notes = _compact_chord_notes(root_val, chord, scale, lo, hi, center, max_leap=7)
        pattern = template[bar % 4]
        if bar % 4 == 2 and random.random() < 0.45:
            pattern = [(beat, (degree + rotation) % len(compact), gesture) for beat, degree, gesture in pattern]
        for idx, (beat, degree, gesture) in enumerate(pattern):
            degree = degree % len(compact)
            pitch = compact[degree]
            if previous is not None:
                pool = [p for p in compact if abs(p - previous) <= (8 if emotion == "fire" else 7)]
                pitch = _nearest_pitch(pool or compact, pitch)
            if previous is not None and abs(pitch - previous) == 1:
                alternatives = [p for p in compact if abs(p - previous) not in (0, 1)]
                pitch = _nearest_pitch(alternatives or compact, previous)
            if gesture == "pickup":
                dur = random.choice([0.16, 0.22, 0.28])
            elif gesture in ("tremolo", "roll"):
                dur = random.choice([0.55, 0.68, 0.82])
            elif gesture == "stab":
                dur = random.choice([0.24, 0.32, 0.42])
            else:
                dur = random.choice([0.34, 0.45, 0.58])
            vel = 58 + int(tension * 24) + (8 if idx == 0 else 0)
            tick = start + int(beat * tpb)
            _emit_regional_gesture(events, tick, pitch, int(dur * tpb), vel, 2, gesture)
            previous = pitch
    return _trim_halfstep_overlaps(events, 2)


def _generate_regional_lead(root_val, progression, scale_chords, scale, tpb, tension, program, profile, avoid_events=None, avoid_channel=2):
    events = [(0, "program", program, 0, 1)]
    emotion = profile["emotion"]
    lanes = {
        "bend": (60, 84),
        "maqam": (58, 82),
        "sweet": (60, 81),
        "fire": (60, 84),
    }
    templates = {
        "bend": [
            [[(0.0, 0, 1.8), (3.5, 1, 0.32)], [(0.0, 1, 1.2), (2.0, 0, 0.9)], [(0.0, 2, 1.4), (2.0, 1, 0.75)], [(0.5, 0, 1.5)]],
            [[(0.0, 1, 1.5)], [(0.0, 0, 1.0), (3.0, 1, 0.4)], [(0.0, 2, 1.2), (2.0, 0, 0.85)], [(0.0, 0, 1.8), (3.5, 1, 0.3)]],
        ],
        "maqam": [
            [[(0.0, 0, 1.65), (2.5, 1, 0.45)], [(0.0, 1, 1.1), (1.5, 0, 0.65)], [(0.0, 2, 1.35), (2.0, 1, 0.8)], [(0.0, 0, 1.8)]],
            [[(0.5, 0, 1.2)], [(0.0, 1, 1.3), (3.0, 0, 0.36)], [(0.0, 2, 1.0), (1.5, 1, 0.55)], [(0.0, 0, 1.7), (2.75, 1, 0.45)]],
        ],
        "sweet": [
            [[(0.0, 0, 1.0), (1.5, 1, 0.55), (2.75, 0, 0.7)], [(0.0, 0, 1.4)], [(0.75, 1, 0.9), (2.5, 0, 0.7)], [(0.0, 0, 1.2), (3.0, 1, 0.42)]],
            [[(0.0, 1, 1.0), (2.0, 0, 0.7)], [(0.5, 0, 1.2), (2.75, 1, 0.45)], [(0.0, 2, 0.9), (1.5, 1, 0.55)], [(0.0, 0, 1.6)]],
        ],
        "fire": [
            [[(0.0, 0, 0.48), (0.75, 1, 0.28), (1.5, 2, 0.42), (2.5, 1, 0.32)], [(0.0, 0, 0.7), (2.0, 1, 0.48), (3.25, 0, 0.28)], [(0.0, 2, 0.55), (1.25, 1, 0.32), (2.5, 0, 0.52)], [(0.0, 0, 0.8), (1.5, 2, 0.42), (3.0, 1, 0.32)]],
            [[(0.0, 1, 0.5), (0.5, 2, 0.24), (1.5, 0, 0.5)], [(0.0, 0, 0.75), (2.5, 1, 0.4)], [(0.0, 2, 0.5), (1.5, 1, 0.34), (3.25, 0, 0.28)], [(0.0, 0, 0.65), (2.0, 1, 0.42)]],
        ],
    }
    lo, hi = lanes[emotion]
    template = random.choice(templates[emotion])
    avoid_notes = _notes_from_events(avoid_events or [], avoid_channel)
    current = _nearest_scale_tone(root_val, scale, lo, hi, root_val + 12)
    for bar, symbol in enumerate(progression):
        start = bar * 4 * tpb
        chord = scale_chords[symbol]
        compact, scale_notes = _compact_chord_notes(root_val, chord, scale, lo, hi, current, max_leap=8)
        phrase = template[bar % 4]
        for idx, (beat, degree, dur) in enumerate(phrase):
            degree = degree % len(compact)
            tick = start + int(beat * tpb)
            pitch = compact[degree]
            if current is not None:
                pitch = _nearest_pitch(_constrain_leap(compact, current, max_leap=8) or compact, pitch)
            pitch = _choose_against_events([pitch], avoid_notes, tick, int(dur * tpb), current) or pitch
            _add_note(events, tick, pitch, int(dur * tpb), 72 + int(tension * 24), 1)
            if emotion in ("bend", "maqam") and dur >= 0.9:
                _cc_curve(events, 1, 11, tick, int(dur * tpb), 42, 96, steps=6)
                ornament = _neighbor_tone(root_val, scale, lo, hi, pitch, direction=random.choice([-1, 1]))
                if abs(ornament - pitch) <= 3 and not _attack_near(avoid_events or [], tick + int(0.16 * tpb), avoid_channel, window=60):
                    _add_note(events, tick + int(0.16 * tpb), ornament, int(0.12 * tpb), 48 + int(tension * 18), 1)
            elif emotion == "fire" and random.random() < 0.22:
                ornament = _neighbor_tone(root_val, scale, lo, hi, pitch)
                _add_note(events, tick + int(0.12 * tpb), ornament, int(0.1 * tpb), 52 + int(tension * 18), 1)
            current = pitch
    return events


def _generate_ostinato(root_val, progression, scale_chords, scale, tpb, tension, program, profile):
    events = [(0, "program", program, 0, 2)]
    if profile["emotion"] == "space":
        return _generate_tokyo_koto(root_val, progression, scale_chords, scale, tpb, tension, program)
    if profile["emotion"] in ("bend", "maqam", "sweet", "fire"):
        return _generate_regional_ostinato(root_val, progression, scale_chords, scale, tpb, tension, program, profile)
    register_by_emotion = {
        "space": (62, 82),
        "bend": (58, 78),
        "maqam": (52, 74),
        "fire": (55, 76),
        "sweet": (57, 77),
        "cry": (50, 74),
    }
    lo, hi = register_by_emotion.get(profile["emotion"], (52, 76))
    previous = None
    for bar, symbol in enumerate(progression):
        start = bar * 4 * tpb
        chord = scale_chords[symbol]
        lead_bars = profile.get("lead_bars", set())
        is_response_bar = profile["emotion"] == "cry" and bar in lead_bars
        if profile["emotion"] == "cry":
            voicing = _guitar_chord_voicing(root_val, chord, scale)
            if is_response_bar:
                support = [note for note in voicing if GUITAR_LOW <= note <= 55] or voicing[:1]
                pitch = support[0]
                _add_note(events, start, pitch, int(0.35 * tpb), 48 + int(tension * 16), 2)
                previous = pitch
                continue

            pattern_name = random.choice(["roll_8th", "malaguena", "rasgueado", "triplet"])
            if pattern_name == "roll_8th":
                pattern = [(0.0, 0, 0.95), (0.5, 1, 0.65), (1.0, 2, 0.65), (1.5, 3, 0.7),
                           (2.0, 0, 0.95), (2.5, 2, 0.65), (3.0, 3, 0.65), (3.5, 1, 0.65)]
            elif pattern_name == "malaguena":
                pattern = [(0.0, 0, 1.35), (0.5, 2, 0.5), (1.0, 3, 0.7),
                           (2.0, 0, 1.35), (2.5, 1, 0.5), (3.0, 4, 0.7)]
            elif pattern_name == "triplet":
                pattern = [(0.0, 0, 0.55), (0.33, 1, 0.45), (0.67, 2, 0.45),
                           (1.5, 3, 0.45), (2.0, 0, 0.55), (2.33, 2, 0.45),
                           (2.67, 3, 0.45), (3.5, 1, 0.45)]
            else:
                pattern = [(0.0, 0, 1.6), (0.04, 1, 1.55), (0.08, 2, 1.5), (0.12, 3, 1.45),
                           (2.0, 0, 1.4), (2.04, 2, 1.35), (2.08, 3, 1.3)]

            for idx, (beat, voice_idx, dur) in enumerate(pattern):
                note = voicing[voice_idx % len(voicing)]
                if not (GUITAR_LOW <= note <= GUITAR_RASGUEO_HIGH):
                    candidates = [n for n in voicing if GUITAR_LOW <= n <= GUITAR_RASGUEO_HIGH]
                    note = candidates[voice_idx % len(candidates)] if candidates else _nearest_scale_tone(root_val, scale, GUITAR_LOW, GUITAR_RASGUEO_HIGH, note)
                if pattern_name != "rasgueado" and idx + 1 < len(pattern):
                    next_beat = pattern[idx + 1][0]
                    dur = min(dur, max(0.16, next_beat - beat - 0.04))
                vel = 58 + int(tension * 24) + (8 if voice_idx == 0 else 0) - min(voice_idx, 4)
                _add_note(events, start + int(beat * tpb), note, int(dur * tpb), vel, 2)
                previous = note
            continue
        else:
            local_lo, local_hi = (lo, hi)
            chord_notes = _chord_pitches(root_val, chord, local_lo, local_hi)
        scale_notes = _scale_pitches(root_val, scale, local_lo, local_hi)
        if not chord_notes:
            chord_notes = scale_notes
        pattern = [0.0] if is_response_bar else random.choice(profile["pluck_grid"])
        chord_anchor = _nearest_chord_tone(root_val, chord, local_lo, local_hi, previous if previous is not None else local_lo + 12)
        chord_notes = sorted(_constrain_leap(chord_notes, chord_anchor, max_leap=12))
        seq = chord_notes + list(reversed(chord_notes[1:-1] or chord_notes))
        for idx, beat in enumerate(pattern):
            is_strong = abs(beat - round(beat)) < 0.02 or idx == 0
            if is_strong:
                target = chord_anchor if idx == 0 else seq[idx % len(seq)]
                pitch = _nearest_chord_tone(root_val, chord, local_lo, local_hi, target)
            elif random.random() < 0.28 and previous is not None:
                pitch = _neighbor_tone(root_val, scale, local_lo, local_hi, previous)
            else:
                pitch = seq[idx % len(seq)] if seq else chord_anchor
            if previous is not None and abs(pitch - previous) > 12:
                pitch = _nearest_pitch(chord_notes or scale_notes, previous)
            dur = 0.35 if is_response_bar else (0.18 if profile["emotion"] in ("fire", "maqam") else 0.42)
            if profile["emotion"] == "space":
                dur = random.choice([0.35, 0.7, 1.1])
            vel = 48 + int(tension * 16) if is_response_bar else 62 + int(tension * 26)
            _add_note(events, start + int(beat * tpb), pitch, int(dur * tpb), vel, 2)
            previous = pitch
            if not is_response_bar and profile["emotion"] in ("cry", "maqam") and random.random() < 0.18:
                grace = _neighbor_tone(root_val, scale, local_lo, local_hi, pitch)
                _add_note(events, start + int((beat + 0.12) * tpb), grace, int(0.12 * tpb), 48 + int(tension * 18), 2)
    return events


def _generate_lead(root_val, progression, scale_chords, scale, tpb, tension, program, profile, avoid_events=None, avoid_channel=2):
    events = [(0, "program", program, 0, 1)]
    if profile["emotion"] == "space":
        return _generate_tokyo_lead(
            root_val, progression, scale_chords, scale, tpb, tension,
            program, avoid_events=avoid_events, avoid_channel=avoid_channel,
        )
    if profile["emotion"] in ("bend", "maqam", "sweet", "fire"):
        return _generate_regional_lead(
            root_val, progression, scale_chords, scale, tpb, tension,
            program, profile, avoid_events=avoid_events, avoid_channel=avoid_channel,
        )
    lead_lanes = {
        "space": (62, 86),
        "bend": (62, 90),
        "maqam": (60, 84),
        "fire": (62, 88),
        "sweet": (60, 82),
        "cry": (GUITAR_PICADO_LOW, GUITAR_PICADO_HIGH),
    }
    lo, hi = lead_lanes.get(profile["emotion"], (60, 86))
    scale_notes = _scale_pitches(root_val, scale, lo, hi)
    root_anchor = _nearest_scale_tone(root_val, scale, lo, hi, root_val + 12)
    current = root_anchor
    motif_contours = {
        "space": [0, 2, -1, 0],
        "bend": [0, 1, 3, 1, 0],
        "maqam": [0, 1, -1, 2, -1, 0],
        "fire": [0, 2, 4, 1, -1, 0],
        "sweet": [0, -1, 1, 0, -2],
        "cry": [0, 2, -1, -2, 0],
    }
    contour = motif_contours.get(profile["emotion"], [0, 1, -1, 0])
    avoid_events = avoid_events or []
    avoid_notes = _notes_from_events(avoid_events, avoid_channel)
    active_lead_bars = profile.get("lead_bars")
    for bar, symbol in enumerate(progression):
        if active_lead_bars is not None and bar not in active_lead_bars:
            continue
        start = bar * 4 * tpb
        chord = scale_chords[symbol]
        chord_notes = _chord_pitches(root_val, chord, lo, hi)
        if not chord_notes:
            chord_notes = scale_notes
        if profile["emotion"] == "cry":
            phrase_start = start + int(0.5 * tpb)
            phrase_dur = int(2.65 * tpb)
            target = _nearest_chord_tone(root_val, chord, lo, hi, current)
            target = _choose_against_events(chord_notes, avoid_notes, phrase_start, phrase_dur, current) or target
            if bar % 4 == 3:
                rootish = [p for p in chord_notes if p % 12 == (root_val + chord[0]) % 12]
                if rootish:
                    target = _choose_against_events(rootish, avoid_notes, phrase_start, phrase_dur, current) or target

            phrase_type = "tremolo" if bar % 4 in (2, 3) and random.random() < 0.65 else "picado_answer"
            if phrase_type == "tremolo":
                _add_tremolo_note(events, phrase_start, target, phrase_dur, 76 + int(tension * 22), 1, repeats_per_beat=5)
                _cc_curve(events, 1, 11, phrase_start, phrase_dur, 45, 102, steps=7)
            else:
                tones = sorted(_constrain_leap(chord_notes, current, max_leap=9))
                if not tones:
                    tones = chord_notes
                shape = random.choice([
                    [(0.55, 0, 0.55), (1.25, 1, 0.45), (2.35, 0, 0.85)],
                    [(0.75, 0, 0.7), (1.65, 1, 0.45), (2.65, 2, 0.55)],
                    [(0.50, 1, 0.55), (1.50, 0, 0.75), (2.75, 0, 0.55)],
                ])
                for beat, tone_idx, dur in shape:
                    tick = start + int(beat * tpb)
                    candidates = [tones[tone_idx % len(tones)]]
                    pitch = _choose_against_events(candidates, avoid_notes, tick, int(dur * tpb), current) or candidates[0]
                    _add_note(events, tick, pitch, int(dur * tpb), 72 + int(tension * 22), 1)
                    current = pitch
            current = target
            continue
        if bar % 4 == 0 or profile["emotion"] == "space":
            target = _nearest_chord_tone(root_val, chord, lo, hi, current)
            hold = 2.75 if profile["emotion"] == "space" else 1.85
            if profile["emotion"] == "cry":
                hold = 1.25
                target = _choose_against_events(chord_notes, avoid_notes, start + int(0.5 * tpb), int(hold * tpb), current) or target
                start_offset = int(0.5 * tpb)
            else:
                start_offset = 0
            _add_note(events, start + start_offset, target, int(hold * tpb), 82 + int(tension * 20), 1)
            _cc_curve(events, 1, 11, start + start_offset, int(hold * tpb), 44, 96, steps=5)
            if tension > 0.55 and profile["emotion"] != "space":
                grace = _neighbor_tone(root_val, scale, lo, hi, target, direction=-1)
                grace_tick = start + int(2.25 * tpb)
                if not _attack_near(avoid_events, grace_tick, avoid_channel):
                    _add_note(events, grace_tick, grace, int(0.18 * tpb), 64, 1)
                resolve_tick = start + int(2.55 * tpb)
                resolve = _choose_against_events([target], avoid_notes, resolve_tick, int(0.9 * tpb), target) or target
                _add_note(events, resolve_tick, resolve, int(0.9 * tpb), 76 + int(tension * 18), 1)
            current = target
            continue
        grid = profile["lead_grid"]
        phrase_grid = sorted(set([g for g in grid if 0 <= g < 4.0]))
        if not phrase_grid or phrase_grid[0] != 0.0:
            phrase_grid = [0.0] + phrase_grid
        for idx, beat in enumerate(phrase_grid):
            next_beat = phrase_grid[idx + 1] if idx + 1 < len(phrase_grid) else 4.0
            dur = max(0.18, min(1.75, next_beat - beat))
            tick = start + int(beat * tpb)
            if profile["emotion"] == "cry" and _attack_near(avoid_events, tick, avoid_channel):
                tick += int(0.25 * tpb)
                dur = max(0.18, dur - 0.25)
            strong = idx == 0 or abs(beat - round(beat)) < 0.02 or beat >= 3.0
            if strong:
                contour_target = current + contour[idx % len(contour)] * 2
                target_pool = _constrain_leap(chord_notes, current, max_leap=9)
                pitch = _nearest_pitch(target_pool, contour_target)
            elif random.random() < 0.65:
                direction = 1 if contour[idx % len(contour)] >= 0 else -1
                pitch = _neighbor_tone(root_val, scale, lo, hi, current, direction=direction)
            else:
                pitch = _nearest_scale_tone(root_val, scale, lo, hi, current + random.choice([-4, -2, 2, 4]))
            if abs(pitch - current) > 9:
                pitch = _nearest_pitch(_constrain_leap(scale_notes, current, max_leap=9), pitch)
            if profile["emotion"] == "cry":
                candidates = _constrain_leap(chord_notes if strong else scale_notes, current, max_leap=9)
                pitch = _choose_against_events(candidates, avoid_notes, tick, int(dur * tpb * 0.82), current) or pitch
            _add_note(events, tick, pitch, int(dur * tpb * 0.82), 72 + int(tension * 24), 1)
            if profile["emotion"] in ("bend", "maqam", "cry") and dur >= 0.7:
                neighbor = _neighbor_tone(root_val, scale, lo, hi, pitch)
                ornament_tick = tick + int(0.12 * tpb)
                if not _attack_near(avoid_events, ornament_tick, avoid_channel, window=60):
                    _add_note(events, ornament_tick, neighbor, int(0.12 * tpb), 50 + int(tension * 18), 1)
            current = pitch
    return events


def _generate_counter(root_val, progression, scale_chords, scale, tpb, tension, program, profile):
    events = [(0, "program", program, 0, 4)]
    lo, hi = (55, 79) if profile["emotion"] != "space" else (62, 86)
    scale_notes = _scale_pitches(root_val, scale, lo, hi)
    previous = None
    if profile["emotion"] == "cry":
        lo, hi = 60, 81
        bar = 0
        phrase_index = 0
        while bar < len(progression):
            symbol = progression[bar]
            start = bar * 4 * tpb + random.randint(-12, 12)
            chord = scale_chords[symbol]
            chord_notes = _chord_pitches(root_val, chord, lo, hi)
            if not chord_notes:
                chord_notes = _scale_pitches(root_val, scale, lo, hi)
            preferred_degree = phrase_index % 3
            sorted_tones = sorted(chord_notes)
            preferred = sorted_tones[min(preferred_degree, len(sorted_tones) - 1)]
            if previous is not None:
                candidates = _constrain_leap(chord_notes, previous, max_leap=7)
                target = _nearest_pitch(candidates, preferred)
            else:
                target = preferred

            span_bars = random.choice([1, 1, 2])
            if bar + span_bars > len(progression):
                span_bars = len(progression) - bar
            dur_beats = random.choice([2.5, 3.0, 3.5]) if span_bars == 1 else random.choice([5.5, 6.5, 7.25])
            dur_ticks = int(min(dur_beats, span_bars * 4 - 0.2) * tpb)
            _add_note(events, start, target, dur_ticks, 58 + int(tension * 24), 4)
            _cc_curve(events, 4, 11, start, dur_ticks, 42, 96, steps=9)
            _cc_curve(events, 4, 1, start, dur_ticks, 35, 72, steps=7)
            previous = target
            bar += span_bars
            phrase_index += 1
        return events
    for bar, symbol in enumerate(progression):
        if bar % 2 == 0 and random.random() > 0.35 + tension * 0.25:
            continue
        start = bar * 4 * tpb
        chord = scale_chords[symbol]
        chord_notes = _chord_pitches(root_val, chord, lo, hi)
        if profile["emotion"] == "fire":
            hits = [0.75, 1.5, 2.5, 3.25]
        elif profile["emotion"] == "space":
            hits = random.choice([[1.5], [2.75], [0.75, 3.5]])
        elif profile["emotion"] == "sweet":
            hits = [0.75, 1.5, 2.75]
        else:
            hits = random.choice([[0.75, 2.75], [1.5, 3.5], [0.0, 2.0, 3.5]])
        for idx, beat in enumerate(hits):
            if idx == 0 or abs(beat - round(beat)) < 0.02 or random.random() < 0.72:
                target = previous if previous is not None else lo + 12
                pitch = _nearest_chord_tone(root_val, chord, lo, hi, target)
            else:
                pitch = _neighbor_tone(root_val, scale, lo, hi, previous if previous is not None else lo + 12)
            if previous is not None and abs(pitch - previous) > 9:
                pitch = _nearest_pitch(_constrain_leap(chord_notes or scale_notes, previous, max_leap=9), pitch)
            dur = 0.35 if profile["emotion"] in ("fire", "maqam") else 0.55
            _add_note(events, start + int(beat * tpb), pitch, int(dur * tpb), 58 + int(tension * 20), 4)
            previous = pitch
    return events


def _generate_percussion(bars, tpb, tension, profile):
    events = []
    for bar in range(bars):
        start = bar * 4 * tpb
        perc = profile["percussion"]
        if perc == "palmas":
            hits = [(0.0, 36, 90), (1.5, 39, 58), (2.0, 37, 62), (3.0, 39, 54), (3.5, 85, 48)]
        elif perc == "taiko":
            hits = [(0.0, 41, 92), (2.0, 45, 62), (3.5, 37, 42)]
        elif perc == "gong_drill":
            hits = [(0.0, 36, 86), (1.5, 42, 42), (2.0, 38, 68), (2.75, 42, 42), (3.5, 52, 48)]
        elif perc == "darbuka":
            hits = [(0.0, 36, 84), (0.5, 64, 52), (1.5, 64, 58), (2.0, 38, 70), (2.5, 64, 54), (3.5, 64, 62)]
        elif perc == "tresillo":
            hits = [(0.0, 36, 78), (0.75, 37, 46), (1.5, 38, 62), (2.5, 36, 70), (3.5, 39, 44)]
        else:
            hits = [(0.0, 36, 86), (0.75, 43, 54), (1.5, 38, 70), (2.5, 43, 56), (3.25, 38, 66)]
        for beat, note, vel in hits:
            _add_note(events, start + int(beat * tpb), note, 70, vel + int(tension * 18), 9)
        if tension > 0.75 and bar % 4 == 3:
            for step in range(4):
                _add_note(events, start + int((3.0 + step * 0.25) * tpb), 85, 55, 40 + step * 8, 9)
    return events


def _events_to_mid(tracks, names, bpm, tpb=480, loop_end_tick=None):
    mid = MidiFile()
    mid.ticks_per_beat = tpb
    for idx, events in enumerate(tracks):
        clamped = []
        for tick, kind, val1, val2, channel in events:
            tick = max(0, int(tick))
            if loop_end_tick is not None:
                if kind == "on" and tick >= loop_end_tick:
                    continue
                tick = min(tick, loop_end_tick)
            if kind in ("on", "off"):
                val1 = max(0, min(127, int(val1)))
                val2 = max(0, min(127, int(val2)))
            if kind == "cc":
                val1 = max(0, min(127, int(val1)))
                val2 = max(0, min(127, int(val2)))
            clamped.append((tick, kind, val1, val2, channel))

        clamped.sort(key=lambda ev: (ev[0], 0 if ev[1] in ("program", "tempo", "off") else 1))
        track = MidiTrack()
        track.append(MetaMessage("track_name", name=names[idx], time=0))
        if idx == 0:
            track.append(MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
        mid.tracks.append(track)

        last_tick = 0
        for tick, kind, val1, val2, channel in clamped:
            delta = max(0, tick - last_tick)
            last_tick = tick
            if kind == "program":
                track.append(Message("program_change", program=val1, channel=channel, time=delta))
            elif kind == "on":
                track.append(Message("note_on", note=val1, velocity=val2, channel=channel, time=delta))
            elif kind == "off":
                track.append(Message("note_off", note=val1, velocity=0, channel=channel, time=delta))
            elif kind == "cc":
                track.append(Message("control_change", control=val1, value=val2, channel=channel, time=delta))
        if loop_end_tick is not None:
            track.append(MetaMessage("end_of_track", time=max(0, loop_end_tick - last_tick)))
    return mid


def _project_title(preset):
    adjectives, nouns = preset["name_words"]
    return f"{random.choice(adjectives)}_{random.choice(nouns)}"


def compose_world(out_dir, preset, key_name, root_val, bpm, bars):
    tpb = 480
    scale_name = preset["scale"]
    scale = WORLD_SCALES[scale_name]
    scale_chords = SCALE_CHORDS[scale_name]
    profile = STYLE_PROFILES[preset["profile"]]
    progression_label, progression = _build_progression(preset, bars)
    loop_end = bars * 4 * tpb
    ostinato = _generate_ostinato(
        root_val, progression, scale_chords, scale, tpb, preset["tension"],
        profile["programs"][2], profile,
    )
    if preset["profile"] == "andalusian":
        ostinato = _sanitize_track_to_scale(
            ostinato, root_val, scale,
            {2: (GUITAR_LOW, GUITAR_RASGUEO_HIGH)},
        )
        ostinato = _trim_halfstep_overlaps(ostinato, 2)
    elif preset["profile"] == "tokyo":
        ostinato = _sanitize_track_to_scale(
            ostinato, root_val, scale,
            {2: (KOTO_LOW, KOTO_HIGH)},
        )
        ostinato = _trim_halfstep_overlaps(ostinato, 2)
    elif preset["profile"] in ("shanghai", "arabian", "latin", "balkan"):
        ost_ranges = {
            "shanghai": (55, 78),
            "arabian": (50, 73),
            "latin": (55, 76),
            "balkan": (53, 76),
        }
        ostinato = _sanitize_track_to_scale(
            ostinato, root_val, scale,
            {2: ost_ranges[preset["profile"]]},
        )
        ostinato = _trim_halfstep_overlaps(ostinato, 2)
    lead = _generate_lead(
        root_val, progression, scale_chords, scale, tpb, preset["tension"],
        profile["programs"][1], profile, avoid_events=ostinato, avoid_channel=2,
    )
    if preset["profile"] == "andalusian":
        lead = _sanitize_track_to_scale(
            lead, root_val, scale,
            {1: (GUITAR_PICADO_LOW, GUITAR_PICADO_HIGH)},
        )
    elif preset["profile"] == "tokyo":
        lead = _sanitize_track_to_scale(
            lead, root_val, scale,
            {1: (SHAKUHACHI_LOW, SHAKUHACHI_HIGH)},
        )
    elif preset["profile"] in ("shanghai", "arabian", "latin", "balkan"):
        lead_ranges = {
            "shanghai": (60, 84),
            "arabian": (58, 82),
            "latin": (60, 81),
            "balkan": (60, 84),
        }
        lead = _sanitize_track_to_scale(
            lead, root_val, scale,
            {1: lead_ranges[preset["profile"]]},
        )

    tracks = [
        _generate_bass(root_val, progression, scale_chords, tpb, preset["tension"], profile["programs"][0], profile),
        lead,
        ostinato,
        _generate_pad(root_val, progression, scale_chords, tpb, preset["tension"], profile["programs"][3]),
        _generate_counter(root_val, progression, scale_chords, scale, tpb, preset["tension"], profile["programs"][4], profile),
        _generate_percussion(bars, tpb, preset["tension"], profile),
    ]
    names = profile["names"]
    mid = _events_to_mid(tracks, names, bpm, tpb, loop_end_tick=loop_end)

    title = _project_title(preset)
    fname = (
        f"{title}__World_Composer_{_slug(preset['region'])}__"
        f"{_slug(progression_label)}__{key_name}_{_slug(scale_name.title())}__"
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
    print(f"  [STYLE]  {preset['region']}")
    print(f"  [PROG ]  {'-'.join(progression)}\n")
    return path, progression


def _select_preset():
    print("""
  Select World Composer Region / Style:
  ____________________________________________________________
    R  -> Random World Minor Style
""")
    for key in sorted(WORLD_PRESETS.keys(), key=int):
        preset = WORLD_PRESETS[key]
        scale_disp = preset["scale"].replace("_", " ").title()
        print(f"    {key}  ->  {preset['region']:<22} {preset['desc']:<45} [{scale_disp}]")
    print("  ____________________________________________________________")
    while True:
        choice = input("  --> ").strip().upper()
        if choice == "R" or choice == "":
            return random.choice(list(WORLD_PRESETS.values())).copy()
        if choice in WORLD_PRESETS:
            return WORLD_PRESETS[choice].copy()
        print(f"  Enter R or one of: {', '.join(sorted(WORLD_PRESETS.keys(), key=int))}")


def _select_key():
    print(f"\n  Select root key (Available: {' / '.join(sorted(ROOTS.keys()))}) or press Enter for random:")
    while True:
        key = input("  --> ").strip()
        if not key:
            key = random.choice(list(ROOTS.keys()))
        if key:
            key = key[0].upper() + key[1:]
        if key in ROOTS:
            return key, ROOTS[key]
        print("  Invalid key. Try C, D#, Eb, F#, Bb, etc.")


def _select_tempo(lo, hi):
    print(f"\n  Select BPM ({lo}-{hi}) or press Enter for style default:")
    value = input("  --> ").strip()
    if value.isdigit():
        return max(lo, min(hi, int(value)))
    return random.randint(lo, hi)


def _select_length():
    print("""
  Select Composition Length:
    1  -> 4 Bars
    2  -> 8 Bars
    3  -> 16 Bars
    R  -> Random
""")
    while True:
        choice = input("  --> ").strip().upper()
        if choice == "1":
            return 4
        if choice == "2" or choice == "":
            return 8
        if choice == "3":
            return 16
        if choice == "R":
            return random.choice([4, 8, 16])
        print("  Enter 1, 2, 3, or R.")


def main(out_dir="midi_files"):
    os.makedirs(out_dir, exist_ok=True)
    print("""
+--------------------------------------------------------------+
|                 W O R L D   C O M P O S E R                  |
|    Minor-scale Spanish / Asian / Oriental trap MIDI engine    |
|  Bass - Lead - Pluck - Pad - Counter - Percussion channels    |
+--------------------------------------------------------------+""")

    while True:
        preset = _select_preset()
        key_name, root_val = _select_key()
        bpm = _select_tempo(*preset["bpm_range"])
        bars = _select_length()

        _div()
        print(f"""
  World Composer Summary
    Style   : {preset['region']}
    Scale   : {preset['scale'].replace('_', ' ').title()}
    Key     : {key_name} Minor
    BPM     : {bpm}
    Length  : {bars} Bars
    Mode    : {GENERATION_MODE.upper()}
    Tension : {'#' * int(preset['tension'] * 10)}{'.' * (10 - int(preset['tension'] * 10))} {int(preset['tension'] * 100)}%
""")
        compose_world(out_dir, preset, key_name, root_val, bpm, bars)

        print("  [G] Generate again  [B] Back  [Q] Quit")
        sub = input("  --> ").strip().lower()
        if sub == "q":
            print("\n  Returning to ANIMA Workstation.\n")
            return
        if sub == "b":
            return


if __name__ == "__main__":
    main()
