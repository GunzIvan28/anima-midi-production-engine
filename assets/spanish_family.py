"""
ANIMA Spanish Family Engine
— Nylon Guitar & Cinematic Pad Composer —
Generates emotional, touching Spanish compositions with five channels:
  1. Harmony: Nylon Guitar (Arpeggios) - Channel 0
  2. Counter-Melody: Nylon Guitar (Lyrical Lead with Tremolo & Grace Notes) - Channel 1
  3. Bass Line: Acoustic Bass (Root/Fifth/Approach Movement) - Channel 2
  4. Trumpet: Harmonized Brass Phrases - Channel 3
  5. Violin: Lyrical Sustained/Answer Phrases - Channel 4
"""

import os
import sys
import random
import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack

GENERATION_MODE = 'simple'

# nylon guitar = 24, acoustic bass = 32
GM_NYLON = 24
GM_ACOUSTIC_BASS = 32
GM_TRUMPET = 56
GM_VIOLIN = 40

# ── SCALES ───────────────────────────────────────────────────────────────────
SPANISH_SCALES = {
    'phrygian_dominant': [0, 1, 4, 5, 7, 8, 10],   # Spanish Gypsy
    'harmonic_minor':    [0, 2, 3, 5, 7, 8, 11],   # Lamento / Mournful
    'phrygian':          [0, 1, 3, 5, 7, 8, 10],   # Melancholic Spanish
    'dorian':            [0, 2, 3, 5, 7, 9, 10],   # Passionate / Bittersweet
    'natural_minor':     [0, 2, 3, 5, 7, 8, 10],   # Nostalgic
    'ionian':            [0, 2, 4, 5, 7, 9, 11],   # Radiant / Bright Major
    'mixolydian':        [0, 2, 4, 5, 7, 9, 10],   # Warm Andalusian Major
    'double_harmonic_major': [0, 1, 4, 5, 7, 8, 11] # Exotic Byzantine Major
}

# ── ROMAN NUMERAL CHORD DEFINITIONS ──────────────────────────────────────────
# Semitones from root for the triads of each scale
SCALE_CHORDS = {
    'harmonic_minor': {
        'i': [0, 3, 7], 'ii°': [2, 5, 8], 'III': [3, 7, 11], 'iv': [5, 8, 0], 'V': [7, 11, 2], 'VI': [8, 0, 3], 'VII': [10, 2, 5]
    },
    'phrygian_dominant': {
        'I': [0, 4, 7], 'bII': [1, 5, 8], 'iii°': [4, 7, 10], 'iv': [5, 8, 0], 'bVI': [8, 0, 4], 'bVII': [10, 1, 5]
    },
    'phrygian': {
        'i': [0, 3, 7], 'bII': [1, 5, 8], 'bIII': [3, 7, 10], 'iv': [5, 8, 0], 'v°': [7, 10, 1], 'bVI': [8, 0, 3], 'bVII': [10, 1, 5]
    },
    'natural_minor': {
        'i': [0, 3, 7], 'ii°': [2, 5, 8], 'bIII': [3, 7, 10], 'iv': [5, 8, 0], 'v': [7, 10, 2], 'bVI': [8, 0, 3], 'bVII': [10, 2, 5]
    },
    'dorian': {
        'i': [0, 3, 7], 'ii': [2, 5, 9], 'bIII': [3, 7, 10], 'IV': [5, 9, 0], 'v': [7, 10, 2], 'vi°': [9, 0, 3], 'bVII': [10, 2, 5]
    },
    'ionian': {
        'I': [0, 4, 7], 'ii': [2, 5, 9], 'iii': [4, 7, 11], 'IV': [5, 9, 0], 'V': [7, 11, 2], 'vi': [9, 0, 4], 'vii°': [11, 2, 5]
    },
    'mixolydian': {
        'I': [0, 4, 7], 'ii': [2, 5, 9], 'iii°': [4, 7, 10], 'IV': [5, 9, 0], 'v': [7, 10, 2], 'vi': [9, 0, 4], 'bVII': [10, 2, 5]
    },
    'double_harmonic_major': {
        'I': [0, 4, 7], 'bII': [1, 5, 8], 'iii': [4, 7, 11], 'IV': [5, 9, 0], 'V': [7, 11, 1], 'bVI': [8, 0, 4], 'vii': [11, 2, 5]
    }
}

# ── HARMONIC TRANSITION GRAPH (Sophisticated Rule-Based Voice Leading Flow) ──
MINOR_TRANSITIONS = {
    'i': ['iv', 'V', 'bVI', 'bVII', 'bII', 'bIII'],
    'I': ['iv', 'V', 'bVI', 'bVII', 'bII'], 
    'iv': ['V', 'bVII', 'i', 'I', 'bVI'],
    'V': ['i', 'I', 'bVI', 'bII'],
    'bVI': ['V', 'bII', 'iv', 'bVII', 'i', 'I'],
    'bVII': ['bVI', 'bIII', 'i', 'I', 'V'],
    'bII': ['i', 'I', 'V', 'bVII', 'iv'],
    'bIII': ['bVI', 'iv', 'bVII', 'i']
}

MAJOR_TRANSITIONS = {
    'I': ['IV', 'V', 'vi', 'ii', 'iii', 'bVII', 'bII'],
    'IV': ['V', 'I', 'ii', 'vi', 'bVII'],
    'V': ['I', 'vi', 'IV', 'ii'],
    'vi': ['IV', 'ii', 'V', 'iii', 'I'],
    'ii': ['V', 'IV', 'vi'],
    'iii': ['vi', 'IV', 'I'],
    'bVII': ['IV', 'I', 'V'],
    'bII': ['I', 'IV', 'V']
}

# ── ROOT MIDI NUMBERS ────────────────────────────────────────────────────────
ROOTS = {'C':60,'C#':61,'Db':61,'D':62,'D#':63,'Eb':63,'E':64,
         'F':65,'F#':66,'Gb':66,'G':67,'G#':68,'Ab':68,'A':69,'Bb':70,'B':71}

# ── PROJECT NAME GENERATOR WORDBANKS ──────────────────────────────────────────
PROJECT_ADJECTIVES = [
    "Andaluz", "Gitano", "Sevillano", "Granadino", "Cordobes", "Malagueno", "Gaditano",
    "Madrileno", "Caribeno", "Costeno", "Serrano", "Moreno", "Dorado", "Rojo", "Azul",
    "Bravio", "Sagrado", "Querido", "Antiguo", "Morisco", "Flamenco", "Rumbero", "Bolero",
    "Nocturno", "Soleado", "Lunado", "Sereno", "Ardiente", "Tierno", "Dulce", "Amargo",
    "Festivo", "Romantico", "Alegre", "Melancolico", "Nostalgico", "Apasionado", "Herido",
    "Lejano", "Cercano", "Errante", "Criollo", "Mestizo", "Latino", "Iberico", "Caliente",
    "Tropical", "Barrial", "Pueblerino", "Marinero", "Patio", "Alba", "Rocio", "Candela",
    "Canela", "Azahar", "Olivo", "Jazmin", "Clavel", "Arena", "Brisa", "Feria",
    "Verbena", "Zambra", "Saeta", "Sombra", "Luz", "Duende", "Corazon", "Alma",
    "Cobre", "Miel", "Sol", "Noche", "Aurora", "Lucero", "Suenos", "Raiz"
]

PROJECT_NOUNS = [
    "Alhambra", "Sevilla", "Granada", "Cordoba", "Cadiz", "Malaga", "Triana", "Ronda",
    "Toledo", "Valencia", "Habana", "Santiago", "Veracruz", "Cartagena", "Oaxaca",
    "Callejon", "Plaza", "Patio", "Barrio", "Rincon", "Camino", "Puerto", "Mercado",
    "Feria", "Verbena", "Procesion", "Serenata", "Copla", "Bolero", "Rumba", "Tango",
    "Fandango", "Buleria", "Solea", "Zambra", "Saeta", "Romance", "Corrido", "Cancion",
    "Guitarra", "Cajon", "Palmas", "Taconeo", "Rasgueo", "Compas", "Falseta", "Tremolo",
    "Lamento", "Suspiro", "Llanto", "Promesa", "Abrazo", "Recuerdo", "Milagro", "Bendicion",
    "Corazon", "Alma", "Duende", "Candela", "Azahar", "Jazmin", "Clavel", "Olivo",
    "Luna", "Lucero", "Alba", "Sol", "Mar", "Sierra", "Arena", "Brisa",
    "Rocio", "Madrugada", "Noche", "Fiesta", "Pueblo", "Casa", "Ermita", "Campana"
]

# ── MOOD PRESETS (Native Spanish, Minor Engine, and Major Engine) ──────────────
NATIVE_MOODS = {
    '1': {'name': 'Duende Oscuro',     'desc': 'Dark passion and deep soul of Flamenco',  'scale': 'phrygian_dominant',    'is_minor': True,  'tension': 0.75, 'bpm_range': (120, 145)},
    '2': {'name': 'Lamento Andaluz',   'desc': 'Melancholy and tragic beauty',             'scale': 'harmonic_minor',       'is_minor': True,  'tension': 0.60, 'bpm_range': (95,  120)},
    '3': {'name': 'Misterio Nocturno', 'desc': 'Spanish night, modal mystery',             'scale': 'phrygian',             'is_minor': True,  'tension': 0.50, 'bpm_range': (90,  115)},
    '4': {'name': 'Nostalgia Gitana',  'desc': 'Passionate dorian yearning',               'scale': 'dorian',               'is_minor': True,  'tension': 0.55, 'bpm_range': (100, 125)},
    '5': {'name': 'Luz del Sol',       'desc': 'Radiant joy and warm morning sun',         'scale': 'ionian',               'is_minor': False, 'tension': 0.40, 'bpm_range': (110, 135)},
    '6': {'name': 'Brisa de Cadiz',    'desc': 'Warm ocean breeze with Spanish edge',      'scale': 'mixolydian',           'is_minor': False, 'tension': 0.50, 'bpm_range': (105, 130)},
    '7': {'name': 'Canto de Esperanza','desc': 'Hopeful and uplifting fantasy',            'scale': 'mixolydian',           'is_minor': False, 'tension': 0.45, 'bpm_range': (100, 125)},
    '8': {'name': 'Fuego de Sevilla',  'desc': 'Festive and energetic major drive',        'scale': 'double_harmonic_major','is_minor': False, 'tension': 0.70, 'bpm_range': (125, 145)},
    # ── Touching Spanish presets — modeled on test MIDI emotional profiles ──────
    '9': {'name': 'Alma Gitana',       'desc': 'Andalusian cadence — raw soulful descent','scale': 'phrygian_dominant',    'is_minor': True,  'tension': 0.65, 'bpm_range': (111, 130)},
    'A': {'name': 'Llanto del Sur',    'desc': 'Weeping south — harmonic minor lament',   'scale': 'harmonic_minor',       'is_minor': True,  'tension': 0.55, 'bpm_range': (100, 120)},
    'B': {'name': 'Camino de Sombras', 'desc': 'Path of shadows — dorian bittersweet',    'scale': 'dorian',               'is_minor': True,  'tension': 0.45, 'bpm_range': (95,  118)},
    'C': {'name': 'Serenata Oscura',   'desc': 'Dark serenade — natural minor nocturne',  'scale': 'natural_minor',        'is_minor': True,  'tension': 0.50, 'bpm_range': (100, 125)},
}

