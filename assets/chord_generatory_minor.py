"""
minor-chord-generatory.py  —  Orchestral Edition
Features:
  1. Generate minor chord progressions by mood (Markov melody + counter-melody)
  2. Load an existing MIDI file and generate melodies on top of it
"""

import mido, os, random, time, math, importlib.util
import sys as _sys

def _load(name, filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Pre-register so sibling modules can detect this load is in progress
    _sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Register ourselves before loading solo_performance_minor so that
# _adopt_minor_engine_progressions() detects the circular reference and skips.
_sys.modules.setdefault("solo_minor_engine_reference", None)
_solo = _load("solo_perf_minor_private", "solo_performance_minor.py")
_sys.modules.pop("solo_minor_engine_reference", None)  # clear sentinel after load

GENERATION_MODE = 'simple'
DEFAULT_BPM = 120

PROJECT_ADJECTIVES = [
    "Apex", "Infinite", "Midnight", "Titan", "Solar", "Gothic", "Ethereal", "Grim", "Silent",
    "Shadow", "Crimson", "Nebula", "Spectral", "Cosmic", "Lost", "Fallen", "Eternal", "Frozen",
    "Abyssal", "Radiant", "Iron", "Storm", "Phoenix", "Astral", "Mystic", "Ancient", "Vortex",
    "Obsidian", "Nocturne", "Velvet", "Ashen", "Cinder", "Hollow", "Distant", "Moonlit",
    "Cathedral", "Wounded", "Funeral", "Tarnished", "Winter", "Bloodless", "Raven", "Umbral",
    "Haunted", "Sable", "Fever", "Shattered", "Marble", "Waning", "Dusklit", "Feral",
    "Forsaken", "Charcoal", "Dread", "Grave", "Hushed", "Bleak", "Scarred", "Widowed",
    "Broken", "Sepulchral", "Buried", "Withered", "Veiled", "Mournful", "Blackened", "Doomed",
    "Cavernous", "Restless", "Frostbitten", "Eclipsed", "Trembling", "Hallowed", "Cursed", "Pale",
    "Sorrowing", "Wraithlike", "Drifting", "Ritual", "Duskbound", "Nocturnal", "Stygian", "Faded",
    "Ironclad", "Gloaming", "Tortured", "Severed", "Lunar", "Aching", "Funereal", "Drowned",
]
PROJECT_NOUNS = [
    "Ascent", "Requiem", "Odyssey", "Eclipse", "Horizon", "Empire", "Sanctuary", "Vanguard",
    "Echo", "Whisper", "Rift", "Conquest", "Genesis", "Destiny", "Void", "Valhalla", "Covenant",
    "Chronicle", "Legacy", "Bastion", "Rebirth", "Summit", "Oracle", "Wasteland", "Mirage",
    "Lament", "Catacomb", "Vigil", "Dirge", "Ashes", "Oath", "Citadel", "Elegy",
    "Sepulcher", "Pilgrimage", "Wound", "Procession", "Signal", "Ember", "Labyrinth", "Crown",
    "Monument", "Aftermath", "Cathedral", "Threshold", "Tomb", "Furnace", "Veil", "Dagger",
    "Ruin", "Grief", "Trial", "Exile", "Hollow", "Cairn", "Penance", "Funeral",
    "Scar", "Relic", "Cataclysm", "Nightfall", "Vow", "Remnant", "Descent", "Apparition",
    "Crypt", "Wraith", "Bells", "Confession", "Betrayal", "Wake", "Oblivion", "Hymn",
    "Burial", "Fever", "Silence", "Stormfront", "Dreadnought", "Abyss", "Rapture", "Gallows",
    "Coven", "Frost", "Memory", "Atonement", "Shroud", "Ravine", "Sorrow", "Gloaming",
]

# ── SCALES ──────────────────────────────────────────────────────────────────
SCALE_AEOLIAN  = [0, 2, 3, 5, 7, 8, 10]
SCALE_HARMONIC = [0, 2, 3, 5, 7, 8, 11]
SCALE_PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]
SCALE_DORIAN   = [0, 2, 3, 5, 7, 9, 10]

# Krumhansl-Schmuckler minor profile for key detection
KS_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

ROOT_NAMES = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']

roots = {'C':36,'C#':37,'D':38,'Eb':39,'E':40,'F':41,
         'F#':42,'G':43,'Ab':44,'A':45,'Bb':46,'B':47}

roman_numerals = {
    'i':    ([0,3,7],    SCALE_AEOLIAN),
    'i7':   ([0,3,7,10], SCALE_AEOLIAN),
    'iio':  ([2,5,8],    SCALE_AEOLIAN),
    'bII':  ([1,5,8],    SCALE_PHRYGIAN),
    'III':  ([3,7,10],   SCALE_AEOLIAN),
    'iv':   ([5,8,12],   SCALE_AEOLIAN),
    'IV':   ([5,9,12],   SCALE_DORIAN),
    'iv7':  ([5,8,12,3], SCALE_HARMONIC),
    'v':    ([7,10,14],  SCALE_AEOLIAN),
    'V':    ([7,11,14],  SCALE_HARMONIC),
    'V7':   ([7,11,14,5],SCALE_HARMONIC),
    'VI':   ([8,12,15],  SCALE_AEOLIAN),
    'VI7':  ([8,12,15,10],SCALE_AEOLIAN),
    'VII':  ([10,14,17], SCALE_AEOLIAN),
    'viio': ([11,14,17], SCALE_HARMONIC),
}

