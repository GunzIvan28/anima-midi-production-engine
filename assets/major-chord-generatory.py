"""
major-chord-generatory.py  —  Orchestral Edition (Major Scale Companion)
Features:
  1. Generate major chord progressions by mood (Markov melody + counter-melody)
  2. Load an existing MIDI file and generate melodies on top of it
"""

import mido, os, random, time, math

GENERATION_MODE = 'simple'
DEFAULT_BPM = 120

PROJECT_ADJECTIVES = [
    "Apex", "Infinite", "Midnight", "Titan", "Solar", "Gothic", "Ethereal", "Grim", "Silent",
    "Shadow", "Crimson", "Nebula", "Spectral", "Cosmic", "Lost", "Fallen", "Eternal", "Frozen",
    "Abyssal", "Radiant", "Iron", "Storm", "Phoenix", "Astral", "Mystic", "Ancient", "Vortex",
    "Golden", "Azure", "Ivory", "Velvet", "Opaline", "Bright", "Celestial", "Halcyon", "Luminous",
    "Emerald", "Silver", "Wildflower", "Arcadian", "Aurora", "Meadow", "Horizon", "Crown",
    "Hearth", "Beacon", "Summit", "Festival", "Morning", "Starlit", "Glass", "River",
    "Saffron", "Pearl", "Amber", "Verdant", "Kinetic", "Heroic", "Noble", "Kindled",
    "Sunlit", "Euphoric", "Glorious", "Open", "Brave", "Voyager", "Prismatic", "Choral",
    "Clear", "Highland", "Royal", "Flourishing", "Magnolia", "Evergreen", "Skylit", "Cobalt",
    "Windswept", "Mosaic", "Jubilant", "Pastoral", "Uplifted", "Seraphic", "Lantern", "Daybreak",
    "Resonant", "Harmonic", "Ascending", "Jade", "Hymnal", "Brilliant", "Fabled", "Keystone",
]
PROJECT_NOUNS = [
    "Ascent", "Requiem", "Odyssey", "Eclipse", "Horizon", "Empire", "Sanctuary", "Vanguard",
    "Echo", "Whisper", "Rift", "Conquest", "Genesis", "Destiny", "Void", "Valhalla", "Covenant",
    "Chronicle", "Legacy", "Bastion", "Rebirth", "Summit", "Oracle", "Wasteland", "Mirage",
    "Bloom", "Cathedral", "Pilgrimage", "Promise", "Reverie", "Harbor", "Crest", "Dawn",
    "Garden", "Lantern", "Solstice", "Voyage", "Citadel", "Pageant", "Vista", "Meadow",
    "Comet", "Fountain", "Bridge", "Kingdom", "Overture", "Parade", "Ember", "Cloud",
    "Anthem", "Procession", "Festival", "Crown", "Haven", "Grove", "Radiance", "Signal",
    "Beacon", "Hymn", "Flourish", "Voyager", "Summons", "Accord", "Hearth", "Promise",
    "Canopy", "Pathway", "Threshold", "Skyline", "Fanfare", "Reunion", "Meadowlark", "Tapestry",
    "Sundial", "Harpsong", "Riverbend", "Triumph", "Laurel", "Morningstar", "Avenue", "Fable",
    "Citadel", "Pageantry", "Bell", "Pavilion", "Compass", "Frontier", "Wonder", "Harmonia",
]

# ── SCALES ──────────────────────────────────────────────────────────────────
SCALE_IONIAN      = [0, 2, 4, 5, 7, 9, 11]  # Natural Major
SCALE_LYDIAN      = [0, 2, 4, 6, 7, 9, 11]  # Bright / Dreamy Lydian
SCALE_MIXOLYDIAN  = [0, 2, 4, 5, 7, 9, 10]  # Warm / Anthem Mixolydian
SCALE_MELODIC_MAJ = [0, 2, 4, 5, 7, 8, 10]  # Mixolydian b6 (Melodic Major)
SCALE_MAJOR_PENT  = [0, 2, 4, 7, 9]         # Open / Playful Pentatonic

# Krumhansl-Schmuckler Major profile for key detection
KS_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]

ROOT_NAMES = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']

roots = {'C':36,'C#':37,'D':38,'Eb':39,'E':40,'F':41,
         'F#':42,'G':43,'Ab':44,'A':45,'Bb':46,'B':47}