# ── TOUCHING SPANISH PROGRESSIONS — derived from test MIDI analysis ────────────
# These progressions reproduce the emotional DNA of the reference recordings.
TOUCHING_SPANISH_PROGRESSIONS = {
    'phrygian_dominant': [
        # Andalusian cadence variants (I→bVII→bVI→V) — the signature of test files 1,4,5
        {'chords': ['I', 'bVII', 'bVI', 'V'],         'label': 'Pure Andalusian',       'tension': 0.65},
        {'chords': ['I', 'bVI', 'bVII', 'I'],          'label': 'Circular Flamenco',     'tension': 0.60},
        {'chords': ['I', 'bII', 'bVII', 'I'],          'label': 'Phrygian Weep',         'tension': 0.70},
        {'chords': ['I', 'iv', 'bVII', 'I'],           'label': 'Gypsy Resolve',         'tension': 0.65},
        {'chords': ['I', 'bVI', 'iv', 'V'],            'label': 'Seville Descent',       'tension': 0.70},
        {'chords': ['I', 'bVII', 'bVI', 'bII'],        'label': 'Darkening Cadence',     'tension': 0.75},
        {'chords': ['I', 'iv', 'bVI', 'bVII'],         'label': 'Flamenco Soul',         'tension': 0.65},
        {'chords': ['bVI', 'bVII', 'I', 'bII'],        'label': 'Upward Longing',        'tension': 0.60},
        {'chords': ['I', 'bVII', 'bVI', 'bVII'],       'label': 'Andalusian Pulse',      'tension': 0.55},
        {'chords': ['I', 'bII', 'I', 'bVII'],          'label': 'Phrygian Breath',       'tension': 0.65},
    ],
    'harmonic_minor': [
        # Touching minor laments — test file 2, 6 character
        {'chords': ['i', 'VII', 'VI', 'V'],            'label': 'Classic Andalusian',    'tension': 0.60},
        {'chords': ['i', 'iv', 'V', 'i'],              'label': 'Lamento Cadence',       'tension': 0.55},
        {'chords': ['i', 'VI', 'III', 'V'],            'label': 'Romantic Sorrow',       'tension': 0.55},
        {'chords': ['i', 'iv', 'VII', 'III'],          'label': 'Fado Descent',          'tension': 0.50},
        {'chords': ['VI', 'VII', 'i', 'V'],            'label': 'Deceptive Longing',     'tension': 0.60},
        {'chords': ['i', 'III', 'VI', 'V'],            'label': 'Hopeful Grief',         'tension': 0.50},
        {'chords': ['i', 'VII', 'VI', 'VII'],          'label': 'Breathing Sorrow',      'tension': 0.55},
        {'chords': ['i', 'VI', 'VII', 'i'],            'label': 'Circular Lament',       'tension': 0.50},
        {'chords': ['i', 'iv', 'i', 'V'],              'label': 'Modal Weeping',         'tension': 0.60},
        {'chords': ['III', 'VII', 'i', 'VI'],          'label': 'Memory of Home',        'tension': 0.45},
    ],
    'dorian': [
        # Bittersweet dorian — test file 6 character
        {'chords': ['i', 'IV', 'bVII', 'i'],           'label': 'Dorian Soul',           'tension': 0.45},
        {'chords': ['i', 'ii', 'bVII', 'i'],           'label': 'Modal Longing',         'tension': 0.45},
        {'chords': ['i', 'IV', 'v', 'i'],              'label': 'Passionate Resolve',    'tension': 0.50},
        {'chords': ['i', 'bVII', 'IV', 'i'],           'label': 'Bittersweet Return',    'tension': 0.40},
        {'chords': ['i', 'ii', 'IV', 'bVII'],          'label': 'Yearning Ascent',       'tension': 0.50},
        {'chords': ['bIII', 'IV', 'i', 'bVII'],        'label': 'Dorian Nostalgia',      'tension': 0.45},
        {'chords': ['i', 'IV', 'bIII', 'bVII'],        'label': 'Gitana Walk',           'tension': 0.50},
        {'chords': ['i', 'v', 'IV', 'bVII'],           'label': 'Dorian Farewell',       'tension': 0.55},
    ],
    'natural_minor': [
        # Natural minor nocturne — test file 7 character
        {'chords': ['i', 'bVII', 'bVI', 'bVII'],       'label': 'Nocturne Pulse',        'tension': 0.45},
        {'chords': ['i', 'bIII', 'bVII', 'bVI'],       'label': 'Dark Wander',           'tension': 0.50},
        {'chords': ['i', 'iv', 'bVII', 'bVI'],         'label': 'Autumn Lament',         'tension': 0.50},
        {'chords': ['i', 'bVI', 'bIII', 'bVII'],       'label': 'Cinematic Ache',        'tension': 0.45},
        {'chords': ['i', 'bVII', 'iv', 'i'],           'label': 'Sombre Resolve',        'tension': 0.45},
        {'chords': ['bVI', 'bVII', 'i', 'bVII'],       'label': 'Moonlit Walk',          'tension': 0.40},
        {'chords': ['i', 'bIII', 'iv', 'bVII'],        'label': 'Lost Serenade',         'tension': 0.50},
        {'chords': ['i', 'iv', 'bVI', 'bVII'],         'label': 'Quiet Despair',         'tension': 0.55},
    ],
}

MINOR_ENGINE_MOODS = {
    '1': {
        'name': 'Lamento Andaluz', 'tension': 0.50, 'bpm_range': (92, 116),
        'progressions': [
            {'chords': ['i','VII','VI','V'],    'label':'Andalusian Lament'},
            {'chords': ['i','iv','V','i'],      'label':'Weeping Cadence'},
            {'chords': ['i','VI','iv','V'],     'label':'Romantic Sorrow'},
            {'chords': ['i','bII','i','V'],     'label':'Phrygian Cry'},
            {'chords': ['i','iv','VII','III'],  'label':'Fado Andaluz'},
            {'chords': ['VI','VII','i','V'],    'label':'Deceptive Longing'},
            {'chords': ['i','VI','VII','i'],    'label':'Circular Grief'},
            {'chords': ['i','iv','i','V'],      'label':'Old Lamento'}
        ]
    },
    '2': {
        'name': 'Serenata de Amor', 'tension': 0.38, 'bpm_range': (88, 112),
        'progressions': [
            {'chords': ['i','VI','III','VII'],  'label':'Tender Romance'},
            {'chords': ['i','iv','VII','III'],  'label':'Moonlit Serenade'},
            {'chords': ['i','III','VI','V'],    'label':'Passionate Resolve'},
            {'chords': ['i','VI','VII','i'],    'label':'Lovers Return'},
            {'chords': ['i','iv','i','V'],      'label':'Intimate Cadence'},
            {'chords': ['VI','VII','i','III'],  'label':'Warm Embrace'},
            {'chords': ['i','VII','VI','VII'],  'label':'Breathing Love'},
            {'chords': ['i','III','iv','VI'],   'label':'Soft Confession'}
        ]
    },
    '3': {
        'name': 'Fuego Gitano', 'tension': 0.76, 'bpm_range': (120, 145),
        'progressions': [
            {'chords': ['I','bVII','bVI','V'],  'label':'Pure Andalusian Fire'},
            {'chords': ['i','VII','VI','V'],    'label':'Minor Fire Descent'},
            {'chords': ['I','bII','bVII','I'],  'label':'Phrygian Blaze'},
            {'chords': ['i','bII','i','VII'],   'label':'Ritmo Gitano'},
            {'chords': ['i','iv','VI','VII'],   'label':'Flamenco Charge'},
            {'chords': ['i','VII','VI','VII'],  'label':'Burning Pulse'},
            {'chords': ['I','iv','bVI','bVII'], 'label':'Gypsy Soul'},
            {'chords': ['i','VI','bII','V'],    'label':'Neapolitan Fire'}
        ]
    },
    '4': {
        'name': 'Nostalgia Gitana', 'tension': 0.42, 'bpm_range': (94, 118),
        'progressions': [
            {'chords': ['i','III','VI','VII'],  'label':'Old Photograph'},
            {'chords': ['i','VII','III','VI'],  'label':'Wandering Memory'},
            {'chords': ['VI','VII','i','v'],    'label':'Reflective Road'},
            {'chords': ['i','VI','III','iv'],   'label':'Memory Lane'},
            {'chords': ['III','VII','i','VI'],  'label':'Faded Summer'},
            {'chords': ['i','iv','III','VII'],  'label':'Childhood Echo'},
            {'chords': ['VI','III','i','VII'],  'label':'Distant Home'},
            {'chords': ['i','VII','VI','III'],  'label':'Bittersweet Return'}
        ]
    },
    '5': {
        'name': 'Serenata de Granada', 'tension': 0.48, 'bpm_range': (96, 122),
        'progressions': [
            {'chords': ['i','VI','III','V'],    'label':'Granada Night'},
            {'chords': ['i','iv','VII','III'],  'label':'Balcony Serenade'},
            {'chords': ['i','bII','VII','i'],   'label':'Moorish Romance'},
            {'chords': ['i','VI','bII','V'],    'label':'Palace Cadence'},
            {'chords': ['III','VII','i','VI'],  'label':'Moonlit Memory'},
            {'chords': ['i','iv','V','i'],      'label':'Classical Serenade'},
            {'chords': ['VI','VII','i','V'],    'label':'Alhambra Longing'},
            {'chords': ['i','III','iv','V'],    'label':'Ornamental Resolve'}
        ]
    },
    '6': {
        'name': 'Camino de Sombras', 'tension': 0.82, 'bpm_range': (112, 138),
        'progressions': [
            {'chords': ['i','bII','i','VII'],   'label':'Shadow Road'},
            {'chords': ['i','VI','bII','i'],    'label':'Dark Descent'},
            {'chords': ['i','v','iv','V'],      'label':'Ominous Buildup'},
            {'chords': ['i','iv','bII','V'],    'label':'Gothic Andaluz'},
            {'chords': ['bII','i','bII','VII'], 'label':'Ritual Tension'},
            {'chords': ['i','VII','bII','i'],   'label':'Nocturnal Pursuit'},
            {'chords': ['i','v','bII','VII'],   'label':'Hidden Threat'},
            {'chords': ['i','VI','v','bII'],    'label':'Dark Oath'}
        ]
    }
}

MAJOR_ENGINE_MOODS = {
    '1': {
        'name': 'Fiesta de Sevilla', 'tension': 0.42, 'bpm_range': (112, 136),
        'progressions': [
            {'chords': ['I', 'IV', 'V', 'I'],        'label': 'Festival Cadence'},
            {'chords': ['I', 'bVII', 'IV', 'I'],     'label': 'Sevilla Mixolydian'},
            {'chords': ['I', 'V', 'IV', 'V'],        'label': 'Bright Palmas'},
            {'chords': ['I', 'IV', 'I', 'V'],        'label': 'Feria Dance'},
            {'chords': ['I', 'vi', 'IV', 'V'],       'label': 'Joyful Procession'},
            {'chords': ['I', 'ii', 'IV', 'V'],       'label': 'Danza Alegre'},
            {'chords': ['I', 'V', 'vi', 'IV'],       'label': 'Sunlit Anthem'},
            {'chords': ['I', 'bVII', 'I', 'IV'],     'label': 'Open Air Fiesta'}
        ]
    },
    '2': {
        'name': 'Brisa de Cadiz', 'tension': 0.32, 'bpm_range': (96, 120),
        'progressions': [
            {'chords': ['I', 'bVII', 'IV', 'I'],     'label': 'Coastal Breeze'},
            {'chords': ['I', 'IV', 'bVII', 'I'],     'label': 'Cadiz Harbor'},
            {'chords': ['I', 'V', 'IV', 'I'],        'label': 'Warm Horizon'},
            {'chords': ['I', 'ii', 'IV', 'I'],       'label': 'Gentle Tide'},
            {'chords': ['I', 'vi', 'IV', 'I'],       'label': 'Golden Shore'},
            {'chords': ['I', 'bVII', 'I', 'IV'],     'label': 'Ocean Walk'},
            {'chords': ['I', 'IV', 'I', 'bVII'],     'label': 'Sea Air'},
            {'chords': ['I', 'vi', 'ii', 'V'],       'label': 'Soft Optimism'}
        ]
    },
    '3': {
        'name': 'Sueno de Granada', 'tension': 0.26, 'bpm_range': (86, 112),
        'progressions': [
            {'chords': ['I', 'IV', 'I', 'IV'],       'label': 'Moonlit Courtyard'},
            {'chords': ['I', 'II', 'I', 'II'],       'label': 'Alhambra Dream'},
            {'chords': ['I', 'vi', 'iii', 'IV'],     'label': 'Dreamy Reflection'},
            {'chords': ['I', 'iii', 'IV', 'V'],      'label': 'Peaceful River'},
            {'chords': ['I', 'bVII', 'I', 'bVII'],   'label': 'Soft Mixolydian Drift'},
            {'chords': ['I', 'IV', 'V', 'I'],        'label': 'Garden Light'},
            {'chords': ['I', 'vi', 'IV', 'ii'],      'label': 'Floating Serenade'},
            {'chords': ['I', 'V', 'vi', 'iii'],      'label': 'Starlit Memory'}
        ]
    },
    '4': {
        'name': 'Gloria Iberica', 'tension': 0.68, 'bpm_range': (116, 142),
        'progressions': [
            {'chords': ['I', 'V', 'vi', 'IV'],       'label': 'Triumphant Lift'},
            {'chords': ['I', 'bVII', 'IV', 'I'],     'label': 'Iberian Anthem'},
            {'chords': ['I', 'V', 'IV', 'I'],        'label': 'Victory Call'},
            {'chords': ['I', 'IV', 'bVII', 'I'],     'label': 'Ascent to Glory'},
            {'chords': ['I', 'II', 'IV', 'I'],       'label': 'Golden Rise'},
            {'chords': ['I', 'V', 'vi', 'iii', 'IV', 'I', 'IV', 'V'], 'label': 'Royal Canon'},
            {'chords': ['I', 'bVI', 'bVII', 'I'],    'label': 'Majestic Fantasy'},
            {'chords': ['I', 'IV', 'V', 'I'],        'label': 'Noble Cadence'}
        ]
    },
    '5': {
        'name': 'Canto de Esperanza', 'tension': 0.40, 'bpm_range': (100, 126),
        'progressions': [
            {'chords': ['I', 'V', 'vi', 'IV'],       'label': 'Hopeful Song'},
            {'chords': ['I', 'vi', 'IV', 'V'],       'label': 'Rising Hope'},
            {'chords': ['I', 'IV', 'vi', 'V'],       'label': 'Open Heart'},
            {'chords': ['I', 'ii', 'IV', 'V'],       'label': 'Bright Resolve'},
            {'chords': ['I', 'V', 'I', 'IV'],        'label': 'Clear Morning'},
            {'chords': ['I', 'vi', 'ii', 'V'],       'label': 'Gentle Promise'},
            {'chords': ['I', 'IV', 'I', 'V'],        'label': 'Hopeful Return'},
            {'chords': ['I', 'bVII', 'IV', 'V'],     'label': 'Warm Horizon Lift'}
        ]
    },
    '6': {
        'name': 'Danza de Luz', 'tension': 0.50, 'bpm_range': (112, 138),
        'progressions': [
            {'chords': ['I', 'IV', 'V', 'IV'],       'label': 'Light Dance'},
            {'chords': ['I', 'V', 'IV', 'V'],        'label': 'Sparkling Steps'},
            {'chords': ['I', 'ii', 'IV', 'V'],       'label': 'Playful Motion'},
            {'chords': ['I', 'bVII', 'IV', 'I'],     'label': 'Folk Celebration'},
            {'chords': ['I', 'IV', 'I', 'bVII'],     'label': 'Lantern Dance'},
            {'chords': ['I', 'vi', 'IV', 'V'],       'label': 'Joyful Turn'},
            {'chords': ['I', 'V', 'vi', 'IV'],       'label': 'Radiant Pattern'},
            {'chords': ['I', 'IV', 'bVII', 'IV'],    'label': 'Danza Brillante'}
        ]
    }
}