# ── MOOD PROGRESSIONS ───────────────────────────────────────────────────────
moods = {
    "1": {"name":"Melancholy & Deep Sorrow","tension":0.5,"progressions":[
        {'chords':['i','VI','III','VII'],'label':'Hopeful Grief'},
        {'chords':['i','iv','i','V'],   'label':'Lamento'},
        {'chords':['i','VI','iv','V'],  'label':'Romantic Sorrow'},
        {'chords':['i','VII','VI','V'], 'label':'Andalusian Cadence'},
        {'chords':['i','bII','i','V'],  'label':'Phrygian Weeping'},
        {'chords':['i','iv','v','i'],   'label':'Austere Church'},
        {'chords':['i','VI','VII','i'], 'label':'Circular Grief'},
        {'chords':['i','iio','V','i'],  'label':'Baroque Descent'},
        {'chords':['i','iv','VII','III'],'label':'Fado'},
        {'chords':['VI','VII','i','i'], 'label':'Deceptive Resolution'},
        {'chords':['i','bII','VII','i'],'label':'Spanish Flamenco'},
        {'chords':['i','VI','bII','V'], 'label':'Neapolitan Lament'},
    ]},
    "2": {"name":"Epic & Heroic","tension":0.75,"progressions":[
        {'chords':['i','VI','III','VII'],'label':'Zimmer Epic'},
        {'chords':['i','v','VI','VII'], 'label':'Triumphant Minor'},
        {'chords':['i','VII','VI','v'], 'label':'Descending Heroic'},
        {'chords':['i','iv','VI','VII'],'label':'Battle March'},
        {'chords':['i','III','VII','VI'],'label':'Inception Style'},
        {'chords':['i','VI','VII','III'],'label':"Hero's Journey"},
        {'chords':['i','v','VII','iv'], 'label':'Fate & Struggle'},
        {'chords':['i','VII','III','VI'],'label':'Dark Triumph'},
        {'chords':['i','VI','v','VII'], 'label':'Warrior Ballad'},
        {'chords':['i','iv','VII','VI'],'label':'Cavalry Charge'},
        {'chords':['i','v','i','VII'],  'label':'Gladiator Ostinato'},
        {'chords':['VI','III','VII','i'],'label':'Rising from Ashes'},
    ]},
    "3": {"name":"Bittersweet & Nostalgic","tension":0.4,"progressions":[
        {'chords':['i','III','VI','VII'],'label':'Hopeful Minor'},
        {'chords':['i','VII','III','VI'],'label':'Wistful'},
        {'chords':['VI','VII','i','v'], 'label':'Reflective'},
        {'chords':['i','VI','III','iv'],'label':'Memory Lane'},
        {'chords':['i','III','iv','VI'],'label':'Tender Regret'},
        {'chords':['III','VII','i','VI'],'label':'Faded Summer'},
        {'chords':['i','iv','III','VII'],'label':'Childhood Echo'},
        {'chords':['VI','III','i','VII'],'label':'Film Nostalgia'},
        {'chords':['i','VII','VI','III'],'label':'Old Photograph'},
        {'chords':['i','VI','VII','III'],'label':'Soft Longing'},
    ]},
    "4": {"name":"Urgent, Dark & Ominous","tension":0.9,"progressions":[
        {'chords':['i','bII','i','VII'],'label':'Templar Phrygian'},
        {'chords':['i','VI','bII','i'], 'label':'Dark Descent'},
        {'chords':['i','v','iv','V'],   'label':'Ominous Buildup'},
        {'chords':['i','iv','bII','V'], 'label':'Gothic Thriller'},
        {'chords':['i','bII','VII','i'],'label':'Assassin Theme'},
        {'chords':['i','viio','i','V7'],'label':'Horror Cadence'},
        {'chords':['i','iv','v','bII'], 'label':'Black Mass'},
        {'chords':['bII','i','bII','VII'],'label':'Gregorian Doom'},
        {'chords':['i','VII','bII','i'],'label':'Venetian Darkness'},
        {'chords':['i','v','bII','VII'],'label':'Inquisition'},
        {'chords':['i','VI','v','bII'], 'label':'Lovecraftian Dread'},
        {'chords':['i7','iv7','V7','i'],'label':'Jazz Noir'},
    ]},
}

# ── MARKOV TRANSITION MATRICES ───────────────────────────────────────────────
# {from_semitone: [(to_semitone, weight), ...]}
MARKOV_AEOLIAN = {
    0: [(0,1),(2,3),(3,5),(5,4),(7,6),(8,3),(10,2)],
    2: [(0,5),(2,1),(3,6),(5,4),(7,3),(8,2),(10,1)],
    3: [(2,4),(3,1),(5,6),(7,5),(8,3),(10,2),(0,3)],
    5: [(3,5),(5,1),(7,6),(8,4),(10,3),(0,2),(2,2)],
    7: [(5,5),(7,1),(8,6),(10,5),(0,4),(2,3),(3,3)],
    8: [(7,5),(8,1),(10,5),(0,3),(2,2),(3,2),(5,3)],
    10:[(8,4),(10,1),(0,7),(2,3),(3,2),(5,2),(7,4)],
}
MARKOV_HARMONIC = {
    0: [(0,1),(2,3),(3,5),(5,4),(7,5),(8,3),(11,6)],
    2: [(0,5),(2,1),(3,6),(5,4),(7,3),(8,2),(11,3)],
    3: [(2,4),(3,1),(5,6),(7,5),(8,3),(11,4),(0,3)],
    5: [(3,5),(5,1),(7,6),(8,4),(11,5),(0,4),(2,2)],
    7: [(5,5),(7,1),(8,5),(11,6),(0,5),(2,3),(3,3)],
    8: [(7,5),(8,1),(11,7),(0,4),(2,2),(3,2),(5,3)],
    11:[(0,9),(11,1),(8,4),(7,3),(5,2),(3,1),(2,1)],
}
MARKOV_PHRYGIAN = {
    0: [(0,1),(1,7),(3,4),(5,3),(7,4),(8,3),(10,2)],
    1: [(0,8),(1,1),(3,5),(5,3),(7,2),(8,2),(10,2)],
    3: [(1,5),(3,1),(5,6),(7,5),(8,3),(10,2),(0,3)],
    5: [(3,5),(5,1),(7,6),(8,4),(10,3),(0,2),(1,3)],
    7: [(5,5),(7,1),(8,6),(10,5),(0,4),(1,4),(3,3)],
    8: [(7,5),(8,1),(10,5),(0,3),(1,4),(3,2),(5,3)],
    10:[(8,4),(10,1),(0,6),(1,5),(3,2),(5,2),(7,4)],
}

def get_markov_matrix(scale_tones):
    if 1 in scale_tones:   return MARKOV_PHRYGIAN
    if 11 in scale_tones:  return MARKOV_HARMONIC
    return MARKOV_AEOLIAN
_solo = _load("solo_perf_minor_private", "solo_performance_minor.py")

GENERATION_MODE = 'simple'
DEFAULT_BPM = 120