# Roman numeral chords and scales mapped for Major scales
roman_numerals = {
    'I':       ([0, 4, 7],     SCALE_IONIAN),
    'Imaj7':   ([0, 4, 7, 11], SCALE_IONIAN),
    'ii':      ([2, 5, 9],     SCALE_IONIAN),
    'ii7':     ([2, 5, 9, 0],  SCALE_IONIAN),
    'iii':     ([4, 7, 11],    SCALE_IONIAN),
    'IV':      ([5, 9, 12],    SCALE_IONIAN),
    'IVmaj7':  ([5, 9, 12, 16], SCALE_LYDIAN),
    'V':       ([7, 11, 14],   SCALE_IONIAN),
    'V7':      ([7, 11, 14, 5], SCALE_IONIAN),
    'vi':      ([9, 12, 16],   SCALE_IONIAN),
    'viio':    ([11, 14, 17],  SCALE_IONIAN),
    'II':      ([2, 6, 9],     SCALE_LYDIAN),      # Lydian major II
    'bIII':    ([3, 7, 10],    SCALE_MIXOLYDIAN), # Modal borrowing
    'iv':      ([5, 8, 12],    SCALE_MELODIC_MAJ), # Minor iv in major key
    'bVI':     ([8, 12, 15],   SCALE_MIXOLYDIAN),
    'bVII':    ([10, 14, 17],  SCALE_MIXOLYDIAN),
    'v':       ([7, 10, 14],   SCALE_MIXOLYDIAN),
}

# ── MOOD PROGRESSIONS (Major scale specific) ─────────────────────────────────
moods = {
    "1": {"name": "Uplifting & Joyful", "tension": 0.35, "progressions": [
        {'chords': ['I', 'V', 'vi', 'IV'],       'label': 'Pop-Punk Anthem'},
        {'chords': ['I', 'IV', 'V', 'I'],        'label': 'Standard Cadence'},
        {'chords': ['I', 'IV', 'vi', 'V'],       'label': 'Optimistic Leap'},
        {'chords': ['I', 'vi', 'IV', 'V'],       'label': 'Classic 50s Stand-By'},
        {'chords': ['I', 'V', 'IV', 'V'],        'label': 'Driving Positivity'},
        {'chords': ['I', 'vi', 'ii', 'V'],       'label': 'Playful Stepwise'},
        {'chords': ['I', 'V', 'I', 'IV'],        'label': 'Bright Morning'},
        {'chords': ['I', 'IV', 'I', 'V'],        'label': 'Folksy Joy'},
    ]},
    "2": {"name": "Majestic & Triumphant", "tension": 0.65, "progressions": [
        {'chords': ['I', 'bVII', 'IV', 'I'],     'label': 'Mixolydian Rock Anthem'},
        {'chords': ['I', 'V', 'vi', 'iii', 'IV', 'I', 'IV', 'V'], 'label': 'Canon Heroic'},
        {'chords': ['I', 'IV', 'bVII', 'I'],     'label': 'Ascent to Glory'},
        {'chords': ['I', 'bIII', 'bVII', 'IV'],  'label': 'Epic Orchestral Lift'},
        {'chords': ['I', 'II', 'IV', 'I'],       'label': 'Lydian Rising'},
        {'chords': ['I', 'bVII', 'I', 'IV'],     'label': 'Royal Procession'},
        {'chords': ['I', 'V', 'IV', 'I'],        'label': 'Triumphant Call'},
        {'chords': ['I', 'bVI', 'bVII', 'I'],    'label': 'Fantasy Anthem'},
    ]},
    "3": {"name": "Serene & Dreamy", "tension": 0.25, "progressions": [
        {'chords': ['I', 'II', 'I', 'II'],       'label': 'Lydian Ethereal Cloud'},
        {'chords': ['Imaj7', 'IVmaj7', 'Imaj7', 'IVmaj7'], 'label': 'Celestial Float'},
        {'chords': ['I', 'IVmaj7', 'V', 'I'],    'label': 'Lush Meadow'},
        {'chords': ['I', 'bVII', 'I', 'bVII'],   'label': 'Mixolydian Drifting'},
        {'chords': ['I', 'iii', 'IV', 'V'],      'label': 'Peaceful River'},
        {'chords': ['I', 'vi', 'iii', 'IV'],     'label': 'Dreamy Reflection'},
        {'chords': ['Imaj7', 'II', 'IVmaj7', 'I'], 'label': 'Ambient Horizon'},
        {'chords': ['I', 'Imaj7', 'IV', 'IVmaj7'], 'label': 'Soft Morning Breeze'},
    ]},
    "4": {"name": "Nostalgic & Bittersweet", "tension": 0.45, "progressions": [
        {'chords': ['I', 'iv', 'I', 'iv'],       'label': 'Melodic Major Sorrow'},
        {'chords': ['I', 'V', 'vi', 'iv'],       'label': 'Bittersweet Epilogue'},
        {'chords': ['I', 'vi', 'ii', 'V'],       'label': 'Jazz Nostalgia'},
        {'chords': ['I', 'iii', 'vi', 'IV'],     'label': 'Wistful Reflection'},
        {'chords': ['I', 'bVI', 'bIII', 'bVII'], 'label': 'Cinematic Memories'},
        {'chords': ['I', 'vi', 'iii', 'IV'],     'label': 'Warm Regret'},
        {'chords': ['I', 'IV', 'iv', 'I'],       'label': 'Tears of Joy'},
        {'chords': ['I', 'bVI', 'IV', 'I'],      'label': 'Solitary Path'},
    ]},
}