# ── COMPOSITIONAL PROCEDURAL ALGORITHMS ───────────────────────────────────────

def generate_unique_progression(scale_name, is_minor, num_bars=8):
    """
    Generates a unique chord progression using scale-specific transition rules.
    Guarantees dominant tension build-up and tonic resolution at key cadences.
    """
    chords_pool = SCALE_CHORDS[scale_name]
    tonic = 'i' if 'i' in chords_pool else 'I'
    progression = [tonic]
    
    transitions = MINOR_TRANSITIONS if is_minor else MAJOR_TRANSITIONS
    
    for bar in range(1, num_bars):
        current = progression[-1]
        candidates = transitions.get(current, list(chords_pool.keys()))
        valid_candidates = [c for c in candidates if c in chords_pool]
        if not valid_candidates:
            valid_candidates = list(chords_pool.keys())
            
        # Cadence logic:
        # Penultimate bar builds dominant tension (V, bII, bVII, etc.)
        if bar == num_bars - 2:
            dominant_chords = ['V', 'bII', 'bVII', 'vii°', 'v°', 'ii°', 'iii°']
            doms = [c for c in dominant_chords if c in valid_candidates]
            next_chord = random.choice(doms) if doms else random.choice(valid_candidates)
        # Final bar resolves back to tonic
        elif bar == num_bars - 1:
            next_chord = tonic
        else:
            next_chord = random.choice(valid_candidates)
            
        progression.append(next_chord)
        
    return progression

def _slug(text):
    keep = []
    for char in str(text):
        keep.append(char if char.isalnum() or char in "#+-" else "_")
    return "_".join(part for part in "".join(keep).split("_") if part)


def _project_title():
    return f"{random.choice(PROJECT_ADJECTIVES)}_{random.choice(PROJECT_NOUNS)}"


def get_best_matching_chord_name(chord_sym, scale_name):
    """
    Finds the key in SCALE_CHORDS[scale_name] that matches the input Roman numeral chord.
    """
    pool = SCALE_CHORDS[scale_name]
    if chord_sym in pool:
        return chord_sym

    alias_candidates = {
        'i': ['I'],
        'I': ['i'],
        'ii': ['ii°', 'iio', 'bII'],
        'II': ['ii', 'bII', 'ii°'],
        'iio': ['ii°', 'ii', 'bII'],
        'ii°': ['iio', 'ii', 'bII'],
        'III': ['bIII', 'iii'],
        'iii': ['III', 'bIII', 'iii°'],
        'iii°': ['iii', 'III', 'bIII'],
        'iv': ['IV'],
        'IV': ['iv'],
        'v': ['V'],
        'V': ['v'],
        'VI': ['bVI', 'vi'],
        'vi': ['VI', 'bVI', 'vi°'],
        'vi°': ['vi', 'VI', 'bVI'],
        'VII': ['bVII', 'vii', 'vii°'],
        'vii': ['VII', 'bVII', 'vii°'],
        'vii°': ['vii', 'VII', 'bVII'],
        'bIII': ['III', 'iii'],
        'bVI': ['VI', 'vi'],
        'bVII': ['VII', 'vii'],
    }
    for candidate in alias_candidates.get(chord_sym, []):
        if candidate in pool:
            return candidate

    alt = chord_sym.lower() if chord_sym.isupper() else chord_sym.upper()
    if alt in pool:
        return alt
    base = chord_sym.replace('7', '').replace('maj', '').replace('°', '').replace('ii°', 'ii').replace('iii°', 'iii').replace('vi°', 'vi').replace('vii°', 'vii')
    if base in pool:
        return base
    base_alt = base.lower() if base.isupper() else base.upper()
    if base_alt in pool:
        return base_alt
    for prefix in ['b', '#']:
        if base.startswith(prefix):
            unprefixed = base[1:]
            if unprefixed in pool:
                return unprefixed
            unprefixed_alt = unprefixed.lower() if unprefixed.isupper() else unprefixed.upper()
            if unprefixed_alt in pool:
                return unprefixed_alt
    for k in pool.keys():
        if k.lower() == chord_sym.lower():
            return k
    fallback = 'i' if 'i' in pool else 'I'
    return fallback


def get_chord_triad_for_scale(chord_sym, scale_name):
    """
    Safely translates any Roman numeral chord (e.g. from Major/Minor engines)
    into the available chords for the target Spanish scale, ensuring no KeyErrors.
    """
    matched_name = get_best_matching_chord_name(chord_sym, scale_name)
    return SCALE_CHORDS[scale_name][matched_name]




def voice_guitar_chord(root_val, chord_notes, scale_notes=None):
    """
    Voices a chord as a clean nylon-guitar shape.
    Strummed sections use the whole voicing, so this deliberately avoids
    fixed open-string drones that can clash outside their home key.
    """
    chord_pcs = [(root_val + n) % 12 for n in chord_notes]
    if scale_notes is not None:
        scale_pcs = {(root_val + n) % 12 for n in scale_notes}
        chord_pcs = [pc for pc in chord_pcs if pc in scale_pcs]
    if not chord_pcs:
        chord_pcs = [(root_val + n) % 12 for n in chord_notes]

    root_pc = chord_pcs[0]
    third_pc = chord_pcs[1] if len(chord_pcs) > 1 else root_pc
    fifth_pc = chord_pcs[2] if len(chord_pcs) > 2 else root_pc
    upper_color_pc = third_pc if len(chord_pcs) > 1 else fifth_pc

    def _above(pc, minimum):
        pitch = pc
        while pitch < minimum:
            pitch += 12
        return pitch

    bass = _above(root_pc, 40)
    if bass > 52:
        bass -= 12

    voicing = [bass]
    for pc, minimum in [
        (third_pc, bass + 3),
        (fifth_pc, bass + 7),
        (root_pc, bass + 12),
        (upper_color_pc, bass + 15),
    ]:
        pitch = _above(pc, minimum)
        while pitch in voicing:
            pitch += 12
        if pitch <= 84:
            voicing.append(pitch)

    return sorted(voicing)


def voice_chord_smooth(prev_voicing, chord_notes, target_octave=3):
    """
    Finds the optimal voice-led inversion of a chord that minimizes distance
    from the previous chord's voicing, preventing jarring register jumps in the Pad.
    """
    if not prev_voicing:
        base = target_octave * 12 + 12
        voicing = []
        for pc in sorted(chord_notes):
            p = pc
            while p < base:
                p += 12
            voicing.append(p)
        return sorted(voicing)
        
    best_voicing = None
    min_dist = float('inf')
    
    import itertools
    for perm in itertools.permutations(chord_notes):
        candidate = []
        for i, pc in enumerate(perm):
            target_pitch = prev_voicing[i]
            best_pitch = pc
            best_p_dist = float('inf')
            for oct_val in range(2, 7):
                p = pc + oct_val * 12
                dist = abs(p - target_pitch)
                if dist < best_p_dist:
                    best_p_dist = dist
                    best_pitch = p
            candidate.append(best_pitch)
            
        candidate_sorted = sorted(candidate)
        total_dist = sum(abs(a - b) for a, b in zip(candidate_sorted, prev_voicing))
        if total_dist < min_dist:
            min_dist = total_dist
            best_voicing = candidate_sorted
            
    return best_voicing

# ── PERFORMANCE EVENT GENERATORS ──────────────────────────────────────────────

