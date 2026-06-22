"""
VVC.py  —  Violin, Viola & Cello String Trio + Quartet Composition Engine
Features:
  1. Compose for Violin I, Violin II (counter), Viola, and Cello
  2. Support both Major and Minor scales
  3. Mood-adaptive progressions with Markov chain melodies
  4. Authentic string instrument registers & voice-leading
  5. MIDI CC Expression curves for realistic phrasing
"""

import mido, os, random, time, math
import specialist_styles

# ── Instrument Ranges (MIDI Note Numbers) ──────────────────────────────────
# Violin:   G3 (55)  to  E7 (100)  — comfortable: 55-96
# Viola:    C3 (48)  to  A6 (93)   — comfortable: 48-84
# Cello:    C2 (36)  to  C6 (84)   — comfortable: 36-72

VIOLIN_LOW  = 55   # G3
VIOLIN_HIGH = 96   # E7
VIOLA_LOW   = 48   # C3
VIOLA_HIGH  = 84   # C6
CELLO_LOW   = 36   # C2
CELLO_HIGH  = 72   # C5

# ── Register Assignments (practical lanes to prevent clashing) ─────────────
# Full instrument ranges overlap by design, but these composition lanes keep
# exported MIDI parts separated for easier mixing and clearer quartet writing.
#   Violin I  (Lead)    :  C5 (72)  –  B5 (83)
#   Violin II (Counter) :  C4 (60)  –  B4 (71)
#   Viola     (Harmony) :  C3 (48)  –  B3 (59)
#   Cello     (Bass)    :  C2 (36)  –  B2 (47)
#   Piano     (High)    :  C6 (84)  –  C7 (96)

VIOLIN1_REGISTER = {'min': 72, 'max': 83, 'center': 76}
VIOLIN2_REGISTER = {'min': 60, 'max': 71, 'center': 64}
VIOLA_REGISTER   = {'min': 48, 'max': 59, 'center': 52}
CELLO_REGISTER   = {'min': 36, 'max': 47, 'center': 41}
PIANO_REGISTER   = {'min': 84, 'max': 96, 'center': 88}

CHOIR_REGISTERS = {
    'soprano': {'min': 72, 'max': 84, 'intro_min': 72, 'intro_max': 76},
    'alto':    {'min': 60, 'max': 71, 'intro_min': 62, 'intro_max': 67},
    'tenor':   {'min': 48, 'max': 59, 'intro_min': 52, 'intro_max': 57},
    'bass':    {'min': 36, 'max': 47, 'intro_min': 40, 'intro_max': 45},
}

# Krumhansl-Schmuckler key detection profiles
KS_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
KS_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

# ── SCALES ──────────────────────────────────────────────────────────────────
# Minor scales
SCALE_AEOLIAN      = [0, 2, 3, 5, 7, 8, 10]
SCALE_HARMONIC     = [0, 2, 3, 5, 7, 8, 11]
SCALE_DORIAN       = [0, 2, 3, 5, 7, 9, 10]
SCALE_PHRYGIAN     = [0, 1, 3, 5, 7, 8, 10]

# Major scales
SCALE_IONIAN       = [0, 2, 4, 5, 7, 9, 11]
SCALE_LYDIAN       = [0, 2, 4, 6, 7, 9, 11]
SCALE_MIXOLYDIAN   = [0, 2, 4, 5, 7, 9, 10]

# All scale sets for lookup
MINOR_SCALES = {
    'Natural Minor (Aeolian)': SCALE_AEOLIAN,
    'Harmonic Minor':          SCALE_HARMONIC,
    'Dorian':                  SCALE_DORIAN,
    'Phrygian':                SCALE_PHRYGIAN,
}

MAJOR_SCALES = {
    'Natural Major (Ionian)':  SCALE_IONIAN,
    'Lydian':                  SCALE_LYDIAN,
    'Mixolydian':              SCALE_MIXOLYDIAN,
}

ROOT_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
ROOTS = {'C': 36, 'C#': 37, 'D': 38, 'Eb': 39, 'E': 40, 'F': 41,
         'F#': 42, 'G': 43, 'Ab': 44, 'A': 45, 'Bb': 46, 'B': 47}

VVC_TRACK_NAMES = [
    "String Ensemble Pad",
    "Violin I - Lead Melody",
    "Violin II - Counter Melody",
    "Viola - Harmonic Fill",
    "Cello - Bass Line",
    "Double Bass - Low Foundation",
    "Spiccato Ostinato - Short Strings",
    "Piano Melody - Colour",
]

# ── Roman Numeral Chord Definitions ─────────────────────────────────────────
# Minor key roman numerals (augmented with borrowed chords for 8-bar expansion)
RN_MINOR = {
    'i':    ([0, 3, 7],     SCALE_AEOLIAN),
    'i7':   ([0, 3, 7, 10], SCALE_AEOLIAN),
    'iio':  ([2, 5, 8],     SCALE_AEOLIAN),
    'bII':  ([1, 5, 8],     SCALE_PHRYGIAN),
    'III':  ([3, 7, 10],    SCALE_AEOLIAN),
    'iv':   ([5, 8, 12],    SCALE_AEOLIAN),
    'IV':   ([5, 9, 12],    SCALE_DORIAN),
    'iv7':  ([5, 8, 12, 3], SCALE_HARMONIC),
    'v':    ([7, 10, 14],   SCALE_AEOLIAN),
    'V':    ([7, 11, 14],   SCALE_HARMONIC),
    'V7':   ([7, 11, 14, 5], SCALE_HARMONIC),
    'bVI':  ([8, 11, 15],   SCALE_HARMONIC),   # Borrowed from Phrygian/Mixolydian
    'VI':   ([8, 12, 15],   SCALE_AEOLIAN),
    'bVII': ([10, 13, 17],  SCALE_PHRYGIAN),   # Borrowed flat VII
    'VII':  ([10, 14, 17],  SCALE_AEOLIAN),
    'viio': ([11, 14, 17],  SCALE_HARMONIC),
}

# Major key roman numerals (augmented with borrowed chords for 8-bar expansion)
RN_MAJOR = {
    'I':       ([0, 4, 7],      SCALE_IONIAN),
    'Imaj7':   ([0, 4, 7, 11],  SCALE_IONIAN),
    'I6':      ([0, 4, 7, 9],   SCALE_IONIAN),
    'ii':      ([2, 5, 9],      SCALE_IONIAN),
    'ii7':     ([2, 5, 9, 0],   SCALE_IONIAN),
    'iii':     ([4, 7, 11],     SCALE_IONIAN),
    'IV':      ([5, 9, 12],     SCALE_IONIAN),
    'IVmaj7':  ([5, 9, 12, 16], SCALE_LYDIAN),
    'IV6':     ([5, 9, 12, 14], SCALE_IONIAN),
    'V':       ([7, 11, 14],    SCALE_IONIAN),
    'V6':      ([7, 11, 14, 16], SCALE_IONIAN),
    'V7':      ([7, 11, 14, 5], SCALE_IONIAN),
    'vi':      ([9, 12, 16],    SCALE_IONIAN),
    'viio':    ([11, 14, 17],   SCALE_IONIAN),
    'II':      ([2, 6, 9],      SCALE_LYDIAN),
    'III':     ([4, 8, 11],     SCALE_LYDIAN),   # Lydian mediant
    'bIII':    ([3, 7, 10],     SCALE_MIXOLYDIAN),
    'iv':      ([5, 8, 12],     SCALE_MIXOLYDIAN),
    'bVI':     ([8, 12, 15],    SCALE_MIXOLYDIAN),
    'bVII':    ([10, 14, 17],   SCALE_MIXOLYDIAN),
    'v':       ([7, 10, 14],    SCALE_MIXOLYDIAN),
}

# ── 8-BAR EXPANSION SYSTEM ─────────────────────────────────────────────────
# 8-bar expansion creates a dramatic tension arc:
#   Bars 1-2: Statement  (original 4-bar progression, bars 0-1)
#   Bars 3-4: Development (original progression bars 2-3, tension +15%)
#   Bar 5:    Pivot       (deceptive or unexpected substitution chord)
#   Bar 6:    Pre-climax  (high-tension borrowed chord)
#   Bar 7:    Climax      (diminished/augmented/subdominant tension peak)
#   Bar 8:    Resolution  (return to tonic with emotional weight)

# Minor key tension-building chords (borrowed from parallel modes)
_TENSION_CHORDS_MINOR = {
    'bII':   1.8,  # Neapolitan
    'viio':  1.7,  # Leading-tone diminished
    'V':     1.5,  # Dominant (harmonic minor)
    'iv':    1.3,  # Subdominant minor
    'bVI':   1.2,  # Flat VI (Mixolydian/Major borrow)
    'bVII':  1.1,  # Flat VII
    'VII':   1.0,  # Natural VII
    'v':     0.9,  # Minor dominant
    'VI':    0.8,  # Flat VI
    'III':   0.7,  # Mediant
    'i':     0.5,  # Tonic
    'iio':   1.4,  # Supertonic diminished
}

# Major key tension-building chords
_TENSION_CHORDS_MAJOR = {
    'viio':  1.8,  # Leading-tone diminished
    'V7':    1.6,  # Dominant 7th
    'V':     1.5,  # Dominant
    'iv':    1.4,  # Minor iv (borrowed)
    'bVII':  1.3,  # Mixolydian flat VII
    'bVI':   1.2,  # Borrowed flat VI
    'bIII':  1.1,  # Borrowed flat III
    'ii':    1.0,  # Supertonic
    'vi':    0.9,  # Submediant
    'III':   0.8,  # Mediant (if present)
    'V6':    0.8,  # Soft dominant color
    'IV':    0.7,  # Subdominant
    'IV6':   0.6,  # Warm subdominant color
    'I6':    0.5,  # Warm tonic color
    'I':     0.5,  # Tonic
}

_TENSION_CHORDS = {'minor': _TENSION_CHORDS_MINOR, 'major': _TENSION_CHORDS_MAJOR}

def expand_to_8_bars(progression, is_minor):
    """
    Expand a 4-bar chord progression into an 8-bar emotional arc.
    Each bar gets a unique chord that builds and releases tension.
    """
    if len(progression) != 4:
        # Already custom — pad or truncate to 8
        result = list(progression)
        while len(result) < 8:
            result.append(result[-1])
        return result[:8]

    chord_pool = _TENSION_CHORDS['minor'] if is_minor else _TENSION_CHORDS['major']
    valid_chords = list(chord_pool.keys())

    a, b, c, d = progression

    # Analytical phase: determine original chord tensions
    def tension_of(chord):
        return chord_pool.get(chord, 1.0)

    base_tension = max(tension_of(ch) for ch in progression)

    # Build emotional arc with substitutions
    bars = [None] * 8

    # Bars 0-1: Statement — use original chords
    bars[0] = a
    bars[1] = b

    # Bars 2-3: Development — original chords c, d but optionally substitute
    # for higher tension if the original is too stable
    if tension_of(c) < 0.9 and random.random() < 0.5:
        # Substitute with a higher-tension chord
        candidates = [ch for ch in valid_chords if chord_pool[ch] >= 1.0 and ch != bars[0] and ch != bars[1]]
        if candidates:
            bars[2] = random.choice(candidates)
        else:
            bars[2] = c
    else:
        bars[2] = c

    if tension_of(d) < 1.0 and random.random() < 0.4:
        candidates = [ch for ch in valid_chords if chord_pool[ch] >= 1.2 and ch != bars[2]]
        if candidates:
            bars[3] = random.choice(candidates)
        else:
            bars[3] = d
    else:
        bars[3] = d

    # Bar 4: Pivot — deceptive or unexpected substitution (e.g., bII in minor, vi in major)
    if is_minor:
        pivot_options = [ch for ch in ['bII', 'VI', 'iv', 'bVII'] if ch in valid_chords and ch != bars[3]]
    else:
        pivot_options = [ch for ch in ['vi', 'bIII', 'IV', 'ii'] if ch in valid_chords and ch != bars[3]]
    if pivot_options:
        bars[4] = random.choice(pivot_options)
    else:
        bars[4] = random.choice(valid_chords)

    # Bar 5: Pre-climax — high tension borrowed chord
    high_tension = [ch for ch in valid_chords if chord_pool[ch] >= 1.3 and ch != bars[4]]
    if high_tension:
        bars[5] = random.choice(high_tension)
    else:
        bars[5] = random.choice(valid_chords)

    # Bar 6: Climax — maximum tension (dominant or diminished)
    max_tension = [ch for ch in valid_chords if chord_pool[ch] >= 1.5]
    if max_tension:
        bars[6] = random.choice(max_tension)
    else:
        bars[6] = bars[5]

    # Bar 7: Resolution — return to tonic or relative tonic
    tonic = 'i' if is_minor else 'I'
    resolution_options = [ch for ch in [tonic, 'VI' if is_minor else 'vi', 'III' if is_minor else 'IV']
                          if ch in valid_chords]
    if resolution_options:
        bars[7] = random.choice(resolution_options)
    else:
        bars[7] = tonic if tonic in valid_chords else bars[0]

    return bars


# ── MOOD PROGRESSIONS (Minor) ───────────────────────────────────────────────
MOODS_MINOR = {
    "1": {"name": "Melancholy & Deep Sorrow", "tension": 0.50, "progressions": [
        {'chords': ['i', 'VI', 'III', 'VII'], 'label': 'Hopeful Grief'},
        {'chords': ['i', 'iv', 'i', 'V'],     'label': 'Lamento'},
        {'chords': ['i', 'VI', 'iv', 'V'],    'label': 'Romantic Sorrow'},
        {'chords': ['i', 'VII', 'VI', 'V'],   'label': 'Andalusian Cadence'},
        {'chords': ['i', 'bII', 'i', 'V'],    'label': 'Phrygian Weeping'},
        {'chords': ['i', 'iv', 'v', 'i'],     'label': 'Austere Church'},
        {'chords': ['i', 'VI', 'VII', 'i'],   'label': 'Circular Grief'},
        {'chords': ['i', 'iio', 'V', 'i'],    'label': 'Baroque Descent'},
        {'chords': ['i', 'VI', 'bII', 'V'],   'label': 'Neapolitan Lament'},
    ]},
    "2": {"name": "Bittersweet & Nostalgic", "tension": 0.40, "progressions": [
        {'chords': ['i', 'III', 'VI', 'VII'], 'label': 'Wistful Memory'},
        {'chords': ['i', 'VII', 'III', 'VI'], 'label': 'Wistful'},
        {'chords': ['VI', 'VII', 'i', 'v'],   'label': 'Reflective'},
        {'chords': ['i', 'VI', 'III', 'iv'],  'label': 'Memory Lane'},
        {'chords': ['i', 'III', 'iv', 'VI'],  'label': 'Tender Regret'},
        {'chords': ['III', 'VII', 'i', 'VI'], 'label': 'Faded Summer'},
        {'chords': ['i', 'iv', 'III', 'VII'], 'label': 'Childhood Echo'},
        {'chords': ['VI', 'III', 'i', 'VII'], 'label': 'Golden Haze'},
        {'chords': ['i', 'VI', 'VII', 'III'], 'label': 'Soft Longing'},
    ]},
    "3": {"name": "Epic & Heroic (Minor)", "tension": 0.75, "progressions": [
        {'chords': ['i', 'v', 'VI', 'VII'],  'label': 'Triumphant Minor'},
        {'chords': ['i', 'VII', 'VI', 'v'],  'label': 'Descending Heroic'},
        {'chords': ['i', 'iv', 'VI', 'VII'], 'label': 'Battle March'},
        {'chords': ['i', 'III', 'VII', 'VI'],'label': 'Inception Style'},
        {'chords': ['i', 'VI', 'VII', 'III'],'label': "Hero's Journey"},
        {'chords': ['i', 'v', 'VII', 'iv'],  'label': 'Fate & Struggle'},
        {'chords': ['i', 'VII', 'III', 'VI'],'label': 'Dark Triumph'},
        {'chords': ['VI', 'III', 'VII', 'i'],'label': 'Rising from Ashes'},
    ]},
    "4": {"name": "Romantic & Emotional", "tension": 0.42, "progressions": [
        {'chords': ['i', 'VI', 'III', 'VII'], 'label': 'Lush Romance'},
        {'chords': ['i', 'III', 'VII', 'VI'], 'label': 'Emotional Sweep'},
        {'chords': ['i', 'VII', 'VI', 'III'], 'label': 'Descending Warmth'},
        {'chords': ['VI', 'VII', 'i', 'III'], 'label': 'Anticipation'},
        {'chords': ['i', 'iv', 'VI', 'VII'],  'label': 'Stirring Emotion'},
        {'chords': ['i', 'VI', 'VII', 'III'], 'label': 'Longing Romance'},
        {'chords': ['III', 'VI', 'VII', 'i'], 'label': 'Building Romance'},
        {'chords': ['i', 'III', 'iv', 'VII'], 'label': 'Heart Swell'},
    ]},
    "5": {"name": "Lonely & Empty", "tension": 0.28, "attributes": "sparse, hollow, unresolved", "progressions": [
        {'chords': ['i', 'i', 'VI', 'i'],       'label': 'Empty Room'},
        {'chords': ['i', 'bVI', 'i', 'v'],      'label': 'Hollow Distance'},
        {'chords': ['i', 'iio', 'i', 'VI'],     'label': 'Cold Stillness'},
        {'chords': ['i', 'v', 'i', 'bII'],      'label': 'Bare Walls'},
        {'chords': ['i', 'VII', 'i', 'v'],      'label': 'Distant Footsteps'},
    ]},
    "6": {"name": "Grieving & Tragic", "tension": 0.65, "attributes": "lamenting, heavy, cadential", "progressions": [
        {'chords': ['i', 'bII', 'V', 'i'],      'label': 'Neapolitan Grief'},
        {'chords': ['i', 'viio', 'V', 'i'],     'label': 'Tragic Cadence'},
        {'chords': ['i', 'iv7', 'bII', 'V7'],   'label': 'Cathedral Lament'},
        {'chords': ['i', 'bVI', 'iv', 'V7'],    'label': 'Final Goodbye'},
        {'chords': ['i', 'VI', 'viio', 'V'],    'label': 'Tears Held Back'},
    ]},
    "7": {"name": "Broken & Vulnerable", "tension": 0.43, "attributes": "fragile, intimate, unresolved", "progressions": [
        {'chords': ['i', 'iv7', 'VI', 'i'],     'label': 'Fragile Confession'},
        {'chords': ['i', 'III', 'iv7', 'i'],    'label': 'Quiet Apology'},
        {'chords': ['i', 'VI', 'iv7', 'v'],     'label': 'Cracked Heart'},
        {'chords': ['VI', 'i', 'iv', 'i'],      'label': 'Soft Collapse'},
        {'chords': ['i', 'v', 'VI', 'iv7'],     'label': 'Unsteady Breath'},
    ]},
    "8": {"name": "Heroic Through Suffering", "tension": 0.78, "attributes": "painful resolve, rising, cinematic", "progressions": [
        {'chords': ['i', 'bVI', 'V', 'i'],      'label': 'Wounded Victory'},
        {'chords': ['i', 'iv', 'bVI', 'V7'],    'label': 'Rise Through Pain'},
        {'chords': ['i', 'bII', 'VI', 'V'],     'label': 'Defiant Wound'},
        {'chords': ['VI', 'V', 'i', 'VII'],     'label': 'Scarred Ascension'},
        {'chords': ['i', 'viio', 'VI', 'V7'],   'label': 'Trial by Fire'},
    ]},
    "9": {"name": "Battle-Hardened & Determined", "tension": 0.84, "attributes": "driving, severe, martial", "progressions": [
        {'chords': ['i', 'V7', 'bVI', 'V'],     'label': 'Iron Resolve'},
        {'chords': ['i', 'iv', 'V7', 'i'],      'label': 'March of Scars'},
        {'chords': ['i', 'bVII', 'bVI', 'V7'],  'label': 'No Retreat'},
        {'chords': ['i', 'V', 'viio', 'V7'],    'label': 'Hard Pursuit'},
        {'chords': ['i', 'iv', 'bII', 'V'],     'label': 'Siege Engine'},
    ]},
    "10": {"name": "Funeral & Ceremonial", "tension": 0.58, "attributes": "processional, solemn, ritual", "progressions": [
        {'chords': ['i', 'iv7', 'V7', 'i'],     'label': 'Funeral Procession'},
        {'chords': ['i', 'bII', 'iv7', 'V7'],   'label': 'Ritual Toll'},
        {'chords': ['i', 'VI', 'iv7', 'V'],     'label': 'Memorial Hymn'},
        {'chords': ['i', 'v', 'iv', 'i'],       'label': 'Slow Cortege'},
        {'chords': ['i', 'iv7', 'bVI', 'V7'],   'label': 'Ceremonial Ashes'},
    ]},
    "11": {"name": "Farewell & Separation", "tension": 0.60, "attributes": "final, restrained, parting", "progressions": [
        {'chords': ['i', 'VI', 'iv7', 'V7'],    'label': 'Last Embrace'},
        {'chords': ['i', 'bII', 'V7', 'VI'],    'label': 'Train Platform'},
        {'chords': ['i', 'iv', 'bVI', 'v'],     'label': 'Leaving at Dawn'},
        {'chords': ['VI', 'iv7', 'i', 'V'],     'label': 'Unsent Goodbye'},
        {'chords': ['i', 'VII', 'iv7', 'V7'],   'label': 'Distance Growing'},
    ]},
    "12": {"name": "Regret & Lost Chances", "tension": 0.58, "attributes": "reflective, unresolved, aching", "progressions": [
        {'chords': ['i', 'III', 'iv7', 'V'],    'label': 'What Could Have Been'},
        {'chords': ['i', 'VI', 'iio', 'V7'],    'label': 'Missed Doorway'},
        {'chords': ['III', 'iv7', 'VI', 'V'],   'label': 'Old Mistake'},
        {'chords': ['i', 'v', 'bII', 'V'],      'label': 'Too Late'},
        {'chords': ['VI', 'i', 'III', 'iv7'],   'label': 'Faded Chance'},
    ]},
    "13": {"name": "Tragic Romance", "tension": 0.62, "attributes": "fatalistic, passionate, cinematic heartbreak", "progressions": [
        {'chords': ['i', 'VI', 'bII', 'V7'],    'label': 'Doomed Lovers'},
        {'chords': ['i', 'iv7', 'viio', 'V7'],  'label': 'Fatal Promise'},
        {'chords': ['i', 'III', 'bVI', 'V'],    'label': 'Love in Ruins'},
        {'chords': ['VI', 'bII', 'i', 'V7'],    'label': 'Kiss Before Nightfall'},
        {'chords': ['i', 'iv7', 'bVI', 'viio'], 'label': 'Heartbreak Oath'},
    ]},
}