# ── RHYTHM MATRICES ──────────────────────────────────────────────────────────
RHYTHM_LYRICAL = [
    (1.0, 0.45),
    (0.5, 0.35),
    (1.5, 0.10),
    (2.0, 0.08),
    (0.25, 0.02)
]

RHYTHM_SUSTAIN = [
    (2.0, 0.50),
    (4.0, 0.30),
    (1.0, 0.15),
    (1.5, 0.05)
]

def w_rhythm(pool, max_dur, t_bias=0.5):
    """Select a duration from pool based on weights, limited by max_dur."""
    fit = [p for p in pool if p[0] <= max_dur + 0.01]
    if not fit:
        return max_dur
    weights = []
    for dur, base_w in fit:
        # High tension biases toward faster rhythms
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
    """Generates simple transition probabilities to prioritize step-wise motion."""
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
    sc = sorted(list(set(scale)))
    pc = current_pc % 12
    if pc not in matrix:
        # Fallback to closest step
        if not sc: return 0
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
    """Build call-and-response map based on style tension."""
    lead_active = [True] * num_bars
    counter_active = [True] * num_bars
    if tension < 0.45:
        # Alternating call-and-response on low tension
        for i in range(num_bars):
            if i % 2 == 0:
                counter_active[i] = False
            else:
                lead_active[i] = False
    elif tension < 0.7:
        # Occasional breathing room
        for i in range(num_bars):
            if i % 4 == 3:
                counter_active[i] = False
            elif i % 4 == 1:
                lead_active[i] = False
    return lead_active, counter_active

def _lead_bar_directions(melody, num_bars):
    """Calculate overall melodic pitch movements per bar."""
    dirs = [0] * num_bars
    if not melody:
        return dirs
    tpb = 480
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

def generate_melody(root_note, progression, tension=0.5):
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
    return _generate_melody_core(root_note, bars_data, tension)

def _violin_pitch_in_shared_octave(root_note, offset):
    """Place a scale offset in the single octave shared by both violins."""
    return root_note + 36 + (offset % 12)

def _sounding_note_at_beat(events, target_beat):
    """Return the lead note sounding at an absolute beat position."""
    elapsed = 0.0
    for note, duration in events or []:
        if elapsed <= target_beat < elapsed + duration - 1e-9:
            return note
        elapsed += duration
    return None

def _choose_counter_pitch(root_note, chord_tones, scale, lead_pitch, previous_pitch,
                          lead_direction=0, strong=False):
    """Voice-lead a consonant counter note inside the lead violin's octave."""
    source = chord_tones if strong else list(dict.fromkeys(chord_tones + scale))
    candidates = [_violin_pitch_in_shared_octave(root_note, tone) for tone in source]
    consonances = {3, 4, 5, 7, 8, 9}

    def score(pitch):
        value = 7.0 if (pitch - root_note) % 12 in {t % 12 for t in chord_tones} else 0.0
        value -= abs(pitch - previous_pitch) * 0.8
        if lead_pitch is not None:
            interval = abs(pitch - lead_pitch)
            value += 13.0 if interval in consonances else -18.0
            if interval == 0:
                value -= 25.0
            # Prefer the counter below the lead, but permit graceful crossings.
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