PROJECT_ADJECTIVES = [
    "Apex", "Infinite", "Midnight", "Titan", "Solar", "Gothic", "Ethereal", "Grim", "Silent",
    "Shadow", "Crimson", "Nebula", "Spectral", "Cosmic", "Lost", "Fallen", "Eternal", "Frozen",
    "Abyssal", "Radiant", "Iron", "Storm", "Phoenix", "Astral", "Mystic", "Ancient", "Vortex",
    "Obsidian", "Nocturne", "Velvet", "Ashen", "Cinder", "Hollow", "Distant", "Moonlit",
    "Cathedral", "Wounded", "Funeral", "Tarnished", "Winter", "Bloodless", "Raven", "Umbral",
    "Haunted", "Sable", "Fever", "Shattered", "Marble", "Waning", "Dusklit", "Feral",
    "Forsaken", "Charcoal", "Dread", "Grave", "Hushed", "Bleak", "Scarred", "Widowed",
    "Broken", "Sepulchral", "Buried", "Withered", "Veiled", "Mournful", "Blackened", "Doomed",
    "Cavernous", "Restless", "Frostbitten", "Eclipsed", "Trembling", "Hallowed", "Cursed", "Pale",
    "Sorrowing", "Wraithlike", "Drifting", "Ritual", "Duskbound", "Nocturnal", "Stygian", "Faded",
    "Ironclad", "Gloaming", "Tortured", "Severed", "Lunar", "Aching", "Funereal", "Drowned",
]
PROJECT_NOUNS = [
    "Ascent", "Requiem", "Odyssey", "Eclipse", "Horizon", "Empire", "Sanctuary", "Vanguard",
    "Echo", "Whisper", "Rift", "Conquest", "Genesis", "Destiny", "Void", "Valhalla", "Covenant",
    "Chronicle", "Legacy", "Bastion", "Rebirth", "Summit", "Oracle", "Wasteland", "Mirage",
    "Lament", "Catacomb", "Vigil", "Dirge", "Ashes", "Oath", "Citadel", "Elegy",
    "Sepulcher", "Pilgrimage", "Wound", "Procession", "Signal", "Ember", "Labyrinth", "Crown",
    "Monument", "Aftermath", "Cathedral", "Threshold", "Tomb", "Furnace", "Veil", "Dagger",
    "Ruin", "Grief", "Trial", "Exile", "Hollow", "Cairn", "Penance", "Funeral",
    "Scar", "Relic", "Cataclysm", "Nightfall", "Vow", "Remnant", "Descent", "Apparition",
    "Crypt", "Wraith", "Bells", "Confession", "Betrayal", "Wake", "Oblivion", "Hymn",
    "Burial", "Fever", "Silence", "Stormfront", "Dreadnought", "Abyss", "Rapture", "Gallows",
    "Coven", "Frost", "Memory", "Atonement", "Shroud", "Ravine", "Sorrow", "Gloaming",
]

# ── SCALES ──────────────────────────────────────────────────────────────────
SCALE_AEOLIAN  = [0, 2, 3, 5, 7, 8, 10]
SCALE_HARMONIC = [0, 2, 3, 5, 7, 8, 11]
SCALE_PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]
SCALE_DORIAN   = [0, 2, 3, 5, 7, 9, 10]

# Krumhansl-Schmuckler minor profile for key detection
KS_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

ROOT_NAMES = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']

roots = {'C':36,'C#':37,'D':38,'Eb':39,'E':40,'F':41,
         'F#':42,'G':43,'Ab':44,'A':45,'Bb':46,'B':47}

roman_numerals = {
    'i':    ([0,3,7],    SCALE_AEOLIAN),
    'i7':   ([0,3,7,10], SCALE_AEOLIAN),
    'iio':  ([2,5,8],    SCALE_AEOLIAN),
    'bII':  ([1,5,8],    SCALE_PHRYGIAN),
    'III':  ([3,7,10],   SCALE_AEOLIAN),
    'iv':   ([5,8,12],   SCALE_AEOLIAN),
    'IV':   ([5,9,12],   SCALE_DORIAN),
    'iv7':  ([5,8,12,3], SCALE_HARMONIC),
    'v':    ([7,10,14],  SCALE_AEOLIAN),
    'V':    ([7,11,14],  SCALE_HARMONIC),
    'V7':   ([7,11,14,5],SCALE_HARMONIC),
    'VI':   ([8,12,15],  SCALE_AEOLIAN),
    'VI7':  ([8,12,15,10],SCALE_AEOLIAN),
    'VII':  ([10,14,17], SCALE_AEOLIAN),
    'viio': ([11,14,17], SCALE_HARMONIC),
}

# ── MOOD PROGRESSIONS ───────────────────────────────────────────────────────
moods = {
    "1": {"name":"Melancholy & Deep Sorrow","tension":0.5,"progressions":[
        {'chords':['i','VI','III','VII'],'label':'Hopeful Grief'},
        {'chords':['i','iv','i','V'],   'label':'Lamento'},
        {'chords':['i','VI','iv','V'],  'label':'Romantic Sorrow'},
        {'chords':['i','VII','VI','V'], 'label':'Andalusian Cadence'},
        {'chords':['i','bII','i','V'],  'label':'Phrygian Weeping'},
        {'chords':['i','iv','v','i'],   'label':'Austere Church'},
        {'chords':['i','VI','VII','i'], 'label':'Circular Grief'},
        {'chords':['i','iio','V','i'],  'label':'Baroque Descent'},
        {'chords':['i','iv','VII','III'],'label':'Fado'},
        {'chords':['VI','VII','i','i'], 'label':'Deceptive Resolution'},
        {'chords':['i','bII','VII','i'],'label':'Spanish Flamenco'},
        {'chords':['i','VI','bII','V'], 'label':'Neapolitan Lament'},
    ]},
    "2": {"name":"Epic & Heroic","tension":0.75,"progressions":[
        {'chords':['i','VI','III','VII'],'label':'Zimmer Epic'},
        {'chords':['i','v','VI','VII'], 'label':'Triumphant Minor'},
        {'chords':['i','VII','VI','v'], 'label':'Descending Heroic'},
        {'chords':['i','iv','VI','VII'],'label':'Battle March'},
        {'chords':['i','III','VII','VI'],'label':'Inception Style'},
        {'chords':['i','VI','VII','III'],'label':"Hero's Journey"},
        {'chords':['i','v','VII','iv'], 'label':'Fate & Struggle'},
        {'chords':['i','VII','III','VI'],'label':'Dark Triumph'},
        {'chords':['i','VI','v','VII'], 'label':'Warrior Ballad'},
        {'chords':['i','iv','VII','VI'],'label':'Cavalry Charge'},
        {'chords':['i','v','i','VII'],  'label':'Gladiator Ostinato'},
        {'chords':['VI','III','VII','i'],'label':'Rising from Ashes'},
    ]},
    "3": {"name":"Bittersweet & Nostalgic","tension":0.4,"progressions":[
        {'chords':['i','III','VI','VII'],'label':'Hopeful Minor'},
        {'chords':['i','VII','III','VI'],'label':'Wistful'},
        {'chords':['VI','VII','i','v'], 'label':'Reflective'},
        {'chords':['i','VI','III','iv'],'label':'Memory Lane'},
        {'chords':['i','III','iv','VI'],'label':'Tender Regret'},
        {'chords':['III','VII','i','VI'],'label':'Faded Summer'},
        {'chords':['i','iv','III','VII'],'label':'Childhood Echo'},
        {'chords':['VI','III','i','VII'],'label':'Film Nostalgia'},
        {'chords':['i','VII','VI','III'],'label':'Old Photograph'},
        {'chords':['i','VI','VII','III'],'label':'Soft Longing'},
    ]},
    "4": {"name":"Urgent, Dark & Ominous","tension":0.9,"progressions":[
        {'chords':['i','bII','i','VII'],'label':'Templar Phrygian'},
        {'chords':['i','VI','bII','i'], 'label':'Dark Descent'},
        {'chords':['i','v','iv','V'],   'label':'Ominous Buildup'},
        {'chords':['i','iv','bII','V'], 'label':'Gothic Thriller'},
        {'chords':['i','bII','VII','i'],'label':'Assassin Theme'},
        {'chords':['i','viio','i','V7'],'label':'Horror Cadence'},
        {'chords':['i','iv','v','bII'], 'label':'Black Mass'},
        {'chords':['bII','i','bII','VII'],'label':'Gregorian Doom'},
        {'chords':['i','VII','bII','i'],'label':'Venetian Darkness'},
        {'chords':['i','v','bII','VII'],'label':'Inquisition'},
        {'chords':['i','VI','v','bII'], 'label':'Lovecraftian Dread'},
        {'chords':['i7','iv7','V7','i'],'label':'Jazz Noir'},
    ]},
}