def generate_guitar_arpeggio(root_val, progression, scale_chords, scale_notes, tension, num_bars, tpb):
    """
    Generates realistic, sophisticated classical-Spanish nylon guitar arpeggios,
    compas, rasgueado strums, and bass-line counterpoints on Channel 0.
    """
    events = []
    
    for bar in range(num_bars):
        bar_start = bar * 4 * tpb
        chord_name = progression[bar % len(progression)]
        chord_notes = scale_chords[chord_name]
        voicing = voice_guitar_chord(root_val, chord_notes, scale_notes)
        
        # Pick pattern based on mood tension
        if tension >= 0.70:
            pattern = random.choice(['triplets', 'rasgueado_strum', 'flamenco_compas'])
        elif tension >= 0.45:
            pattern = random.choice(['roll_8th', 'sync_8th', 'flamenco_compas', 'malaguena_bass'])
        else:
            pattern = random.choice(['slow_fingerstyle', 'malaguena_bass', 'roll_8th'])
            
        vel_base = int(62 + tension * 22)
        
        if pattern == 'roll_8th':
            # Straight eighths: p-i-m-a arpeggio sweep
            step_ticks = tpb // 2
            pick_seq = [0, 1, 2, 3, 4, 3, 2, 1]
            for step in range(8):
                tick = bar_start + step * step_ticks
                note_idx = pick_seq[step] % len(voicing)
                note = voicing[note_idx]
                
                stagger = random.randint(-4, 4)
                vel = vel_base + random.choice([-5, -2, 0, 2, 5])
                if note_idx == 0:
                    vel += 12  # Accentuated bass
                vel = max(10, min(127, vel))
                
                dur = int(tpb * 1.5)  # Let notes ring out
                events.append((tick + stagger, 'on', note, vel, 0))
                events.append((tick + stagger + dur, 'off', note, 0, 0))
                
        elif pattern == 'sync_8th':
            # Syncopated fingerstyle
            step_ticks = tpb // 2
            pick_seq = [0, 2, 1, 3, 2, 4, 3, 1]
            for step in range(8):
                tick = bar_start + step * step_ticks
                note_idx = pick_seq[step] % len(voicing)
                note = voicing[note_idx]
                
                stagger = random.randint(-4, 4)
                vel = vel_base + random.choice([-4, -1, 1, 4])
                if note_idx == 0:
                    vel += 10
                vel = max(10, min(127, vel))
                
                dur = int(tpb * 1.25)
                events.append((tick + stagger, 'on', note, vel, 0))
                events.append((tick + stagger + dur, 'off', note, 0, 0))
                
        elif pattern == 'triplets':
            # Rapid 12/8 Flamenco triplets
            step_ticks = tpb // 3
            pick_seq = [0, 1, 2, 3, 2, 1, 4, 3, 2, 3, 2, 1]
            for step in range(12):
                tick = bar_start + step * step_ticks
                note_idx = pick_seq[step] % len(voicing)
                note = voicing[note_idx]
                
                stagger = random.randint(-3, 3)
                vel = vel_base - 4 + random.choice([-3, 0, 3])
                if note_idx == 0:
                    vel += 10
                vel = max(10, min(127, vel))
                
                dur = int(tpb * 0.95)
                events.append((tick + stagger, 'on', note, vel, 0))
                events.append((tick + stagger + dur, 'off', note, 0, 0))
                
        elif pattern == 'flamenco_compas':
            # 4/4 syncopated flamenco rhythm (accents on offbeats)
            # Beats: 0 (bass), 0.5 (mid), 1.0 (mid), 1.5 (high accent), 2.0 (bass), 2.5 (high accent), 3.0 (mid), 3.5 (high accent)
            steps = [
                (0.0, 0, 1.2, True),   # beat, voicing_index, duration, is_accent
                (0.5, 1, 0.4, False),
                (1.0, 2, 0.4, False),
                (1.5, 3, 0.8, True),
                (2.0, 0, 0.9, False),
                (2.5, 4, 0.9, True),
                (3.0, 2, 0.4, False),
                (3.5, 3, 1.2, True)
            ]
            for beat, idx, dur_beats, accent in steps:
                tick = bar_start + int(beat * tpb)
                note_idx = idx % len(voicing)
                note = voicing[note_idx]
                
                stagger = random.randint(-4, 4)
                vel = vel_base + (14 if accent else -6) + random.randint(-3, 3)
                vel = max(15, min(127, vel))
                
                dur = int(dur_beats * tpb)
                events.append((tick + stagger, 'on', note, vel, 0))
                events.append((tick + stagger + dur, 'off', note, 0, 0))
                
        elif pattern == 'rasgueado_strum':
            # Flamenco rasgueado rolls on beat 0 and beat 2, syncopated 16th picks in between
            
            # Strum rolls
            for beat in [0.0, 2.0]:
                strum_start = bar_start + int(beat * tpb)
                for i, note in enumerate(voicing):
                    # Stagger each string strike by 16 ticks (~20ms)
                    tick = strum_start + i * 16
                    vel = vel_base + 8 + i * 4 + random.randint(-4, 4)
                    vel = max(20, min(127, vel))
                    dur = int(1.4 * tpb)
                    events.append((tick, 'on', note, vel, 0))
                    events.append((tick + dur, 'off', note, 0, 0))
            
            # Mid-strum picking
            picks = [
                (1.0, 3, 0.4),
                (1.5, 4, 0.4),
                (3.0, 3, 0.4),
                (3.5, 2, 0.4)
            ]
            for beat, idx, dur_beats in picks:
                tick = bar_start + int(beat * tpb)
                note_idx = idx % len(voicing)
                note = voicing[note_idx]
                
                stagger = random.randint(-2, 2)
                vel = vel_base - 5 + random.randint(-3, 3)
                vel = max(10, min(127, vel))
                dur = int(dur_beats * tpb * 1.1)
                events.append((tick + stagger, 'on', note, vel, 0))
                events.append((tick + stagger + dur, 'off', note, 0, 0))
                
        elif pattern == 'malaguena_bass':
            # Melodic bass walk in the thumb, high string responses
            chord_pcs = [(root_val + n) % 12 for n in chord_notes]
            scale_pcs = {(root_val + n) % 12 for n in scale_notes}
            root_bass = voicing[0]
            fifth_bass = _pitch_in_range_for_pc(chord_pcs[2 if len(chord_pcs) > 2 else 0], 40, 55, root_bass)
            next_chord = scale_chords[progression[(bar + 1) % len(progression)]]
            next_root = _pitch_in_range_for_pc((root_val + next_chord[0]) % 12, 40, 55, root_bass)
            approach = _scale_approach_pitch(root_bass, next_root, root_val, scale_notes, 40, 55)
            if approach % 12 not in scale_pcs:
                approach = root_bass
            
            steps = [
                (0.0, 'bass', root_bass, 1.8, True),
                (0.5, 'treble', voicing[1:4], 0.4, False),
                (1.0, 'treble', voicing[2:5], 0.8, False),
                (2.0, 'bass', random.choice([root_bass, fifth_bass, approach]), 1.8, True),
                (2.5, 'treble', voicing[1:4], 0.4, False),
                (3.0, 'treble', voicing[2:5], 0.8, False)
            ]
            for beat, kind, val, dur_beats, is_bass in steps:
                tick = bar_start + int(beat * tpb)
                stagger = random.randint(-4, 4)
                dur = int(dur_beats * tpb)
                
                if is_bass:
                    vel = vel_base + 12 + random.randint(-4, 4)
                    vel = max(20, min(127, vel))
                    events.append((tick + stagger, 'on', val, vel, 0))
                    events.append((tick + stagger + dur, 'off', val, 0, 0))
                else:
                    for i, note in enumerate(val):
                        tick_strum = tick + i * 12
                        vel = vel_base - 8 + random.randint(-3, 3)
                        vel = max(10, min(127, vel))
                        events.append((tick_strum + stagger, 'on', note, vel, 0))
                        events.append((tick_strum + stagger + dur, 'off', note, 0, 0))
                        
        else: # slow_fingerstyle
            # Sparse classical statement
            steps = [
                (0.0, 0, 2.0),
                (0.5, 1, 1.0),
                (1.0, 2, 1.0),
                (1.5, 3, 1.0),
                (2.0, 0, 2.0),
                (2.5, 2, 1.0),
                (3.0, 3, 1.0),
                (3.5, 4, 1.0)
            ]
            for beat, idx, dur_beats in steps:
                tick = bar_start + int(beat * tpb)
                note_idx = idx % len(voicing)
                note = voicing[note_idx]
                
                stagger = random.randint(-5, 5)
                vel = vel_base + random.choice([-6, -2, 2, 6])
                if note_idx == 0:
                    vel += 8
                vel = max(10, min(127, vel))
                
                dur = int(dur_beats * tpb * 1.3)
                events.append((tick + stagger, 'on', note, vel, 0))
                events.append((tick + stagger + dur, 'off', note, 0, 0))
                
    return events