def _generate_melody_core(root_note, bars_data, tension=0.5):
    """Lyrical top melody generator tuned for major environments."""
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
            if random.random() < 0.4:
                ct, sc = get_bar_harmony_at_beat(bar_harmony, 0.0)
                pitch = _violin_pitch_in_shared_octave(root_note, random.choice(ct))
                melody.append((pitch, 4.0))
            else:
                melody.append((None, 4.0))
            continue
            
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
                
            pitch = _violin_pitch_in_shared_octave(root_note, off)
                
            melody.append((pitch, dur))
            cur = off
            beat_pos += dur
            
    return melody

def generate_counter(root_note, progression, tension=0.5, lead_melody=None):
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
    return _generate_counter_core(root_note, bars_data, tension, lead_melody)

def _generate_counter_core(root_note, bars_data, tension=0.5, lead_melody=None):
    """Sustained counterpoint in the same octave as the lead violin."""
    counter = []
    previous_pitch = _violin_pitch_in_shared_octave(root_note, 4)
    _, counter_active = _activity_map(tension, len(bars_data))
    lead_dirs = _lead_bar_directions(lead_melody, len(bars_data)) if lead_melody else [0]*len(bars_data)
    
    for bar_idx, bar_harmony in enumerate(bars_data):
        if isinstance(bar_harmony, list):
            first_scale = bar_harmony[0][1]
        else:
            first_scale = bar_harmony[1]
            
        if not counter_active[bar_idx]:
            if random.random() < 0.3:
                ct, sc = get_bar_harmony_at_beat(bar_harmony, 0.0)
                lead_pitch = _sounding_note_at_beat(lead_melody, bar_idx * 4.0)
                pitch = _choose_counter_pitch(
                    root_note, ct, sc, lead_pitch, previous_pitch,
                    lead_dirs[bar_idx], strong=True
                )
                counter.append((pitch, 4.0))
                previous_pitch = pitch
            else:
                counter.append((None, 4.0))
            continue
            
        beats_left = 4.0
        beat_pos = 0.0
        while beats_left > 0.01:
            dur = w_rhythm(RHYTHM_SUSTAIN, beats_left, tension * 0.4)
            ct, sc = get_bar_harmony_at_beat(bar_harmony, beat_pos)
            absolute_beat = bar_idx * 4.0 + beat_pos
            lead_pitch = _sounding_note_at_beat(lead_melody, absolute_beat)
            pitch = _choose_counter_pitch(
                root_note, ct, sc, lead_pitch, previous_pitch,
                lead_dirs[bar_idx], strong=(beat_pos % 2.0 < 0.01)
            )
            counter.append((pitch, dur))
            previous_pitch = pitch
            beats_left -= dur
            beat_pos += dur
    return counter

def generate_driving_arpeggio(root_note, progression, tension=0.5):
    """Create a harmonically locked, phrase-shaped arpeggio ostinato.

    Strong subdivisions always use chord tones. Weak subdivisions may use a
    neighboring scale tone as an approach, then resolve immediately back into
    the active chord. Nearest-note voice leading and a rise/fall phrase contour
    keep the part emotional and melodic without competing with the lead.
    """
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

    step = 0.25 if tension >= 0.72 else 0.5
    steps_per_bar = int(round(4.0 / step))
    patterns = (
        [0, 1, 2, 1, 0, 2, 1, 2],
        [0, 2, 1, 2, 0, 1, 2, 1],
        [0, 1, 2, 3, 2, 1, 0, 2],
        [2, 1, 0, 1, 2, 1, 0, 1],
    )
    arp = []
    previous_pitch = root_note + 24

    def place_near(pc, target):
        candidates = [p for p in range(root_note + 22, root_note + 39) if p % 12 == (root_note + pc) % 12]
        return min(candidates, key=lambda p: abs(p - target))

    for bar_idx, bar_harmony in enumerate(bars_data):
        phrase_phase = bar_idx % 4
        pattern = patterns[phrase_phase]
        for step_idx in range(steps_per_bar):
            beat_pos = step_idx * step
            chord_tones, scale = get_bar_harmony_at_beat(bar_harmony, beat_pos)
            chord_tones = list(dict.fromkeys(chord_tones))
            pattern_pos = int(step_idx * 8 / steps_per_bar) % len(pattern)
            chord_index = pattern[pattern_pos] % len(chord_tones)
            offset = chord_tones[chord_index]

            # A restrained non-chord approach on weak eighth-note positions.
            weak_pulse = (step_idx % max(1, int(round(1.0 / step)))) != 0
            if weak_pulse and random.random() < 0.16 + tension * 0.16:
                scale_sorted = sorted(set(scale))
                chord_pc = offset % 12
                scale_index = min(range(len(scale_sorted)),
                                  key=lambda i: abs(scale_sorted[i] - chord_pc))
                direction = 1 if phrase_phase in (0, 2) else -1
                offset = scale_sorted[(scale_index + direction) % len(scale_sorted)]

            contour = (step_idx / max(1, steps_per_bar - 1))
            contour_shift = int(round((contour if phrase_phase in (0, 2) else 1.0 - contour) * 5))
            target = previous_pitch + max(-4, min(4, contour_shift - 2))
            pitch = place_near(offset, target)

            # Bar three is the emotional lift; bar four settles the phrase.
            if phrase_phase == 2 and step_idx >= steps_per_bar // 2 and pitch + 12 <= root_note + 40:
                pitch += 12
            elif phrase_phase == 3 and step_idx >= steps_per_bar - 2:
                root_pc = chord_tones[0]
                pitch = place_near(root_pc, root_note + 24)

            arp.append((pitch, step))
            previous_pitch = pitch

    return arp