# ── MARKOV TRANSITION MATRICES ───────────────────────────────────────────────
# {from_semitone: [(to_semitone, weight), ...]}
MARKOV_AEOLIAN = {
    0: [(0,1),(2,3),(3,5),(5,4),(7,6),(8,3),(10,2)],
    2: [(0,5),(2,1),(3,6),(5,4),(7,3),(8,2),(10,1)],
    3: [(2,4),(3,1),(5,6),(7,5),(8,3),(10,2),(0,3)],
    5: [(3,5),(5,1),(7,6),(8,4),(10,3),(0,2),(2,2)],
    7: [(5,5),(7,1),(8,6),(10,5),(0,4),(2,3),(3,3)],
    8: [(7,5),(8,1),(10,5),(0,3),(2,2),(3,2),(5,3)],
    10:[(8,4),(10,1),(0,7),(2,3),(3,2),(5,2),(7,4)],
}
MARKOV_HARMONIC = {
    0: [(0,1),(2,3),(3,5),(5,4),(7,5),(8,3),(11,6)],
    2: [(0,5),(2,1),(3,6),(5,4),(7,3),(8,2),(11,3)],
    3: [(2,4),(3,1),(5,6),(7,5),(8,3),(11,4),(0,3)],
    5: [(3,5),(5,1),(7,6),(8,4),(11,5),(0,4),(2,2)],
    7: [(5,5),(7,1),(8,5),(11,6),(0,5),(2,3),(3,3)],
    8: [(7,5),(8,1),(11,7),(0,4),(2,2),(3,2),(5,3)],
    11:[(0,9),(11,1),(8,4),(7,3),(5,2),(3,1),(2,1)],
}
MARKOV_PHRYGIAN = {
    0: [(0,1),(1,7),(3,4),(5,3),(7,4),(8,3),(10,2)],
    1: [(0,8),(1,1),(3,5),(5,3),(7,2),(8,2),(10,2)],
    3: [(1,5),(3,1),(5,6),(7,5),(8,3),(10,2),(0,3)],
    5: [(3,5),(5,1),(7,6),(8,4),(10,3),(0,2),(1,3)],
    7: [(5,5),(7,1),(8,6),(10,5),(0,4),(1,4),(3,3)],
    8: [(7,5),(8,1),(10,5),(0,3),(1,4),(3,2),(5,3)],
    10:[(8,4),(10,1),(0,6),(1,5),(3,2),(5,2),(7,4)],
}

def get_markov_matrix(scale_tones):
    if 1 in scale_tones:   return MARKOV_PHRYGIAN
    if 11 in scale_tones:  return MARKOV_HARMONIC
    return MARKOV_AEOLIAN

def pick_markov_next(cur, scale_tones, matrix):
    cur = cur % 12
    if cur not in matrix:
        cur = min(matrix.keys(), key=lambda x: abs(x-cur))
    candidates = matrix[cur]
    total = sum(w for _,w in candidates)
    r = random.uniform(0, total)
    cumulative = 0
    for tone, weight in candidates:
        cumulative += weight
        if r <= cumulative:
            if tone in scale_tones: return tone
    return random.choice(scale_tones)

# ── WEIGHTED RHYTHM ──────────────────────────────────────────────────────────
RHYTHM_MELODY  = [0.5, 0.5, 1.0, 1.0, 1.0, 1.5, 2.0]   # legacy / from-midi
RHYTHM_LEAD    = [0.25, 0.25, 0.5, 0.5, 0.5, 1.0, 1.0]  # staccato-biased
RHYTHM_LYRICAL = [0.5, 1.0, 1.0, 1.5, 2.0, 2.0, 3.0, 4.0] # memorable / breathing
RHYTHM_SUSTAIN = [1.0, 2.0, 2.0, 3.0, 4.0]               # legato-biased
RHYTHM_COUNTER = [1.0, 2.0, 2.0, 4.0]                     # legacy / from-midi

def w_rhythm(pool, beats_left, tension):
    filtered = [d for d in pool if d <= beats_left]
    if not filtered: return beats_left
    def w(d): return (1.0/d)*tension + d*(1.0-tension) + 0.1
    weights = [w(d) for d in filtered]
    total = sum(weights)
    r = random.uniform(0, total)
    cum = 0
    for d, wt in zip(filtered, weights):
        cum += wt
        if r <= cum: return d
    return filtered[-1]

# ── CALL-AND-RESPONSE ACTIVITY MAP ──────────────────────────────────────────
def _activity_map(tension, num_bars):
    """Per-bar activity schedule for lead and counter voices.
    Returns (lead_active[], counter_active[]) bool lists."""
    lead    = [False] * num_bars
    counter = [False] * num_bars
    for bar in range(num_bars):
        phase = bar % 4
        if tension < 0.4:
            # Low tension: strict call-and-response alternation
            lead[bar]    = phase in (0, 2)
            counter[bar] = phase in (1, 3)
        elif tension < 0.7:
            # Mid tension: overlap on climax bar
            lead[bar]    = phase in (0, 2, 3)
            counter[bar] = phase in (1, 2, 3)
        else:
            # High tension: both active, polarity enforced via rhythm
            lead[bar]    = True
            counter[bar] = True
    return lead, counter

def _lead_bar_directions(melody, num_bars):
    """Compute per-bar pitch direction from the lead melody.
    Returns a list of ints: positive = lead moved up, negative = down."""
    dirs = [0] * num_bars
    bar = 0
    beats = 0.0
    prev = None
    delta = 0
    for note, dur in melody:
        if note is not None:
            if prev is not None:
                delta += (note - prev)
            prev = note
        beats += dur
        while beats >= 4.0 - 0.01 and bar < num_bars:
            dirs[bar] = delta
            bar += 1
            beats -= 4.0
            delta = 0
    return dirs