# ── MOOD PROGRESSIONS (Major) ───────────────────────────────────────────────
MOODS_MAJOR = {
    "1": {"name": "Uplifting & Joyful", "tension": 0.35, "progressions": [
        {'chords': ['I', 'V', 'vi', 'IV'],      'label': 'Pop-Punk Anthem'},
        {'chords': ['I', 'IV', 'V', 'I'],       'label': 'Standard Cadence'},
        {'chords': ['I', 'IV', 'vi', 'V'],      'label': 'Optimistic Leap'},
        {'chords': ['I', 'vi', 'IV', 'V'],      'label': 'Classic 50s Stand-By'},
        {'chords': ['I', 'V', 'I', 'IV'],       'label': 'Bright Morning'},
        {'chords': ['I', 'IV', 'I', 'V'],       'label': 'Folksy Joy'},
    ]},
    "2": {"name": "Majestic & Triumphant", "tension": 0.65, "progressions": [
        {'chords': ['I', 'bVII', 'IV', 'I'],    'label': 'Mixolydian Rock Anthem'},
        {'chords': ['I', 'V', 'vi', 'iii','IV','I','IV','V'], 'label': 'Canon Heroic'},
        {'chords': ['I', 'IV', 'bVII', 'I'],    'label': 'Ascent to Glory'},
        {'chords': ['I', 'bIII', 'bVII', 'IV'], 'label': 'Epic Orchestral Lift'},
        {'chords': ['I', 'II', 'IV', 'I'],      'label': 'Lydian Rising'},
        {'chords': ['I', 'bVII', 'I', 'IV'],    'label': 'Royal Procession'},
        {'chords': ['I', 'bVI', 'bVII', 'I'],   'label': 'Fantasy Anthem'},
    ]},
    "3": {"name": "Serene & Dreamy", "tension": 0.25, "progressions": [
        {'chords': ['I', 'II', 'I', 'II'],             'label': 'Lydian Ethereal Cloud'},
        {'chords': ['Imaj7', 'IVmaj7', 'Imaj7', 'IVmaj7'], 'label': 'Celestial Float'},
        {'chords': ['I', 'IVmaj7', 'V', 'I'],          'label': 'Lush Meadow'},
        {'chords': ['I', 'bVII', 'I', 'bVII'],         'label': 'Mixolydian Drifting'},
        {'chords': ['I', 'iii', 'IV', 'V'],            'label': 'Peaceful River'},
        {'chords': ['I', 'vi', 'iii', 'IV'],           'label': 'Dreamy Reflection'},
        {'chords': ['I', 'Imaj7', 'IV', 'IVmaj7'],     'label': 'Soft Morning Breeze'},
    ]},
    "4": {"name": "Nostalgic & Bittersweet (Major)", "tension": 0.45, "progressions": [
        {'chords': ['I', 'iv', 'I', 'iv'],             'label': 'Melodic Major Sorrow'},
        {'chords': ['I', 'V', 'vi', 'iv'],             'label': 'Bittersweet Epilogue'},
        {'chords': ['I', 'vi', 'ii', 'V'],             'label': 'Jazz Nostalgia'},
        {'chords': ['I', 'iii', 'vi', 'IV'],           'label': 'Wistful Reflection'},
        {'chords': ['I', 'bVI', 'bIII', 'bVII'],       'label': 'Cinematic Memories'},
        {'chords': ['I', 'vi', 'iii', 'IV'],           'label': 'Warm Regret'},
        {'chords': ['I', 'bVI', 'IV', 'I'],            'label': 'Solitary Path'},
    ]},
    "5": {"name": "Warm & Romantic", "tension": 0.43, "attributes": "lush, tender, consonant", "progressions": [
        {'chords': ['Imaj7', 'vi', 'IVmaj7', 'V'],      'label': 'Golden Embrace'},
        {'chords': ['I6', 'IVmaj7', 'ii7', 'V'],        'label': 'Candlelight Turn'},
        {'chords': ['I', 'iii', 'IVmaj7', 'ii7'],       'label': 'Tender Promise'},
        {'chords': ['Imaj7', 'ii7', 'IV6', 'V'],        'label': 'Open Heart'},
        {'chords': ['Imaj7', 'vi', 'IV6', 'V6'],        'label': 'Soft Devotion'},
    ]},
    "6": {"name": "Glorious & Epic", "tension": 0.82, "attributes": "wide, triumphant, cinematic", "progressions": [
        {'chords': ['I', 'V7', 'bVI', 'bVII'],          'label': 'Crowned Horizon'},
        {'chords': ['I', 'II', 'V', 'bVII'],            'label': 'Lydian Banner'},
        {'chords': ['I', 'bIII', 'IV', 'V7'],           'label': 'Mythic Lift'},
        {'chords': ['I', 'V', 'bVII', 'IV'],            'label': 'Glory March'},
        {'chords': ['I', 'IV', 'viio', 'V7'],           'label': 'Radiant Climax'},
    ]},
    "7": {"name": "Intimate & Vulnerable", "tension": 0.38, "attributes": "quiet, close, exposed", "progressions": [
        {'chords': ['Imaj7', 'iii', 'vi', 'ii7'],       'label': 'Quiet Confession'},
        {'chords': ['I', 'ii7', 'Imaj7', 'vi'],         'label': 'Small Voice'},
        {'chords': ['I6', 'iii', 'IVmaj7', 'I'],        'label': 'Handwritten Letter'},
        {'chords': ['I', 'vi', 'IVmaj7', 'ii7'],        'label': 'Open Window'},
        {'chords': ['Imaj7', 'iv', 'I6', 'ii7'],        'label': 'Tender Fracture'},
    ]},
    "8": {"name": "Tropical & Relaxed", "tension": 0.32, "attributes": "syncopated, major-sixth color, breezy", "progressions": [
        {'chords': ['I6', 'IV6', 'V6', 'IV6'],          'label': 'Island Sway'},
        {'chords': ['I6', 'bVII', 'IV6', 'I6'],         'label': 'Coastal Mixolydian'},
        {'chords': ['I6', 'ii7', 'IV6', 'V6'],          'label': 'Warm Current'},
        {'chords': ['I', 'IV6', 'ii7', 'V6'],           'label': 'Palm Shade'},
        {'chords': ['I6', 'V6', 'IV6', 'I6'],           'label': 'Easy Tide'},
    ]},
    "9": {"name": "Inspiring & Encouraging", "tension": 0.52, "attributes": "hopeful, grounded, forward-moving", "progressions": [
        {'chords': ['I', 'V6', 'vi', 'IVmaj7'],         'label': 'Steady Hope'},
        {'chords': ['I6', 'IV', 'ii7', 'V7'],           'label': 'Lifted Resolve'},
        {'chords': ['I', 'V', 'IV6', 'I6'],             'label': 'You Can Rise'},
        {'chords': ['Imaj7', 'vi', 'ii7', 'V6'],        'label': 'Gentle Momentum'},
        {'chords': ['I', 'II', 'IV6', 'V'],             'label': 'Bright Path Forward'},
    ]},
    "10": {"name": "Grateful & Content", "tension": 0.32, "attributes": "settled, peaceful, warmly resolved", "progressions": [
        {'chords': ['I6', 'IV6', 'I', 'V6'],            'label': 'Quiet Thanks'},
        {'chords': ['Imaj7', 'IVmaj7', 'I6', 'V'],      'label': 'Peaceful Hearth'},
        {'chords': ['I', 'vi', 'IV6', 'I'],             'label': 'At Ease'},
        {'chords': ['I6', 'ii7', 'V6', 'I'],            'label': 'Home Again'},
        {'chords': ['Imaj7', 'iii', 'IV6', 'I6'],       'label': 'Soft Gratitude'},
    ]},
}

# ── RHYTHM GRIDS ────────────────────────────────────────────────────────────
# Lyrical rhythm pool (for Violin I lead)
RHYTHM_LYRICAL = [
    (1.0, 0.45),
    (0.5, 0.35),
    (1.5, 0.10),
    (2.0, 0.08),
    (0.25, 0.02)
]

# Sustained rhythm pool (for Viola & Violin II counter)
RHYTHM_SUSTAIN = [
    (2.0, 0.50),
    (4.0, 0.30),
    (1.0, 0.15),
    (1.5, 0.05)
]

# Cello rhythm pool (more root motion / rhythmic)
RHYTHM_CELLO = [
    (1.0, 0.40),
    (2.0, 0.30),
    (4.0, 0.20),
    (0.5, 0.10)
]

# Piano rhythm pool (high emotional melody, density controlled by tension)
RHYTHM_PIANO = [
    (0.25, 0.12),
    (0.5, 0.34),
    (1.0, 0.34),
    (1.5, 0.10),
    (2.0, 0.10),
]


# ── HELPER FUNCTIONS (from minor/major generators) ─────────────────────────

def sample_from_scores(candidates, scores, temperature=0.5):
    """Softmax weighted sampling with scaling for melodic decision making."""
    if not candidates:
        return 76
    import math
    scaled_scores = [s / 10.0 for s in scores]
    max_s = max(scaled_scores)
    adj_scores = [s - max_s for s in scaled_scores]
    exp_w = [math.exp(s / max(0.05, temperature)) for s in adj_scores]
    sum_w = sum(exp_w)
    if sum_w < 1e-6:
        import random
        return random.choice(candidates)
    import random
    r = random.uniform(0, sum_w)
    acc = 0.0
    for c, w in zip(candidates, exp_w):
        acc += w
        if r <= acc:
            return c
    return candidates[-1]


def w_rhythm(pool, max_dur, t_bias=0.5):
    """Select a duration from weighted pool, limited by max_dur."""
    fit = [p for p in pool if p[0] <= max_dur + 0.01]
    if not fit:
        return max_dur
    weights = []
    for dur, base_w in fit:
        w = base_w
        if t_bias > 0.65 and dur < 1.0:
            w *= 2.0
        elif t_bias < 0.4 and dur > 1.5:
            w *= 1.8
        weights.append(w)
    s = sum(weights)
    if s < 1e-5:
        return fit[0][0]
    r = random.uniform(0, s)
    acc = 0.0
    for idx, w in enumerate(weights):
        acc += w
        if r <= acc:
            return fit[idx][0]
    return fit[-1][0]


def get_markov_matrix(scale):
    """Generate Markov transition matrix with step-wise bias."""
    sc = sorted(list(set(scale)))
    matrix = {}
    for i, note in enumerate(sc):
        row = {}
        for j, next_note in enumerate(sc):
            dist = abs(i - j)
            if dist == 0:
                row[next_note] = 0.12
            elif dist == 1:
                row[next_note] = 0.55
            elif dist == 2:
                row[next_note] = 0.22
            else:
                row[next_note] = 0.11 / (dist - 1)
        s = sum(row.values())
        if s > 0:
            row = {k: v / s for k, v in row.items()}
        matrix[note] = row
    return matrix


def pick_markov_next(current_pc, scale, matrix):
    """Pick next pitch class using Markov probabilities."""
    sc = sorted(list(set(scale)))
    pc = current_pc % 12
    if pc not in matrix:
        if not sc:
            return 0
        return min(sc, key=lambda x: abs(x - pc))
    row = matrix[pc]
    r = random.random()
    acc = 0.0
    for note, prob in row.items():
        acc += prob
        if r <= acc:
            return note
    return sc[0]


def _activity_map(tension, num_bars):
    """Call-and-response activity schedule for lead/counter voices."""
    lead_active = [True] * num_bars
    counter_active = [True] * num_bars
    if tension < 0.45:
        # Low tension: strict call-and-response alternation
        for i in range(num_bars):
            if i % 2 == 0:
                counter_active[i] = False
            else:
                lead_active[i] = False
    elif tension < 0.7:
        # Mid tension: occasional breathing room
        for i in range(num_bars):
            if i % 4 == 3:
                counter_active[i] = False
            elif i % 4 == 1:
                lead_active[i] = False
    # High tension: both active
    return lead_active, counter_active


def _lead_bar_directions(melody, num_bars):
    """Calculate per-bar pitch direction for contrary motion."""
    dirs = [0] * num_bars
    if not melody:
        return dirs
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


GENERATION_MODE = 'simple'

def generate_decoupled_progression(tension, scale_tones, is_minor=True):
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
    roman_numerals = RN_MINOR if is_minor else RN_MAJOR
    symbol_roots = {}
    for sym, (offsets, _) in roman_numerals.items():
        symbol_roots[sym] = offsets[0] % 12
        
    rn_list = list(roman_numerals.keys())
    if is_minor:
        current_symbol = 'i' if 'i' in rn_list else rn_list[0]
    else:
        current_symbol = 'I' if 'I' in rn_list else rn_list[0]
    
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

# ── CHORD GENERATION ────────────────────────────────────────────────────────

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

def generate_chords(root_note, progression, roman_numerals):
    """Generate MIDI chord voicings from roman numeral progression."""
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