# ── MIDI FILE ANALYSIS (Feature 2) ──────────────────────────────────────────

def build_midi(chords, melody, counter, base_tpb=480, bpm=DEFAULT_BPM, arpeggio=None):
    mid = mido.MidiFile()
    mid.ticks_per_beat = base_tpb
    tpb = base_tpb
    chord_dur = tpb * 4

    tr_meta = mido.MidiTrack(); mid.tracks.append(tr_meta)
    tr_ch = mido.MidiTrack(); mid.tracks.append(tr_ch)
    tr_mel = mido.MidiTrack(); mid.tracks.append(tr_mel)
    tr_cnt = mido.MidiTrack(); mid.tracks.append(tr_cnt)
    tr_arp = mido.MidiTrack(); mid.tracks.append(tr_arp)

    tr_meta.name = "Tempo & Meta"
    tr_ch.name = "Chord Pad"
    tr_mel.name = "Violin I - Lead Melody"
    tr_cnt.name = "Violin II - Counter Melody"
    tr_arp.name = "Driving Arpeggio Melody"

    tr_meta.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
    tr_meta.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
    tr_ch.append(mido.Message('program_change', program=89, channel=0, time=0))
    tr_mel.append(mido.Message('program_change', program=40, channel=1, time=0))
    tr_cnt.append(mido.Message('program_change', program=40, channel=2, time=0))
    tr_arp.append(mido.Message('program_change', program=81, channel=3, time=0))

    if chords:
        for bar_item in chords:
            if isinstance(bar_item, list) and bar_item and isinstance(bar_item[0], (list, tuple)):
                # Subdivided bar: list of (voicing, duration) tuples
                cum_time = 0
                for voicing, dur in bar_item:
                    c_dur = int(dur * tpb)
                    for n in voicing:
                        tr_ch.append(mido.Message('note_on', note=n, velocity=68, channel=0, time=cum_time))
                    for i, n in enumerate(voicing):
                        tr_ch.append(mido.Message('note_off', note=n, velocity=68, channel=0,
                                                  time=c_dur if i == 0 else 0))
                    cum_time = 0
            else:
                # Simple whole-bar voicing: list of ints
                for n in bar_item:
                    tr_ch.append(mido.Message('note_on', note=n, velocity=68, channel=0, time=0))
                for i, n in enumerate(bar_item):
                    tr_ch.append(mido.Message('note_off', note=n, velocity=68, channel=0,
                                              time=chord_dur if i == 0 else 0))

    # Lead melody: accented velocity (90), rests advance time
    rest_accum = 0
    for nv, db in melody:
        dt = max(1, int(db * tpb))
        if nv is None:
            rest_accum += dt
        else:
            tr_mel.append(mido.Message('note_on',  note=nv, velocity=90, channel=1, time=rest_accum))
            tr_mel.append(mido.Message('note_off', note=nv, velocity=90, channel=1, time=dt))
            rest_accum = 0

    # Counter-melody: soft supportive velocity (62), rests advance time
    rest_accum = 0
    for nv, db in counter:
        dt = max(1, int(db * tpb))
        if nv is None:
            rest_accum += dt
        else:
            tr_cnt.append(mido.Message('note_on',  note=nv, velocity=62, channel=2, time=rest_accum))
            tr_cnt.append(mido.Message('note_off', note=nv, velocity=62, channel=2, time=dt))
            rest_accum = 0

    if arpeggio:
        for note_index, (nv, db) in enumerate(arpeggio):
            dt = max(1, int(db * tpb))
            accent = note_index % max(1, int(round(1.0 / db))) == 0
            velocity = (82 if accent else 68) + random.randint(-4, 4)
            gate = max(1, int(dt * 0.82))
            tr_arp.append(mido.Message('note_on', note=nv, velocity=velocity, channel=3, time=0))
            tr_arp.append(mido.Message('note_off', note=nv, velocity=velocity, channel=3, time=gate))
            tr_arp.append(mido.Message('note_off', note=nv, velocity=0, channel=3, time=dt - gate))

    return mid