def generate_counter_melody(root_val, progression, scale_chords, scale_notes, tension, num_bars, tpb):
    """
    Touching counter-melody biased toward stepwise motion, chord-tone landings,
    and emotional descending/arch contours — modeled on the test MIDI profiles.
    """
    events = []

    # Build pitch pool in melody register — wide range matching test files (47-84)
    melody_pitches = []
    for oct_offset in [-24, -12, 0, 12, 24]:
        for degree in scale_notes:
            p = root_val + degree + oct_offset
            if 52 <= p <= 84:
                melody_pitches.append(p)
    melody_pitches = sorted(list(set(melody_pitches)))
    if not melody_pitches:
        melody_pitches = [root_val + d for d in scale_notes]

    # Start in mid register
    cur_idx = len(melody_pitches) // 2
    vel_base = int(68 + tension * 24)

    def _chord_tones_for_bar(bar):
        chord_name = progression[bar % len(progression)]
        chord_pts = scale_chords[chord_name]
        tones = []
        for oct_offset in [-12, 0, 12]:
            for n in chord_pts:
                p = root_val + n + oct_offset
                if p in melody_pitches:
                    tones.append(p)
        return tones if tones else melody_pitches[:3]

    def _emit(tick, pitch, vel, dur_ticks):
        p = max(0, min(127, pitch))
        v = max(20, min(127, vel))
        stagger = random.randint(-4, 4)
        events.append((tick + stagger, 'on', p, v, 1))
        events.append((tick + stagger + max(10, dur_ticks - 12), 'off', p, 0, 1))

    def _snap_to_chord(chord_tones):
        """Move cur_idx to nearest chord tone."""
        nonlocal cur_idx
        if not chord_tones:
            return
        best = min(chord_tones, key=lambda p: abs(p - melody_pitches[cur_idx]))
        if best in melody_pitches:
            cur_idx = melody_pitches.index(best)

    # ── ALGORITHM 1: Touching stepwise descent (Andalusian DNA) ──────────────
    def _algo_stepwise_descent(bar_start, chord_tones):
        nonlocal cur_idx
        # Land on a chord tone peak, then step down over the bar
        if chord_tones:
            peak = max(chord_tones)
            if peak in melody_pitches:
                cur_idx = melody_pitches.index(peak)
        n_steps = random.choice([4, 5, 6])
        step_beats = 4.0 / n_steps
        for s in range(n_steps):
            tick = bar_start + int(s * step_beats * tpb)
            vel = vel_base + random.randint(-6, 6)
            if s == 0:
                vel += 10  # accent the peak
            # Snap to chord tone on downbeat
            if s % 2 == 0 and chord_tones:
                nearby = [p for p in chord_tones if abs(p - melody_pitches[cur_idx]) <= 4]
                if nearby:
                    ct = min(nearby, key=lambda p: abs(p - melody_pitches[cur_idx]))
                    cur_idx = melody_pitches.index(ct) if ct in melody_pitches else cur_idx
            dur = int(step_beats * tpb * 0.88)
            _emit(tick, melody_pitches[cur_idx], vel, dur)
            # Step down 1-2 degrees
            step = random.choice([-2, -1, -1, -1, -2])
            cur_idx = max(0, cur_idx + step)

    # ── ALGORITHM 2: Arch contour (rise then fall — vocal-style) ─────────────
    def _algo_arch(bar_start, chord_tones):
        nonlocal cur_idx
        n = random.choice([5, 6, 7])
        half = n // 2
        if chord_tones:
            peak_target = random.choice(chord_tones)
            if peak_target in melody_pitches:
                peak_idx = melody_pitches.index(peak_target)
            else:
                peak_idx = min(cur_idx + 3, len(melody_pitches) - 1)
        else:
            peak_idx = min(cur_idx + 3, len(melody_pitches) - 1)

        step_beats = 4.0 / n
        for s in range(n):
            tick = bar_start + int(s * step_beats * tpb)
            if s <= half:
                target_idx = cur_idx + (peak_idx - cur_idx) * s // max(1, half)
            else:
                target_idx = peak_idx - (peak_idx - cur_idx) * (s - half) // max(1, n - half)
            target_idx = max(0, min(len(melody_pitches) - 1, target_idx))
            vel = vel_base + (8 if s == half else -4) + random.randint(-4, 4)
            dur = int(step_beats * tpb * 0.85)
            _emit(tick, melody_pitches[target_idx], vel, dur)
            cur_idx = target_idx

    # ── ALGORITHM 3: Long notes with ornament (classical Spanish sustain) ─────
    def _algo_sustained_ornament(bar_start, chord_tones):
        nonlocal cur_idx
        _snap_to_chord(chord_tones)
        main_note = melody_pitches[cur_idx]
        # Play main note for 2 beats
        vel = vel_base + 8 + random.randint(-4, 4)
        _emit(bar_start, main_note, vel, int(2.0 * tpb * 0.92))
        # Ornament: quick neighbor note then back
        neighbor_idx = cur_idx + random.choice([-1, 1, 2, -2])
        neighbor_idx = max(0, min(len(melody_pitches) - 1, neighbor_idx))
        _emit(bar_start + int(2.1 * tpb), melody_pitches[neighbor_idx], vel - 8, int(0.35 * tpb))
        # Resolve to chord tone for second half
        if chord_tones:
            resolve = min(chord_tones, key=lambda p: abs(p - main_note))
            if resolve in melody_pitches:
                cur_idx = melody_pitches.index(resolve)
        _emit(bar_start + int(2.5 * tpb), melody_pitches[cur_idx], vel - 4, int(1.4 * tpb * 0.9))

    # ── ALGORITHM 4: Call and response (2-bar emotional dialogue) ────────────
    def _algo_call_response(bar_start, chord_tones):
        nonlocal cur_idx
        # Call: 3 notes ascending into beat 2
        call_start = cur_idx
        call_peak = min(call_start + random.randint(2, 4), len(melody_pitches) - 1)
        for s in range(3):
            idx = call_start + (call_peak - call_start) * s // 2
            idx = max(0, min(len(melody_pitches) - 1, idx))
            tick = bar_start + int(s * 0.5 * tpb)
            vel = vel_base - 4 + s * 4 + random.randint(-3, 3)
            _emit(tick, melody_pitches[idx], vel, int(0.45 * tpb))
        cur_idx = call_peak
        # Response: step back down with longer notes
        if chord_tones:
            _snap_to_chord(chord_tones)
        response_steps = random.choice([2, 3])
        for s in range(response_steps):
            tick = bar_start + int((1.5 + s * 0.8) * tpb)
            vel = vel_base - 6 + random.randint(-4, 4)
            dur = int(0.75 * tpb * 0.9)
            _emit(tick, melody_pitches[cur_idx], vel, dur)
            cur_idx = max(0, cur_idx - random.choice([1, 2]))

    # ── ALGORITHM 5: Tremolo swell (one pitch, crescendo — test file 3 style) ─
    def _algo_tremolo(bar_start, chord_tones):
        nonlocal cur_idx
        _snap_to_chord(chord_tones)
        pitch = melody_pitches[cur_idx]
        n_rep = random.choice([10, 12, 14])
        rep_dur = int(3.6 * tpb / n_rep)
        for r in range(n_rep):
            pct = r / float(n_rep)
            v = int((vel_base - 22) + pct * 38) + random.randint(-2, 2)
            v = max(20, min(127, v))
            _emit(bar_start + r * rep_dur, pitch, v, rep_dur - 6)

    # ── ALGORITHM 6: Pentatonic grace run (flamenco flourish) ────────────────
    def _algo_flamenco_run(bar_start, chord_tones):
        nonlocal cur_idx
        # Build pentatonic from scale notes (degrees 0,2,4,7,9)
        pent_degrees = [scale_notes[i] for i in [0, 1, 2, 4, 5] if i < len(scale_notes)]
        pent_pitches = []
        for oct_off in [-12, 0, 12]:
            for d in pent_degrees:
                p = root_val + d + oct_off
                if 52 <= p <= 84:
                    pent_pitches.append(p)
        pent_pitches = sorted(set(pent_pitches))
        if not pent_pitches:
            pent_pitches = melody_pitches

        # Start run from a high position, descend quickly
        start_idx = min(len(pent_pitches) - 1, len(pent_pitches) * 3 // 4)
        run_len = random.choice([5, 6, 7])
        step_ticks = int(0.5 * tpb)
        for s in range(run_len):
            idx = max(0, start_idx - s)
            tick = bar_start + s * step_ticks
            vel = vel_base + 6 - s * 2 + random.randint(-3, 3)
            vel = max(20, min(127, vel))
            _emit(tick, pent_pitches[idx], vel, int(step_ticks * 0.8))
        cur_idx = melody_pitches.index(min(melody_pitches, key=lambda p: abs(p - pent_pitches[max(0, start_idx - run_len + 1)])))

    # ── Selection weights biased by tension ───────────────────────────────────
    algos = [
        _algo_stepwise_descent,   # 0 — most "touching" — high weight
        _algo_arch,               # 1
        _algo_sustained_ornament, # 2
        _algo_call_response,      # 3
        _algo_tremolo,            # 4
        _algo_flamenco_run,       # 5
    ]
    if tension >= 0.65:
        weights = [3, 2, 2, 2, 3, 4]
    elif tension >= 0.45:
        weights = [4, 3, 3, 3, 1, 2]
    else:
        weights = [4, 3, 4, 2, 1, 1]  # bias descent and sustain for touching/lyrical

    # Phrasing: rest 1 in 5 bars naturally
    last_algo = -1
    for bar in range(num_bars):
        if bar > 0 and bar % 4 == 2 and random.random() < 0.25:
            continue  # breath rest
        bar_start = bar * 4 * tpb
        chord_tones = _chord_tones_for_bar(bar)
        w = list(weights)
        if last_algo >= 0:
            w[last_algo] = max(0, w[last_algo] - 2)
        algo_idx = random.choices(range(len(algos)), weights=w, k=1)[0]
        last_algo = algo_idx
        algos[algo_idx](bar_start, chord_tones)

    return events



    cur_idx = len(melody_pitches) // 2
    vel_base = int(72 + tension * 28)

    # Build chord-tone lookup per bar
    def _chord_tones_for_bar(bar):
        chord_name = progression[bar % len(progression)]
        chord_pts = scale_chords[chord_name]
        tones = []
        for oct_offset in [-12, 0, 12]:
            for n in chord_pts:
                p = root_val + n + oct_offset
                if p in melody_pitches:
                    tones.append(p)
        return tones if tones else melody_pitches

    # Phrasing mask — rest some bars for breathing
    phrasing_mask = []
    for b in range(num_bars):
        if b % 4 == 2:
            phrasing_mask.append(random.random() < 0.3)
        elif b % 8 == 5:
            phrasing_mask.append(random.random() < 0.4)
        else:
            phrasing_mask.append(True)

    # ── Algorithm library ─────────────────────────────────────────

    def _emit(tick, pitch, vel, dur_ticks):
        """Helper to emit a note_on/off pair with clamping."""
        p = max(0, min(127, pitch))
        v = max(20, min(127, vel))
        stagger = random.randint(-5, 5)
        events.append((tick + stagger, 'on', p, v, 1))
        events.append((tick + stagger + max(10, dur_ticks - 10), 'off', p, 0, 1))

    def _algo_arch_contour(bar_start, chord_tones):
        """Rising-then-falling melodic arch (classic vocal contour)."""
        nonlocal cur_idx
        target_peak = random.choice(chord_tones) if chord_tones else melody_pitches[-2]
        peak_idx = melody_pitches.index(target_peak) if target_peak in melody_pitches else len(melody_pitches) - 2
        start_idx = max(0, peak_idx - random.randint(3, 5))
        end_idx = max(0, peak_idx - random.randint(1, 3))

        # Number of notes in phrase
        n_notes = random.choice([5, 6, 7, 8])
        indices = []
        # Rise
        rise_count = n_notes // 2 + 1
        for i in range(rise_count):
            idx = start_idx + int((peak_idx - start_idx) * i / max(1, rise_count - 1))
            indices.append(max(0, min(len(melody_pitches) - 1, idx)))
        # Fall
        for i in range(1, n_notes - rise_count + 1):
            idx = peak_idx - int((peak_idx - end_idx) * i / max(1, n_notes - rise_count))
            indices.append(max(0, min(len(melody_pitches) - 1, idx)))

        beat_dur = 4.0 / n_notes
        for i, idx in enumerate(indices):
            tick = bar_start + int(i * beat_dur * tpb)
            dur = int(beat_dur * tpb * random.uniform(0.85, 1.1))
            vel = vel_base + random.randint(-6, 6)
            if i == rise_count - 1:
                vel += 10  # peak accent
            _emit(tick, melody_pitches[idx], vel, dur)
        cur_idx = indices[-1] if indices else cur_idx

    def _algo_descending_lament(bar_start, chord_tones):
        """Sighing descending line — very Spanish/emotional."""
        nonlocal cur_idx
        start_idx = min(len(melody_pitches) - 1, cur_idx + random.randint(2, 5))
        end_idx = max(0, start_idx - random.randint(4, 7))
        n_notes = start_idx - end_idx + 1
        if n_notes < 3:
            n_notes = 4
            start_idx = min(len(melody_pitches) - 1, end_idx + 3)

        durations = random.choice([
            [1.5, 1.0, 0.5, 1.0],
            [1.0, 1.0, 1.0, 1.0],
            [2.0, 0.5, 0.5, 1.0],
            [0.5, 0.5, 1.0, 0.5, 1.0, 0.5],
            [1.0, 0.5, 0.5, 0.5, 0.5, 1.0],
        ])
        beat_pos = 0.0
        for i, dur in enumerate(durations):
            if beat_pos >= 4.0:
                break
            idx = start_idx - int((start_idx - end_idx) * i / max(1, len(durations) - 1))
            idx = max(0, min(len(melody_pitches) - 1, idx))
            tick = bar_start + int(beat_pos * tpb)
            vel = vel_base + 6 - i * 2 + random.randint(-3, 3)
            _emit(tick, melody_pitches[idx], vel, int(dur * tpb * 0.9))
            beat_pos += dur
        cur_idx = end_idx

    def _algo_call_response(bar_start, chord_tones):
        """Two-phrase call-and-response: short motif then varied answer."""
        nonlocal cur_idx
        # Call (beats 0-1.5)
        call_notes = random.randint(2, 4)
        call_pitches = []
        idx = cur_idx
        for _ in range(call_notes):
            idx = max(0, min(len(melody_pitches) - 1, idx + random.choice([-2, -1, 1, 2])))
            call_pitches.append(idx)

        step = 1.5 / call_notes
        for i, pidx in enumerate(call_pitches):
            tick = bar_start + int(i * step * tpb)
            _emit(tick, melody_pitches[pidx], vel_base + random.randint(-4, 4), int(step * tpb * 0.85))

        # Response (beats 2-4) — inverted/varied
        resp_start = bar_start + int(2.0 * tpb)
        resp_notes = random.randint(2, 5)
        resp_step = 2.0 / resp_notes
        resp_idx = call_pitches[-1] if call_pitches else cur_idx
        for i in range(resp_notes):
            # Contrary motion or embellishment
            direction = -1 if random.random() < 0.6 else 1
            resp_idx = max(0, min(len(melody_pitches) - 1, resp_idx + direction * random.randint(1, 3)))
            tick = resp_start + int(i * resp_step * tpb)
            vel = vel_base + random.randint(-5, 5)
            if i == resp_notes - 1:
                # Resolve to chord tone
                ct = random.choice(chord_tones)
                if ct in melody_pitches:
                    resp_idx = melody_pitches.index(ct)
            _emit(tick, melody_pitches[resp_idx], vel, int(resp_step * tpb * 0.9))
        cur_idx = resp_idx

    def _algo_pentatonic_run(bar_start, chord_tones):
        """Fast scalar run using pentatonic subset — flamenco flourish."""
        nonlocal cur_idx
        # Build pentatonic subset from scale
        pent_intervals = [0, 2, 4, 5, 6]  # pick 5 from the 7-note scale
        if len(scale_notes) >= 5:
            pent_degrees = [scale_notes[i % len(scale_notes)] for i in pent_intervals]
        else:
            pent_degrees = scale_notes
        pent_pitches = [p for p in melody_pitches if (p - root_val) % 12 in pent_degrees]
        if len(pent_pitches) < 4:
            pent_pitches = melody_pitches

        # Run direction
        ascending = random.random() < 0.5
        n_notes = random.choice([6, 8, 10, 12])
        start_idx = random.randint(0, max(0, len(pent_pitches) - n_notes)) if ascending else random.randint(min(n_notes, len(pent_pitches) - 1), len(pent_pitches) - 1)

        run_dur = random.uniform(1.5, 3.0)  # beats for the run
        note_dur = run_dur / n_notes
        rest_after = 4.0 - run_dur
        run_start_beat = random.uniform(0, max(0, rest_after))

        for i in range(n_notes):
            if ascending:
                idx = min(len(pent_pitches) - 1, start_idx + i)
            else:
                idx = max(0, start_idx - i)
            tick = bar_start + int((run_start_beat + i * note_dur) * tpb)
            vel = vel_base - 8 + int(12 * (i / max(1, n_notes - 1))) + random.randint(-2, 2)
            _emit(tick, pent_pitches[idx], vel, int(note_dur * tpb * 0.8))

        cur_idx = melody_pitches.index(pent_pitches[min(idx, len(pent_pitches) - 1)]) if pent_pitches[min(idx, len(pent_pitches) - 1)] in melody_pitches else cur_idx

    def _algo_rhythmic_motif(bar_start, chord_tones):
        """Short rhythmic cell repeated with pitch variation — memorable hook."""
        nonlocal cur_idx
        # Define a rhythmic cell (in beats)
        cells = [
            [0.5, 0.25, 0.25, 1.0],
            [0.75, 0.25, 0.5, 0.5],
            [1.0, 0.5, 0.5],
            [0.25, 0.25, 0.5, 0.5, 0.5],
            [0.5, 0.5, 0.25, 0.25, 0.5],
        ]
        cell = random.choice(cells)
        cell_len = sum(cell)

        beat_pos = 0.0
        repetition = 0
        while beat_pos < 3.8:
            for dur in cell:
                if beat_pos >= 4.0:
                    break
                # Vary pitch each repetition
                step = random.choice([-2, -1, 0, 1, 2])
                if repetition > 0 and random.random() < 0.4:
                    # Transpose motif up/down
                    step = random.choice([-3, -2, 2, 3])
                cur_idx = max(0, min(len(melody_pitches) - 1, cur_idx + step))

                # Snap to chord tone occasionally
                if random.random() < 0.3:
                    ct = random.choice(chord_tones)
                    if ct in melody_pitches:
                        cur_idx = melody_pitches.index(ct)

                tick = bar_start + int(beat_pos * tpb)
                vel = vel_base + random.randint(-5, 5)
                if beat_pos % cell_len < 0.01:
                    vel += 6  # downbeat accent
                _emit(tick, melody_pitches[cur_idx], vel, int(dur * tpb * 0.85))
                beat_pos += dur
            repetition += 1

    def _algo_tremolo_swell(bar_start, chord_tones):
        """Sustained tremolo swell on a single pitch — intense Spanish guitar effect."""
        nonlocal cur_idx
        pitch = random.choice(chord_tones)
        if pitch in melody_pitches:
            cur_idx = melody_pitches.index(pitch)

        # Grace note slide into the main pitch
        grace = pitch - random.choice([1, 2])
        grace_dur = tpb // 8
        _emit(bar_start, grace, vel_base - 15, grace_dur)

        # Tremolo: rapid repeated notes with crescendo
        trem_start = bar_start + grace_dur + 5
        n_repeats = random.choice([12, 16, 20])
        total_dur = int(3.5 * tpb)
        rep_dur = total_dur // n_repeats

        for r in range(n_repeats):
            progress = r / float(n_repeats)
            r_vel = int((vel_base - 20) + progress * 35)
            r_vel = max(20, min(127, r_vel)) + random.randint(-2, 2)
            r_vel = max(20, min(127, r_vel))
            r_tick = trem_start + r * rep_dur
            _emit(r_tick, pitch, r_vel, rep_dur - 8)


def _pitch_in_range_for_pc(pc, low=40, high=59, prev_pitch=None):
    candidates = [p for p in range(low, high + 1) if p % 12 == pc % 12]
    if not candidates:
        p = pc
        while p < low:
            p += 12
        while p > high:
            p -= 12
        return max(0, min(127, p))
    if prev_pitch is None:
        center = (low + high) // 2
        return min(candidates, key=lambda p: abs(p - center))
    return min(candidates, key=lambda p: abs(p - prev_pitch))


def _scale_approach_pitch(current_pitch, target_pitch, root_val, scale_notes, low=40, high=59):
    scale_pcs = {(root_val + degree) % 12 for degree in scale_notes}
    direction = 1 if target_pitch >= current_pitch else -1
    search = range(current_pitch + direction, target_pitch + direction, direction)
    for pitch in reversed(list(search)):
        if low <= pitch <= high and pitch % 12 in scale_pcs:
            return pitch

    chromatic = target_pitch - direction
    while chromatic < low:
        chromatic += 12
    while chromatic > high:
        chromatic -= 12
    return chromatic


def generate_bass_line(root_val, progression, scale_chords, scale_notes, tension, num_bars, tpb):
    """
    Generates a low guitar/acoustic-bass line on Channel 2.
    The patterns mirror the reference MIDIs: clear roots, octave/fifth answers,
    and occasional phrase-end approaches into the next chord.
    """
    events = []
    prev_pitch = None
    vel_base = int(68 + tension * 24)

    chord_roots = []
    chord_fifths = []
    for bar in range(num_bars):
        chord_name = progression[bar % len(progression)]
        chord_notes = scale_chords[chord_name]
        root_pc = (root_val + chord_notes[0]) % 12
        fifth_pc = (root_val + chord_notes[2 if len(chord_notes) > 2 else 0]) % 12
        chord_roots.append(root_pc)
        chord_fifths.append(fifth_pc)

    def _emit(tick, pitch, vel, dur_beats):
        stagger = random.randint(-3, 3)
        pitch = max(0, min(127, pitch))
        vel = max(24, min(127, vel))
        dur = max(20, int(dur_beats * tpb) - 12)
        events.append((tick + stagger, 'on', pitch, vel, 2))
        events.append((tick + stagger + dur, 'off', pitch, 0, 2))

    for bar in range(num_bars):
        bar_start = bar * 4 * tpb
        root_pitch = _pitch_in_range_for_pc(chord_roots[bar], prev_pitch=prev_pitch)
        fifth_pitch = _pitch_in_range_for_pc(chord_fifths[bar], prev_pitch=root_pitch)
        octave_root = root_pitch + 12 if root_pitch + 12 <= 59 else root_pitch
        next_root = _pitch_in_range_for_pc(chord_roots[(bar + 1) % num_bars], prev_pitch=root_pitch)

        if tension >= 0.68:
            pattern = random.choice(['compas_drive', 'anticipated_walk', 'root_fifth_pulse'])
        elif tension >= 0.45:
            pattern = random.choice(['root_fifth_pulse', 'halfbar_answer', 'anticipated_walk'])
        else:
            pattern = random.choice(['halfbar_answer', 'sustained_root', 'root_fifth_pulse'])

        if pattern == 'sustained_root':
            _emit(bar_start, root_pitch, vel_base + 4, 3.6)
            if random.random() < 0.45:
                approach = _scale_approach_pitch(root_pitch, next_root, root_val, scale_notes)
                _emit(bar_start + int(3.5 * tpb), approach, vel_base - 10, 0.45)

        elif pattern == 'halfbar_answer':
            _emit(bar_start, root_pitch, vel_base + 8, 1.75)
            answer = random.choice([fifth_pitch, octave_root, root_pitch])
            _emit(bar_start + int(2.0 * tpb), answer, vel_base, 1.55)
            if random.random() < 0.35:
                approach = _scale_approach_pitch(answer, next_root, root_val, scale_notes)
                _emit(bar_start + int(3.5 * tpb), approach, vel_base - 8, 0.42)

        elif pattern == 'anticipated_walk':
            _emit(bar_start, root_pitch, vel_base + 8, 1.0)
            _emit(bar_start + int(1.5 * tpb), fifth_pitch, vel_base - 2, 0.65)
            _emit(bar_start + int(2.5 * tpb), octave_root, vel_base - 4, 0.65)
            approach = _scale_approach_pitch(octave_root, next_root, root_val, scale_notes)
            _emit(bar_start + int(3.5 * tpb), approach, vel_base - 6, 0.42)

        elif pattern == 'compas_drive':
            steps = [
                (0.0, root_pitch, 0.82, 10),
                (1.0, fifth_pitch, 0.55, -2),
                (2.0, root_pitch, 0.82, 4),
                (3.0, random.choice([fifth_pitch, octave_root]), 0.52, -4),
                (3.5, _scale_approach_pitch(fifth_pitch, next_root, root_val, scale_notes), 0.38, -8),
            ]
            for beat, pitch, dur, vel_adj in steps:
                _emit(bar_start + int(beat * tpb), pitch, vel_base + vel_adj, dur)

        else:
            steps = [
                (0.0, root_pitch, 0.7, 8),
                (0.5, fifth_pitch, 0.45, -3),
                (1.0, root_pitch, 0.7, 2),
                (1.5, octave_root, 0.45, -5),
                (2.5, fifth_pitch, 0.55, -4),
                (3.0, root_pitch, 0.75, 0),
            ]
            for beat, pitch, dur, vel_adj in steps:
                _emit(bar_start + int(beat * tpb), pitch, vel_base + vel_adj, dur)

        prev_pitch = root_pitch

    return events


def _notes_from_events(events, channel):
    active = {}
    notes = []
    for tick, etype, pitch, vel, ch in sorted(events, key=lambda ev: (ev[0], ev[1])):
        if ch != channel:
            continue
        if etype == 'on' and vel > 0:
            active.setdefault(pitch, []).append((tick, vel))
        elif etype == 'off' and active.get(pitch):
            start, start_vel = active[pitch].pop(0)
            notes.append((start, tick, pitch, start_vel))
    return notes


def _active_pitch_near_tick(notes, tick, window_ticks):
    candidates = []
    for start, end, pitch, _vel in notes:
        if start - window_ticks <= tick <= end + window_ticks:
            candidates.append((abs(tick - start), pitch))
    if not candidates:
        return None
    return min(candidates)[1]


def _trumpet_pitch_candidates(root_val, chord_notes, scale_notes, low=58, high=82):
    scale_pcs = {(root_val + degree) % 12 for degree in scale_notes}
    chord_pcs = [(root_val + degree) % 12 for degree in chord_notes]
    pcs = [pc for pc in chord_pcs if pc in scale_pcs]
    if not pcs:
        pcs = chord_pcs
    return sorted(p for p in range(low, high + 1) if p % 12 in pcs)


def _choose_trumpet_harmony(candidates, reference_pitch, prev_pitch=None):
    if not candidates:
        return None

    consonant_classes = {3, 4, 7, 8, 9}
    avoid_classes = {0, 1, 2, 6, 10, 11}
    scored = []
    for pitch in candidates:
        score = 0
        if reference_pitch is not None:
            interval = abs(pitch - reference_pitch) % 12
            if interval in consonant_classes:
                score -= 55
            if interval in avoid_classes:
                score += 500
            if pitch == reference_pitch:
                score += 700
            if pitch > reference_pitch:
                score -= 8
            score += abs(pitch - reference_pitch) * 0.35
        else:
            score += abs(pitch - 70)
        if prev_pitch is not None:
            score += abs(pitch - prev_pitch) * 0.45
        scored.append((score + random.random() * 3, pitch))
    return min(scored)[1]


def _choose_trumpet_for_span(candidates, counter_notes, tick, dur_ticks, prev_pitch=None):
    reference_pitch = _active_pitch_near_tick(counter_notes, tick, int(0.6 * 480))
    if not candidates:
        return None

    scored = []
    for pitch in candidates:
        score = 0
        bad_overlaps = 0
        if prev_pitch is not None:
            score += abs(pitch - prev_pitch) * 0.45
        if reference_pitch is not None:
            interval = abs(pitch - reference_pitch) % 12
            if interval in {3, 4, 7, 8, 9}:
                score -= 35
            if interval in {1, 2, 6, 10, 11} or pitch == reference_pitch:
                score += 400
                bad_overlaps += 1

        for start, end, counter_pitch, _vel in counter_notes:
            if tick < end and start < tick + dur_ticks:
                interval = abs(pitch - counter_pitch) % 12
                if interval in {3, 4, 7, 8, 9}:
                    score -= 18
                if interval in {1, 2, 6, 10, 11} or pitch == counter_pitch:
                    score += 900
                    bad_overlaps += 1
        score += abs(pitch - 70) * 0.25
        scored.append((bad_overlaps, score + random.random() * 2, pitch))
    clean = [item for item in scored if item[0] == 0]
    if not clean:
        return None
    return min(clean)[2]


def generate_trumpet_line(root_val, progression, scale_chords, scale_notes, tension, num_bars, tpb, counter_events=None):
    """
    Generates a sparse harmonized trumpet line on Channel 3.
    It favors chord tones and consonant intervals against the guitar counter-line,
    avoiding unisons/seconds so the brass supports instead of colliding.
    """
    events = []
    counter_notes = _notes_from_events(counter_events or [], 1)
    prev_pitch = None
    vel_base = int(64 + tension * 20)

    def _emit(tick, pitch, vel, dur_beats):
        if pitch is None:
            return
        stagger = random.randint(-5, 5)
        dur = max(40, int(dur_beats * tpb) - 18)
        events.append((tick + stagger, 'on', max(0, min(127, pitch)), max(24, min(112, vel)), 3))
        events.append((tick + stagger + dur, 'off', max(0, min(127, pitch)), 0, 3))

    for bar in range(num_bars):
        if bar % 4 == 2 and random.random() < 0.65:
            continue
        if bar % 8 == 5 and random.random() < 0.50:
            continue

        bar_start = bar * 4 * tpb
        chord_name = progression[bar % len(progression)]
        chord_notes = scale_chords[chord_name]
        candidates = _trumpet_pitch_candidates(root_val, chord_notes, scale_notes)
        if not candidates:
            continue

        phrase_shape = random.choice(['answer', 'sustain', 'cadence']) if tension < 0.65 else random.choice(['answer', 'cadence', 'fanfarish'])

        if phrase_shape == 'sustain':
            beat = random.choice([0.0, 2.0])
            tick = bar_start + int(beat * tpb)
            dur_beats = random.choice([1.45, 1.85, 2.25])
            pitch = _choose_trumpet_for_span(candidates, counter_notes, tick, int(dur_beats * tpb), prev_pitch)
            _emit(tick, pitch, vel_base - 4, dur_beats)
            prev_pitch = pitch

        elif phrase_shape == 'cadence':
            beats = [2.0, 3.0] if random.random() < 0.55 else [1.5, 2.5, 3.25]
            for i, beat in enumerate(beats):
                tick = bar_start + int(beat * tpb)
                dur_beats = 0.72 if i < len(beats) - 1 else 0.95
                pitch = _choose_trumpet_for_span(candidates, counter_notes, tick, int(dur_beats * tpb), prev_pitch)
                _emit(tick, pitch, vel_base + i * 3, dur_beats)
                prev_pitch = pitch

        elif phrase_shape == 'fanfarish':
            rootish = [p for p in candidates if p % 12 == (root_val + chord_notes[0]) % 12]
            target = min(rootish, key=lambda p: abs(p - (prev_pitch or 70))) if rootish else _choose_trumpet_for_span(candidates, counter_notes, bar_start, int(0.45 * tpb), prev_pitch)
            for beat, pitch, dur, vel_adj in [
                (0.0, target, 0.45, 8),
                (0.75, None, 0.45, 2),
                (1.5, target, 0.8, 5),
            ]:
                tick = bar_start + int(beat * tpb)
                if pitch is None:
                    pitch = _choose_trumpet_for_span(candidates, counter_notes, tick, int(dur * tpb), prev_pitch)
                else:
                    pitch = _choose_trumpet_for_span(candidates, counter_notes, tick, int(dur * tpb), prev_pitch)
                _emit(bar_start + int(beat * tpb), pitch, vel_base + vel_adj, dur)
                prev_pitch = pitch

        else:
            beats = random.choice([[0.5, 1.5], [1.0, 2.0, 3.0], [2.0, 2.75, 3.5]])
            for i, beat in enumerate(beats):
                tick = bar_start + int(beat * tpb)
                pitch = _choose_trumpet_for_span(candidates, counter_notes, tick, int(0.55 * tpb), prev_pitch)
                _emit(tick, pitch, vel_base + (4 if i == 0 else -2), 0.55)
                prev_pitch = pitch

    return events


def _violin_pitch_candidates(root_val, chord_notes, scale_notes, low=60, high=88):
    scale_pcs = {(root_val + degree) % 12 for degree in scale_notes}
    chord_pcs = [(root_val + degree) % 12 for degree in chord_notes]
    pcs = [pc for pc in chord_pcs if pc in scale_pcs] or chord_pcs
    return sorted(p for p in range(low, high + 1) if p % 12 in pcs)


def _scale_pitches_in_range(root_val, scale_notes, low=60, high=88):
    scale_pcs = {(root_val + degree) % 12 for degree in scale_notes}
    return sorted(p for p in range(low, high + 1) if p % 12 in scale_pcs)


def _nearest_pitch(candidates, target, prev_pitch=None):
    if not candidates:
        return None
    anchor = prev_pitch if prev_pitch is not None else target
    return min(candidates, key=lambda p: (abs(p - anchor), abs(p - target)))


def generate_violin_line(root_val, progression, scale_chords, scale_notes, tension, num_bars, tpb):
    """
    Generates a lyrical violin layer on Channel 4.
    The line is intentionally freer than trumpet: still scale/chord-safe, but
    allowed to weave through sustained arcs and phrase answers.
    """
    events = []
    scale_pool = _scale_pitches_in_range(root_val, scale_notes, 60, 88)
    if not scale_pool:
        return events

    prev_pitch = scale_pool[len(scale_pool) // 2]
    vel_base = int(58 + tension * 22)

    def _emit(tick, pitch, vel, dur_beats):
        if pitch is None:
            return
        stagger = random.randint(-6, 6)
        dur = max(50, int(dur_beats * tpb) - 16)
        pitch = max(0, min(127, pitch))
        vel = max(24, min(110, vel))
        events.append((tick + stagger, 'on', pitch, vel, 4))
        events.append((tick + stagger + dur, 'off', pitch, 0, 4))

    for bar in range(num_bars):
        if bar % 8 == 2 and random.random() < 0.55:
            continue
        if bar % 8 == 6 and random.random() < 0.40:
            continue

        bar_start = bar * 4 * tpb
        chord_name = progression[bar % len(progression)]
        chord_notes = scale_chords[chord_name]
        chord_candidates = _violin_pitch_candidates(root_val, chord_notes, scale_notes)
        phrase = random.choice(['sustain', 'answer', 'arc', 'turn'])

        if phrase == 'sustain':
            target = _nearest_pitch(chord_candidates, prev_pitch + random.choice([-3, 0, 3]), prev_pitch)
            beat = random.choice([0.0, 1.0, 2.0])
            dur = random.choice([1.65, 2.0, 2.6, 3.2])
            _emit(bar_start + int(beat * tpb), target, vel_base + random.randint(-5, 5), dur)
            prev_pitch = target or prev_pitch

        elif phrase == 'answer':
            beats = random.choice([[0.5, 1.5, 2.5], [1.0, 2.0, 3.0], [2.0, 2.75, 3.5]])
            for i, beat in enumerate(beats):
                target_pool = chord_candidates if i == len(beats) - 1 else scale_pool
                direction = random.choice([-2, -1, 1, 2])
                target = _nearest_pitch(target_pool, prev_pitch + direction, prev_pitch)
                _emit(bar_start + int(beat * tpb), target, vel_base + (4 if i == 0 else -2), 0.62)
                prev_pitch = target or prev_pitch

        elif phrase == 'arc':
            start = _nearest_pitch(chord_candidates, prev_pitch, prev_pitch) or prev_pitch
            peak = _nearest_pitch(scale_pool, start + random.choice([3, 4, 5, 7]), start) or start
            end = _nearest_pitch(chord_candidates, start - random.choice([0, 2, 3]), peak) or start
            for beat, pitch, dur, vel_adj in [
                (0.0, start, 0.85, -2),
                (1.25, peak, 0.85, 6),
                (2.5, end, 1.25, 0),
            ]:
                _emit(bar_start + int(beat * tpb), pitch, vel_base + vel_adj, dur)
            prev_pitch = end

        else:
            chord_target = _nearest_pitch(chord_candidates, prev_pitch, prev_pitch) or prev_pitch
            neighbor = _nearest_pitch(scale_pool, chord_target + random.choice([-2, -1, 1, 2]), chord_target) or chord_target
            return_note = _nearest_pitch(chord_candidates, chord_target, neighbor) or chord_target
            for beat, pitch, dur, vel_adj in [
                (0.0, chord_target, 0.72, 2),
                (0.85, neighbor, 0.38, -5),
                (1.25, return_note, 1.1, 0),
                (3.0, _nearest_pitch(chord_candidates, return_note + random.choice([-2, 2]), return_note), 0.72, -2),
            ]:
                _emit(bar_start + int(beat * tpb), pitch, vel_base + vel_adj, dur)
                prev_pitch = pitch or prev_pitch

    return events

# ── MIDI ASSEMBLY AND EXPORT ──────────────────────────────────────────────────

def _last_note_off_tick(events, channel):
    offs = [tick for tick, etype, _val1, _val2, ch in events if etype == 'off' and ch == channel]
    return max(offs) if offs else 0


def add_loop_closure_events(root_val, progression, scale_chords, scale_notes, num_bars, tpb, tr_harmony, tr_bass, tr_trumpet=None, tr_counter=None, tr_violin=None):
    """
    Fills only genuine end gaps, then lets the assembler seal the MIDI exactly
    at the bar boundary. This keeps 8-bar loops from breathing into silence.
    """
    loop_end = num_bars * 4 * tpb
    last_chord = progression[(num_bars - 1) % len(progression)]
    chord_notes = scale_chords[last_chord]
    voicing = voice_guitar_chord(root_val, chord_notes, scale_notes)
    close_start = loop_end - tpb
    off_tick = loop_end - 2

    if _last_note_off_tick(tr_harmony, 0) < loop_end - (tpb // 8):
        root_note = voicing[0]
        upper_notes = voicing[1:4] if len(voicing) >= 4 else voicing[1:]
        tr_harmony.append((close_start, 'on', root_note, 62, 0))
        tr_harmony.append((off_tick, 'off', root_note, 0, 0))
        for i, note in enumerate(upper_notes):
            tick = close_start + (tpb // 2) + i * 14
            tr_harmony.append((tick, 'on', note, 54 + i * 4, 0))
            tr_harmony.append((off_tick, 'off', note, 0, 0))

    if _last_note_off_tick(tr_bass, 2) < loop_end - (tpb // 8):
        bass_pc = (root_val + chord_notes[0]) % 12
        bass_note = _pitch_in_range_for_pc(bass_pc, 40, 55)
        tr_bass.append((close_start, 'on', bass_note, 70, 2))
        tr_bass.append((off_tick, 'off', bass_note, 0, 2))

    if tr_trumpet is not None and _last_note_off_tick(tr_trumpet, 3) < loop_end - (tpb // 8):
        candidates = _trumpet_pitch_candidates(root_val, chord_notes, scale_notes)
        trumpet_tick = close_start + (tpb // 2)
        counter_notes = _notes_from_events(tr_counter or [], 1)
        trumpet_note = _choose_trumpet_for_span(candidates, counter_notes, trumpet_tick, off_tick - trumpet_tick)
        if trumpet_note is not None:
            tr_trumpet.append((trumpet_tick, 'on', trumpet_note, 60, 3))
            tr_trumpet.append((off_tick, 'off', trumpet_note, 0, 3))

    if tr_violin is not None and _last_note_off_tick(tr_violin, 4) < loop_end - (tpb // 8):
        candidates = _violin_pitch_candidates(root_val, chord_notes, scale_notes)
        violin_note = _nearest_pitch(candidates, voicing[-1] + 5 if voicing else 72)
        if violin_note is not None:
            tr_violin.append((close_start, 'on', violin_note, 56, 4))
            tr_violin.append((off_tick, 'off', violin_note, 0, 4))


def build_midi_from_tracks_events(tracks_events, tpb=480, loop_end_tick=None):
    """
    Assembles track events containing absolute ticks into delta-time MIDI format.
    """
    mid = mido.MidiFile()
    mid.ticks_per_beat = tpb
    
    track_names = [
        'Harmony (Nylon Guitar)',
        'Counter-Melody (Nylon Guitar)',
        'Bass Line (Acoustic Bass)',
        'Trumpet (Harmonized Brass)',
        'Violin (Lyrical Strings)'
    ]
    
    for t_idx, ch_events in enumerate(tracks_events):
        # Clamping and filtering to ensure safe MIDI data bytes
        clamped_events = []
        for ev in ch_events:
            tick, etype, val1, val2, ch = ev
            tick = max(0, tick)
            if loop_end_tick is not None:
                if etype == 'on' and tick >= loop_end_tick:
                    continue
                tick = min(tick, loop_end_tick)
            if etype in ['on', 'off']:
                val1 = max(0, min(127, val1))
                val2 = max(0, min(127, val2))
            elif etype == 'cc':
                val1 = max(0, min(127, val1))
                val2 = max(0, min(127, val2))
            clamped_events.append((tick, etype, val1, val2, ch))
            
        # Sort by absolute tick
        clamped_events.sort(key=lambda x: (x[0], 0 if x[1] in ['program', 'tempo'] else 1))
        track = mido.MidiTrack()
        if t_idx < len(track_names):
            track.append(mido.MetaMessage('track_name', name=track_names[t_idx], time=0))
        mid.tracks.append(track)
        
        last_tick = 0
        for ev in clamped_events:
            tick, etype, val1, val2, ch = ev
            dt = tick - last_tick
            last_tick = tick
            
            if etype == 'program':
                track.append(mido.Message('program_change', program=val1, channel=ch, time=dt))
            elif etype == 'tempo':
                track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(val1), time=dt))
            elif etype == 'on':
                track.append(mido.Message('note_on', note=val1, velocity=val2, channel=ch, time=dt))
            elif etype == 'off':
                track.append(mido.Message('note_off', note=val1, velocity=val2, channel=ch, time=dt))
            elif etype == 'cc':
                track.append(mido.Message('control_change', control=val1, value=val2, channel=ch, time=dt))

        if loop_end_tick is not None:
            end_dt = max(0, loop_end_tick - last_tick)
            track.append(mido.MetaMessage('end_of_track', time=end_dt))

    return mid


def compose_spanish_family(out_dir, mood, key_name, root_val, bpm, num_bars=8):
    """
    Core composer entry point. Creates tracks, generates performance, and saves file.
    """
    tpb = 480
    scale_name = mood['scale']
    tension = mood['tension']
    mood_name = mood['name']
    is_minor = mood['is_minor']
    
    scale_notes = SPANISH_SCALES[scale_name]
    scale_chords = SCALE_CHORDS[scale_name]
    
    # 1. Generate Chord Progression (or use the one in the selected mood)
    if 'progression' in mood:
        raw_prog = mood['progression']
        progression = [raw_prog[i % len(raw_prog)] for i in range(num_bars)]
    else:
        progression = generate_unique_progression(scale_name, is_minor, num_bars)
        
    # Map the progression chords so they exist in the scale chords pool
    mapped_progression = [get_best_matching_chord_name(c, scale_name) for c in progression]
    
    # 2. Build Event Tracks
    tr_harmony = [(0, 'program', GM_NYLON, 0, 0), (0, 'tempo', bpm, 0, 0)]
    tr_counter = [(0, 'program', GM_NYLON, 0, 1)]
    tr_bass    = [(0, 'program', GM_ACOUSTIC_BASS, 0, 2)]
    tr_trumpet = [(0, 'program', GM_TRUMPET, 0, 3)]
    tr_violin  = [(0, 'program', GM_VIOLIN, 0, 4)]
    
    # Populate notes
    tr_harmony.extend(generate_guitar_arpeggio(root_val, mapped_progression, scale_chords, scale_notes, tension, num_bars, tpb))
    tr_counter.extend(generate_counter_melody(root_val, mapped_progression, scale_chords, scale_notes, tension, num_bars, tpb))
    tr_bass.extend(generate_bass_line(root_val, mapped_progression, scale_chords, scale_notes, tension, num_bars, tpb))
    tr_trumpet.extend(generate_trumpet_line(root_val, mapped_progression, scale_chords, scale_notes, tension, num_bars, tpb, counter_events=tr_counter))
    tr_violin.extend(generate_violin_line(root_val, mapped_progression, scale_chords, scale_notes, tension, num_bars, tpb))
    loop_end_tick = num_bars * 4 * tpb
    add_loop_closure_events(root_val, mapped_progression, scale_chords, scale_notes, num_bars, tpb, tr_harmony, tr_bass, tr_trumpet, tr_counter, tr_violin)
    
    # 3. Assemble MIDI
    mid = build_midi_from_tracks_events([tr_harmony, tr_counter, tr_bass, tr_trumpet, tr_violin], tpb, loop_end_tick=loop_end_tick)
    
    # 4. Save and Format Names
    project_title = _project_title()
    mood_tag = _slug(mood_name)
    style_label = mood.get('style_label', 'Custom_Spanish')
    style_tag = _slug(style_label)
    scale_tag = _slug(scale_name.replace('_', '').title())
    prog_tag = _slug('-'.join(mapped_progression))
    
    fname = f"{project_title}__Spanish_Family_{mood_tag}__{style_tag}__{key_name}_{scale_tag}__{bpm}BPM__{prog_tag}"
    fpath = os.path.join(out_dir, fname + ".mid")
    
    idx = 1
    while os.path.exists(fpath):
        fpath = os.path.join(out_dir, f"{fname}_v{idx}.mid")
        idx += 1
        
    mid.save(fpath)
    
    print(f"\n  [SAVED]  {os.path.basename(fpath)}")
    print(f"  [PATH ]  {fpath}")
    print(f"  [PROG ]  {'-'.join(mapped_progression)}\n")
    return fpath, mapped_progression

# ── CLI MENUS ─────────────────────────────────────────────────────────────────

def _div(c='-', w=62):
    print(c * w)


def _select_mood_cli():
    print("""
  Select Mood Source:
  ____________________________________________________________
    1  →  Native Spanish Presets (Classic 8 moods)
    2  →  Touching Spanish (modeled on reference recordings)
    3  →  Minor Engine Moods (Adapted to Spanish Scales)
    4  →  Major Engine Moods (Adapted to Spanish Scales)
  ____________________________________________________________""")
    while True:
        mode_choice = input("  --> ").strip()
        if mode_choice in ('1', '2', '3', '4'):
            break
        print("  Enter 1, 2, 3, or 4.")

    if mode_choice == '1':
        # Original 8 native presets
        print("\n  Select a Native Spanish Preset:")
        print("  ____________________________________________________________")
        native_8 = {k: v for k, v in NATIVE_MOODS.items() if k in [str(i) for i in range(1, 9)]}
        for k, m in sorted(native_8.items()):
            scale_disp = m['scale'].replace('_', ' ').title()
            print(f"    {k}  →  {m['name']:<22} {m['desc']:<36} [{scale_disp}]")
        print("  ____________________________________________________________")
        while True:
            choice = input("  --> ").strip()
            if choice in native_8:
                m = native_8[choice].copy()
                m['style_label'] = 'Native_Preset'
                print(f"  [{m['name']}] selected.")
                return m
            print(f"  Enter one of: {', '.join(sorted(native_8.keys()))}")

    elif mode_choice == '2':
        # Touching Spanish — modeled on test MIDI emotional profiles
        touching = {k: v for k, v in NATIVE_MOODS.items() if k in ('9', 'A', 'B', 'C')}
        print("\n  Select Touching Spanish Preset:")
        print("  ____________________________________________________________")
        for k, m in sorted(touching.items()):
            scale_disp = m['scale'].replace('_', ' ').title()
            print(f"    {k}  →  {m['name']:<22} {m['desc']:<36} [{scale_disp}]")
        print("  ____________________________________________________________")
        while True:
            choice = input("  --> ").strip().upper()
            if choice in touching:
                m = touching[choice].copy()
                # Pick a random touching progression for this scale
                scale = m['scale']
                pool = TOUCHING_SPANISH_PROGRESSIONS.get(scale, [])
                if pool:
                    prog_entry = random.choice(pool)
                    m['progression'] = prog_entry['chords']
                    m['tension'] = prog_entry['tension']
                    m['style_label'] = prog_entry['label']
                else:
                    m['style_label'] = 'Touching_Spanish'
                print(f"  [{m['name']}] · [{m.get('style_label','')}] selected.")
                return m
            print(f"  Enter one of: {', '.join(sorted(touching.keys()))}")

    elif mode_choice == '3':
        # Minor Engine Moods
        print("\n  Select a Minor Engine Mood:")
        print("  ____________________________________________________________")
        for k, m in sorted(MINOR_ENGINE_MOODS.items(), key=lambda x: int(x[0])):
            print(f"    {k}  →  {m['name']}")
        print("  ____________________________________________________________")
        while True:
            choice = input("  --> ").strip()
            if choice in MINOR_ENGINE_MOODS:
                minor_mood = MINOR_ENGINE_MOODS[choice]
                break
            print(f"  Enter one of: {', '.join(sorted(MINOR_ENGINE_MOODS.keys()))}")

        prog_entry = random.choice(minor_mood['progressions'])

        print("\n  Select target Spanish Minor Scale:")
        print("  ____________________________________________________________")
        minor_scales = {
            '1': ('phrygian_dominant', 'Phrygian Dominant (Spanish Gypsy)'),
            '2': ('harmonic_minor',    'Harmonic Minor (Mournful / Lamento)'),
            '3': ('phrygian',          'Phrygian (Melancholic Spanish)'),
            '4': ('dorian',            'Dorian (Passionate / Bittersweet)'),
            '5': ('natural_minor',     'Natural Minor (Nostalgic)')
        }
        for k, v in sorted(minor_scales.items()):
            print(f"    {k}  →  {v[1]}")
        print("  ____________________________________________________________")
        while True:
            scale_choice = input("  --> ").strip()
            if scale_choice in minor_scales:
                target_scale = minor_scales[scale_choice][0]
                break
            print("  Enter 1-5.")

        return {
            'name': minor_mood['name'],
            'scale': target_scale,
            'is_minor': True,
            'tension': minor_mood['tension'],
            'bpm_range': minor_mood['bpm_range'],
            'progression': prog_entry['chords'],
            'style_label': prog_entry['label']
        }

    else:
        # Major Engine Moods
        print("\n  Select a Major Engine Mood:")
        print("  ____________________________________________________________")
        for k, m in sorted(MAJOR_ENGINE_MOODS.items(), key=lambda x: int(x[0])):
            print(f"    {k}  →  {m['name']}")
        print("  ____________________________________________________________")
        while True:
            choice = input("  --> ").strip()
            if choice in MAJOR_ENGINE_MOODS:
                major_mood = MAJOR_ENGINE_MOODS[choice]
                break
            print(f"  Enter one of: {', '.join(sorted(MAJOR_ENGINE_MOODS.keys()))}")

        prog_entry = random.choice(major_mood['progressions'])

        print("\n  Select target Spanish Major Scale:")
        print("  ____________________________________________________________")
        major_scales = {
            '1': ('ionian',               'Ionian (Radiant / Bright Major)'),
            '2': ('mixolydian',            'Mixolydian (Warm Andalusian Major)'),
            '3': ('double_harmonic_major', 'Double Harmonic Major (Exotic Seville)')
        }
        for k, v in sorted(major_scales.items()):
            print(f"    {k}  →  {v[1]}")
        print("  ____________________________________________________________")
        while True:
            scale_choice = input("  --> ").strip()
            if scale_choice in major_scales:
                target_scale = major_scales[scale_choice][0]
                break
            print("  Enter 1-3.")

        return {
            'name': major_mood['name'],
            'scale': target_scale,
            'is_minor': False,
            'tension': major_mood['tension'],
            'bpm_range': major_mood['bpm_range'],
            'progression': prog_entry['chords'],
            'style_label': prog_entry['label']
        }



def _select_key_cli():
    print(f"\n  Select root key (Available: {' · '.join(sorted(ROOTS.keys()))}):")
    while True:
        k = input("  --> ").strip()
        # Handle capitalization
        if len(k) > 0:
            k = k[0].upper() + k[1:]
        if k in ROOTS:
            return k, ROOTS[k]
        print("  Invalid key. Try C, D, Em, F#, etc.")


def _select_tempo_cli(lo, hi):
    print(f"\n  Select BPM ({lo}–{hi}) or press [Enter] for mood default:")
    val = input("  --> ").strip()
    if val.isdigit():
        return max(lo, min(hi, int(val)))
    return random.randint(lo, hi)


def _select_length_cli():
    print("""
  Select Composition Length:
    1  →  8 Bars (Loop/Phrase)
    2  →  16 Bars (Double Period Theme)
    --> """)
    while True:
        choice = input("  --> ").strip()
        if choice == '1':
            return 8
        elif choice == '2':
            return 16
        print("  Enter 1 or 2.")



def main(out_dir='midi_files'):
    os.makedirs(out_dir, exist_ok=True)
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║       S P A N I S H   F A M I L Y   C O M P O S E R        ║
║ Harmony · Counter · Bass · Trumpet · Violin (5 Channels)   ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝""")

    while True:
        mood = _select_mood_cli()
        key_name, root_val = _select_key_cli()
        bpm_lo, bpm_hi = mood['bpm_range']
        bpm = _select_tempo_cli(bpm_lo, bpm_hi)
        num_bars = _select_length_cli()

        _div()
        desc = mood.get('desc', mood.get('style_label', ''))
        print(f"""
  ── Spanish Family Composition Summary ───────────────
    Mood    : {mood['name']} ({desc})
    Scale   : {mood['scale'].replace('_',' ').title()}
    Key     : {key_name}
    BPM     : {bpm}
    Length  : {num_bars} Bars
    Tension : {'#'*int(mood['tension']*10)}{'.'*(10-int(mood['tension']*10))} {int(mood['tension']*100)}%
  ─────────────────────────────────────────────────────
""")

        fpath, prog = compose_spanish_family(out_dir, mood, key_name, root_val, bpm, num_bars)

        print("  [G] Generate again  [B] Back  [Q] Quit")
        sub = input("  --> ").strip().lower()
        if sub == 'q':
            print("\n  ♪ The session ends here, but the progression keeps moving. ♪")
            print("  Returning to ANIMA Workstation.\n")
            return
        elif sub == 'b':
            return


if __name__ == '__main__':
    main()