# ── GENERATION ───────────────────────────────────────────────────────────────
def get_bar_harmony_at_beat(bar_harmony, beat_pos):
    """
    bar_harmony is either:
      - (ct, scale) [legacy whole bar]
      - a list of (ct, scale, duration) tuples that sum to 4.0 beats
    Returns the active (ct, scale) at the given beat_pos.
    """
    if isinstance(bar_harmony, tuple):
        return bar_harmony
    cum = 0.0
    for ct, sc, dur in bar_harmony:
        cum += dur
        if beat_pos < cum + 0.001:
            return ct, sc
    return bar_harmony[-1][0], bar_harmony[-1][1]

def generate_decoupled_progression(tension, scale_tones):
    """
    Layer 1: Choose a duration template based on tension.
    Layer 2: Random walk chord symbols from Markov matrix.
    """
    if tension < 0.5:
        templates = [
            [[4.0], [4.0], [4.0], [4.0]],
            [[4.0], [2.0, 2.0], [4.0], [4.0]],
            [[4.0], [4.0], [4.0], [2.0, 2.0]],
            [[2.0, 2.0], [4.0], [4.0], [4.0]],
        ]
    else:
        templates = [
            [[4.0], [2.0, 2.0], [4.0], [2.0, 1.0, 1.0]],
            [[2.0, 2.0], [2.0, 2.0], [4.0], [2.0, 2.0]],
            [[4.0], [4.0], [2.0, 2.0], [1.0, 1.0, 1.0, 1.0]],
            [[2.0, 1.0, 1.0], [4.0], [2.0, 2.0], [2.0, 1.0, 1.0]],
        ]
    
    dur_template = random.choice(templates)
    
    matrix = get_markov_matrix(scale_tones)
    symbol_roots = {}
    for sym, (offsets, _) in roman_numerals.items():
        symbol_roots[sym] = offsets[0] % 12
        
    rn_list = list(roman_numerals.keys())
    current_symbol = 'i' if 'i' in rn_list else rn_list[0]
    
    decoupled_prog = []
    for bar_durations in dur_template:
        bar_chords = []
        for dur in bar_durations:
            bar_chords.append((current_symbol, dur))
            
            # Markov step
            cur_root = symbol_roots.get(current_symbol, 0)
            next_root = pick_markov_next(cur_root, scale_tones, matrix)
            candidates = [sym for sym, r in symbol_roots.items() if r == next_root]
            if candidates:
                candidates.sort(key=lambda s: len(s))
                current_symbol = candidates[0]
            else:
                current_symbol = random.choice(rn_list)
        decoupled_prog.append(bar_chords)

    return decoupled_prog

def generate_chords(root_note, progression):
    chords = []
    for bar_item in progression:
        if isinstance(bar_item, list):
            # Decoupled Mode subdivided bar chords
            bar_chords = []
            for num, dur in bar_item:
                offsets = roman_numerals[num][0]
                voicing = [root_note + 12 + (o % 24) for o in offsets]
                bar_chords.append((voicing, dur))
            chords.append(bar_chords)
        else:
            offsets = roman_numerals[bar_item][0]
            voicing = [root_note + 12 + (o % 24) for o in offsets]
            chords.append(voicing)
    return chords

def build_midi(chords, root_val, progression, bpm=DEFAULT_BPM, base_tpb=480):
    tpb = base_tpb
    SCALE_NAME = "chord_engine_minor"
    MINOR_CHORDS = {}
    for sym, (offsets, _) in roman_numerals.items():
        MINOR_CHORDS[sym] = [o % 12 for o in offsets]
    _solo.MINOR_SCALES[SCALE_NAME] = list(SCALE_AEOLIAN)
    _solo.SCALE_CHORDS[SCALE_NAME] = MINOR_CHORDS

    def _minor_bars_data(prog, _scale_name):
        return [
            ([t % 12 for t in roman_numerals[symbol][0]], [t % 12 for t in roman_numerals[symbol][1]])
            for symbol in prog
        ]
    _solo._solo_bars_data = _minor_bars_data

    harmonic_plan = _solo._build_harmonic_plan(root_val, progression, SCALE_NAME)
    hook_lead = _solo._generate_main_hook_lead(root_val, harmonic_plan, SCALE_NAME, tpb)
    
    pad_events = [(0, "program", 48, 0, 0)]
    current_tick = 0
    for bar_item in chords:
        if isinstance(bar_item, list) and bar_item and isinstance(bar_item[0], (list, tuple)):
            for voicing, dur in bar_item:
                dur_ticks = int(dur * tpb)
                for n in voicing:
                    pad_events.append((current_tick, "on", n, 68, 0))
                for n in voicing:
                    pad_events.append((current_tick + dur_ticks, "off", n, 68, 0))
                current_tick += dur_ticks
        else:
            dur_ticks = 4 * tpb
            for n in bar_item:
                pad_events.append((current_tick, "on", n, 68, 0))
            for n in bar_item:
                pad_events.append((current_tick + dur_ticks, "off", n, 68, 0))
            current_tick += dur_ticks

    rhythmic = _solo._generate_rhythmic_layer(harmonic_plan, tpb, bpm)
    staccato = _solo._generate_staccato(root_val, progression, SCALE_NAME, tpb, bpm, _solo.INSTRUMENTS["1"])
    sub_bass = _solo._generate_sub_bass(root_val, progression, SCALE_NAME, tpb, bpm)
    cry_lead, cry_counter, _, _ = _solo._generate_crying_violin_parts(root_val, progression, SCALE_NAME, tpb)

    tracks = [
        hook_lead,
        pad_events,
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
        "Staccato Phrases - Solo Performance",
        "Sub-Bass - Progression Root Support",
        "Crying Violin Lead Melody",
        "Crying Violin Counter",
    ]
    
    loop_end = 4 * 4 * tpb
    mid = _solo._events_to_mid(tracks, names, bpm, tpb, loop_end)
    return mid