def _detect_scale(prog):
    if 'iv' in prog: return 'Melodic Major'
    if 'II' in prog: return 'Lydian'
    if 'bVII' in prog: return 'Mixolydian'
    return 'Natural Major (Ionian)'

def _again_or_back():
    print("  [G] Generate again    [B] Back to main menu")
    return input("  --> ").strip().lower() == 'g'

# ── EMOTIONAL STYLE CLUSTERS (Option 6) ─────────────────────────────────────
STYLE_CLUSTERS = {
    'A': {
        'names': ['uplifting', 'joyful', 'bright'],
        'tension': 0.35,
        'progressions': [
            {'chords': ['I', 'V', 'vi', 'IV'],       'label': 'Pop-Punk Anthem'},
            {'chords': ['I', 'IV', 'V', 'I'],        'label': 'Standard Cadence'},
            {'chords': ['I', 'IV', 'vi', 'V'],       'label': 'Optimistic Leap'},
            {'chords': ['I', 'vi', 'IV', 'V'],       'label': 'Classic 50s Stand-By'},
            {'chords': ['I', 'V', 'IV', 'V'],        'label': 'Driving Positivity'},
            {'chords': ['I', 'vi', 'ii', 'V'],       'label': 'Playful Stepwise'},
            {'chords': ['I', 'V', 'I', 'IV'],        'label': 'Bright Morning'},
            {'chords': ['I', 'IV', 'I', 'V'],        'label': 'Folksy Joy'},
        ]
    },
    'B': {
        'names': ['majestic', 'triumphant', 'heroic'],
        'tension': 0.65,
        'progressions': [
            {'chords': ['I', 'bVII', 'IV', 'I'],     'label': 'Mixolydian Rock Anthem'},
            {'chords': ['I', 'V', 'vi', 'iii', 'IV', 'I', 'IV', 'V'], 'label': 'Canon Heroic'},
            {'chords': ['I', 'IV', 'bVII', 'I'],     'label': 'Ascent to Glory'},
            {'chords': ['I', 'bIII', 'bVII', 'IV'],  'label': 'Epic Orchestral Lift'},
            {'chords': ['I', 'II', 'IV', 'I'],       'label': 'Lydian Rising'},
            {'chords': ['I', 'bVII', 'I', 'IV'],     'label': 'Royal Procession'},
            {'chords': ['I', 'V', 'IV', 'I'],        'label': 'Triumphant Call'},
            {'chords': ['I', 'bVI', 'bVII', 'I'],    'label': 'Fantasy Anthem'},
        ]
    },
    'C': {
        'names': ['serene', 'dreamy', 'ambient'],
        'tension': 0.25,
        'progressions': [
            {'chords': ['I', 'II', 'I', 'II'],       'label': 'Lydian Ethereal Cloud'},
            {'chords': ['Imaj7', 'IVmaj7', 'Imaj7', 'IVmaj7'], 'label': 'Celestial Float'},
            {'chords': ['I', 'IVmaj7', 'V', 'I'],    'label': 'Lush Meadow'},
            {'chords': ['I', 'bVII', 'I', 'bVII'],   'label': 'Mixolydian Drifting'},
            {'chords': ['I', 'iii', 'IV', 'V'],      'label': 'Peaceful River'},
            {'chords': ['I', 'vi', 'iii', 'IV'],     'label': 'Dreamy Reflection'},
            {'chords': ['Imaj7', 'II', 'IVmaj7', 'I'], 'label': 'Ambient Horizon'},
            {'chords': ['I', 'Imaj7', 'IV', 'IVmaj7'], 'label': 'Soft Morning Breeze'},
        ]
    },
    'D': {
        'names': ['nostalgic', 'bittersweet', 'reflective'],
        'tension': 0.45,
        'progressions': [
            {'chords': ['I', 'iv', 'I', 'iv'],       'label': 'Melodic Major Sorrow'},
            {'chords': ['I', 'V', 'vi', 'iv'],       'label': 'Bittersweet Epilogue'},
            {'chords': ['I', 'vi', 'ii', 'V'],       'label': 'Jazz Nostalgia'},
            {'chords': ['I', 'iii', 'vi', 'IV'],     'label': 'Wistful Reflection'},
            {'chords': ['I', 'bVI', 'bIII', 'bVII'], 'label': 'Cinematic Memories'},
            {'chords': ['I', 'vi', 'iii', 'IV'],     'label': 'Warm Regret'},
            {'chords': ['I', 'IV', 'iv', 'I'],       'label': 'Tears of Joy'},
            {'chords': ['I', 'bVI', 'IV', 'I'],      'label': 'Solitary Path'},
        ]
    },
}