def _pitch_in_register(root_note, offset, register, preferred=None):
    """Choose the octave of a scale/chord offset that sits in an instrument lane."""
    register_min = register['min']
    register_max = register['max']
    center = preferred if preferred is not None else register.get('center', (register_min + register_max) // 2)
    pc = (root_note + offset) % 12
    candidates = [pitch for pitch in range(register_min, register_max + 1) if pitch % 12 == pc]
    if candidates:
        return min(candidates, key=lambda pitch: (abs(pitch - center), pitch))

    pitch = root_note + offset
    while pitch < register_min:
        pitch += 12
    while pitch > register_max:
        pitch -= 12
    return max(register_min, min(register_max, pitch))


def _melody_bar_pitch_sets(melody, num_bars):
    """Collect sounding notes by bar so adjacent parts can avoid unisons."""
    bars = [set() for _ in range(num_bars)]
    beat_pos = 0.0
    for note, dur in melody or []:
        if note is not None:
            start_bar = int(beat_pos // 4.0)
            end_bar = int(max(beat_pos, beat_pos + dur - 0.001) // 4.0)
            for bar in range(start_bar, min(num_bars - 1, end_bar) + 1):
                bars[bar].add(note)
        beat_pos += dur
    return bars


def _avoid_bar_unison(pitch, avoid_notes, register):
    """Move by octave within the lane if a neighboring instrument owns the note."""
    if not avoid_notes or pitch not in avoid_notes:
        return pitch
    for candidate in (pitch - 12, pitch + 12):
        if register['min'] <= candidate <= register['max'] and candidate not in avoid_notes:
            return candidate
    return pitch


# ── MELODY GENERATION ───────────────────────────────────────────────────────

def generate_violin_lead(root_note, progression, roman_numerals, tension=0.5):
    """Generate Violin I lead melody in a warm lead register."""
    bars_data = []
    for bar_item in progression:
        if isinstance(bar_item, list):
            bar_data = []
            for num, dur in bar_item:
                ct_raw, scale = roman_numerals[num]
                bar_data.append(([t % 12 for t in ct_raw], [t % 12 for t in scale], dur))
            bars_data.append(bar_data)
        else:
            ct_raw, scale = roman_numerals[bar_item]
            bars_data.append(([t % 12 for t in ct_raw], [t % 12 for t in scale]))
    return _generate_lead_core(root_note, bars_data, tension)


def _generate_lead_core(root_note, bars_data, tension=0.5):
    """Core lead melody generator — lyrical Violin I part."""
    melody = []
    cur = 0
    lead_active, _ = _activity_map(tension, len(bars_data))
    motif_rhythm = None

    for bar_idx, bar_harmony in enumerate(bars_data):
        if isinstance(bar_harmony, list):
            first_scale = bar_harmony[0][1]
        else:
            first_scale = bar_harmony[1]
        matrix = get_markov_matrix(first_scale)

        if not lead_active[bar_idx]:
            # Inactive bar: rest or sustained chord tone
            if random.random() < 0.4:
                ct, sc = get_bar_harmony_at_beat(bar_harmony, 0.0)
                pitch = _pitch_in_register(root_note, random.choice(ct), VIOLIN1_REGISTER)
                melody.append((pitch, 4.0))
            else:
                melody.append((None, 4.0))
            continue

        # Active bar: lyrical motif
        bar_rhythm = []
        if motif_rhythm is None or tension > 0.65:
            beats_left = 4.0
            while beats_left > 0.01:
                dur = w_rhythm(RHYTHM_LYRICAL, beats_left, tension * 0.7)
                bar_rhythm.append(dur)
                beats_left -= dur
            if motif_rhythm is None:
                motif_rhythm = bar_rhythm
        else:
            bar_rhythm = motif_rhythm

        beat_pos = 0.0
        for dur in bar_rhythm:
            ct, sc = get_bar_harmony_at_beat(bar_harmony, beat_pos)
            matrix = get_markov_matrix(sc)

            strong = (beat_pos % 2.0 < 0.01)
            if strong or random.random() < 0.5:
                off = random.choice(ct)
            else:
                off = pick_markov_next(cur, sc, matrix)

            pitch = _pitch_in_register(root_note, off, VIOLIN1_REGISTER)

            # Expressive octave jump on strong downbeat
            if strong and random.random() < 0.10 and pitch + 12 <= VIOLIN1_REGISTER['max']:
                pitch += 12

            melody.append((pitch, dur))
            cur = off
            beat_pos += dur

    return melody


def _violin2_activity_map(tension, num_bars):
    """
    Dedicated activity schedule for Violin II — inverse of Violin I lead.
    When lead is active (bars 0,2 for low tension), Violin II rests.
    When lead rests (bars 1,3), Violin II responds.
    Creates genuine call-and-response between the two violins.
    Returns a bool list where True = active.
    """
    active = [False] * num_bars
    if tension < 0.45:
        # Strict alternation: Violin II opposite to Violin I
        for i in range(num_bars):
            if i % 2 == 0:
                active[i] = False   # Violin I plays
            else:
                active[i] = True    # Violin II responds
    elif tension < 0.7:
        # Mid tension: Violin II active on development and climax bars
        for i in range(num_bars):
            if i % 4 == 0:
                active[i] = False   # Violin I plays statement
            elif i % 4 == 1:
                active[i] = True    # Violin II answers
            elif i % 4 == 2:
                active[i] = True    # Both develop together
            elif i % 4 == 3:
                active[i] = False   # Both breathe
    else:
        # High tension: both active on all bars
        for i in range(num_bars):
            active[i] = True
    return active


def generate_violin_counter(root_note, progression, roman_numerals, tension=0.5, lead_melody=None):
    """Generate Violin II counter-melody below Violin I.
    Uses dedicated call-and-response: Violin II responds when Violin I rests."""
    bars_data = []
    for bar_item in progression:
        if isinstance(bar_item, list):
            bar_data = []
            for num, dur in bar_item:
                ct_raw, scale = roman_numerals[num]
                bar_data.append(([t % 12 for t in ct_raw], [t % 12 for t in scale], dur))
            bars_data.append(bar_data)
        else:
            ct_raw, scale = roman_numerals[bar_item]
            bars_data.append(([t % 12 for t in ct_raw], [t % 12 for t in scale]))
    return _generate_counter_core(root_note, bars_data, tension, lead_melody,
                                   register=VIOLIN2_REGISTER,
                                   activity_map_override='violin2')  # use staggered schedule


def generate_viola(root_note, progression, roman_numerals, tension=0.5, lead_melody=None):
    """Generate Viola harmony line below Violin II.
    Provides continuous harmonic support using chord tones."""
    bars_data = []
    for bar_item in progression:
        if isinstance(bar_item, list):
            bar_data = []
            for num, dur in bar_item:
                ct_raw, scale = roman_numerals[num]
                bar_data.append(([t % 12 for t in ct_raw], [t % 12 for t in scale], dur))
            bars_data.append(bar_data)
        else:
            ct_raw, scale = roman_numerals[bar_item]
            bars_data.append(([t % 12 for t in ct_raw], [t % 12 for t in scale]))
    return _generate_counter_core(root_note, bars_data, tension * 0.8, lead_melody,
                                   register=VIOLA_REGISTER,
                                   activity_map_override='continuous')  # always active


def _generate_counter_core(root_note, bars_data, tension=0.5, lead_melody=None,
                            register_min=48, register_max=72, base_octave=12,
                            chord_bias=0.75, activity_map_override=None,
                            register=None):
    """
    Core counter-melody generator — sustained legato with chord-tone harmony.
    """
    counter = []
    cur = 7
    if register is None:
        register = {'min': register_min, 'max': register_max, 'center': (register_min + register_max) // 2}

    # Determine activity schedule
    if activity_map_override == 'violin2':
        counter_active = _violin2_activity_map(tension, len(bars_data))
    elif activity_map_override == 'continuous':
        counter_active = [True] * len(bars_data)
    else:
        _, counter_active = _activity_map(tension, len(bars_data))

    lead_dirs = _lead_bar_directions(lead_melody, len(bars_data)) if lead_melody else [0] * len(bars_data)
    avoid_by_bar = _melody_bar_pitch_sets(lead_melody, len(bars_data)) if lead_melody else [set() for _ in bars_data]

    for bar_idx, bar_harmony in enumerate(bars_data):
        if isinstance(bar_harmony, list):
            first_scale = bar_harmony[0][1]
        else:
            first_scale = bar_harmony[1]
        matrix = get_markov_matrix(first_scale)

        if not counter_active[bar_idx]:
            if random.random() < 0.3:
                ct, sc = get_bar_harmony_at_beat(bar_harmony, 0.0)
                # Sustained chord root on inactive bars
                pitch = _pitch_in_register(root_note, ct[0], register)
                pitch = _avoid_bar_unison(pitch, avoid_by_bar[bar_idx], register)
                counter.append((pitch, 4.0))
            else:
                counter.append((None, 4.0))
            continue

        beats_left = 4.0
        beat_pos = 0.0
        while beats_left > 0.01:
            dur = w_rhythm(RHYTHM_SUSTAIN, beats_left, tension * 0.4)
            ct, sc = get_bar_harmony_at_beat(bar_harmony, beat_pos)
            matrix = get_markov_matrix(sc)
            strong = (beat_pos % 2.0 < 0.01)

            if strong:
                # Strong beats: ALWAYS pick a chord tone for harmonic clarity
                off = random.choice(ct)
            elif random.random() < chord_bias:
                # Weak beats: biased toward chord tones, but allow passing tones
                off = random.choice(ct)
            else:
                # Passing tone from scale
                off = pick_markov_next(cur, sc, matrix)

            # Contrary motion: if lead went up, go down (and vice versa)
            if lead_dirs[bar_idx] > 0 and off > cur:
                lower = [t for t in ct if t < cur]
                if lower:
                    off = random.choice(lower)
            elif lead_dirs[bar_idx] < 0 and off < cur:
                higher = [t for t in ct if t > cur]
                if higher:
                    off = random.choice(higher)

            pitch = _pitch_in_register(root_note, off, register)
            pitch = _avoid_bar_unison(pitch, avoid_by_bar[bar_idx], register)

            counter.append((pitch, dur))
            cur = off
            beats_left -= dur
            beat_pos += dur

    return counter


def generate_cello(root_note, progression, roman_numerals, tension=0.5):
    """Generate Cello bass line — sustained root/fifth pedal tones."""
    cello = []
    chords_data = []
    for bar_item in progression:
        if isinstance(bar_item, list):
            bar_data = []
            for num, dur in bar_item:
                ct_raw, scale = roman_numerals[num]
                bar_data.append(([t % 12 for t in ct_raw], [t % 12 for t in scale], dur))
            chords_data.append(bar_data)
        else:
            ct_raw, scale = roman_numerals[bar_item]
            chords_data.append(([t % 12 for t in ct_raw], [t % 12 for t in scale]))

    for bar_idx, bar_harmony in enumerate(chords_data):
        if isinstance(bar_harmony, list):
            # Subdivided chords: play root of each subdivision
            for ct, sc, dur in bar_harmony:
                root_pc = ct[0]
                root_pitch = _pitch_in_register(root_note, root_pc, CELLO_REGISTER)
                cello.append((root_pitch, dur))
        else:
            ct, sc = bar_harmony
            root_pc = ct[0]
            fifth_pc = ct[2 % len(ct)] if len(ct) > 2 else ct[1 % len(ct)]

            # ── Root pitch in the cello's low composition lane ──
            root_pitch = _pitch_in_register(root_note, root_pc, CELLO_REGISTER)

            # ── Fifth pitch, voice-led close to root ──
            fifth_pitch = _pitch_in_register(root_note, fifth_pc, CELLO_REGISTER, preferred=root_pitch + 7)

            # ── Compose the bar — always sustained ──
            if tension < 0.45:
                # Whole note: root held for the entire bar
                cello.append((root_pitch, 4.0))
            elif tension < 0.7:
                # Two half notes: root + fifth
                cello.append((root_pitch, 2.0))
                cello.append((fifth_pitch, 2.0))
            else:
                # Half note root + quarter fifth + quarter leading tone
                next_bar = (bar_idx + 1) % len(chords_data)
                next_item = chords_data[next_bar]
                if isinstance(next_item, list):
                    next_root_pc = next_item[0][0][0]
                else:
                    next_root_pc = next_item[0][0]
                next_root_pitch = _pitch_in_register(root_note, next_root_pc, CELLO_REGISTER, preferred=root_pitch)
                # Approach from a half-step below the next root
                approach = next_root_pitch - 1
                if approach < CELLO_REGISTER['min']:
                    approach += 12
                if approach > CELLO_REGISTER['max']:
                    approach -= 12

                cello.append((root_pitch, 2.0))
                cello.append((fifth_pitch, 1.0))
                cello.append((approach, 1.0))

    return cello


def generate_piano_melody(root_note, bars_data, tension=0.5):
    """
    Generate a high piano melody that decorates the harmony above the strings.
    Low tension stays sparse; higher tension increases rhythmic activity.
    """
    piano = []
    cur = 0

    for bar_idx, bar_harmony in enumerate(bars_data):
        if isinstance(bar_harmony, list):
            first_scale = bar_harmony[0][1]
        else:
            first_scale = bar_harmony[1]
        matrix = get_markov_matrix(first_scale)
        active_chance = 0.45 + tension * 0.45
        forced_anchor = (bar_idx == 0)
        if not forced_anchor and random.random() > active_chance:
            piano.append((None, 4.0))
            continue

        beats_left = 4.0
        beat_pos = 0.0
        while beats_left > 0.01:
            dur = w_rhythm(RHYTHM_PIANO, beats_left, tension)
            ct, sc = get_bar_harmony_at_beat(bar_harmony, beat_pos)
            matrix = get_markov_matrix(sc)
            strong = (beat_pos % 2.0 < 0.01)

            if strong or random.random() < 0.70:
                off = random.choice(ct)
            else:
                off = pick_markov_next(cur, sc, matrix)

            pitch = _pitch_in_register(root_note, off, PIANO_REGISTER)
            if strong and tension > 0.65 and random.random() < 0.20 and pitch + 12 <= PIANO_REGISTER['max']:
                pitch += 12

            piano.append((pitch, dur))
            cur = off
            beats_left -= dur
            beat_pos += dur

            rest_chance = 0.35 - tension * 0.25
            if beats_left > 0.01 and random.random() < rest_chance:
                rest_dur = min(beats_left, random.choice([0.5, 1.0]))
                piano.append((None, rest_dur))
                beats_left -= rest_dur
                beat_pos += rest_dur

    return piano


# ── VOICE LEADING ────────────────────────────────────────────────────────────

def voice_lead_chord(prev_voicing, target_pcs, register_min=36, register_max=84):
    """Voice-leading: minimize pitch movement between chord transitions."""
    if not prev_voicing:
        voicing = []
        for i in range(6):
            pc = target_pcs[i % len(target_pcs)]
            voicing.append(48 + 12 * (i // len(target_pcs)) + pc)
        return sorted(voicing)

    voicing = []
    for i, prev_pitch in enumerate(prev_voicing):
        pc = target_pcs[i % len(target_pcs)]
        best_pitch = None
        best_dist = 9999
        for octave in range(register_min, register_max + 1, 12):
            pitch = octave + pc
            dist = abs(pitch - prev_pitch)
            if dist < best_dist:
                best_dist = dist
                best_pitch = pitch
        voicing.append(best_pitch)

    voicing = sorted(list(set(voicing)))
    while len(voicing) < len(prev_voicing):
        new_note = voicing[0] + 12
        while new_note in voicing:
            new_note += 12
        voicing.append(new_note)
        voicing = sorted(list(set(voicing)))
    return voicing[:len(prev_voicing)]


# ── OSTINATO ENGINE ───────────────────────────────────────────────────────
# A single unified ostinato voice that plays both high arpeggiated chord tones
# AND low root/fifth punches in one track, weaving them together into a rich,
# composite rhythmic tapestry that follows the chord progression.
#
# Pattern selection is driven by BPM:
#   Slow/Flowing  (100-115 BPM): Broad arpeggios, pedal anchor points
#   Moderate      (116-130 BPM): 8th-note interlock, syncopation
#   Driving       (131-140 BPM): 16th-note runs, triplet subdivisions
#   Energetic     (141-150 BPM): Rapid hocket, cross-rhythm drive
#
# Each pattern interleaves a "high" step (arpeggiated chord tone, G4-D6)
# and a "low" step (root/fifth punch, C3-C4) within the same bar.
# The high notes shimmer over the chords, the low notes anchor the rhythm.

# Ostinato composite patterns — each step is (offset_beats, duration_beats, register)
# where register is 'high' or 'low' to determine pitch selection.
OST_SLOW_PATTERNS = {
    'sweep_and_anchor': [
        (0.0, 0.5, 'low'),   # Low root punch
        (0.5, 0.5, 'high'),  # High arpeggio
        (1.0, 0.5, 'low'),   # Low fifth
        (1.5, 0.5, 'high'),  # High arpeggio
        (2.0, 0.5, 'low'),   # Low root
        (2.5, 0.5, 'high'),  # High arpeggio
        (3.0, 0.5, 'low'),   # Low fifth
        (3.5, 0.5, 'high'),  # High arpeggio
    ],
    'broad_lift': [
        (0.0, 1.0, 'low'),   # Low root held
        (1.0, 1.0, 'high'),  # High third/fifth
        (2.0, 1.0, 'low'),   # Low fifth
        (3.0, 1.0, 'high'),  # High octave
    ],
    'lilt_and_pedal': [
        (0.0, 0.75, 'low'),  # Low root
        (0.75, 0.25, 'high'),# High grace note
        (1.0, 0.5, 'high'),  # High sustain
        (1.5, 0.5, 'low'),   # Low fifth
        (2.0, 0.75, 'low'),  # Low root
        (2.75, 0.25, 'high'),# High grace note
        (3.0, 0.5, 'high'),  # High sustain
        (3.5, 0.5, 'low'),   # Low fifth
    ],
}

OST_MODERATE_PATTERNS = {
    'interlock_3_3_2': [
        (0.0, 0.75, 'low'),  (0.75, 0.75, 'high'),
        (1.5, 0.5, 'low'),   (2.0, 0.75, 'high'),
        (2.75, 0.75, 'low'), (3.5, 0.5, 'high'),
    ],
    'eighth_weave': [
        (0.0, 0.5, 'low'),   (0.5, 0.5, 'high'),
        (1.0, 0.5, 'low'),   (1.5, 0.5, 'high'),
        (2.0, 0.5, 'low'),   (2.5, 0.5, 'high'),
        (3.0, 0.5, 'low'),   (3.5, 0.5, 'high'),
    ],
    'pulse_and_swell': [
        (0.5, 0.5, 'low'),   (1.0, 0.5, 'high'),
        (1.5, 0.5, 'low'),   (2.0, 0.5, 'high'),
        (2.5, 0.5, 'low'),   (3.0, 0.5, 'high'),
        (3.5, 0.25, 'low'),  (3.75, 0.25, 'high'),
    ],
    'syncopated_halfstep': [
        (0.0, 0.25, 'low'),  (0.25, 0.5, 'high'),
        (0.75, 0.25, 'low'), (1.0, 0.5, 'high'),
        (1.5, 0.25, 'low'),  (1.75, 0.5, 'high'),
        (2.25, 0.25, 'low'), (2.5, 0.5, 'high'),
        (3.0, 0.25, 'low'),  (3.25, 0.5, 'high'),
        (3.75, 0.25, 'low'),
    ],
}

OST_DRIVING_PATTERNS = {
    'sixteenth_alternation': [
        (0.0, 0.25, 'low'),   (0.25, 0.25, 'high'),
        (0.5, 0.25, 'low'),   (0.75, 0.25, 'high'),
        (1.0, 0.25, 'low'),   (1.25, 0.25, 'high'),
        (1.5, 0.25, 'low'),   (1.75, 0.25, 'high'),
        (2.0, 0.25, 'low'),   (2.25, 0.25, 'high'),
        (2.5, 0.25, 'low'),   (2.75, 0.25, 'high'),
        (3.0, 0.25, 'low'),   (3.25, 0.25, 'high'),
        (3.5, 0.25, 'low'),   (3.75, 0.25, 'high'),
    ],
    'triplet_interplay': [
        (0.0, 0.25, 'low'),   (0.25, 0.25, 'high'),
        (0.5, 0.25, 'low'),   (0.75, 0.25, 'high'),
        (1.0, 0.5, 'low'),    (1.5, 0.25, 'high'),
        (1.75, 0.25, 'low'),  (2.0, 0.5, 'high'),
        (2.5, 0.25, 'low'),   (2.75, 0.25, 'high'),
        (3.0, 0.25, 'low'),   (3.25, 0.25, 'high'),
        (3.5, 0.25, 'low'),   (3.75, 0.25, 'high'),
    ],
    'cinematic_5_over_4': [
        (0.0, 0.25, 'low'),   (0.25, 0.25, 'high'),
        (0.5, 0.25, 'low'),   (0.75, 0.25, 'high'),
        (1.0, 0.25, 'low'),   (1.25, 0.25, 'high'),
        (1.5, 0.25, 'low'),   (1.75, 0.25, 'high'),
        (2.0, 0.25, 'low'),   (2.25, 0.25, 'high'),
        (2.5, 0.25, 'low'),   (2.75, 0.25, 'high'),
        (3.0, 0.25, 'low'),   (3.25, 0.25, 'high'),
        (3.5, 0.25, 'low'),   (3.75, 0.25, 'high'),
    ],
    'accelerando_Riff': [
        (0.0, 0.5, 'low'),    (0.5, 0.25, 'high'),
        (0.75, 0.25, 'low'),  (1.0, 0.25, 'high'),
        (1.25, 0.125, 'low'), (1.375, 0.125, 'high'),
        (1.5, 0.125, 'low'),  (1.625, 0.125, 'high'),
        (1.75, 0.25, 'low'),  (2.0, 0.5, 'high'),
        (2.5, 0.25, 'low'),   (2.75, 0.25, 'high'),
        (3.0, 0.125, 'low'),  (3.125, 0.125, 'high'),
        (3.25, 0.125, 'low'), (3.375, 0.125, 'high'),
        (3.5, 0.125, 'low'),  (3.625, 0.125, 'high'),
        (3.75, 0.25, 'low'),
    ],
}

OST_ENERGETIC_PATTERNS = {
    'rapid_hocket': [
        (0.0, 0.125, 'low'),  (0.125, 0.125, 'high'),
        (0.25, 0.125, 'low'), (0.375, 0.125, 'high'),
        (0.5, 0.125, 'low'),  (0.625, 0.125, 'high'),
        (0.75, 0.125, 'low'), (0.875, 0.125, 'high'),
        (1.0, 0.125, 'low'),  (1.125, 0.125, 'high'),
        (1.25, 0.125, 'low'), (1.375, 0.125, 'high'),
        (1.5, 0.125, 'low'),  (1.625, 0.125, 'high'),
        (1.75, 0.125, 'low'), (1.875, 0.125, 'high'),
        (2.0, 0.125, 'low'),  (2.125, 0.125, 'high'),
        (2.25, 0.125, 'low'), (2.375, 0.125, 'high'),
        (2.5, 0.125, 'low'),  (2.625, 0.125, 'high'),
        (2.75, 0.125, 'low'), (2.875, 0.125, 'high'),
        (3.0, 0.125, 'low'),  (3.125, 0.125, 'high'),
        (3.25, 0.125, 'low'), (3.375, 0.125, 'high'),
        (3.5, 0.125, 'low'),  (3.625, 0.125, 'high'),
        (3.75, 0.125, 'low'), (3.875, 0.125, 'high'),
    ],
    'cinematic_7_8': [
        (0.0, 0.25, 'low'),   (0.25, 0.25, 'high'),
        (0.5, 0.25, 'low'),   (0.75, 0.25, 'high'),
        (1.0, 0.25, 'low'),   (1.25, 0.25, 'high'),
        (1.5, 0.25, 'low'),   (1.75, 0.25, 'high'),
        (2.0, 0.25, 'low'),   (2.25, 0.25, 'high'),
        (2.5, 0.25, 'low'),   (2.75, 0.25, 'high'),
        (3.0, 0.25, 'low'),   (3.25, 0.25, 'high'),
    ],
    'tremolo_run': [
        (0.0, 0.125, 'low'),  (0.125, 0.125, 'high'),
        (0.25, 0.125, 'low'), (0.375, 0.125, 'high'),
        (0.5, 0.125, 'low'),  (0.625, 0.125, 'high'),
        (0.75, 0.125, 'low'), (0.875, 0.125, 'high'),
        (1.0, 0.125, 'low'),  (1.125, 0.125, 'high'),
        (1.25, 0.125, 'low'), (1.375, 0.125, 'high'),
        (1.5, 0.125, 'low'),  (1.625, 0.125, 'high'),
        (1.75, 0.125, 'low'), (1.875, 0.125, 'high'),
        (2.0, 0.125, 'low'),  (2.125, 0.125, 'high'),
        (2.25, 0.125, 'low'), (2.375, 0.125, 'high'),
        (2.5, 0.125, 'low'),  (2.625, 0.125, 'high'),
        (2.75, 0.125, 'low'), (2.875, 0.125, 'high'),
        (3.0, 0.125, 'low'),  (3.125, 0.125, 'high'),
        (3.25, 0.125, 'low'), (3.375, 0.125, 'high'),
        (3.5, 0.125, 'low'),  (3.625, 0.125, 'high'),
        (3.75, 0.125, 'low'), (3.875, 0.125, 'high'),
    ],
}

# Map every key (slow, moderate, driving, energetic) to a flat pool
_OST_POOLS = {
    **OST_SLOW_PATTERNS,
    **OST_MODERATE_PATTERNS,
    **OST_DRIVING_PATTERNS,
    **OST_ENERGETIC_PATTERNS,
}

def _select_ostinato_pool(bpm, tension):
    """Select the pattern pool based on BPM range."""
    if bpm <= 115:
        return OST_SLOW_PATTERNS
    elif bpm <= 130:
        return OST_MODERATE_PATTERNS
    elif bpm <= 140:
        return OST_DRIVING_PATTERNS
    else:
        return OST_ENERGETIC_PATTERNS


def _get_pitch_for_step(chord, step_idx, total_steps, high_base=67):
    """Map a chord tone into the high ostinato register (G4-D6)."""
    if not chord:
        return high_base

    pcs = sorted(set(note % 12 for note in chord))
    if not pcs:
        return high_base

    if len(pcs) == 1:
        pc = pcs[0]
    else:
        contour = list(range(len(pcs))) + list(range(len(pcs) - 2, 0, -1))
        pc = pcs[contour[step_idx % len(contour)]]

    pitch = high_base + ((pc - high_base) % 12)
    if total_steps > len(pcs) and (step_idx // len(pcs)) % 2 == 1:
        pitch += 12

    while pitch > 86:
        pitch -= 12
    while pitch < high_base:
        pitch += 12
    return pitch


def generate_ostinato(chords, bpm, tension):
    """
    Professional short-string ostinato.

    Uses the BPM-specific ostinato pools above, but varies pattern choice and
    density per render. Pitches stay in compact playable lanes, favor chord
    tones, avoid wide octave jumps, and include bow-aware accents/humanization.
    """
    tpb = 480
    ost_events = []
    if not chords:
        return ost_events, "spiccato_empty"

    pattern_pool = _select_ostinato_pool(bpm, tension)
    pattern_names = list(pattern_pool.keys())
    home_pattern = random.choice(pattern_names)
    answer_pattern = random.choice([name for name in pattern_names if name != home_pattern] or pattern_names)
    release_pattern = random.choice(pattern_names)
    phrase_arcs = random.choice([
        [0.68, 0.86, 1.08, 0.78],
        [0.74, 0.92, 0.96, 1.12],
        [0.62, 0.82, 1.14, 0.86],
    ])
    pattern_plan = [
        home_pattern,
        home_pattern if random.random() < 0.58 else answer_pattern,
        answer_pattern,
        release_pattern,
    ]

    low_reg = {'min': 50, 'max': 60, 'center': 55}
    high_reg = {'min': 60, 'max': 72, 'center': 66}
    prev_pitch = None
    prev_high = None
    prev_low = None

    def nearest(pc, register, preferred=None):
        candidates = [p for p in range(register['min'], register['max'] + 1) if p % 12 == pc % 12]
        if not candidates:
            return register['center']
        target = preferred if preferred is not None else register['center']
        return min(candidates, key=lambda p: (abs(p - target), abs(p - register['center'])))

    for bar_idx, chord in enumerate(chords):
        bar_start = bar_idx * 4 * tpb
        chord_notes = list(chord)
        pcs = sorted(list(set(n % 12 for n in chord_notes)))
        if not pcs:
            pcs = [0, 4, 7]
            chord_notes = [60, 64, 67]

        bass_pc = chord_notes[0] % 12
        fifth_pc = pcs[2 % len(pcs)] if len(pcs) > 2 else pcs[1 % len(pcs)]
        upper_cycle = [pc for pc in pcs if pc != bass_pc] or pcs
        if random.random() < 0.35:
            upper_cycle = list(reversed(upper_cycle))

        pattern_name = pattern_plan[bar_idx % 4]
        pattern = list(pattern_pool[pattern_name])
        if phrase_arcs[bar_idx % 4] < 0.75:
            pattern = [step for step in pattern if step[0] in (0.0, 1.0, 2.0, 3.0) or random.random() > 0.35]
        elif phrase_arcs[bar_idx % 4] > 1.02 and random.random() < 0.45:
            insert_at = random.choice([0.75, 1.75, 2.75, 3.75])
            pattern.append((insert_at, 0.25, random.choice(['high', 'low'])))
            pattern.sort(key=lambda step: step[0])

        bar_energy = phrase_arcs[bar_idx % 4]
        high_step = 0
        low_step = 0

        for step_idx, (offset, dur, register_name) in enumerate(pattern):
            if bpm >= 140 and dur <= 0.125 and random.random() < 0.35:
                continue
            if bar_energy < 0.72 and offset % 1.0 not in (0.0, 0.5) and random.random() < 0.50:
                continue

            tick = bar_start + round(offset * tpb)
            jitter = 0 if offset == 0.0 else random.randint(-5, 6)
            tick = max(bar_start, tick + jitter)
            dur_ticks = max(24, round(dur * tpb))

            if register_name == 'low':
                pc = bass_pc if low_step % 2 == 0 else fifth_pc
                preferred = prev_low if prev_low is not None else low_reg['center']
                pitch = nearest(pc, low_reg, preferred)
                prev_low = pitch
                low_step += 1
                articulation = 'staccato'
                gate = 0.58
            else:
                pc = upper_cycle[high_step % len(upper_cycle)]
                if high_step % 4 == 3 and random.random() < 0.40:
                    pc = bass_pc
                preferred = prev_high if prev_high is not None else high_reg['center']
                pitch = nearest(pc, high_reg, preferred)
                prev_high = pitch
                high_step += 1
                articulation = 'spiccato'
                gate = 0.40 if dur <= 0.25 else 0.52

            if prev_pitch is not None and abs(pitch - prev_pitch) > 10:
                combined_reg = {'min': 55, 'max': 69, 'center': 62}
                pitch = nearest(pitch % 12, combined_reg, prev_pitch)
            prev_pitch = pitch

            beat_pos = int(offset)
            bow_is_down = step_idx % 2 == 0
            base_vel = int(60 + tension * 24 + bar_energy * 14)
            if offset == 0.0:
                vel = base_vel + 16
            elif beat_pos == 2 and abs(offset - 2.0) < 0.01:
                vel = base_vel + 10
            elif abs(offset - round(offset)) < 0.01:
                vel = base_vel + 5
            else:
                vel = base_vel - (7 if articulation == 'spiccato' else 3)
            if not bow_is_down:
                vel -= 4
            vel += random.randint(-5, 5)
            vel = max(42, min(118, vel))

            off_tick = tick + max(18, int(dur_ticks * gate) - random.randint(0, 8))
            ost_events.append((tick, 'on', pitch, vel, 6))
            ost_events.append((off_tick, 'off', pitch, 0, 6))

    return ost_events, "spiccato_bpm_phrase_varied"


# ── MIDI GENERATION ─────────────────────────────────────────────────────────

def _apply_vvc_track_names(mid):
    """Attach DAW-friendly track names to generated VVC MIDI tracks."""
    for idx, name in enumerate(VVC_TRACK_NAMES):
        if idx < len(mid.tracks):
            mid.tracks[idx].name = name
    return mid


VVC_PROJECT_ADJECTIVES = [
    "Apex", "Infinite", "Midnight", "Titan", "Solar", "Gothic", "Ethereal", "Grim",
    "Silent", "Shadow", "Crimson", "Nebula", "Spectral", "Cosmic", "Lost", "Fallen",
    "Eternal", "Frozen", "Abyssal", "Radiant", "Iron", "Storm", "Phoenix", "Astral",
    "Mystic", "Ancient", "Vortex", "Golden", "Obsidian", "Celestial", "Wounded",
    "Ivory", "Silver", "Marble", "Luminous", "Starlit", "Velvet", "Arcadian",
]

VVC_PROJECT_NOUNS = [
    "Ascent", "Requiem", "Odyssey", "Eclipse", "Horizon", "Empire", "Sanctuary",
    "Vanguard", "Echo", "Whisper", "Rift", "Conquest", "Genesis", "Destiny", "Void",
    "Valhalla", "Covenant", "Chronicle", "Legacy", "Bastion", "Rebirth", "Summit",
    "Oracle", "Wasteland", "Mirage", "Lament", "Citadel", "Overture", "Pilgrimage",
    "Elegy", "Procession", "Crown", "Harbor", "Cathedral", "Reverie", "Signal",
]


def _vvc_project_title():
    return f"{random.choice(VVC_PROJECT_ADJECTIVES)}_{random.choice(VVC_PROJECT_NOUNS)}"


def _vvc_slug(text):
    keep = []
    for char in str(text):
        keep.append(char if char.isalnum() or char in "#+-" else "_")
    return "_".join(part for part in "".join(keep).split("_") if part)


def _vvc_progression_from_chord_groups(chord_groups, root_pc=None, max_items=8):
    if not chord_groups:
        return "Detected_Progression"
    labels = []
    for pcs in chord_groups[:max_items]:
        if root_pc is None:
            labels.append("+".join(ROOT_NAMES[pc % 12] for pc in sorted(set(pcs))))
        else:
            rel = sorted(set((pc - root_pc) % 12 for pc in pcs))
            labels.append("+".join(str(pc) for pc in rel))
    return "-".join(labels)


def _vvc_filename(engine_mood, style, root_name, key_label, bpm, progression_label):
    project_title = _vvc_project_title()
    return (
        f"{project_title}__VVC_{_vvc_slug(engine_mood)}__{_vvc_slug(style)}__"
        f"{root_name}_{_vvc_slug(key_label)}__{bpm}BPM__{_vvc_slug(progression_label)}"
    )


def _vvc_unique_path(out_dir, fname):
    fpath = os.path.join(out_dir, fname + ".mid")
    idx = 1
    while os.path.exists(fpath):
        fpath = os.path.join(out_dir, f"{fname}_v{idx}.mid")
        idx += 1
    return fpath


def generate_string_quartet(bpm, root_name, root_val, progression, roman_numerals,
                             tension, mood_name, label_name, num_bars=4):
    """
    Main MIDI generator for the string quartet + double bass + ostinato + piano.
    Produces 8 tracks using the chord-tone-centric expressive generators:
      Track 0 (Ch 0): String Ensemble Pad (GM 48)
      Track 1 (Ch 1): Violin I - Lead Melody (GM 40)
      Track 2 (Ch 2): Violin II - Counter Melody (GM 40)
      Track 3 (Ch 3): Viola - Harmonic Fill (GM 41)
      Track 4 (Ch 4): Cello - Bass Line (GM 42)
      Track 5 (Ch 5): Double Bass - Low Foundation (GM 43)
      Track 6 (Ch 6): Spiccato Ostinato - Short Strings (GM 49)
      Track 7 (Ch 7): Piano Melody - Colour (GM 0)
    """
    tpb = 480
    full_prog = [progression[i % len(progression)] for i in range(num_bars)]
    bars_data = []
    for bar_item in full_prog:
        if isinstance(bar_item, list):
            bar_data = []
            for num, dur in bar_item:
                ct_raw, scale = roman_numerals[num]
                bar_data.append(([t % 12 for t in ct_raw], [t % 12 for t in scale], dur))
            bars_data.append(bar_data)
        else:
            ct_raw, scale = roman_numerals[bar_item]
            bars_data.append(([t % 12 for t in ct_raw], [t % 12 for t in scale]))

    # ── Generate all voices using the chord-tone-centric expressive generators ──
    # Compute shared active_bars for call-and-response between Violin I and Violin II
    _num_bars = len(bars_data)
    _v1_active = []
    for _bi in range(_num_bars):
        if _bi == 0:
            _v1_active.append(random.choice([True, False]))
        else:
            _v1_active.append(not _v1_active[-1] if random.random() < 0.6 else _v1_active[-1])

    violin1     = _generate_violin1_expressive(root_val, bars_data, tension, active_bars=_v1_active)
    violin2     = _generate_violin2_expressive(root_val, bars_data, tension,
                                               violin1_melody=violin1, violin1_active_bars=_v1_active)
    double_bass = _generate_double_bass_expressive(root_val, bars_data, tension)
    cello       = _generate_cello_expressive(root_val, bars_data, tension, double_bass_melody=double_bass)
    viola       = _generate_viola_expressive(root_val, bars_data, tension,
                                             violin1_melody=violin1, violin2_melody=violin2,
                                             cello_melody=cello, double_bass_melody=double_bass)
    piano = generate_piano_melody(root_val, bars_data, tension)

    # Build voiced chords for String Pad and Ostinato
    chords = []
    prev_voicing = []

    for bar in range(num_bars):
        bar_item = full_prog[bar]
        if isinstance(bar_item, list):
            bar_chords = []
            for num, dur in bar_item:
                if num in roman_numerals:
                    offsets, _ = roman_numerals[num]
                    target_pcs = [(root_val + offset) % 12 for offset in offsets]
                else:
                    target_pcs = [root_val, (root_val + 4) % 12, (root_val + 7) % 12]

                root_pc = target_pcs[0]
                third_pc = target_pcs[1 % len(target_pcs)]
                fifth_pc = target_pcs[2 % len(target_pcs)] if len(target_pcs) > 2 else third_pc

                if not prev_voicing:
                    voicing = sorted(list(set([
                        48 + root_pc, 48 + third_pc, 48 + fifth_pc,
                        60 + root_pc, 60 + third_pc, 60 + fifth_pc
                    ])))
                else:
                    voicing = voice_lead_chord(prev_voicing, target_pcs, register_min=48, register_max=72)
                prev_voicing = voicing
                bar_chords.append((voicing, dur))
            chords.append(bar_chords)
        else:
            prog = bar_item
            if prog in roman_numerals:
                offsets, _ = roman_numerals[prog]
                target_pcs = [(root_val + offset) % 12 for offset in offsets]
            else:
                target_pcs = [root_val, (root_val + 4) % 12, (root_val + 7) % 12]

            root_pc = target_pcs[0]
            third_pc = target_pcs[1 % len(target_pcs)]
            fifth_pc = target_pcs[2 % len(target_pcs)] if len(target_pcs) > 2 else third_pc

            if bar == 0 or not prev_voicing:
                voicing = sorted(list(set([
                    48 + root_pc, 48 + third_pc, 48 + fifth_pc,
                    60 + root_pc, 60 + third_pc, 60 + fifth_pc
                ])))
            else:
                voicing = voice_lead_chord(prev_voicing, target_pcs, register_min=48, register_max=72)
            prev_voicing = voicing
            chords.append(voicing)

    # A subdivided bar is a list of (voicing, dur) tuples; c[0] is a tuple.
    # A simple bar is already the flat voicing list; c[0] is an int.
    chords_for_ostinato = [c[0][0] if isinstance(c, list) and isinstance(c[0], tuple) else c for c in chords]
    ost_events, _ = generate_ostinato(chords_for_ostinato, bpm, tension)

    # Build 8 tracks (Ch 0–7)
    tracks_events = [[] for _ in range(8)]

    # ── Track 0: String Ensemble Pad (GM 48, Ch 0) ──
    tracks_events[0].append((0, 'program', 48, 0, 0))
    tracks_events[0].append((0, 'tempo', bpm, 0, 0))

    for bar in range(num_bars):
        bar_start_tick = bar * 4 * tpb
        bar_item = chords[bar]
        bar_dur = 4 * tpb
        vel_pad = int(48 + tension * 20)

        if isinstance(bar_item, list) and bar_item and isinstance(bar_item[0], tuple):
            # Decoupled: list of (voicing, dur) tuples
            cum_ticks = 0
            for voicing, dur in bar_item:
                dur_ticks = int(dur * tpb)
                for note in voicing:
                    tracks_events[0].append((bar_start_tick + cum_ticks, 'on', note, vel_pad, 0))
                    tracks_events[0].append((bar_start_tick + cum_ticks + dur_ticks - 15, 'off', note, 0, 0))
                cum_ticks += dur_ticks
        else:
            # Simple: flat list of pitches (the voicing itself)
            for note in bar_item:
                tracks_events[0].append((bar_start_tick, 'on', note, vel_pad, 0))
                tracks_events[0].append((bar_start_tick + bar_dur - 15, 'off', note, 0, 0))

        specialist_styles.generate_cc_curve(tracks_events[0], 1, bar_start_tick, bar_dur,
                                             start_val=50, end_val=int(60 + tension * 25), curve_type="sine", ch=0)
        specialist_styles.generate_cc_curve(tracks_events[0], 11, bar_start_tick, bar_dur,
                                             start_val=45, end_val=int(55 + tension * 30), curve_type="linear", ch=0)

    # ── Track 1: Violin I (GM 40, Ch 1) ──
    tracks_events[1].append((0, 'program', 40, 0, 1))
    current_tick = 0
    for note, duration in violin1:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_v1 = int(68 + tension * 25)
        stagger = random.randint(-4, 4)
        on_t = max(0, current_tick + stagger)
        tracks_events[1].append((on_t, 'on', note, min(127, vel_v1), 1))
        tracks_events[1].append((current_tick + dur_ticks - 15, 'off', note, 0, 1))
        c_type = "crescendo" if duration >= 2.0 and random.random() < 0.5 else "sine"
        specialist_styles.generate_cc_curve(tracks_events[1], 1, current_tick, dur_ticks,
                                             start_val=55, end_val=int(75 + tension * 20), curve_type=c_type, ch=1)
        specialist_styles.generate_cc_curve(tracks_events[1], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=int(70 + tension * 25), curve_type="sine", ch=1)
        current_tick += dur_ticks

    # ── Track 2: Violin II (GM 40, Ch 2) ──
    tracks_events[2].append((0, 'program', 40, 0, 2))
    current_tick = 0
    for note, duration in violin2:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_v2 = int(62 + tension * 22)
        stagger = random.randint(-4, 4)
        on_t = max(0, current_tick + stagger)
        tracks_events[2].append((on_t, 'on', note, min(127, vel_v2), 2))
        tracks_events[2].append((current_tick + dur_ticks - 15, 'off', note, 0, 2))
        specialist_styles.generate_cc_curve(tracks_events[2], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=int(68 + tension * 20), curve_type="sine", ch=2)
        current_tick += dur_ticks

    # ── Track 3: Viola (GM 41, Ch 3) ──
    tracks_events[3].append((0, 'program', 41, 0, 3))
    current_tick = 0
    for note, duration in viola:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_va = int(60 + tension * 20)
        stagger = random.randint(-4, 4)
        on_t = max(0, current_tick + stagger)
        tracks_events[3].append((on_t, 'on', note, min(127, vel_va), 3))
        tracks_events[3].append((current_tick + dur_ticks - 15, 'off', note, 0, 3))
        specialist_styles.generate_cc_curve(tracks_events[3], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=int(66 + tension * 20), curve_type="sine", ch=3)
        current_tick += dur_ticks

    # ── Track 4: Cello (GM 42, Ch 4) ──
    tracks_events[4].append((0, 'program', 42, 0, 4))
    current_tick = 0
    for note, duration in cello:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_vc = int(62 + tension * 22)
        stagger = random.randint(-4, 4)
        on_t = max(0, current_tick + stagger)
        tracks_events[4].append((on_t, 'on', note, min(127, vel_vc), 4))
        tracks_events[4].append((current_tick + dur_ticks - 15, 'off', note, 0, 4))
        specialist_styles.generate_cc_curve(tracks_events[4], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=int(68 + tension * 22), curve_type="sine", ch=4)
        current_tick += dur_ticks

    # ── Track 5: Double Bass (GM 43, Ch 5) ──
    tracks_events[5].append((0, 'program', 43, 0, 5))
    current_tick = 0
    for note, duration in double_bass:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_bass = int(60 + tension * 20)
        stagger = random.randint(-3, 3)
        on_t = max(0, current_tick + stagger)
        tracks_events[5].append((on_t, 'on', note, min(127, vel_bass), 5))
        tracks_events[5].append((current_tick + dur_ticks - 10, 'off', note, 0, 5))
        specialist_styles.generate_cc_curve(tracks_events[5], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=vel_bass, curve_type="sine", ch=5)
        current_tick += dur_ticks

    # ── Track 6: Spiccato Ostinato - Short Strings (GM 49, Ch 6) ──
    tracks_events[6].append((0, 'program', 49, 0, 6))
    for ev in ost_events:
        tick, etype, note, velocity, old_ch = ev
        tracks_events[6].append((tick, etype, note, velocity, 6))
    specialist_styles.generate_cc_curve(tracks_events[6], 11, 0, num_bars * 4 * tpb,
                                         start_val=int(50 + tension * 30), end_val=int(70 + tension * 30), curve_type="sine", ch=6)

    # ── Track 7: Piano Melody (GM 0, Ch 7) ──
    tracks_events[7].append((0, 'program', 0, 0, 7))
    current_tick = 0
    for note, duration in piano:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_piano = int(50 + tension * 30)
        if duration <= 0.5:
            vel_piano = max(38, vel_piano - 8)
        tracks_events[7].append((current_tick, 'on', note, min(112, vel_piano), 7))
        tracks_events[7].append((current_tick + max(1, dur_ticks - 20), 'off', note, 0, 7))
        current_tick += dur_ticks

    # Build MIDI file
    mid = specialist_styles.build_midi_from_events(tracks_events, tpb)
    _apply_vvc_track_names(mid)
    return mid


# ── USER INTERFACE ─────────────────────────────────────────────────────────

def _div(char='-', w=62):
    print(char * w)


def select_scale_type():
    """Prompt user to choose between major and minor scales."""
    print("\n  Select Scale Type:\n")
    print("    1  ->  Minor (Aeolian, Harmonic Minor, Dorian, Phrygian)")
    print("    2  ->  Major (Ionian, Lydian, Mixolydian)")
    _div()
    choice = input("  --> ").strip()
    while choice not in ['1', '2']:
        print("  [!] Enter 1 or 2.")
        choice = input("  --> ").strip()
    return choice


def select_mood(is_minor):
    """Prompt user to select a mood and return (mood_name, tension, progression, label)."""
    moods = MOODS_MINOR if is_minor else MOODS_MAJOR
    scale_type = "Minor" if is_minor else "Major"

    print(f"\n  Select Mood ({scale_type}):\n")
    for key, mood in moods.items():
        attrs = f" | {mood['attributes']}" if 'attributes' in mood else ""
        print(f"    {key}  ->  {mood['name']}  (tension: {int(mood['tension']*100)}%){attrs}")
    print("    R  ->  Random")
    _div()
    choice = input("  --> ").strip().lower()

    if choice == 'r':
        key = random.choice(list(moods.keys()))
    elif choice in moods:
        key = choice
    else:
        print(f"  [!] Invalid. Choosing random.")
        key = random.choice(list(moods.keys()))

    mood_data = moods[key]
    entry = random.choice(mood_data['progressions'])
    return mood_data['name'], mood_data['tension'], entry['chords'], entry['label']


def select_tempo():
    """Prompt user for tempo between 100-150 BPM."""
    print("\n  Select Tempo (100 - 150 BPM):\n")
    print("    1  ->  Flowing      (100 – 110 BPM)")
    print("    2  ->  Moderate     (111 – 125 BPM)")
    print("    3  ->  Driving      (126 – 140 BPM)")
    print("    4  ->  Energetic    (141 – 150 BPM)")
    print("    C  ->  Custom BPM")
    _div()
    choice = input("  --> ").strip().lower()

    clusters = {
        '1': (100, 110),
        '2': (111, 125),
        '3': (126, 140),
        '4': (141, 150),
    }

    if choice in clusters:
        lo, hi = clusters[choice]
        return random.randint(lo, hi)
    elif choice == 'c':
        try:
            bpm = int(input("  Enter BPM (100-150): ").strip())
            return max(100, min(150, bpm))
        except ValueError:
            print("  [!] Invalid. Using 120 BPM.")
            return 120
    else:
        print("  [!] Invalid. Using 120 BPM.")
        return 120


def select_key(is_minor):
    """Select a random key automatically."""
    return random.choice(list(ROOTS.items()))


# ── MIDI FILE ANALYSIS ─────────────────────────────────────────────────────

def detect_chord_root(midi_notes):
    """
    Given a list of MIDI notes played simultaneously, returns a list of pitch classes 
    ordered as [root, third, fifth, ...].
    Uses interval analysis (perfect fifths, thirds) to reliably detect the root 
    even for inverted chords.
    """
    pcs = sorted(list(set(n % 12 for n in midi_notes)))
    if not pcs:
        return []
    if len(pcs) == 1:
        return pcs
    
    best_root = None
    best_score = -1
    
    for pc in pcs:
        score = 0
        has_fifth = (pc + 7) % 12 in pcs
        has_maj3 = (pc + 4) % 12 in pcs
        has_min3 = (pc + 3) % 12 in pcs
        
        if has_fifth:
            score += 3
        if has_maj3 or has_min3:
            score += 2
            
        if score > best_score:
            best_score = score
            best_root = pc
            
    if best_score == 0:
        best_root = min(midi_notes) % 12
        
    ordered_pcs = [best_root]
    
    # Prioritize third and fifth next
    for pc in pcs:
        if pc != best_root and pc not in ordered_pcs:
            if (pc - best_root) % 12 in (3, 4, 7):
                ordered_pcs.append(pc)
    
    # Add remaining
    for pc in pcs:
        if pc not in ordered_pcs:
            ordered_pcs.append(pc)
            
    return ordered_pcs


def parse_midi_chords(filepath):
    """Extract simultaneous note groups (chords) from a MIDI file, ignoring choir channels."""
    mid = mido.MidiFile(filepath)
    tpb = mid.ticks_per_beat
    note_ons = []
    for track in mid.tracks:
        track_name = (getattr(track, 'name', '') or '').lower()
        if any(w in track_name for w in ['choir', 'soprano', 'alto', 'tenor', 'bass']):
            continue
        t = 0
        for msg in track:
            t += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                if getattr(msg, 'channel', 0) in (7, 8, 9, 10):
                    continue
                note_ons.append((t, msg.note))
    note_ons.sort()
    if not note_ons:
        return [], tpb
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
        pcs = detect_chord_root(grp)
        if len(pcs) >= 2:
            groups.append(pcs)
        i = j
    collapsed = []
    prev = None
    for g in groups:
        t = tuple(g)
        if t != prev:
            collapsed.append(g)
            prev = t
    return collapsed, tpb


def parse_midi_chord_timeline(filepath):
    """Extract ordered chord groups from a MIDI file without collapsing repeats, ignoring choir channels."""
    mid = mido.MidiFile(filepath)
    tpb = mid.ticks_per_beat
    note_ons = []
    for track in mid.tracks:
        track_name = (getattr(track, 'name', '') or '').lower()
        if any(w in track_name for w in ['choir', 'soprano', 'alto', 'tenor', 'bass']):
            continue
        t = 0
        for msg in track:
            t += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                if getattr(msg, 'channel', 0) in (7, 8, 9, 10):
                    continue
                note_ons.append((t, msg.note))
    note_ons.sort()
    if not note_ons:
        return [], tpb

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
        pcs = detect_chord_root(grp)
        if len(pcs) >= 2:
            if not groups or groups[-1][0] != t0 or groups[-1][1] != pcs:
                groups.append((t0, pcs))
        i = j
    return groups, tpb


def detect_tempo(filepath):
    """Detect BPM from MIDI file by finding set_tempo meta events."""
    try:
        mid = mido.MidiFile(filepath)
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    return int(round(mido.tempo2bpm(msg.tempo)))
    except Exception:
        pass
    return 120  # Default fallback


def detect_key(chord_groups):
    """Krumhansl-Schmuckler key detection — try both major and minor profiles.
    Returns (root_name, root_pc, scale, scale_name, is_minor).
    """
    pc_counts = [0] * 12
    for pcs in chord_groups:
        for pc in pcs:
            pc_counts[pc % 12] += 1

    # Test all 12 major key candidates
    best_major_score, best_major_root = -1e9, 0
    for root in range(12):
        profile = [KS_MAJOR[(i - root) % 12] for i in range(12)]
        score = sum(pc_counts[i] * profile[i] for i in range(12))
        if score > best_major_score:
            best_major_score, best_major_root = score, root

    # Test all 12 minor key candidates
    best_minor_score, best_minor_root = -1e9, 0
    for root in range(12):
        profile = [KS_MINOR[(i - root) % 12] for i in range(12)]
        score = sum(pc_counts[i] * profile[i] for i in range(12))
        if score > best_minor_score:
            best_minor_score, best_minor_root = score, root

    # Determine which profile fits best
    if best_major_score >= best_minor_score:
        root_pc = best_major_root
        root_name = ROOT_NAMES[root_pc]
        # Check for Lydian (sharp 4) vs Mixolydian (flat 7) vs Ionian
        sharp4 = (root_pc + 6) % 12
        flat7  = (root_pc + 10) % 12
        nat4   = (root_pc + 5) % 12
        maj7   = (root_pc + 11) % 12
        if pc_counts[sharp4] > pc_counts[nat4]:
            return root_name, root_pc, SCALE_LYDIAN, 'Lydian', False
        elif pc_counts[flat7] > pc_counts[maj7]:
            return root_name, root_pc, SCALE_MIXOLYDIAN, 'Mixolydian', False
        return root_name, root_pc, SCALE_IONIAN, 'Natural Major', False
    else:
        root_pc = best_minor_root
        root_name = ROOT_NAMES[root_pc]
        # Check Harmonic Minor (raised 7th) vs Phrygian (flat 2)
        raised7 = (root_pc + 11) % 12
        nat7    = (root_pc + 10) % 12
        if pc_counts[raised7] > pc_counts[nat7]:
            return root_name, root_pc, SCALE_HARMONIC, 'Harmonic Minor', True
        flat2 = (root_pc + 1) % 12
        if pc_counts[flat2] >= 2:
            return root_name, root_pc, SCALE_PHRYGIAN, 'Phrygian', True
        return root_name, root_pc, SCALE_AEOLIAN, 'Natural Minor', True


def get_active_pitch_at_beat(melody, beat_pos):
    """
    Finds the active pitch in a list of (pitch, duration) tuples at a given beat_pos.
    Robust against floating-point precision issues.
    """
    if not melody:
        return None
    cum = 0.0
    for pitch, dur in melody:
        if cum - 0.005 <= beat_pos < cum + dur - 0.005:
            return pitch
        cum += dur
    return melody[-1][0]


def get_chord_tone_role(pc, ct):
    """
    Classifies a pitch class (pc) relative to the chord tones (ct).
    Assumes ct[0] is the chord root.
    """
    if not ct:
        return 'other'
    root_pc = ct[0]
    diff = (pc - root_pc) % 12
    if diff == 0:
        return 'root'
    elif diff in (3, 4):
        return 'third'
    elif diff == 7:
        return 'fifth'
    return 'other'


def score_voicing_candidate(pitch, ct, active_pitches, prev_pitch, register, role_name, root_note):
    """
    Heuristically scores a candidate pitch for a string section voice.
    Incorporates chord-tone priorities, doubling rules, spacing, voice crossing,
    and voice-leading tendency resolution.
    """
    score = 100.0
    
    # 1. Register boundaries check
    if pitch < register['min'] or pitch > register['max']:
        return -9999.0
        
    # 2. Voice crossing check (Rule 31)
    # Order: bass < cello < viola < violin2 < violin1
    order = ['bass', 'cello', 'viola', 'violin2', 'violin1']
    my_idx = order.index(role_name)
    
    for other_role, other_pitch in active_pitches.items():
        if other_pitch is None:
            continue
        other_idx = order.index(other_role)
        if other_idx < my_idx and pitch <= other_pitch:
            return -9999.0  # Cannot cross lower voice
        if other_idx > my_idx and pitch >= other_pitch:
            return -9999.0  # Cannot cross upper voice
            
    # 3. Spacing check (Rule 33-37)
    for other_role, other_pitch in active_pitches.items():
        if other_pitch is None:
            continue
        other_idx = order.index(other_role)
        dist = abs(pitch - other_pitch)
        
        # Upper neighbor
        if other_idx == my_idx + 1:
            if dist > 14:  # excessive separation (Rule 36)
                score -= (dist - 14) * 5.0
            if dist < 3:   # too close / unison (Rule 33)
                score -= (3 - dist) * 10.0
                
        # Lower neighbor
        if other_idx == my_idx - 1:
            if role_name in ('violin1', 'violin2', 'viola'):
                if dist > 14:
                    score -= (dist - 14) * 5.0
                if dist < 3:
                    score -= (3 - dist) * 10.0
            elif role_name == 'cello':
                # Cello to bass spacing: keep sufficiently separated to prevent mud (Rule 37)
                if dist < 8:
                    score -= (8 - dist) * 15.0
                if dist > 20:
                    score -= (dist - 20) * 3.0
                    
    # 4. Proximity / Leap Penalty (Rule 28, 29)
    if prev_pitch is not None:
        leap = abs(pitch - prev_pitch)
        if leap == 0:
            score += 2.0  # Oblique motion / static holds are good for inner voices
        elif leap <= 2:
            score += 8.0  # Stepwise motion is highly preferred! (Rule 28)
        elif leap <= 4:
            score -= leap * 1.5  # Small leaps are fine
        else:
            score -= leap * 4.0  # Large leaps are penalized (Rule 29)
            
    # 5. Chord Tone Allocation & Doubling (Rules 5-9)
    pc = (pitch - root_note) % 12
    if pc in ct:
        score += 15.0  # Chord tones are structural
        
        role = get_chord_tone_role(pc, ct)
        
        other_roles = []
        for other_role, other_pitch in active_pitches.items():
            if other_pitch is not None:
                other_pc = (other_pitch - root_note) % 12
                other_roles.append(get_chord_tone_role(other_pc, ct))
                
        third_count = other_roles.count('third')
        root_count = other_roles.count('root')
        fifth_count = other_roles.count('fifth')
        
        if role == 'third':
            if third_count == 0:
                score += 25.0  # Third must be present (Rule 8)
            else:
                score -= 15.0  # Avoid excessive doubling of the third (Rule 5, 8)
        elif role == 'root':
            if root_count == 0:
                score += 15.0
            elif root_count == 1:
                score += 10.0  # Prefer doubling root first (Rule 6)
            else:
                score -= 5.0
        elif role == 'fifth':
            if fifth_count == 0:
                score += 12.0
            elif root_count >= 1 and fifth_count == 1:
                score += 8.0   # Prioritize fifth doubling (Rule 7)
            else:
                score -= 5.0
    else:
        # Non-chord tone
        score -= 20.0
        
    # 6. Tendency tone resolution (Rule 30)
    if prev_pitch is not None:
        prev_pc_key = (prev_pitch - root_note) % 12
        # Leading tone (11) resolves up to tonic (0)
        if prev_pc_key == 11:
            if (pitch - root_note) % 12 == 0 and pitch > prev_pitch:
                score += 20.0
            else:
                score -= 10.0
        # Flat 6th (8) resolves down to 5th (7)
        elif prev_pc_key == 8:
            if (pitch - root_note) % 12 == 7 and pitch < prev_pitch:
                score += 20.0
            else:
                score -= 10.0
        # 4th degree (5) resolves down to 3rd (3 or 4)
        elif prev_pc_key == 5:
            if (pitch - root_note) % 12 in (3, 4) and pitch < prev_pitch:
                score += 15.0
                
    return score


def _generate_double_bass_expressive(root_note, bars_data, tension=0.5):
    """
    Generates the Double Bass line (Ch 5/Track 5).
    Plays the root note of each chord as a sustained whole-chord note.
    """
    double_bass = []
    prev_pitch = None
    DB_REG = {'min': 28, 'max': 48, 'center': 38}

    for bar_harmony in bars_data:
        if isinstance(bar_harmony, list):
            # Decoupled: one sustained note per chord segment
            for ct, sc, dur in bar_harmony:
                root_pc = ct[0]
                pitch = _pitch_in_register(root_note, root_pc, DB_REG, preferred=prev_pitch)
                double_bass.append((pitch, dur))
                prev_pitch = pitch
        else:
            # Simple: one sustained note for the full bar
            ct, sc = bar_harmony
            root_pc = ct[0]
            pitch = _pitch_in_register(root_note, root_pc, DB_REG, preferred=prev_pitch)
            double_bass.append((pitch, 4.0))
            prev_pitch = pitch

    return double_bass


def _generate_cello_expressive(root_note, bars_data, tension=0.5, double_bass_melody=None):
    """
    Generates the Cello line (Ch 4/Track 4).
    Independently follows the chord progression — plays the root note of each
    chord sustained for its full duration, in the cello register (one octave
    above the bass).
    """
    cello = []
    prev_pitch = None
    CELLO_REG = {'min': 40, 'max': 57, 'center': 48}

    for bar_harmony in bars_data:
        if isinstance(bar_harmony, list):
            # Decoupled: one sustained note per chord segment
            for ct, sc, dur in bar_harmony:
                root_pc = ct[0]
                pitch = _pitch_in_register(root_note, root_pc, CELLO_REG, preferred=prev_pitch)
                cello.append((pitch, dur))
                prev_pitch = pitch
        else:
            # Simple: one sustained note for the full bar
            ct, sc = bar_harmony
            root_pc = ct[0]
            pitch = _pitch_in_register(root_note, root_pc, CELLO_REG, preferred=prev_pitch)
            cello.append((pitch, 4.0))
            prev_pitch = pitch

    return cello


def _generate_violin1_expressive(root_note, bars_data, tension=0.5, active_bars=None):
    """
    Generates a unique, catchy, and highly expressive Violin I melody line (Ch 1/Track 1).
    Uses a Call-and-Response architecture with randomly decided active/passive bars.
    In active bars it plays melodic motifs; in passive bars it sustains chord tones.
    active_bars: optional pre-computed list of bool per bar (shared with Violin II).
    """
    melody = []
    prev_pitch = None
    prev_was_nct = False
    prev_dir = 0

    num_bars = len(bars_data)

    # Use provided active_bars or generate randomly (~60% alternation)
    if active_bars is None:
        active_bars = []
    if len(active_bars) < num_bars:
        active_bars = []
        for bar_idx in range(num_bars):
            if bar_idx == 0:
                active_bars.append(random.choice([True, False]))
            else:
                if random.random() < 0.6:
                    active_bars.append(not active_bars[-1])
                else:
                    active_bars.append(active_bars[-1])

    rhythm_motifs = [
        [1.5, 0.5, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 0.5, 0.5, 1.0],
        [1.5, 0.5, 1.5, 0.5],
        [2.0, 1.0, 1.0],
        [1.0, 2.0, 1.0],
        [0.5, 0.5, 1.0, 0.5, 0.5, 1.0],
        [0.5, 0.5, 0.5, 0.5, 1.0, 1.0],
    ]
    motif_rhythm = random.choice(rhythm_motifs)

    contour = []
    for bar_idx in range(num_bars):
        pct = bar_idx / max(1, num_bars - 1)
        if pct < 0.25:
            center = 76
        elif pct < 0.5:
            center = 80
        elif pct < 0.75:
            center = 84
        else:
            center = 76
        contour.append(center)

    first_active_notes = []

    for bar_idx, bar_harmony in enumerate(bars_data):
        target_center = contour[bar_idx]
        is_active = active_bars[bar_idx]
        violin1_reg = {'min': 72, 'max': 93, 'center': target_center}

        if not is_active:
            # PASSIVE: hold a single chord tone for the full bar
            if isinstance(bar_harmony, list):
                beat_pos = 0.0
                for ct, sc, dur in bar_harmony:
                    pitch_pc = ct[0]
                    pitch = _pitch_in_register(root_note, pitch_pc, violin1_reg, preferred=prev_pitch)
                    melody.append((pitch, dur))
                    prev_pitch = pitch
                    beat_pos += dur
            else:
                ct, sc = bar_harmony
                pitch_pc = ct[0]
                pitch = _pitch_in_register(root_note, pitch_pc, violin1_reg, preferred=prev_pitch)
                melody.append((pitch, 4.0))
                prev_pitch = pitch
            continue

        # ACTIVE: play melodic motif
        is_first_active = (bar_idx == 0) or (not active_bars[bar_idx - 1])
        bar_rhythm = motif_rhythm if is_first_active else random.choice(rhythm_motifs)

        beat_pos = 0.0
        for dur in bar_rhythm:
            ct, sc = get_bar_harmony_at_beat(bar_harmony, beat_pos)
            strong = (beat_pos % 2.0 < 0.01) or (beat_pos % 1.0 < 0.01)
            ct_pcs = [c % 12 for c in ct]
            sc_pcs = [s % 12 for s in sc]

            candidates = []
            for p in range(violin1_reg['min'], violin1_reg['max'] + 1):
                if (p - root_note) % 12 in sc_pcs:
                    candidates.append(p)
            if not candidates:
                candidates = [76, 79, 81, 84]

            # Diatonic sequencing from first active phrase
            sequenced_pitch = None
            if not is_first_active and first_active_notes:
                note_idx = min(len(first_active_notes) - 1, int(beat_pos))
                b1_pitch, _ = first_active_notes[note_idx]
                prev_active_bar = bar_idx - 1
                while prev_active_bar > 0 and not active_bars[prev_active_bar]:
                    prev_active_bar -= 1
                b1_harmony = bars_data[prev_active_bar]
                ct1, _ = get_bar_harmony_at_beat(b1_harmony, beat_pos)
                shift = (ct[0] - ct1[0]) % 12
                target_p = b1_pitch + shift
                while target_p < violin1_reg['min']:
                    target_p += 12
                while target_p > violin1_reg['max']:
                    target_p -= 12
                sequenced_pitch = target_p

            scores = []
            for p in candidates:
                score = 0.0
                pc = (p - root_note) % 12
                score -= abs(p - target_center) * 1.5
                is_chord_tone = pc in ct_pcs
                if is_chord_tone:
                    score += 20.0 if strong else 10.0
                    if len(ct) > 1 and pc == ct[1 % len(ct)]:
                        score -= 5.0
                else:
                    score += -15.0 if strong else 2.0
                if prev_pitch is not None:
                    step = abs(p - prev_pitch)
                    if step == 0:
                        score -= 8.0
                    elif step in (1, 2):
                        score += 15.0
                    elif step in (3, 4, 5):
                        score += 5.0
                    elif step in (7, 12):
                        score += 8.0
                    else:
                        score -= (step - 5) * 4.0
                    if prev_was_nct:
                        score += 35.0 if (is_chord_tone and step in (1, 2)) else -20.0
                    my_dir = 1 if p > prev_pitch else (-1 if p < prev_pitch else 0)
                    if my_dir == prev_dir and my_dir != 0:
                        score += 4.0
                        
                    # 6. Resolve leaps
                    prev_step = abs(prev_pitch - (melody[-2][0] if len(melody) >= 2 else prev_pitch))
                    if prev_step >= 5:
                        prev_dir_actual = 1 if prev_pitch > (melody[-2][0] if len(melody) >= 2 else prev_pitch) else -1
                        if my_dir == -prev_dir_actual and step in (1, 2):
                            score += 25.0
                
                # 7. Sequenced pitch bonus
                if sequenced_pitch is not None and p == sequenced_pitch:
                    score += 40.0
                    
                scores.append(score)
                
            temp = 0.45 + (tension * 0.15)
            pitch = sample_from_scores(candidates, scores, temperature=temp)
            
            prev_was_nct = ((pitch - root_note) % 12) not in ct_pcs
            if prev_pitch is not None:
                prev_dir = 1 if pitch > prev_pitch else (-1 if pitch < prev_pitch else 0)
                
            melody.append((pitch, dur))
            if is_first_active:
                first_active_notes.append((pitch, dur))
                
            prev_pitch = pitch
            beat_pos += dur
            
    return melody


def _generate_violin2_expressive(root_note, bars_data, tension=0.5, violin1_melody=None, violin1_active_bars=None):
    """
    Generates a complementary Violin II line (Ch 2/Track 2).
    Call-and-Response: active when Violin I is passive, sustains when Violin I is active.
    """
    melody = []
    prev_pitch = None
    v2_reg = {'min': 60, 'max': 71, 'center': 64}

    rhythm_motifs = [
        [1.5, 0.5, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 0.5, 0.5, 1.0],
        [1.5, 0.5, 1.5, 0.5],
        [2.0, 1.0, 1.0],
        [1.0, 2.0, 1.0],
        [0.5, 0.5, 1.0, 0.5, 0.5, 1.0],
    ]
    motif_rhythm = random.choice(rhythm_motifs)

    num_bars = len(bars_data)
    # Violin II is active exactly when Violin I is passive, and vice versa
    if violin1_active_bars is not None:
        v2_active_bars = [not b for b in violin1_active_bars]
    else:
        # fallback: alternate
        v2_active_bars = [(bar_idx % 2 == 1) for bar_idx in range(num_bars)]

    for bar_idx, bar_harmony in enumerate(bars_data):
        is_active = v2_active_bars[bar_idx]
        v1_pitch_bar = get_active_pitch_at_beat(violin1_melody, bar_idx * 4.0)

        if not is_active:
            # PASSIVE: hold a chord tone below Violin I
            ct, sc = get_bar_harmony_at_beat(bar_harmony, 0.0)
            ct_pcs = [c % 12 for c in ct]
            if isinstance(bar_harmony, list):
                beat_pos = 0.0
                for ct_sub, sc_sub, dur in bar_harmony:
                    ct_pcs_sub = [c % 12 for c in ct_sub]
                    candidates = [p for p in range(v2_reg['min'], v2_reg['max'] + 1)
                                  if (p - root_note) % 12 in ct_pcs_sub
                                  and (v1_pitch_bar is None or p < v1_pitch_bar)]
                    pitch = (max(candidates) if candidates
                             else _pitch_in_register(root_note, ct_sub[0], v2_reg))
                    melody.append((pitch, dur))
                    prev_pitch = pitch
                    beat_pos += dur
            else:
                candidates = [p for p in range(v2_reg['min'], v2_reg['max'] + 1)
                              if (p - root_note) % 12 in ct_pcs
                              and (v1_pitch_bar is None or p < v1_pitch_bar)]
                pitch = (max(candidates) if candidates
                         else _pitch_in_register(root_note, ct[0], v2_reg))
                melody.append((pitch, 4.0))
                prev_pitch = pitch
            continue

        # ACTIVE: play counter-melody motif
        is_first_active = (bar_idx == 0) or (not v2_active_bars[bar_idx - 1])
        bar_rhythm = motif_rhythm if is_first_active else random.choice(rhythm_motifs)
        beat_pos = 0.0
        for dur in bar_rhythm:
            ct, sc = get_bar_harmony_at_beat(bar_harmony, beat_pos)
            v1_pitch = get_active_pitch_at_beat(violin1_melody, bar_idx * 4.0 + beat_pos)
            ct_pcs = [c % 12 for c in ct]
            sc_pcs = [s % 12 for s in sc]

            candidates = [p for p in range(v2_reg['min'], v2_reg['max'] + 1)
                          if (p - root_note) % 12 in sc_pcs
                          and (v1_pitch is None or p < v1_pitch)]
            if not candidates:
                candidates = [60, 62, 64, 67]

            scores = []
            for p in candidates:
                score = score_voicing_candidate(p, ct_pcs, {'violin1': v1_pitch},
                                                prev_pitch, v2_reg, 'violin2', root_note)
                if v1_pitch is not None and (p - root_note) % 12 in ct_pcs:
                    dist = v1_pitch - p
                    if dist > 0:
                        score += (12 - dist) * 1.5
                if prev_pitch is not None and v1_pitch is not None:
                    prev_v1 = get_active_pitch_at_beat(violin1_melody, bar_idx * 4.0 + beat_pos - 0.5)
                    if prev_v1 is not None and prev_v1 != v1_pitch:
                        if (v1_pitch - prev_v1) * (p - prev_pitch) > 0:
                            score -= 8.0
                scores.append(score)

            pitch = sample_from_scores(candidates, scores, temperature=0.25)
            melody.append((pitch, dur))
            prev_pitch = pitch
            beat_pos += dur

    return melody


def _generate_viola_expressive(root_note, bars_data, tension=0.5,
                               violin1_melody=None, violin2_melody=None,
                               cello_melody=None, double_bass_melody=None):
    """
    Generates the Viola line (Ch 3/Track 3).
    The ONLY always-dynamic channel — plays rhythmic figures every bar,
    dynamically harmonizing all other voices by filling missing chord tones.
    """
    melody = []
    prev_pitch = None
    viola_reg = {'min': 48, 'max': 59, 'center': 52}

    # Always active rhythmic pools by tension
    if tension < 0.4:
        rhythm_pool = [[2.0, 2.0], [1.5, 1.5, 1.0], [1.0, 1.0, 2.0]]
    elif tension < 0.65:
        rhythm_pool = [[1.0, 1.0, 1.0, 1.0], [1.5, 1.5, 1.0], [1.0, 2.0, 1.0], [2.0, 2.0]]
    else:
        rhythm_pool = [[1.0, 1.0, 1.0, 1.0], [1.5, 0.5, 1.5, 0.5],
                       [1.0, 2.0, 1.0], [0.5, 0.5, 1.0, 0.5, 0.5, 1.0]]

    for bar_idx, bar_harmony in enumerate(bars_data):
        # Viola is ALWAYS active — never sustains
        bar_rhythm = random.choice(rhythm_pool)
        beat_pos = 0.0
        for dur in bar_rhythm:
            ct, sc = get_bar_harmony_at_beat(bar_harmony, beat_pos)
            abs_beat = bar_idx * 4.0 + beat_pos

            v1_pitch  = get_active_pitch_at_beat(violin1_melody,      abs_beat)
            v2_pitch  = get_active_pitch_at_beat(violin2_melody,      abs_beat)
            cel_pitch = get_active_pitch_at_beat(cello_melody,        abs_beat)
            db_pitch  = get_active_pitch_at_beat(double_bass_melody,  abs_beat)

            ct_pcs = [c % 12 for c in ct]
            sc_pcs = [s % 12 for s in sc]

            # Find pitch classes already covered by other voices
            voiced_pcs = set()
            for ref in (v1_pitch, v2_pitch, cel_pitch, db_pitch):
                if ref is not None:
                    voiced_pcs.add((ref - root_note) % 12)
            missing_ct = [c for c in ct_pcs if c not in voiced_pcs]

            candidates = [p for p in range(viola_reg['min'], viola_reg['max'] + 1)
                          if (p - root_note) % 12 in sc_pcs
                          and (cel_pitch is None or p > cel_pitch)
                          and (v2_pitch  is None or p < v2_pitch)]
            if not candidates:
                candidates = [p for p in range(viola_reg['min'] - 3, viola_reg['max'] + 4)
                              if (cel_pitch is None or p > cel_pitch)
                              and (v2_pitch  is None or p < v2_pitch)]
            if not candidates:
                candidates = [50, 52, 55, 57]

            scores = []
            for p in candidates:
                pc = (p - root_note) % 12
                score = score_voicing_candidate(
                    p, ct_pcs,
                    {'violin1': v1_pitch, 'violin2': v2_pitch, 'cello': cel_pitch},
                    prev_pitch, viola_reg, 'viola', root_note)

                # Priority: fill missing chord tones
                if pc in missing_ct:
                    score += 30.0
                elif pc in ct_pcs:
                    score += 10.0

                # Suspension bonus at bar boundary
                if beat_pos == 0.0 and prev_pitch is not None and p == prev_pitch:
                    score += 12.0

                scores.append(score)

            pitch = sample_from_scores(candidates, scores, temperature=0.2)
            melody.append((pitch, dur))
            prev_pitch = pitch
            beat_pos += dur

    return melody


def generate_quartet_over_midi(filepath, out_dir):
    """
    Upgraded VVC Option 5 Overlayer.
    Loads an existing MIDI file, extracts chords/key/tempo, and generates
    8-track orchestrations following chord-tone allocation, registers,
    stepwise voice leading, and dynamic texture.
    Preserves all original tracks/channels from the source MIDI.

    NOTE: This function is intentionally isolated from the global
    GENERATION_MODE toggle (Toggle T in the main menu). It always uses
    the chord-tone-centric expressive generators regardless of whether
    'Simple' or 'Decoupled' mode is active — the toggle only affects
    the VVC String Quartet composer (Option 3).
    """
    # Guard: pin local mode — never inherit global GENERATION_MODE toggle
    _overlay_mode = 'expressive'  # noqa: F841 — intentional isolation sentinel

    print(f"\n  Analyzing: {os.path.basename(filepath)} ...")
    try:
        chord_groups, src_tpb = parse_midi_chords(filepath)
    except Exception as e:
        print(f"  [ERROR] Could not read file: {e}")
        return

    if not chord_groups:
        print("  [ERROR] No clear chord progression detected in MIDI. Exiting.")
        return

    # Detect key and tempo
    root_name, root_pc, scale, scale_name, is_minor = detect_key(chord_groups)
    root_midi = ROOTS.get(root_name, 45)
    bpm = detect_tempo(filepath)

    print(f"  [DETECTED] Key   : {root_name} {scale_name}")
    print(f"  [DETECTED] Tempo : {bpm} BPM")
    print(f"  [DETECTED] Chords: {len(chord_groups)} bars detected.")

    # Build bars_data
    bars_data = []
    for pcs in chord_groups:
        ct = [(pc - root_pc) % 12 for pc in pcs]
        sc = [t % 12 for t in scale]
        bars_data.append((ct, sc))

    # Setup harmonic foundation for Pad and Ostinato
    chords_for_ostinato = []
    prev_voicing = []
    for bar_idx in range(len(chord_groups)):
        pcs = chord_groups[bar_idx]
        root_pc_bar = pcs[0]
        third_pc = pcs[1 % len(pcs)]
        fifth_pc = pcs[2 % len(pcs)] if len(pcs) > 2 else pcs[1 % len(pcs)]
        target_pcs = [root_pc_bar, third_pc, fifth_pc]
        
        if bar_idx == 0 or not prev_voicing:
            voicing = sorted(list(set([
                48 + root_pc_bar, 48 + third_pc, 48 + fifth_pc,
                60 + root_pc_bar, 60 + third_pc, 60 + fifth_pc
            ])))
        else:
            voicing = voice_lead_chord(prev_voicing, target_pcs, register_min=48, register_max=72)
        prev_voicing = voicing
        chords_for_ostinato.append(voicing)

    # Set tension based on scale type/mood properties
    tension = 0.65 if is_minor else 0.50

    # 1. Generate Voice Parts using new expressive algorithms
    # Compute shared active_bars for call-and-response between Violin I and Violin II
    _num_bars = len(bars_data)
    _v1_active = []
    for _bi in range(_num_bars):
        if _bi == 0:
            _v1_active.append(random.choice([True, False]))
        else:
            _v1_active.append(not _v1_active[-1] if random.random() < 0.6 else _v1_active[-1])

    violin1     = _generate_violin1_expressive(root_midi, bars_data, tension, active_bars=_v1_active)
    violin2     = _generate_violin2_expressive(root_midi, bars_data, tension,
                                               violin1_melody=violin1, violin1_active_bars=_v1_active)
    double_bass = _generate_double_bass_expressive(root_midi, bars_data, tension)
    cello_notes = _generate_cello_expressive(root_midi, bars_data, tension, double_bass_melody=double_bass)
    viola_notes  = _generate_viola_expressive(root_midi, bars_data, tension,
                                              violin1_melody=violin1, violin2_melody=violin2,
                                              cello_melody=cello_notes, double_bass_melody=double_bass)

    # 2. Generate Ostinato and Piano
    # Use the cinematic engine's professional short-string spiccato/staccato ostinato
    # (cell-based, BPM-aware density, phrase arcs, role-driven chord-tone assignment).
    try:
        import cinematic as _cinematic_mod
        ost_events = _cinematic_mod.generate_staccato_ostinato(bars_data, root_midi, bpm, tpb=src_tpb)
        _ost_is_cinematic = True
    except Exception:
        ost_events, _ = generate_ostinato(chords_for_ostinato, bpm, tension)
        _ost_is_cinematic = False
    piano_notes = generate_piano_melody(root_midi, bars_data, tension)

    # Build 8 VVC tracks (Ch 0 to Ch 7)
    tpb = src_tpb  # Align exactly to source MIDI's ticks_per_beat
    tracks_events = [[] for _ in range(8)]

    # ── Track 0: String Pad (GM 48 String Ensemble 1, Ch 0) ──
    tracks_events[0].append((0, 'program', 48, 0, 0))
    tracks_events[0].append((0, 'tempo', bpm, 0, 0))
    for bar_idx in range(len(chord_groups)):
        voicing = chords_for_ostinato[bar_idx]
        bar_start_tick = bar_idx * 4 * tpb
        bar_dur = 4 * tpb
        vel_pad = int(48 + tension * 20)
        for note in voicing:
            tracks_events[0].append((bar_start_tick, 'on', note, vel_pad, 0))
            tracks_events[0].append((bar_start_tick + bar_dur - 15, 'off', note, 0, 0))
        specialist_styles.generate_cc_curve(tracks_events[0], 1, bar_start_tick, bar_dur,
                                             start_val=50, end_val=int(60 + tension * 25), curve_type="sine", ch=0)
        specialist_styles.generate_cc_curve(tracks_events[0], 11, bar_start_tick, bar_dur,
                                             start_val=45, end_val=int(55 + tension * 30), curve_type="linear", ch=0)

    # ── Track 1: Violin I (GM 40 Violin, Ch 1) ──
    tracks_events[1].append((0, 'program', 40, 0, 1))
    current_tick = 0
    for note, duration in violin1:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_v1 = int(68 + tension * 25)
        stagger = random.randint(-4, 4)
        on_t = max(0, current_tick + stagger)
        tracks_events[1].append((on_t, 'on', note, min(127, vel_v1), 1))
        tracks_events[1].append((current_tick + dur_ticks - 15, 'off', note, 0, 1))
        
        # CC 1 & CC 11 curves for human expression
        c_type = "crescendo" if duration >= 2.0 and random.random() < 0.5 else "sine"
        specialist_styles.generate_cc_curve(tracks_events[1], 1, current_tick, dur_ticks,
                                             start_val=55, end_val=int(75 + tension * 20), curve_type=c_type, ch=1)
        specialist_styles.generate_cc_curve(tracks_events[1], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=int(70 + tension * 25), curve_type="sine", ch=1)
        current_tick += dur_ticks

    # ── Track 2: Violin II (GM 40 Violin, Ch 2) ──
    tracks_events[2].append((0, 'program', 40, 0, 2))
    current_tick = 0
    for note, duration in violin2:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_v2 = int(62 + tension * 22)
        stagger = random.randint(-4, 4)
        on_t = max(0, current_tick + stagger)
        tracks_events[2].append((on_t, 'on', note, min(127, vel_v2), 2))
        tracks_events[2].append((current_tick + dur_ticks - 15, 'off', note, 0, 2))
        specialist_styles.generate_cc_curve(tracks_events[2], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=int(68 + tension * 20), curve_type="sine", ch=2)
        current_tick += dur_ticks

    # ── Track 3: Viola (GM 41 Viola, Ch 3) ──
    tracks_events[3].append((0, 'program', 41, 0, 3))
    current_tick = 0
    for note, duration in viola_notes:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_va = int(60 + tension * 20)
        stagger = random.randint(-4, 4)
        on_t = max(0, current_tick + stagger)
        tracks_events[3].append((on_t, 'on', note, min(127, vel_va), 3))
        tracks_events[3].append((current_tick + dur_ticks - 15, 'off', note, 0, 3))
        specialist_styles.generate_cc_curve(tracks_events[3], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=int(66 + tension * 20), curve_type="sine", ch=3)
        current_tick += dur_ticks

    # ── Track 4: Cello (GM 42 Cello, Ch 4) ──
    tracks_events[4].append((0, 'program', 42, 0, 4))
    current_tick = 0
    for note, duration in cello_notes:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_vc = int(62 + tension * 22)
        stagger = random.randint(-4, 4)
        on_t = max(0, current_tick + stagger)
        tracks_events[4].append((on_t, 'on', note, min(127, vel_vc), 4))
        tracks_events[4].append((current_tick + dur_ticks - 15, 'off', note, 0, 4))
        specialist_styles.generate_cc_curve(tracks_events[4], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=int(68 + tension * 22), curve_type="sine", ch=4)
        current_tick += dur_ticks

    # ── Track 5: Double Bass (GM 43 Contrabass, Ch 5) ──
    tracks_events[5].append((0, 'program', 43, 0, 5))
    current_tick = 0
    for note, duration in double_bass:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_bass = int(60 + tension * 20)
        stagger = random.randint(-3, 3)
        on_t = max(0, current_tick + stagger)
        tracks_events[5].append((on_t, 'on', note, min(127, vel_bass), 5))
        tracks_events[5].append((current_tick + dur_ticks - 10, 'off', note, 0, 5))
        specialist_styles.generate_cc_curve(tracks_events[5], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=vel_bass, curve_type="sine", ch=5)
        current_tick += dur_ticks

    # ── Track 6: Spiccato Ostinato - Short Strings (GM 49 String Ensemble 2, Ch 6) ──
    tracks_events[6].append((0, 'program', 49, 0, 6))
    for ev in ost_events:
        if _ost_is_cinematic:
            # cinematic generator returns 4-tuples: (tick, type, note, velocity)
            tick, etype, note, velocity = ev
        else:
            # legacy generator returns 5-tuples: (tick, type, note, velocity, ch)
            tick, etype, note, velocity, _ = ev
        tracks_events[6].append((tick, etype, note, velocity, 6))
    specialist_styles.generate_cc_curve(tracks_events[6], 11, 0, len(chord_groups) * 4 * tpb,
                                         start_val=int(50 + tension * 30), end_val=int(70 + tension * 30), curve_type="sine", ch=6)

    # ── Track 7: Piano Melody (GM 0 Acoustic Grand, Ch 7) ──
    tracks_events[7].append((0, 'program', 0, 0, 7))
    current_tick = 0
    for note, duration in piano_notes:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel_piano = int(50 + tension * 30)
        if duration <= 0.5:
            vel_piano = max(38, vel_piano - 8)
        tracks_events[7].append((current_tick, 'on', note, min(112, vel_piano), 7))
        tracks_events[7].append((current_tick + max(1, dur_ticks - 20), 'off', note, 0, 7))
        current_tick += dur_ticks

    # Build VVC Midi tracks from these events
    vvc_mid = specialist_styles.build_midi_from_events(tracks_events, tpb)
    _apply_vvc_track_names(vvc_mid)

    # Load original MIDI file
    original_mid = mido.MidiFile(filepath)

    # Combine original tracks and VVC tracks
    final_mid = mido.MidiFile()
    final_mid.ticks_per_beat = src_tpb

    # Copy all original tracks
    for track in original_mid.tracks:
        final_mid.tracks.append(track)

    # Copy all VVC tracks
    for track in vvc_mid.tracks:
        final_mid.tracks.append(track)

    base = os.path.splitext(os.path.basename(filepath))[0]
    progression_label = _vvc_progression_from_chord_groups(chord_groups, root_pc)
    key_label = f"{scale_name}_{'Minor' if is_minor else 'Major'}"
    fname = _vvc_filename("Quartet Overlay", f"Expressive Overlay from {base}",
                          root_name, key_label, bpm, progression_label)
    fpath = _vvc_unique_path(out_dir, fname)

    final_mid.save(fpath)
    print(f"\n  [SAVED]  {os.path.basename(fpath)}")
    print(f"  [PATH ]  {fpath}")
    print("       VVC Tracks (Ch 0-7): String Ensemble Pad | Violin I | Violin II | Viola | Cello | Double Bass | Spiccato Ostinato | Piano Melody\n")


def _generate_cello_core(root_note, bars_data, tension=0.5):
    """Cello bass line generator for MIDI overlay — uses bars_data directly."""
    cello = []
    cur = 0
    for bar_idx, (ct, sc) in enumerate(bars_data):
        matrix = get_markov_matrix(sc)
        beats_left = 4.0
        beat_pos = 0.0
        while beats_left > 0.01:
            dur = w_rhythm(RHYTHM_CELLO, beats_left, tension * 0.5)
            strong = (beat_pos % 2.0 < 0.01)
            if strong:
                off = random.choice([ct[0], ct[1 % len(ct)]])
            else:
                off = pick_markov_next(cur, sc, matrix)
            pitch = _pitch_in_register(root_note, off, CELLO_REGISTER)
            cello.append((pitch, dur))
            cur = off
            beats_left -= dur
            beat_pos += dur
    return cello


# ── CINEMATIC CHOIR GENERATION ─────────────────────────────────────────────

def _choir_phase(bar_idx, total_bars):
    pct = bar_idx / max(1, total_bars)
    if pct < 0.20:
        return 'mystery'
    if pct < 0.42:
        return 'awakening'
    if pct < 0.68:
        return 'ascent'
    if pct < 0.86:
        return 'revelation'
    return 'resolution'


def _choir_active_voices(phase):
    if phase == 'mystery':
        return {'alto', 'tenor'}
    if phase == 'awakening':
        return {'alto', 'tenor', 'bass'}
    if phase == 'ascent':
        return {'soprano', 'alto', 'tenor'}
    if phase == 'revelation':
        return {'soprano', 'alto', 'tenor', 'bass'}
    return {'alto', 'tenor'}


def _choir_register_for_phase(voice, phase):
    reg = CHOIR_REGISTERS[voice]
    if phase == 'mystery':
        return {'min': reg['intro_min'], 'max': reg['intro_max'], 'center': (reg['intro_min'] + reg['intro_max']) // 2}
    if phase == 'awakening':
        return {'min': max(reg['min'], reg['intro_min'] - 4), 'max': min(reg['max'], reg['intro_max'] + 3), 'center': (reg['intro_min'] + reg['intro_max']) // 2}
    if phase == 'ascent' and voice == 'soprano':
        return {'min': 72, 'max': reg['max'], 'center': 78}
    if phase == 'resolution':
        return {'min': reg['intro_min'], 'max': min(reg['max'], reg['intro_max'] + 2), 'center': (reg['intro_min'] + reg['intro_max']) // 2}
    return {'min': reg['min'], 'max': reg['max'], 'center': (reg['min'] + reg['max']) // 2}


def _nearest_pc_pitch(pc, register, prev_pitch=None):
    candidates = [p for p in range(register['min'], register['max'] + 1) if p % 12 == pc % 12]
    if not candidates:
        return register.get('center', (register['min'] + register['max']) // 2)
    target = prev_pitch if prev_pitch is not None else register.get('center', (register['min'] + register['max']) // 2)
    return min(candidates, key=lambda p: (abs(p - target), abs(p - register.get('center', target))))


def _cinematic_pc_pool(pcs, scale, intensity):
    pool = list(pcs)
    root_pc = pcs[0]
    scale_pcs = [s % 12 for s in scale]
    color_pcs = [(root_pc + 2) % 12, (root_pc + 5) % 12, (root_pc + 9) % 12]
    for pc in color_pcs:
        if pc in scale_pcs and pc not in pool and random.random() < intensity:
            pool.append(pc)
    return sorted(set(pool))


def _choose_choir_pc(voice, pcs, color_pool, prev_pitch, phase):
    root_pc = pcs[0]
    fifth_pc = pcs[2 % len(pcs)] if len(pcs) > 2 else pcs[1 % len(pcs)]
    if voice == 'bass':
        return root_pc if phase in ('mystery', 'awakening', 'resolution') or random.random() < 0.7 else fifth_pc
    if voice == 'tenor':
        choices = pcs if random.random() < 0.75 else color_pool
    elif voice == 'alto':
        choices = color_pool if phase in ('ascent', 'revelation') else pcs
    else:
        choices = color_pool if phase in ('ascent', 'revelation') else pcs

    if prev_pitch is not None:
        prev_pc = prev_pitch % 12
        if prev_pc in choices and random.random() < 0.60:
            return prev_pc
    return random.choice(choices)


def _add_choir_note(track, start_tick, dur_ticks, note, velocity, ch):
    breath = random.randint(35, 85)
    entry = random.randint(0, 18)
    on_tick = max(0, start_tick + entry)
    off_tick = max(on_tick + 1, start_tick + dur_ticks - breath)
    track.append((on_tick, 'on', note, min(127, max(1, velocity)), ch))
    track.append((off_tick, 'off', note, 0, ch))


def generate_dynamic_choir_from_chords(chord_groups, root_pc, scale, bpm, tension=0.65, phases=None):
    """Generate an evolving SATB cinematic choir from detected chord groups."""
    tpb = 480
    total_bars = max(1, len(chord_groups))
    tracks_events = [[] for _ in range(4)]
    voice_order = [('soprano', 0), ('alto', 1), ('tenor', 2), ('bass', 3)]
    prev = {voice: None for voice, _ in voice_order}

    for voice, ch in voice_order:
        tracks_events[ch].append((0, 'program', 52, 0, ch))
        tracks_events[ch].append((0, 'tempo', bpm, 0, ch))

    for bar_idx, pcs in enumerate(chord_groups):
        if phases is not None and bar_idx < len(phases):
            phase = phases[bar_idx]
        else:
            phase = _choir_phase(bar_idx, total_bars)
        active = _choir_active_voices(phase)
        intensity = {'mystery': 0.25, 'awakening': 0.45, 'ascent': 0.65, 'revelation': 0.90, 'resolution': 0.35}[phase]
        color_pool = _cinematic_pc_pool(pcs, scale, intensity)
        bar_start = bar_idx * 4 * tpb

        for voice, ch in voice_order:
            if voice not in active:
                continue

            register = _choir_register_for_phase(voice, phase)
            base_vel = int(42 + intensity * 45 + tension * 12)
            phrase_start = bar_start + random.randint(0, 55 if phase in ('mystery', 'resolution') else 30)
            phrase_len = max(tpb, bar_start + 4 * tpb - phrase_start)
            if phase in ('mystery', 'resolution'):
                segments = [phrase_len]
            elif phase == 'revelation' and voice in ('soprano', 'alto') and random.random() < 0.55:
                segments = [tpb * 2, tpb, tpb]
            elif phase in ('ascent', 'revelation') and voice != 'bass' and random.random() < 0.45:
                segments = [tpb * 2, tpb * 2]
            else:
                segments = [phrase_len]

            local_start = phrase_start
            for seg_idx, seg_ticks in enumerate(segments):
                pc = _choose_choir_pc(voice, pcs, color_pool, prev[voice], phase)
                if seg_idx > 0 and random.random() < 0.40:
                    step_options = [candidate for candidate in color_pool
                                    if min((candidate - pc) % 12, (pc - candidate) % 12) in (1, 2)]
                    if step_options:
                        pc = random.choice(step_options)
                note = _nearest_pc_pitch(pc, register, prev[voice])
                _add_choir_note(tracks_events[ch], local_start, seg_ticks, note, base_vel + seg_idx * 5, ch)
                swell_start = max(0, local_start)
                specialist_styles.generate_cc_curve(tracks_events[ch], 11, swell_start, seg_ticks,
                                                     start_val=max(28, base_vel - 20),
                                                     end_val=min(118, base_vel + 18),
                                                     curve_type="sine", ch=ch)
                specialist_styles.generate_cc_curve(tracks_events[ch], 1, swell_start, seg_ticks,
                                                     start_val=max(20, base_vel - 25),
                                                     end_val=min(112, base_vel + 12),
                                                     curve_type="sine", ch=ch)
                prev[voice] = note
                local_start += seg_ticks

    return specialist_styles.build_midi_from_events(tracks_events, tpb)


def generate_choir_over_midi(filepath, out_dir):
    """Analyze a chord-progression MIDI file and create an evolving SATB choir arrangement."""
    print(f"\n  Analyzing: {os.path.basename(filepath)} ...")
    try:
        chord_timeline, _ = parse_midi_chord_timeline(filepath)
    except Exception as e:
        print(f"  [ERROR] Could not read file: {e}")
        return

    if not chord_timeline:
        print("  [ERROR] No chord groups found.")
        print("  Tip: The file must contain block chords or clear simultaneous harmony.")
        return

    chord_groups = [pcs for _, pcs in chord_timeline]
    root_name, root_pc, scale, scale_name, is_minor = detect_key(chord_groups)
    bpm = detect_tempo(filepath)

    print(f"  Detected Key  : {root_name} {scale_name} ({'Minor' if is_minor else 'Major'})")
    print(f"  Detected BPM  : {bpm}")
    print(f"  Chord events  : {len(chord_groups)}")

    print("\n  Choir intensity:")
    print("  1. Sacred / Sparse   2. Cinematic Build   3. Massive / Revelatory")
    tc = input("  Choice (1-3, default 2): ").strip() or '2'
    tension = {'1': 0.45, '2': 0.65, '3': 0.85}.get(tc, 0.65)

    mid = generate_dynamic_choir_from_chords(chord_groups, root_pc, scale, bpm, tension)

    base = os.path.splitext(os.path.basename(filepath))[0]
    intensity_label = {'1': 'Sacred Sparse', '2': 'Cinematic Build', '3': 'Massive Revelatory'}.get(tc, 'Cinematic Build')
    progression_label = _vvc_progression_from_chord_groups(chord_groups, root_pc)
    key_label = f"{scale_name}_{'Minor' if is_minor else 'Major'}"
    fname = _vvc_filename("Cinematic Choir", f"{intensity_label} from {base}",
                          root_name, key_label, bpm, progression_label)
    fpath = _vvc_unique_path(out_dir, fname)

    mid.save(fpath)
    print(f"\n  [SAVED]  {os.path.basename(fpath)}")
    print(f"  [PATH ]  {fpath}")
    print("       Tracks: [Soprano] + [Alto] + [Tenor] + [Bass]\n")


ARRANGEMENT_SECTIONS_120 = [
    {'name': 'Intro', 'start': 0, 'bars': 16, 'energy': 0.25},
    {'name': 'Build-up', 'start': 16, 'bars': 16, 'energy': 0.50},
    {'name': 'Main Theme A', 'start': 32, 'bars': 32, 'energy': 0.80},
    {'name': 'Development', 'start': 64, 'bars': 16, 'energy': 0.45},
    {'name': 'Climax', 'start': 80, 'bars': 24, 'energy': 1.00},
    {'name': 'Final Chorus', 'start': 104, 'bars': 8, 'energy': 0.90},
    {'name': 'Outro', 'start': 112, 'bars': 8, 'energy': 0.30},
]


def _absolute_track_messages(track):
    tick = 0
    messages = []
    for msg in track:
        tick += msg.time
        messages.append((tick, msg))
    return messages


def _track_program_and_channel(abs_messages):
    program = None
    channel = None
    for _, msg in abs_messages:
        if hasattr(msg, 'channel'):
            channel = msg.channel if channel is None else channel
        if msg.type == 'program_change':
            program = msg.program
            channel = msg.channel
            break
    return program, channel


def _classify_arrangement_track(track_index, track_name, program, avg_note):
    name = (track_name or '').lower()
    if 'ost' in name or program in (45, 49):
        return 'ostinato'
    if 'piano' in name or program in (0, 1):
        return 'piano'
    if 'cello' in name or program == 42 or (avg_note is not None and avg_note < 50):
        return 'cello'
    if 'viola' in name or program == 41 or (avg_note is not None and avg_note < 60):
        return 'viola'
    if 'violin ii' in name or 'counter' in name or track_index == 2:
        return 'counter'
    if 'violin' in name or 'lead' in name or program == 40:
        return 'lead'
    if 'pad' in name or 'string' in name or program in (48, 50, 51):
        return 'pad'
    if avg_note is not None and avg_note >= 80:
        return 'piano'
    return 'unknown'


def _role_active_in_section_120(role, section_name, section_bar, section_bars):
    """Determine if an instrument role is active at this stage of the 120-bar arrangement."""
    if section_name == 'Intro':
        return role in ('pad', 'piano')
    elif section_name == 'Build-up':
        if role in ('pad', 'piano', 'cello', 'bass'):
            return True
        if role in ('viola', 'ostinato') and section_bar >= 8:
            return True
        return False
    elif section_name == 'Main Theme A':
        return True
    elif section_name == 'Development':
        return role not in ('lead', 'ostinato')
    elif section_name == 'Climax':
        return True
    elif section_name == 'Final Chorus':
        return True
    elif section_name == 'Outro':
        if role in ('pad', 'piano', 'cello', 'bass') and section_bar < 4:
            return True
        if role in ('pad', 'piano') and section_bar >= 4:
            return True
        return False
    return True


def _section_velocity_scale_120(section_name, section_bar, section_bars):
    """Scale notes dynamically for expressive performance based on the arrangement energy."""
    base = {
        'Intro': 0.45,
        'Build-up': 0.55,
        'Main Theme A': 0.85,
        'Development': 0.60,
        'Climax': 1.15,
        'Final Chorus': 0.95,
        'Outro': 0.50,
    }[section_name]
    
    if section_name == 'Build-up':
        base += 0.25 * (section_bar / max(1, section_bars - 1))
    elif section_name == 'Outro':
        base -= 0.25 * (section_bar / max(1, section_bars - 1))
    return base


def _choir_phase_for_section_120(section_name):
    """Map arrangement sections to matching choir evolution phases."""
    if section_name == 'Intro':
        return 'mystery'
    elif section_name == 'Build-up':
        return 'awakening'
    elif section_name == 'Main Theme A':
        return 'ascent'
    elif section_name == 'Development':
        return 'mystery'
    elif section_name == 'Climax':
        return 'revelation'
    elif section_name == 'Final Chorus':
        return 'revelation'
    elif section_name == 'Outro':
        return 'resolution'
    return 'mystery'


def _extract_source_tracks_for_arrangement(filepath, source_bars=4):
    mid = mido.MidiFile(filepath)
    tpb = mid.ticks_per_beat
    loop_ticks = source_bars * 4 * tpb
    tracks = []
    for idx, track in enumerate(mid.tracks):
        abs_messages = _absolute_track_messages(track)
        notes = [msg.note for tick, msg in abs_messages
                 if tick < loop_ticks and msg.type == 'note_on' and msg.velocity > 0]
        musical = bool(notes)
        program, channel = _track_program_and_channel(abs_messages)
        avg_note = sum(notes) / len(notes) if notes else None
        role = _classify_arrangement_track(idx, getattr(track, 'name', ''), program, avg_note)
        tracks.append({
            'index': idx,
            'name': getattr(track, 'name', '') or f'Track {idx}',
            'program': program,
            'channel': channel if channel is not None else min(idx, 15),
            'role': role,
            'musical': musical,
            'messages': [(tick, msg) for tick, msg in abs_messages if tick <= loop_ticks],
        })
    return mid, tpb, loop_ticks, tracks


def _arranged_source_tracks_120(source_tracks, tpb, loop_ticks):
    musical_tracks = [tr for tr in source_tracks if tr['musical']]
    arranged = []
    for rank, src in enumerate(musical_tracks):
        out = []
        ch = src['channel']
        if src['program'] is not None:
            out.append((0, 'program', src['program'], 0, ch))

        for section in ARRANGEMENT_SECTIONS_120:
            for section_bar in range(section['bars']):
                absolute_bar = section['start'] + section_bar
                source_bar = absolute_bar % 4
                source_start = source_bar * 4 * tpb
                source_end = source_start + 4 * tpb
                dest_start = absolute_bar * 4 * tpb

                if not _role_active_in_section_120(src['role'], section['name'], section_bar, section['bars']):
                    continue

                scale = _section_velocity_scale_120(section['name'], section_bar, section['bars'])
                for tick, msg in src['messages']:
                    if tick < source_start or tick >= source_end:
                        continue
                    dest_tick = dest_start + (tick - source_start)
                    if msg.type == 'note_on':
                        if msg.velocity > 0:
                            vel = int(msg.velocity * scale)
                            out.append((dest_tick, 'on', msg.note, max(1, min(127, vel)), ch))
                        else:
                            out.append((dest_tick, 'off', msg.note, 0, ch))
                    elif msg.type == 'note_off':
                        out.append((dest_tick, 'off', msg.note, 0, ch))
                    elif msg.type == 'control_change':
                        out.append((dest_tick, 'cc', msg.control, msg.value, ch))

                specialist_styles.generate_cc_curve(out, 11, dest_start, 4 * tpb,
                                                     start_val=max(25, int(45 * scale)),
                                                     end_val=min(118, int(72 * scale)),
                                                     curve_type="sine", ch=ch)
        arranged.append(out)
    return arranged


def _repeat_chord_groups_to_120(chord_groups):
    if not chord_groups:
        return []
    return [chord_groups[i % len(chord_groups)] for i in range(120)]


def merge_choir_into_midi(input_midi_path, choir_midi, choir_channel_base=7):
    """Merge choir tracks into the input MIDI file, routing them to choir channels and stripping old ones."""
    input_mid = mido.MidiFile(input_midi_path)
    
    # Strip existing choir tracks
    new_tracks = []
    for track in input_mid.tracks:
        track_name = (getattr(track, 'name', '') or '').lower()
        if any(w in track_name for w in ['choir', 'soprano', 'alto', 'tenor', 'bass']):
            continue
        
        # Filter out messages on channels 7-10
        filtered_track = mido.MidiTrack()
        for msg in track:
            if not msg.is_meta and getattr(msg, 'channel', 0) in (7, 8, 9, 10):
                continue
            filtered_track.append(msg)
        new_tracks.append(filtered_track)
    input_mid.tracks = new_tracks
    
    target_tpb = input_mid.ticks_per_beat
    choir_tpb = choir_midi.ticks_per_beat
    tick_scale = target_tpb / float(choir_tpb or target_tpb)

    for idx, track in enumerate(choir_midi.tracks):
        new_track = mido.MidiTrack()
        voice_name = ['Soprano', 'Alto', 'Tenor', 'Bass'][idx % 4]
        new_track.append(mido.MetaMessage('track_name', name=voice_name, time=0))
        
        ch = choir_channel_base + idx
        new_track.append(mido.Message('program_change', program=52, channel=ch, time=0))
        
        for msg in track:
            if msg.is_meta:
                if msg.type in ('set_tempo', 'time_signature', 'key_signature'):
                    continue
                new_msg = msg.copy(time=round(msg.time * tick_scale))
                new_track.append(new_msg)
            elif hasattr(msg, 'channel'):
                new_msg = msg.copy(channel=ch, time=round(msg.time * tick_scale))
                new_track.append(new_msg)
            else:
                new_msg = msg.copy(time=round(msg.time * tick_scale))
                new_track.append(new_msg)
                
        input_mid.tracks.append(new_track)
        
    return input_mid


def generate_120bar_arrangement_from_midi(filepath, out_dir):
    """Create a 120-bar cinematic arrangement plus SATB choir from a user-edited 4-bar MIDI."""
    print(f"\n  Analyzing arrangement source: {os.path.basename(filepath)} ...")
    try:
        source_mid, tpb, loop_ticks, source_tracks = _extract_source_tracks_for_arrangement(filepath)
        chord_timeline, _ = parse_midi_chord_timeline(filepath)
    except Exception as e:
        print(f"  [ERROR] Could not read file: {e}")
        return

    musical_tracks = [tr for tr in source_tracks if tr['musical']]
    if not musical_tracks:
        print("  [ERROR] No playable note tracks found in the MIDI.")
        return
    if not chord_timeline:
        print("  [ERROR] No chord progression detected. Use a 4-bar MIDI with clear harmony.")
        return

    chord_groups_4 = [pcs for tick, pcs in chord_timeline if tick < loop_ticks]
    if not chord_groups_4:
        chord_groups_4 = [pcs for _, pcs in chord_timeline]
    chord_groups_120 = _repeat_chord_groups_to_120(chord_groups_4)

    root_name, root_pc, scale, scale_name, is_minor = detect_key(chord_groups_4)
    bpm = detect_tempo(filepath)

    print(f"  Detected Key     : {root_name} {scale_name} ({'Minor' if is_minor else 'Major'})")
    print(f"  Detected BPM     : {bpm}")
    print(f"  Source tracks    : {len(musical_tracks)}")
    print("  Arrangement Arc  : Intro -> Build-up -> Main Theme A -> Development -> Climax -> Final Chorus -> Outro (120 bars)")

    # Build phases for 120 bars based on arrangement sections
    phases = []
    for section in ARRANGEMENT_SECTIONS_120:
        for _ in range(section['bars']):
            phases.append(_choir_phase_for_section_120(section['name']))

    arranged_tracks = _arranged_source_tracks_120(source_tracks, tpb, loop_ticks)
    if arranged_tracks:
        arranged_tracks[0].append((0, 'tempo', bpm, 0, 0))

    # Generate 120-bar section-aware choir
    choir_mid = generate_dynamic_choir_from_chords(chord_groups_120, root_pc, scale, bpm, tension=0.75, phases=phases)
    
    # Temporarily save arranged instruments
    final_instrument_mid = specialist_styles.build_midi_from_events(arranged_tracks, tpb)
    
    base = os.path.splitext(os.path.basename(filepath))[0]
    progression_label = _vvc_progression_from_chord_groups(chord_groups_4, root_pc)
    key_label = f"{scale_name}_{'Minor' if is_minor else 'Major'}"
    fname = _vvc_filename("120Bar Epic Arrangement", f"Source {base}",
                          root_name, key_label, bpm, progression_label)
    fpath = _vvc_unique_path(out_dir, fname)
        
    final_instrument_mid.save(fpath)
    
    # Merge choir into the file
    final_mid = merge_choir_into_midi(fpath, choir_mid)
    final_mid.save(fpath)

    print(f"\n  [SAVED]  {os.path.basename(fpath)}")
    print(f"  [PATH ]  {fpath}")
    print(f"       Tracks: {len(musical_tracks)} source instrument tracks + SATB choir")
    for section in ARRANGEMENT_SECTIONS_120:
        print(f"       {section['name']:<15}: bars {section['start'] + 1}-{section['start'] + section['bars']}")
    print()


def show_instrument_routing():
    """Display the full DAW routing guide for all ANIMA engines."""
    print("""
  ====================================================================
   A N I M A   D A W   R O U T I N G   &   M I D I   C H A N N E L
   M A N U A L
  ====================================================================

  ====================================================================
   ENGINE 1 & 2 -- Minor / Major Scale Engine
  ====================================================================
   Generates a 4-bar Markov-chain MIDI.  Track structure:

    Ch 0  ->  String Ensemble Pad    GM 48  (String Ensemble 1)
              Voice-led chord pad; sustains the full bar.
              CC#11 Expression & CC#1 ModWheel swells.

    Ch 1  ->  Violin I  (Lead Melody)  GM 40
              Lyrical melody -- register C5-B5 (MIDI 72-83).
              Markov walk with occasional octave leaps.

    Ch 2  ->  Violin II  (Counter)     GM 40
              Contrary motion -- register C4-B4 (MIDI 60-71).

    Ch 3  ->  Viola  (Harmonic fill)   GM 41
              Warm sustained counter-line -- C3-B3 (MIDI 48-59).

    Ch 4  ->  Cello  (Bass line)       GM 42
              Root/fifth motion -- C2-B2 (MIDI 36-47).

    Ch 5  ->  Spiccato Ostinato        GM 49  (String Ensemble 2)
              Compact short-string chord-tone pulses with bow-aware accents.

    Ch 6  ->  Piano Melody  (Colour)   GM 0
              Sparse decoration -- C6-C7 (MIDI 84-96).

  ====================================================================
   ENGINE 3 -- VVC String Orchestra  (standalone)
  ====================================================================
   Generates an 8-channel VVC layout:

    Ch 0  ->  String Ensemble Pad        GM 48
    Ch 1  ->  Violin I - Lead Melody     GM 40
    Ch 2  ->  Violin II - Counter Melody GM 40
    Ch 3  ->  Viola - Harmonic Fill      GM 41
    Ch 4  ->  Cello - Bass Line          GM 42
    Ch 5  ->  Double Bass - Low Foundation GM 43  (Contrabass)
    Ch 6  ->  Spiccato Ostinato - Short Strings GM 49
    Ch 7  ->  Piano Melody - Colour      GM 0

   All tracks include humanised CC#11/CC#1 expression curves.

  ====================================================================
   ENGINE 4 -- Melodic Overlayer  (Quartet Overlay)
  ====================================================================
   Appends 8 named VVC tracks to your existing MIDI:

    Ch 0  ->  String Ensemble Pad          GM 48
    Ch 1  ->  Violin I - Lead Melody       GM 40
    Ch 2  ->  Violin II - Counter Melody   GM 40
    Ch 3  ->  Viola - Harmonic Fill        GM 41
    Ch 4  ->  Cello - Bass Line            GM 42
    Ch 5  ->  Double Bass - Low Foundation GM 43  (Contrabass)
    Ch 6  ->  Spiccato Ostinato - Short Strings GM 49
    Ch 7  ->  Piano Melody - Colour        GM 0

  ====================================================================
   ENGINE 5 -- Spanish Guitar Composer
  ====================================================================
   Generates a 4-track nylon-guitar arrangement:

    Ch 0  ->  Bajo  (bass thumb strokes)       GM 25  (Steel Guitar)
    Ch 1  ->  Rasgueado  (strummed chords)     GM 25
    Ch 2  ->  Alzapua  (counter-melody thumb)  GM 24  (Nylon Guitar)
    Ch 3  ->  Picado  (single-note lead runs)  GM 24

  ====================================================================
   ENGINE 6 -- Modern Cinematic Trailer Engine
  ====================================================================
   Generates a 4-bar stem-ready arrangement.

   FOUNDATION TRACKS  (present in every mood):
    Ch 0  ->  Chord Pad          GM 89  (Warm Pad)       MIDI 52-76
              Voice-led inversion pad -- nearest-pitch per bar.
    Ch 1  ->  Sub Bass           GM 43  (Contrabass)    MIDI 36-48
              Sustained root on every bar.
    Ch 2  ->  High Drone         GM 48  (String Ens 1)  MIDI 84-96
              Long sustained tension note for the full cue.
    Ch 3  ->  Staccato / Spiccato Strings GM 48         MIDI 55-72
              BPM-aware short-string cells with phrase arcs and humanized bow accents.

   MINOR MOODS:
    Mood 1 -- Ethereal Gothic Fantasy  (10 tracks)
      Ch 4  ->  Choir - Bass       GM 52  (Choir Aahs)  MIDI 43-55
      Ch 5  ->  Choir - Tenor      GM 52               MIDI 53-65
      Ch 6  ->  Choir - Alto       GM 52               MIDI 59-71
      Ch 7  ->  Choir - Soprano    GM 52               MIDI 65-77
      Ch 8  ->  Harp / Nylon Arps  GM 46  (Harp)
      Ch 9  ->  Piano Melody       GM 0   (Grand Piano) MIDI 72-84

    Mood 2 -- Epic Heroic Action  (10 tracks)
      Ch 4  ->  Heavy Brass        GM 61  (Brass Section) MIDI 41-60
      Ch 5  ->  Choir - Bass       GM 52
      Ch 6  ->  Choir - Tenor      GM 52
      Ch 7  ->  Choir - Alto       GM 52
      Ch 8  ->  Choir - Soprano    GM 52
      Ch 9  ->  Piano Melody       GM 0   (Grand Piano) MIDI 72-84

    Mood 3 -- Dark Assassin Stealth  (11 tracks)
      Ch 4  ->  Nylon Guitars      GM 24  (Nylon Guitar)
      Ch 5  ->  Dark Piano         GM 0   (Grand Piano)
      Ch 6  ->  Choir - Bass       GM 52
      Ch 7  ->  Choir - Tenor      GM 52
      Ch 8  ->  Choir - Alto       GM 52
      Ch 9  ->  Choir - Soprano    GM 52
      Ch 10 ->  Piano Melody       GM 0   (Grand Piano) MIDI 72-84

   MAJOR MOODS:
    Mood 1 -- Triumphant Ascent  (10 tracks)
      Ch 4  ->  Brass Fanfare      GM 61  MIDI 53-72
      Ch 5  ->  Choir - Bass       GM 52
      Ch 6  ->  Choir - Tenor      GM 52
      Ch 7  ->  Choir - Alto       GM 52
      Ch 8  ->  Choir - Soprano    GM 52
      Ch 9  ->  Piano Melody       GM 0   MIDI 72-84

    Mood 2 -- Celestial Wonder  (10 tracks)
      Ch 4  ->  Celesta Arps       GM 8   (Celesta)      MIDI 72-90
      Ch 5  ->  Choir - Bass       GM 52
      Ch 6  ->  Choir - Tenor      GM 52
      Ch 7  ->  Choir - Alto       GM 52
      Ch 8  ->  Choir - Soprano    GM 52
      Ch 9  ->  Piano Melody       GM 0   MIDI 72-84

    Mood 3 -- Golden Pastoral  (11 tracks)
      Ch 4  ->  Pastoral Harp      GM 46  (Harp)
      Ch 5  ->  Woodwind Lead      GM 73  (Flute)        MIDI 65-79
      Ch 6  ->  Choir - Bass       GM 52
      Ch 7  ->  Choir - Tenor      GM 52
      Ch 8  ->  Choir - Alto       GM 52
      Ch 9  ->  Choir - Soprano    GM 52
      Ch 10 ->  Piano Melody       GM 0   MIDI 72-84

  ====================================================================
   PRO TIPS
  ====================================================================
   * Route each MIDI channel to its own sampler instrument/patch.
   * Enable CC#1 (ModWheel) and CC#11 (Expression) response for
     realistic dynamic shaping on string/choir patches.
   * For Cinematic Engine output, load each stem into a separate DAW
     track and apply your own reverb / room to each layer.
   * Spitfire LABS / BBC Symphony and EastWest Hollywood Strings
     respond well to the CC curves already baked into Engines 1-4.
  ====================================================================
""")


def main(out_dir='midi_files'):
    os.makedirs(out_dir, exist_ok=True)

    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║      V V C   —   S T R I N G   O R C H E S T R A          ║
║     String Orchestra Composition Engine                    ║
║                                                            ║
║    Scales: Major · Minor  |  Mood-Adaptive Progressions    ║
║    8 Tracks: Strings + Double Bass + Ostinato + Piano      ║
║    Humanized Phrasing  |  MIDI CC Expression Curves        ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

    while True:
        print("""  Select a mode:
  ____________________________________________________________

    1  ->  Compose New String Quartet
           Generates a 4-bar orchestral loop in your chosen key and mood

    2  ->  DAW Routing Guide
           View track assignments for your sampler

    3  ->  Analyze MIDI File & Create Quartet Overlay
           Load an existing MIDI, detect key/tempo, add VVC string parts

    4  ->  Create 120-Bar Epic Arrangement + Choir
           Expand a user-edited 4-bar MIDI into a full 120-bar cinematic song arc

    0  ->  Exit
  ____________________________________________________________
""")
        _div()
        choice = input("  --> ").strip().lower()
        _div('=')

        if choice == '0':
            print("  Exiting. May your strings sing!\n")
            break

        elif choice == '1':
            # Step 1: Select scale type
            scale_type = select_scale_type()
            is_minor = (scale_type == '1')

            # Step 2: Select key
            root_name, root_val = select_key(is_minor)

            # Step 3: Select tempo
            bpm = select_tempo()

            # Step 4: Select mood
            mood_name, tension, progression, label = select_mood(is_minor)

            # Step 5: Fixed 4-bar loop
            num_bars = 4
            length_label = "4-Bar Loop"
            
            gen_mode = globals().get('GENERATION_MODE', 'simple')
            if gen_mode == 'decoupled':
                roman_numerals = RN_MINOR if is_minor else RN_MAJOR
                start_chord = progression[0]
                _, scale_tones = roman_numerals[start_chord]
                expanded = generate_decoupled_progression(tension, scale_tones, is_minor=is_minor)
                display_prog = "Double-Layer Decoupled Markov Walk"
            else:
                expanded = progression[:num_bars]
                display_prog = '-'.join(expanded)
            prog_label = label

            # Step 6: Display summary
            scale_label = "Minor" if is_minor else "Major"
            tbar = '#' * int(tension * 10) + '.' * (10 - int(tension * 10))

            print(f"""
  ── Composition Summary ──────────────────────────────
    Structure    :  {length_label}
    Scale        :  {scale_label}
    Key          :  {root_name}
    BPM          :  {bpm}
    Mood         :  {mood_name}
    Style        :  {label}
    Progression  :  {display_prog}
    Tension      :  [{tbar}] {int(tension*100)}%
  ────────────────────────────────────────────────────
""")

            # Step 7: Generate
            print(f"  Generating {length_label} String Quartet...\n")

            roman_numerals = RN_MINOR if is_minor else RN_MAJOR
            mid = generate_string_quartet(bpm, root_name, root_val, expanded,
                                           roman_numerals, tension, mood_name,
                                           prog_label, num_bars=num_bars)

            # Step 8: Save
            fname = _vvc_filename(f"String Quartet 4Bar {mood_name}", prog_label,
                                  root_name, scale_label, bpm, display_prog)
            fpath = _vvc_unique_path(out_dir, fname)

            mid.save(fpath)
            print(f"  [SAVED]  {os.path.basename(fpath)}")
            print(f"  [PATH ]  {fpath}\n")

            print("  [G] Generate again with new key/mood  [B] Back  [Q] Exit")
            sub = input("  --> ").strip().lower()
            if sub == 'q':
                print("  Exiting. May your strings sing!\n")
                break
            elif sub == 'b':
                continue
            # else: loop continues (generate again)

        elif choice == '2':
            show_instrument_routing()
            input("  Press [Enter] to return to Main Menu...")

        elif choice == '3':
            print("  ANALYZE MIDI FILE & GENERATE STRING QUARTET OVERLAY")
            _div()
            filepath = input("  Enter path to MIDI file: ").strip().strip('"').strip("'")
            if not os.path.isfile(filepath):
                print(f"  [ERROR] File not found: {filepath}")
            else:
                generate_quartet_over_midi(filepath, out_dir)

        elif choice == '4':
            print("  CREATE 120-BAR EPIC ARRANGEMENT + CHOIR")
            _div()
            print("  Source should be a user-edited 4-bar MIDI with your instrument tracks/channels.")
            filepath = input("  Enter path to 4-bar MIDI file: ").strip().strip('"').strip("'")
            if not os.path.isfile(filepath):
                print(f"  [ERROR] File not found: {filepath}")
            else:
                generate_120bar_arrangement_from_midi(filepath, out_dir)

        else:
            print("  [!] Invalid choice. Enter 1-5, or 0.\n")

        _div()
        time.sleep(0.1)


if __name__ == '__main__':
    main()