# ── MIDI FILE ANALYSIS (Feature 2) ──────────────────────────────────────────
def parse_midi_chords(filepath):
    """Extract simultaneous note groups from a MIDI file."""
    mid = mido.MidiFile(filepath)
    tpb = mid.ticks_per_beat
    # Merge all tracks into absolute-time note-on events
    note_ons = []
    for track in mid.tracks:
        t = 0
        for msg in track:
            t += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                note_ons.append((t, msg.note))
    note_ons.sort()
    if not note_ons:
        return [], tpb
    # Group notes within a 32nd-note window
    threshold = max(1, tpb // 8)
    groups = []
    i = 0
    while i < len(note_ons):
        t0, n0 = note_ons[i]
        grp = [n0]
        j = i + 1
        while j < len(note_ons) and note_ons[j][0] - t0 <= threshold:
            grp.append(note_ons[j][1])
            j += 1
        pcs = sorted(set(n % 12 for n in grp))
        if len(pcs) >= 2:
            groups.append(pcs)
        i = j
    # Collapse consecutive duplicates
    collapsed = []
    prev = None
    for g in groups:
        t = tuple(g)
        if t != prev:
            collapsed.append(g)
            prev = t
    return collapsed, tpb

def detect_key(chord_groups):
    """Krumhansl-Schmuckler key detection — returns (root_name, root_pc, scale, scale_name)."""
    pc_counts = [0] * 12
    for pcs in chord_groups:
        for pc in pcs:
            pc_counts[pc % 12] += 1
    best_score, best_root = -1e9, 0
    for root in range(12):
        profile = [KS_MINOR[(i - root) % 12] for i in range(12)]
        score = sum(pc_counts[i] * profile[i] for i in range(12))
        if score > best_score:
            best_score, best_root = score, root
    root_name = ROOT_NAMES[best_root]
    # Harmonic vs. natural: check raised 7th
    raised7 = (best_root + 11) % 12
    nat7    = (best_root + 10) % 12
    if pc_counts[raised7] > pc_counts[nat7]:
        return root_name, best_root, SCALE_HARMONIC, 'Harmonic Minor'
    # Check Phrygian (flat 2 prominent)
    flat2 = (best_root + 1) % 12
    if pc_counts[flat2] >= 2:
        return root_name, best_root, SCALE_PHRYGIAN, 'Phrygian'
    return root_name, best_root, SCALE_AEOLIAN, 'Natural Minor'

def generate_from_midi(filepath, out_dir):
    import VVC
    VVC.generate_quartet_over_midi(filepath, out_dir)

# ── EMOTIONAL STYLE CLUSTERS (Option 6) ─────────────────────────────────────
STYLE_CLUSTERS = {
    'A': {
        'names': ['sorrowful', 'sad', 'heartbreaking'],
        'tension': 0.58,
        'progressions': [
            {'chords': ['i','iv','v','i'],          'label': 'Austere Grief'},
            {'chords': ['i','VI','iv','V'],          'label': 'Classical Sorrow'},
            {'chords': ['i','VII','VI','V'],         'label': 'Andalusian Tears'},
            {'chords': ['i','bII','VII','i'],        'label': 'Phrygian Heartbreak'},
            {'chords': ['i','viio','i','v'],         'label': 'Baroque Lament'},
            {'chords': ['i','iv','bII','v'],         'label': 'Gothic Sorrow'},
            {'chords': ['i','VI','VII','v'],         'label': 'Falling Darkness'},
            {'chords': ['iv','i','iv','v'],          'label': 'Endless Despair'},
            {'chords': ['i','v','iv','i'],           'label': 'Circular Pain'},
            {'chords': ['i','bII','i','VII'],        'label': 'Templar Dirge'},
            {'chords': ['i','iv','VII','i'],         'label': 'Mournful Return'},
            {'chords': ['i','VI','bII','V'],         'label': 'Neapolitan Grief'},
            {'chords': ['i','iio','V','i'],          'label': 'Baroque Descent'},
            {'chords': ['i','iv','v','VI'],          'label': 'Unresolved Anguish'},
        ]
    },
    'B': {
        'names': ['romantic', 'emotional'],
        'tension': 0.42,
        'progressions': [
            {'chords': ['i','VI','III','VII'],       'label': 'Lush Romance'},
            {'chords': ['i','III','VII','VI'],       'label': 'Emotional Sweep'},
            {'chords': ['i','VII','VI','III'],       'label': 'Descending Warmth'},
            {'chords': ['VI','VII','i','III'],       'label': 'Anticipation'},
            {'chords': ['i','iv','VI','VII'],        'label': 'Stirring Emotion'},
            {'chords': ['III','VI','VII','i'],       'label': 'Building Romance'},
            {'chords': ['i','v','VI','III'],         'label': 'Intimate Pull'},
            {'chords': ['i','VI','VII','III'],       'label': 'Longing Romance'},
            {'chords': ['i','III','VI','v'],         'label': 'Tender Ache'},
            {'chords': ['VI','III','iv','i'],        'label': 'Warm Resolution'},
            {'chords': ['i','VI','iv','III'],        'label': 'Rich Emotion'},
            {'chords': ['i','III','iv','VII'],       'label': 'Heart Swell'},
            {'chords': ['i','iv','III','v'],         'label': 'Quiet Devotion'},
            {'chords': ['VI','i','III','VII'],       'label': 'Moonlit Evening'},
        ]
    },
    'C': {
        'names': ['yearning', 'nostalgic'],
        'tension': 0.40,
        'progressions': [
            {'chords': ['i','VII','VI','VII'],       'label': 'Suspended Longing'},
            {'chords': ['i','III','VI','VII'],       'label': 'Wistful Memory'},
            {'chords': ['VI','VII','i','v'],         'label': 'Reflective Gaze'},
            {'chords': ['i','VI','VII','i'],         'label': 'Circular Longing'},
            {'chords': ['i','III','iv','VI'],        'label': 'Tender Remembrance'},
            {'chords': ['III','VII','i','VI'],       'label': 'Faded Glory'},
            {'chords': ['i','v','VII','VI'],         'label': 'Receding Dream'},
            {'chords': ['VI','III','i','VII'],       'label': 'Golden Haze'},
            {'chords': ['i','iv','III','VI'],        'label': 'Warm Memory'},
            {'chords': ['i','VII','III','IV'],       'label': 'Nostalgic Lift'},
            {'chords': ['i','VI','III','iv'],        'label': 'Aching Beauty'},
            {'chords': ['VI','i','v','VII'],         'label': 'Twilight Echo'},
            {'chords': ['i','III','VII','iv'],       'label': 'Lost Paradise'},
            {'chords': ['i','VII','iv','VI'],        'label': 'Soft Reverie'},
        ]
    },
    'D': {
        'names': ['hopeful', 'uplifting'],
        'tension': 0.32,
        'progressions': [
            {'chords': ['i','III','VII','VI'],       'label': 'Rising Hope'},
            {'chords': ['VI','III','VII','i'],       'label': 'Victorious Resolve'},
            {'chords': ['i','VII','III','VI'],       'label': 'Lifting Spirits'},
            {'chords': ['i','iv','III','VII'],       'label': 'Cautious Hope'},
            {'chords': ['III','VII','VI','i'],       'label': 'Anthem Hope'},
            {'chords': ['i','VI','VII','III'],       'label': 'Swelling Hope'},
            {'chords': ['i','v','III','VII'],        'label': 'Determined Spirit'},
            {'chords': ['VI','VII','III','i'],       'label': 'Triumphant Minor'},
            {'chords': ['i','III','iv','VII'],       'label': 'Tender Hope'},
            {'chords': ['i','VI','III','VII'],       'label': 'Light Breaking Through'},
            {'chords': ['III','i','VI','VII'],       'label': 'Morning Light'},
            {'chords': ['i','VII','VI','III'],       'label': 'Ascending Dawn'},
            {'chords': ['VI','III','i','VII'],       'label': 'Renewal'},
            {'chords': ['i','III','VI','iv'],        'label': 'Bittersweet Optimism'},
        ]
    },
    'E': {
        'names': ['tragic', 'epic'],
        'tension': 0.82,
        'progressions': [
            {'chords': ['i','v','VI','VII'],         'label': 'Zimmer Tragedy'},
            {'chords': ['i','VI','III','VII'],       'label': 'Orchestral Epic'},
            {'chords': ['i','VII','VI','v'],         'label': 'Descending Power'},
            {'chords': ['i','iv','VI','VII'],        'label': 'Battle Cry'},
            {'chords': ['VI','III','VII','i'],       'label': 'Triumphant Finale'},
            {'chords': ['i','v','iv','V'],           'label': 'Tragic Climax'},
            {'chords': ['i','VII','bII','i'],        'label': 'Dark Fate'},
            {'chords': ['i','v','VII','iv'],         'label': 'Dramatic Struggle'},
            {'chords': ['i','VI','v','VII'],         'label': 'Surging Tide'},
            {'chords': ['i','iv','v','VI'],          'label': 'Tragic Ascent'},
            {'chords': ['i','bII','v','i'],          'label': 'Doomed Hero'},
            {'chords': ['VI','i','v','VII'],         'label': 'Last Stand'},
            {'chords': ['i','VII','iv','V'],         'label': 'Sacrifice Theme'},
            {'chords': ['i','v','bII','VII'],        'label': 'Inquisition March'},
        ]
    },
}

STYLE_MAP = {}
for _ck, _cv in STYLE_CLUSTERS.items():
    for _sn in _cv['names']:
        STYLE_MAP[_sn] = _ck

# ── HELPERS ───────────────────────────────────────────────────────────────────
def _div(char='-', w=62): print(char * w)

def _detect_scale(prog):
    if any(n in prog for n in ['bII','viio']): return 'Phrygian / Harmonic Minor'
    if any(n in prog for n in ['V','V7','iv7']): return 'Harmonic Minor'
    return 'Natural Minor (Aeolian)'

def _slug(text):
    keep = []
    for char in str(text):
        keep.append(char if char.isalnum() or char in "#+-" else "_")
    return "_".join(part for part in "".join(keep).split("_") if part)

def _project_title():
    return f"{random.choice(PROJECT_ADJECTIVES)}_{random.choice(PROJECT_NOUNS)}"

def _tempo_for_tension(tension):
    return random.randint(130, 146) if tension >= 0.70 else random.randint(104, 128)

def _save_midi(mid, fname_base, out_dir):
    fpath = os.path.join(out_dir, fname_base + '.mid')
    idx = 1
    while os.path.exists(fpath):
        fpath = os.path.join(out_dir, f"{fname_base}_v{idx}.mid"); idx += 1
    mid.save(fpath)
    print(f"\n  [SAVED]  {os.path.basename(fpath)}")
    print(f"  [PATH ]  {fpath}\n")

def _cinematic_fname(mood_name, style_label, root_name, tonality, bpm, prog_display):
    project_title = _project_title()
    mood_tag = _slug(mood_name)
    style_tag = _slug(style_label)
    prog_tag = _slug(prog_display)
    return f"{project_title}__Minor_Engine_{mood_tag}__{style_tag}__{root_name}_{tonality}__{bpm}BPM__{prog_tag}"

def _again_or_back():
    print("  [G] Generate again    [B] Back to main menu")
    return input("  --> ").strip().lower() == 'g'

_FLAVOUR = {
    frozenset(['A','B']): "Romantic love twisted by grief -- passion meets heartache.",
    frozenset(['A','C']): "Wistful sorrow -- longing for something painfully lost.",
    frozenset(['A','D']): "A flicker of hope burning inside deep sadness.",
    frozenset(['A','E']): "Grand cinematic tragedy -- sacrifice on a heroic scale.",
    frozenset(['B','C']): "Tender nostalgia -- a love remembered from a distance.",
    frozenset(['B','D']): "Warm, swelling emotion rising toward the light.",
    frozenset(['B','E']): "Passionate love tested by epic, world-shaking stakes.",
    frozenset(['C','D']): "Bittersweet optimism -- hope laced with beautiful longing.",
    frozenset(['C','E']): "Nostalgic grandeur -- mourning something once magnificent.",
    frozenset(['D','E']): "Triumphant ascent -- rising from darkness into heroic glory.",
}
def _flavour(cs): return _FLAVOUR.get(frozenset(cs), "A unique blend drawn from multiple harmonic worlds.")

def _run_quick_cluster(cluster_key, out_dir):
    """Generate a 4-bar loop from a STYLE_CLUSTERS family."""
    cluster = STYLE_CLUSTERS[cluster_key]
    names   = ' / '.join(n.capitalize() for n in cluster['names'])
    tension = cluster['tension']
    again   = True
    while again:
        root_name, root_val = random.choice(list(roots.items()))
        entry    = random.choice(cluster['progressions'])
        prog     = entry['chords']
        tbar     = '#'*int(tension*10) + '.'*(10-int(tension*10))
        
        gen_mode = globals().get('GENERATION_MODE', 'simple')
        if gen_mode == 'decoupled':
            _, scale_tones = roman_numerals[prog[0]]
            full_prog = generate_decoupled_progression(tension, scale_tones)
            prog_display = "Double-Layer Decoupled Markov Walk"
        else:
            full_prog = [prog[i % len(prog)] for i in range(4)]
            prog_display = '-'.join(prog)
            
        print(f"\n  Family      :  {names}")
        print(f"  Key         :  {root_name} Minor")
        print(f"  Style       :  {entry['label']}")
        print(f"  Progression :  {prog_display}")
        print(f"  Scale       :  {_detect_scale(prog)}")
        print(f"  Tension     :  [{tbar}] {int(tension*100)}%")
        print(f"  Gen Mode    :  {gen_mode.upper()}")

        _div('=')
        print("  Generating 4-Bar Loop...")
        chords  = generate_chords(root_val, full_prog)
        flat_prog = []
        for bar_item in full_prog:
            if isinstance(bar_item, list):
                flat_prog.append(bar_item[0][0])
            else:
                flat_prog.append(bar_item)
        bpm     = _tempo_for_tension(tension)
        mid     = build_midi(chords, root_val, flat_prog, bpm=bpm)
        _save_midi(mid, _cinematic_fname(names, entry['label'], root_name, "Minor", bpm, prog_display), out_dir)
        again = _again_or_back()

def _run_blend(out_dir, surprise=False):
    cluster_keys = sorted(STYLE_CLUSTERS.keys())
    if surprise:
        chosen_cks = random.sample(cluster_keys, random.randint(2,3))
        chosen_names = [STYLE_CLUSTERS[ck]['names'][0] for ck in chosen_cks]
        print(f"\n  Surprise blend:  {', '.join(s.capitalize() for s in chosen_names)}\n")
        parts = chosen_cks
    else:
        print(f"\n  {len(cluster_keys)} emotion families available -- type names or numbers, comma-separated:\n")
        for i, ck in enumerate(cluster_keys, 1):
            names_str = ' / '.join([n.capitalize() for n in STYLE_CLUSTERS[ck]['names']])
            print(f"    {i:>2}. {names_str}")
        print()
        raw   = input("  Your blend  (e.g.  bright,dreamy  or  1,3): ").strip()
        parts = [p.strip().lower() for p in raw.replace(' ',',').split(',') if p.strip()]

    clusters = set()
    for p in parts:
        if p.upper() in cluster_keys:
            clusters.add(p.upper())
        elif p.isdigit():
            i = int(p)-1
            if 0 <= i < len(cluster_keys):
                clusters.add(cluster_keys[i])
        elif p in STYLE_MAP:
            clusters.add(STYLE_MAP[p])
        else:
            print(f"  [!] '{p}' not recognised -- skipped.")
    if not clusters: print("  [!] No valid styles. Returning.\n"); return
    
    names = [STYLE_CLUSTERS[ck]['names'][0] for ck in clusters]

    again = True
    while again:
        merged, seen, tensions = [], set(), []
        for ck in clusters:
            tensions.append(STYLE_CLUSTERS[ck]['tension'])
            for p in STYLE_CLUSTERS[ck]['progressions']:
                if p['label'] not in seen: merged.append(p); seen.add(p['label'])
        tension  = sum(tensions)/len(tensions)

        root_name, root_val = random.choice(list(roots.items()))
        entry    = random.choice(merged)
        prog     = entry['chords']
        tag      = '+'.join(s.capitalize() for s in sorted(names))
        tbar     = '#'*int(tension*10)+'.'*(10-int(tension*10))

        # Determine mode
        gen_mode = globals().get('GENERATION_MODE', 'simple')
        if gen_mode == 'decoupled':
            _, scale_tones = roman_numerals[prog[0]]
            full_prog = generate_decoupled_progression(tension, scale_tones)
            prog_display = "Double-Layer Decoupled Markov Walk"
        else:
            full_prog = [prog[i % len(prog)] for i in range(4)]
            prog_display = '-'.join(prog)

        print(f"\n  Blend       :  {tag}")
        print(f"  Vibe        :  {_flavour(clusters)}")
        print(f"  Key         :  {root_name} Minor")
        print(f"  Style       :  {entry['label']}")
        print(f"  Progression :  {prog_display}")
        print(f"  Scale       :  {_detect_scale(prog)}")
        print(f"  Tension     :  [{tbar}] {int(tension*100)}%")
        print(f"  Pool        :  {len(merged)} progressions available")
        print(f"  Gen Mode    :  {gen_mode.upper()}")

        _div('=')
        print("  Generating 4-Bar Loop...")
        chords  = generate_chords(root_val, full_prog)
        flat_prog = []
        for bar_item in full_prog:
            if isinstance(bar_item, list):
                flat_prog.append(bar_item[0][0])
            else:
                flat_prog.append(bar_item)
        bpm = _tempo_for_tension(tension)
        mid = build_midi(chords, root_val, flat_prog, bpm=bpm)
        _save_midi(mid, _cinematic_fname(f"Blend {tag}", entry['label'], root_name, "Minor", bpm, prog_display), out_dir)
        again = _again_or_back()

def main(out_dir='midi_files'):
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    os.makedirs(out_dir, exist_ok=True)

    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║      A N I M A   M I D I   O R C H E S T R A T I O N       ║
║             —  Procedural Composition Engine  —            ║
║                                                            ║
║    Mood-Adaptive  |  Multi-Track  |  Humanized Phrasing    ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
    while True:
        n_blend = sum(len(c['progressions']) for c in STYLE_CLUSTERS.values())
        print(f"""  Select a compositional mode:
  ____________________________________________________________

   [ ── DIRECT GENERATION ── ]
     1  →  Emotion Family Selector
           Choose one of 5 emotion families and generate a 4-bar loop

     2  →  Emotion Fusion Studio
           Combine multiple emotional profiles for complex arrangements

     S  →  Surprise Me!
           Let the generator design a custom mood cocktail

   [ ── UTILITIES ── ]
     3  →  Melodic Overlayer (Quartet)
           Analyze MIDI file and build a custom 7-track string/piano overlay
  ____________________________________________________________
     0  →  Exit

  ({n_blend} blend pathways  |  46 quick progressions  |  12 minor scales)
""")
        _div()
        choice = input("  --> ").strip().lower()
        _div('=')

        if choice == '0':
            print("\n  See you next session. Happy composing!\n"); break

        elif choice == 's':
            print("  SURPRISE ME -- Generating a random emotion cocktail...\n")
            _run_blend(out_dir, surprise=True)

        elif choice == '1':
            print("  EMOTION FAMILY SELECTOR")
            print("  Pick an emotional world — a random progression is chosen for you.\n")
            _FAMILY_KEYS = sorted(STYLE_CLUSTERS.keys())  # A, B, C, D, E
            for i, ck in enumerate(_FAMILY_KEYS, 1):
                names_str = ' / '.join(n.capitalize() for n in STYLE_CLUSTERS[ck]['names'])
                tension_pct = int(STYLE_CLUSTERS[ck]['tension'] * 100)
                n_progs = len(STYLE_CLUSTERS[ck]['progressions'])
                print(f"    {i}  ->  {names_str}")
                print(f"           Tension: {tension_pct}%  |  {n_progs} progressions\n")
            print("    B  ->  Back\n")
            _div()
            sub = input("  -->  ").strip().lower()
            if sub == 'b':
                pass
            elif sub.isdigit() and 1 <= int(sub) <= len(_FAMILY_KEYS):
                _div('=')
                ck = _FAMILY_KEYS[int(sub) - 1]
                names_str = ' / '.join(n.capitalize() for n in STYLE_CLUSTERS[ck]['names'])
                print(f"  {names_str.upper()}")
                _div()
                _run_quick_cluster(ck, out_dir)
            else:
                print("  [!] Enter 1-5 or B.")

        elif choice == '2':
            print("  EMOTION BLENDING")
            print("  Combine emotions to unlock their shared harmonic power.\n")
            _div()
            _run_blend(out_dir, surprise=False)

        elif choice == '3':
            print("  ADD MELODIES TO EXISTING MIDI")
            print("  Paste or drag the file path below.\n")
            _div()
            path = input("  File path: ").strip().strip('"').strip("'")
            if not os.path.isfile(path):
                print(f"\n  [ERROR] File not found:\n  {path}\n")
            else:
                generate_from_midi(path, out_dir)
        else:
            print("  [!] Invalid -- enter 1-3, S or 0.\n")

        _div()
        time.sleep(0.2)

if __name__ == '__main__':
    main()