STYLE_MAP = {}
for _ck, _cv in STYLE_CLUSTERS.items():
    for _sn in _cv['names']:
        STYLE_MAP[_sn] = _ck

def _div(char='-', w=62): print(char * w)

def _slug(text):
    keep = []
    for char in str(text):
        keep.append(char if char.isalnum() or char in "#+-" else "_")
    return "_".join(part for part in "".join(keep).split("_") if part)

def _project_title():
    return f"{random.choice(PROJECT_ADJECTIVES)}_{random.choice(PROJECT_NOUNS)}"

def _tempo_for_tension(tension):
    return random.randint(126, 142) if tension >= 0.65 else random.randint(108, 128)

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
    return f"{project_title}__Major_Engine_{mood_tag}__{style_tag}__{root_name}_{tonality}__{bpm}BPM__{prog_tag}"

_FLAVOUR = {
    frozenset(['A','B']): "Uplifting triumph -- high-energy joy and majestic victory.",
    frozenset(['A','C']): "Serene brightness -- peaceful joy like a sunny afternoon meadow.",
    frozenset(['A','D']): "Bittersweet happiness -- nostalgia with a warm, hopeful smile.",
    frozenset(['B','C']): "Majestic serenity -- magnificent and calm epic vistas.",
    frozenset(['B','D']): "Nostalgic grandeur -- sweet memories of epic achievements.",
    frozenset(['C','D']): "Dreamy nostalgia -- floating through beautiful memories.",
}
def _flavour(cs): return _FLAVOUR.get(frozenset(cs), "A beautiful blend of major scale emotional colors.")

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
        
        # Determine mode
        gen_mode = globals().get('GENERATION_MODE', 'simple')
        if gen_mode == 'decoupled':
            _, scale_tones = roman_numerals[prog[0]]
            full_prog = generate_decoupled_progression(tension, scale_tones)
            prog_display = "Double-Layer Decoupled Markov Walk"
        else:
            full_prog = [prog[i % len(prog)] for i in range(4)]
            prog_display = '-'.join(prog)
            
        print(f"\n  Family      :  {names}")
        print(f"  Key         :  {root_name} Major")
        print(f"  Style       :  {entry['label']}")
        print(f"  Progression :  {prog_display}")
        print(f"  Scale       :  {_detect_scale(prog)}")
        print(f"  Tension     :  [{tbar}] {int(tension*100)}%")
        print(f"  Gen Mode    :  {gen_mode.upper()}")

        _div('=')
        print("  Generating 4-Bar Loop...")
        chords  = generate_chords(root_val, full_prog)
        melody  = generate_melody(root_val, full_prog, tension)
        counter = generate_counter(root_val, full_prog, tension, lead_melody=melody)
        arpeggio = generate_driving_arpeggio(root_val, full_prog, tension)
        bpm     = _tempo_for_tension(tension)
        mid     = build_midi(chords, melody, counter, bpm=bpm, arpeggio=arpeggio)
        _save_midi(mid, _cinematic_fname(names, entry['label'], root_name, "Major", bpm, prog_display), out_dir)
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
        print(f"  Key         :  {root_name} Major")
        print(f"  Style       :  {entry['label']}")
        print(f"  Progression :  {prog_display}")
        print(f"  Scale       :  {_detect_scale(prog)}")
        print(f"  Tension     :  [{tbar}] {int(tension*100)}%")
        print(f"  Pool        :  {len(merged)} progressions available")
        print(f"  Gen Mode    :  {gen_mode.upper()}")

        _div('=')
        print("  Generating 4-Bar Loop...")
        chords  = generate_chords(root_val, full_prog)
        melody  = generate_melody(root_val, full_prog, tension)
        counter = generate_counter(root_val, full_prog, tension, lead_melody=melody)
        arpeggio = generate_driving_arpeggio(root_val, full_prog, tension)
        bpm = _tempo_for_tension(tension)
        mid = build_midi(chords, melody, counter, bpm=bpm, arpeggio=arpeggio)
        _save_midi(mid, _cinematic_fname(f"Blend {tag}", entry['label'], root_name, "Major", bpm, prog_display), out_dir)
        again = _again_or_back()

def parse_midi_chords(filepath):
    mid = mido.MidiFile(filepath)
    tpb = mid.ticks_per_beat
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
    collapsed = []
    prev = None
    for g in groups:
        t = tuple(g)
        if t != prev:
            collapsed.append(g)
            prev = t
    return collapsed, tpb

def detect_key(chord_groups):
    """Krumhansl-Schmuckler major key detection with Ionian, Lydian, and Mixolydian scaling."""
    pc_counts = [0] * 12
    for pcs in chord_groups:
        for pc in pcs:
            pc_counts[pc % 12] += 1
    best_score, best_root = -1e9, 0
    for root in range(12):
        profile = [KS_MAJOR[(i - root) % 12] for i in range(12)]
        score = sum(pc_counts[i] * profile[i] for i in range(12))
        if score > best_score:
            best_score, best_root = score, root
    root_name = ROOT_NAMES[best_root]
    
    # Check Lydian (sharp 4) vs Mixolydian (flat 7) vs Natural Major (Ionian)
    sharp4 = (best_root + 6) % 12
    flat7  = (best_root + 10) % 12
    nat4   = (best_root + 5) % 12
    maj7   = (best_root + 11) % 12
    
    if pc_counts[sharp4] > pc_counts[nat4]:
        return root_name, best_root, SCALE_LYDIAN, 'Lydian'
    elif pc_counts[flat7] > pc_counts[maj7]:
        return root_name, best_root, SCALE_MIXOLYDIAN, 'Mixolydian'
    return root_name, best_root, SCALE_IONIAN, 'Natural Major'

def generate_from_midi(filepath, out_dir):
    import VVC
    VVC.generate_quartet_over_midi(filepath, out_dir)

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
║             —  Major Scale Edition Engine  —               ║
║                                                            ║
║    Mood-Adaptive  |  Multi-Track  |  Major Phrasing        ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
    while True:
        n_blend = sum(len(c['progressions']) for c in STYLE_CLUSTERS.values())
        print(f"""  Select a compositional mode:
  ____________________________________________________________

   [ ── DIRECT GENERATION ── ]
     1  →  Emotion Family Selector
           Choose one of 4 major emotion families and generate a 4-bar loop

     2  →  Emotion Fusion Studio (Major)
           Combine multiple major-scale emotional profiles

     S  →  Surprise Me!
           Let the generator design a custom mood cocktail

   [ ── UTILITIES ── ]
     3  →  Melodic Overlayer (Quartet)
           Analyze MIDI file and build a custom 7-track string/piano overlay
  ____________________________________________________________
     0  →  Exit

  ({n_blend} blend pathways  |  21 quick progressions  |  12 major scales)
""")
        _div()
        choice = input("  --> ").strip().lower()
        _div('=')
        
        if choice == '0':
            print("  Exiting. Have a creative day!\n"); break
        elif choice == 's':
            print("  SURPRISE ME -- Generating a random emotion cocktail...\n")
            _run_blend(out_dir, surprise=True)
        elif choice == '1':
            print("  EMOTION FAMILY SELECTOR (Major)")
            print("  Pick an emotional world -- a random progression is chosen for you.\n")
            _FAMILY_KEYS = sorted(STYLE_CLUSTERS.keys())
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
                print("  [!] Enter 1-4 or B.")
        elif choice == '2':
            _run_blend(out_dir)
        elif choice == '3':
            print("\n  MELODIC OVERLAYER (Major Scale Mode)")
            _div()
            filepath = input("  Enter path to Major chord MIDI file: ").strip().replace('"','')
            if not os.path.exists(filepath):
                print("  [ERROR] File does not exist."); continue
            generate_from_midi(filepath, out_dir)
        else:
            print("  [!] Invalid -- enter 1-3, S or 0.\n")

if __name__ == '__main__':
    main()
