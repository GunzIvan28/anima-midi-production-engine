"""
CINEMATIC.PY — Modern Cinematic, Ethereal, & Action Trailer Engine
Generates professional, stem-based MIDI compositions focusing on Fantasy/Gothic,
Ethereal, and Epic Action moods. Features 4-bar progressions, dynamic track
allocation, and beautiful, touching chord progressions.
"""

import os
import random
import mido

# ── SCALES & KEYS ───────────────────────────────────────────────────────────
SCALE_AEOLIAN  = [0, 2, 3, 5, 7, 8, 10]
SCALE_HARMONIC = [0, 2, 3, 5, 7, 8, 11]
SCALE_DORIAN   = [0, 2, 3, 5, 7, 9, 10]
SCALE_PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]

ROOTS = {
    'C': 48, 'C#': 49, 'D': 50, 'Eb': 51, 'E': 52, 'F': 53,
    'F#': 54, 'G': 55, 'G#': 44, 'A': 45, 'Bb': 46, 'B': 47
}

# ── FULL CINEMATIC CHORD POOL ───────────────────────────────────────────────
# Roman numerals mapped to (chord_tones_relative_to_root, scale_degrees)
RN_ALL = {
    'i':   ([0, 3, 7], SCALE_AEOLIAN),
    'I':   ([0, 4, 7], SCALE_AEOLIAN),
    'ii°': ([2, 5, 8], SCALE_AEOLIAN),
    'ii':  ([2, 5, 9], SCALE_DORIAN),
    'II':  ([2, 6, 9], SCALE_AEOLIAN),
    'iii': ([3, 7, 10], SCALE_PHRYGIAN),
    'III': ([3, 7, 10], SCALE_AEOLIAN),
    'iv':  ([5, 8, 0], SCALE_AEOLIAN),
    'IV':  ([5, 9, 0], SCALE_DORIAN),
    'v':   ([7, 10, 2], SCALE_AEOLIAN),
    'V':   ([7, 11, 2], SCALE_HARMONIC),
    'VI':  ([8, 0, 3], SCALE_AEOLIAN),
    'vi':  ([9, 0, 4], SCALE_DORIAN),
    'vii°':([11, 2, 5], SCALE_HARMONIC),
    'VII': ([10, 2, 5], SCALE_AEOLIAN)
}

# ── MAJOR SCALES ─────────────────────────────────────────────────────────────
SCALE_IONIAN      = [0, 2, 4, 5, 7, 9, 11]  # Natural Major — bright, triumphant
SCALE_LYDIAN      = [0, 2, 4, 6, 7, 9, 11]  # Lydian — floating, wonder (raised 4th)
SCALE_MIXOLYDIAN  = [0, 2, 4, 5, 7, 9, 10]  # Mixolydian — anthemic, warm (flat 7th)
SCALE_MELODIC_MAJ = [0, 2, 4, 5, 7, 8, 10]  # Melodic Major — bittersweet (flat 6 & 7)

# ── MAJOR CHORD POOL ─────────────────────────────────────────────────────────
RN_MAJOR = {
    'I':      ([0, 4, 7],      SCALE_IONIAN),
    'Imaj7':  ([0, 4, 7, 11],  SCALE_IONIAN),
    'ii':     ([2, 5, 9],      SCALE_IONIAN),
    'iii':    ([4, 7, 11],     SCALE_IONIAN),
    'IV':     ([5, 9, 0],      SCALE_IONIAN),
    'IVmaj7': ([5, 9, 0, 4],   SCALE_LYDIAN),
    'V':      ([7, 11, 2],     SCALE_IONIAN),
    'V7':     ([7, 11, 2, 5],  SCALE_IONIAN),
    'vi':     ([9, 0, 4],      SCALE_IONIAN),
    'II':     ([2, 6, 9],      SCALE_LYDIAN),       # Lydian super-tonic major
    'bVII':   ([10, 2, 5],     SCALE_MIXOLYDIAN),   # Mixolydian flat-7
    'bVI':    ([8, 0, 3],      SCALE_MELODIC_MAJ),  # Borrowed flat-6
    'bIII':   ([3, 7, 10],     SCALE_MIXOLYDIAN),   # Borrowed flat-3
    'iv':     ([5, 8, 0],      SCALE_MELODIC_MAJ),  # Minor iv borrowing
}

# Authentic major cinematic progressions
CINEMATIC_MAJOR_PROGRESSIONS = [
    # Triumphant / Heroic (Ionian & Mixolydian)
    ['I', 'bVII', 'IV', 'I'],
    ['I', 'V', 'vi', 'IV'],
    ['I', 'IV', 'bVII', 'I'],
    ['I', 'bIII', 'bVII', 'IV'],
    ['I', 'V', 'IV', 'I'],
    ['I', 'bVI', 'bVII', 'I'],

    # Lydian Wonder (floating, magical, John-Williams style)
    ['I', 'II', 'I', 'V'],
    ['I', 'II', 'IV', 'I'],
    ['Imaj7', 'II', 'IVmaj7', 'I'],
    ['I', 'II', 'I', 'II'],
    ['I', 'iii', 'IV', 'V'],
    ['I', 'II', 'V', 'I'],

    # Mixolydian Anthem (warm, rock-epic, Game-of-Thrones feel)
    ['I', 'bVII', 'I', 'IV'],
    ['I', 'IV', 'I', 'bVII'],
    ['I', 'bVII', 'bVI', 'bVII'],
    ['I', 'V', 'bVII', 'IV'],
    ['I', 'IV', 'V', 'I'],
    ['I', 'bVII', 'IV', 'V'],

    # Bittersweet / Melodic Major / Nostalgic Cinematic
    ['I', 'vi', 'IV', 'V'],
    ['I', 'iv', 'I', 'V'],
    ['I', 'bVI', 'IV', 'I'],
    ['I', 'vi', 'ii', 'V'],
    ['I', 'IV', 'iv', 'I'],
    ['I', 'bVI', 'bIII', 'bVII'],
]

# Authentic progressions extracted directly from the cinematic sample packs
CINEMATIC_PROGRESSIONS = [
    # Kit 1 Style (Epic / Touching)
    ['i', 'III', 'VI', 'VII'],
    ['i', 'III', 'iv', 'VII'],
    ['i', 'III', 'iv', 'V'],
    ['i', 'VI', 'III', 'VII'],
    ['i', 'v', 'VI', 'III'],
    ['i', 'iv', 'VI', 'V'],
    
    # Kit 4 Style (Heroic / Action)
    ['VI', 'VII', 'i', 'v'],
    ['VI', 'VII', 'iv', 'V'],
    ['VI', 'VII', 'i', 'VII'],
    ['VI', 'III', 'iv', 'i'],
    ['VI', 'i', 'VII', 'i'],
    
    # Kit 2 Style (Ethereal / Fantasy / Gothic)
    ['i', 'VI', 'iv', 'V'],
    ['i', 'VII', 'VI', 'V'],
    ['i', 'VII', 'v', 'VI'],
    ['i', 'iv', 'III', 'VII'],
    ['i', 'v', 'VI', 'VII'],
    ['i', 'VI', 'i', 'VII'],
    
    # Dorian & Phrygian Modes (Exotic & Soaring)
    ['i', 'IV', 'VI', 'VII'],
    ['i', 'ii', 'v', 'i'],
    ['i', 'II', 'VI', 'VII'],
    ['i', 'v', 'iv', 'V'],
    ['i', 'IV', 'i', 'VII'],
    ['i', 'iv', 'v', 'VI'],
    ['i', 'v', 'i', 'V']
]

# ── PROCEDURAL GENERATORS ───────────────────────────────────────────────────

def _fit_to_register(pc, reg_min, reg_max):
    """Shift pitch class to fit within a specific MIDI register."""
    pitch = 60 + ((pc - 60) % 12)
    while pitch < reg_min: pitch += 12
    while pitch > reg_max: pitch -= 12
    return pitch

def generate_sub_bass(bars_data, root_val, tpb=480):
    """Deep foundation bass (MIDI 36-48). Sustained roots."""
    events = []
    for bar_idx, (ct, _) in enumerate(bars_data):
        tick_start = bar_idx * 4 * tpb
        dur_ticks = 4 * tpb
        
        root_pc = (root_val + ct[0]) % 12
        pitch = _fit_to_register(root_pc, 36, 48)
        
        events.append((tick_start, 'on', pitch, 100))
        events.append((tick_start + dur_ticks - 10, 'off', pitch, 0))
    return events

def generate_drone(bars_data, root_val, tpb=480):
    """Piercing high tension drone (MIDI 84-96)."""
    events = []
    pitch = _fit_to_register(root_val, 84, 96)
    dur_ticks = len(bars_data) * 4 * tpb
    events.append((0, 'on', pitch, 70))
    events.append((dur_ticks - 10, 'off', pitch, 0))
    return events

def _nearest_choir_pitch(pc, register, prev_pitch=None):
    """Resolves a pitch class to the nearest candidate in a given register."""
    candidates = [p for p in range(register['min'], register['max'] + 1) if p % 12 == pc % 12]
    if not candidates:
        return register['center']
    target = prev_pitch if prev_pitch is not None else register['center']
    return min(candidates, key=lambda p: abs(p - target))

def _choose_best_voice_pitch(ct_pcs, register, prev_pitch=None):
    """Selects the chord tone that allows the voice to move by the smallest possible interval."""
    candidates = []
    for pc in ct_pcs:
        p = _nearest_choir_pitch(pc, register, prev_pitch)
        candidates.append(p)
    if not candidates:
        return register['center']
    if prev_pitch is not None:
        return min(candidates, key=lambda p: abs(p - prev_pitch))
    return min(candidates, key=lambda p: abs(p - register['center']))

def generate_choir_satb(bars_data, root_val, tpb=480):
    """
    Generates realistic SATB choir parts using nearest-pitch voice leading,
    natural timing/staggering, breathing release offsets, and individual voice tracks.
    """
    CHOIR_REGISTERS = {
        'soprano': {'min': 65, 'max': 77, 'center': 71},
        'alto':    {'min': 59, 'max': 71, 'center': 65},
        'tenor':   {'min': 53, 'max': 65, 'center': 59},
        'bass':    {'min': 43, 'max': 55, 'center': 49}
    }
    
    voices = ['bass', 'tenor', 'alto', 'soprano']
    events = {v: [] for v in voices}
    prev = {v: None for v in voices}
    
    for bar_idx, (ct, _) in enumerate(bars_data):
        bar_start = bar_idx * 4 * tpb
        ct_pcs = [(root_val + offset) % 12 for offset in ct]
        
        # 1. Determine pitches for each voice in this bar
        pitches = {}
        
        # Bass always plays the root
        bass_pc = ct_pcs[0]
        pitches['bass'] = _nearest_choir_pitch(bass_pc, CHOIR_REGISTERS['bass'], prev['bass'])
        
        # Other voices do smooth voice leading
        for voice in ['tenor', 'alto', 'soprano']:
            pitches[voice] = _choose_best_voice_pitch(ct_pcs, CHOIR_REGISTERS[voice], prev[voice])
            
        # 2. Add notes with timing staggering and breathing
        for voice in voices:
            pitch = pitches[voice]
            prev[voice] = pitch
            
            # Stagger note-on entry (0 to 18 ticks) for human feel
            entry_delay = random.randint(0, 18)
            tick_on = bar_start + entry_delay
            
            # Breathing space: release notes early (35 to 80 ticks) before the bar end
            breath_offset = random.randint(35, 80)
            dur_ticks = int(4 * tpb * 1.05) - entry_delay - breath_offset
            tick_off = tick_on + dur_ticks
            
            # Velocity: soft/ethereal choir (around 58-68)
            vel = random.randint(58, 68)
            
            events[voice].append((tick_on, 'on', pitch, vel))
            events[voice].append((tick_off, 'off', pitch, 0))
            
    return events

def generate_staccato_ostinato(bars_data, root_val, bpm, tpb=480):
    """Dynamic, sleek rhythmic ostinato varying by bar and beat."""
    events = []
    
    # Define a pool of sleek 1-beat rhythmic cells
    # Format: (offset, duration, chord_tone_index)
    cell_driving = [(0.0, 0.25, 0), (0.25, 0.25, 1), (0.5, 0.25, 2), (0.75, 0.25, 1)]
    cell_gallop  = [(0.0, 0.5, 0), (0.5, 0.25, 1), (0.75, 0.25, 0)]
    cell_sync    = [(0.0, 0.25, 0), (0.25, 0.5, 2), (0.75, 0.25, 1)]
    cell_pedal   = [(0.0, 0.25, 0), (0.25, 0.25, 0), (0.5, 0.25, 0), (0.75, 0.25, 0)]
    
    for bar_idx, (ct, _) in enumerate(bars_data):
        bar_start = bar_idx * 4 * tpb
        
        for beat in range(4):
            # Dynamically select cell based on the beat to create sleek, breathing motion
            if beat == 0:
                cell = cell_driving
            elif beat == 1:
                cell = cell_gallop if random.random() > 0.5 else cell_driving
            elif beat == 2:
                cell = cell_sync
            else:
                cell = cell_pedal if bar_idx % 2 == 0 else cell_driving
                
            for offset, dur, ct_idx in cell:
                tick = bar_start + int(beat * tpb) + int(offset * tpb)
                dur_ticks = int(dur * tpb)
                
                pc = (root_val + ct[ct_idx % len(ct)]) % 12
                pitch = _fit_to_register(pc, 55, 72)
                
                # Dynamic velocity for sleekness
                if offset == 0.0:
                    vel = random.randint(105, 115) # Downbeat accent
                elif offset == 0.5:
                    vel = random.randint(95, 105)  # Upbeat accent
                else:
                    vel = random.randint(75, 85)   # Soft 16ths
                    
                events.append((tick, 'on', pitch, vel))
                events.append((tick + max(1, dur_ticks - 5), 'off', pitch, 0))
    return events

def generate_harp_arpeggios(bars_data, root_val, tpb=480):
    """Cascading 16th note fingerpicked arpeggios crossing octaves (MIDI 60-84)."""
    events = []
    pattern = [
        (0.0, 0, 0), (0.25, 1, 0), (0.5, 2, 0), (0.75, 0, 1),
        (1.0, 1, 1), (1.25, 0, 1), (1.5, 2, 0), (1.75, 1, 0)
    ]
    for bar_idx, (ct, _) in enumerate(bars_data):
        bar_start = bar_idx * 4 * tpb
        for half_bar in range(2): 
            start_tick = bar_start + half_bar * 2 * tpb
            for offset, ct_idx, octave_shift in pattern:
                tick = start_tick + int(offset * tpb)
                dur_ticks = int(0.25 * tpb)
                
                pc = (root_val + ct[ct_idx % len(ct)]) % 12
                base_pitch = _fit_to_register(pc, 55, 67)
                pitch = base_pitch + (octave_shift * 12)
                
                vel = random.randint(70, 95)
                events.append((tick, 'on', pitch, vel))
                events.append((tick + dur_ticks - 5, 'off', pitch, 0))
    return events

def generate_heavy_brass(bars_data, root_val, tpb=480):
    """Epic low brass sustains and stabs (MIDI 41-55)."""
    events = []
    for bar_idx, (ct, _) in enumerate(bars_data):
        tick_start = bar_idx * 4 * tpb
        
        root_pc = (root_val + ct[0]) % 12
        fifth_pc = (root_val + ct[2 % len(ct)]) % 12
        
        p1 = _fit_to_register(root_pc, 41, 53)
        p2 = _fit_to_register(fifth_pc, 48, 60)
        
        for beat in [0, 2]:
            t = tick_start + beat * tpb
            dur = tpb - 20
            events.append((t, 'on', p1, 120))
            events.append((t, 'on', p2, 110))
            events.append((t + dur, 'off', p1, 0))
            events.append((t + dur, 'off', p2, 0))
    return events

def generate_piano_melody(bars_data, root_val, tpb=480):
    """Sparse, touching, sweet high piano melody (MIDI 72-84)."""
    events = []
    for bar_idx, (ct, sc) in enumerate(bars_data):
        bar_start = bar_idx * 4 * tpb
        
        pc1 = (root_val + ct[1 % len(ct)]) % 12
        p1 = _fit_to_register(pc1, 72, 84)
        events.append((bar_start, 'on', p1, 75))
        events.append((bar_start + 2*tpb, 'off', p1, 0))
        
        if random.random() < 0.6:
            pc2 = (root_val + random.choice(sc)) % 12
            p2 = _fit_to_register(pc2, 72, 84)
            events.append((bar_start + 2*tpb, 'on', p2, 65))
            events.append((bar_start + 4*tpb, 'off', p2, 0))
            
    return events

def get_chord_tones_in_window(ct_raw, root_val, w_min, w_max):
    """Extract all chord tones of the current chord mapped to the octave window."""
    tones = []
    for offset in ct_raw:
        pc = (root_val + offset) % 12
        p = w_min + ((pc - w_min) % 12)
        while p <= w_max:
            tones.append(p)
            p += 12
    return sorted(list(set(tones)))

def get_scale_tones_in_window(scale_deg, root_val, w_min, w_max):
    """Extract all scale degrees of the current key/scale mapped to the octave window."""
    tones = []
    for deg in scale_deg:
        pc = (root_val + deg) % 12
        p = w_min + ((pc - w_min) % 12)
        while p <= w_max:
            tones.append(p)
            p += 12
    return sorted(list(set(tones)))

def generate_melody_pitches(bars_data, root_val):
    """Uses DFS search with backtracking and fallbacks to generate melody pitches matching constraints."""
    octave_min = root_val + 12
    octave_max = root_val + 24
    
    bar_ct = []
    bar_st = []
    for ct_raw, scale_deg in bars_data:
        ct = get_chord_tones_in_window(ct_raw, root_val, octave_min, octave_max)
        st = get_scale_tones_in_window(scale_deg, root_val, octave_min, octave_max)
        bar_ct.append(ct)
        bar_st.append(st)
        
    note_to_bar = [0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3]
    # 9 chord tones, 4 scale tones (mostly chord tones)
    is_ct = [True, False, True, True, False, True, True, False, True, True, True, False, True]
    
    # 6 fallback levels to ensure a solution is always found:
    for level in range(6):
        solutions = []
        
        def dfs(index, current_path, leap_count):
            if len(solutions) >= 50:
                return
            
            # Prune early to save search time:
            # Check contour of A (first vs second bar) as soon as index 6 is reached
            if index == 6:
                # Require at least 2 distinct notes in the core 3-note idea (Phrase A)
                if len(set(current_path[0:3])) < 2:
                    return
                
                sign_A1 = 1 if current_path[1] > current_path[0] else (-1 if current_path[1] < current_path[0] else 0)
                sign_A2 = 1 if current_path[2] > current_path[1] else (-1 if current_path[2] < current_path[1] else 0)
                sign_A_bar2_1 = 1 if current_path[4] > current_path[3] else (-1 if current_path[4] < current_path[3] else 0)
                sign_A_bar2_2 = 1 if current_path[5] > current_path[4] else (-1 if current_path[5] < current_path[4] else 0)
                if sign_A1 != sign_A_bar2_1 or sign_A2 != sign_A_bar2_2:
                    return
            
            if index == 13:
                # 1. Check leaps
                if level < 4:
                    if leap_count != 1:
                        return
                else:
                    if leap_count == 0:
                        return
                
                # 2. Check within one octave
                if max(current_path) - min(current_path) > 12:
                    return
                
                # 3. Check contour of A' (level 0 requires match)
                sign_A1 = 1 if current_path[1] > current_path[0] else (-1 if current_path[1] < current_path[0] else 0)
                sign_A2 = 1 if current_path[2] > current_path[1] else (-1 if current_path[2] < current_path[1] else 0)
                if level == 0:
                    sign_A_prime1 = 1 if current_path[11] > current_path[10] else (-1 if current_path[11] < current_path[10] else 0)
                    sign_A_prime2 = 1 if current_path[12] > current_path[11] else (-1 if current_path[12] < current_path[11] else 0)
                    if sign_A_prime1 != sign_A1 or sign_A_prime2 != sign_A2:
                        return
                
                # 4. Check climax uniqueness and position
                max_pitch = max(current_path)
                max_count = current_path.count(max_pitch)
                if level < 2:
                    if max_count != 1:
                        return
                else:
                    if max_count > 2:
                        return
                
                climax_index = current_path.index(max_pitch)
                if level < 3:
                    if climax_index < 6: # must be in bar 3 or 4
                        return
                else:
                    if climax_index < 3: # must be in bar 2, 3 or 4
                        return
                
                solutions.append(current_path.copy())
                return
            
            b = note_to_bar[index]
            cands = list(bar_ct[b] if is_ct[index] else bar_st[b])
            
            # Shuffle candidates for diversity and randomized DFS paths
            random.shuffle(cands)
            
            for p in cands:
                if index == 0:
                    dfs(index + 1, current_path + [p], 0)
                else:
                    prev_p = current_path[-1]
                    interval = abs(p - prev_p)
                    
                    if interval in (5, 7, 8, 12):
                        dfs(index + 1, current_path + [p], leap_count + 1)
                    elif interval in (0, 1, 2, 3, 4):
                        dfs(index + 1, current_path + [p], leap_count)
                        
        dfs(0, [], 0)
        if solutions:
            return random.choice(solutions)
            
    # Absolute fallback: construct a simple arpeggio/scale
    fallback_path = []
    for k in range(13):
        b = note_to_bar[k]
        ct = bar_ct[b]
        fallback_path.append(ct[k % len(ct)])
    return fallback_path

def generate_melody(bars_data, root_val, tpb=480):
    """
    Generates a 4-bar vocal-like melody (Violin/Piano/Theremin)
    staying within 1 octave, containing 1 defining leap,
    A-A-B-A' structure, and a unique climax note.
    """
    pitches = generate_melody_pitches(bars_data, root_val)
    
    # Note timings: (bar_index, beat_offset, beat_duration)
    note_timing = [
        # Bar 1 (A)
        (0, 0.0, 1.0), (0, 1.0, 1.0), (0, 2.0, 2.0),
        # Bar 2 (A)
        (1, 0.0, 1.0), (1, 1.0, 1.0), (1, 2.0, 2.0),
        # Bar 3 (B)
        (2, 0.0, 1.0), (2, 1.0, 1.0), (2, 2.0, 1.0), (2, 3.0, 1.0),
        # Bar 4 (A')
        (3, 0.0, 1.0), (3, 1.0, 1.0), (3, 2.0, 2.0)
    ]
    
    max_p = max(pitches)
    climax_idx = pitches.index(max_p)
    
    events = []
    for k, p in enumerate(pitches):
        bar_idx, beat_offset, beat_duration = note_timing[k]
        
        tick_start = bar_idx * 4 * tpb + int(beat_offset * tpb)
        dur_ticks = int(beat_duration * tpb)
        
        # Expressive velocity
        if k == climax_idx:
            vel = 118  # Strong climax accent
        elif beat_offset == 0.0:
            vel = 105  # Downbeat accent
        else:
            vel = random.randint(85, 95)
            
        events.append((tick_start, 'on', p, vel))
        events.append((tick_start + dur_ticks - 10, 'off', p, 0))
        
    return events

# ── MAJOR-SPECIFIC GENERATORS ────────────────────────────────────────────────

def generate_brass_fanfare(bars_data, root_val, tpb=480):
    """
    Triumphant major brass fanfare — punchy dotted-quarter + eighth hits
    on beats 1 and 3, voiced in root + major 3rd + 5th (MIDI 53-72).
    """
    events = []
    for bar_idx, (ct, _) in enumerate(bars_data):
        tick_start = bar_idx * 4 * tpb
        root_pc  = (root_val + ct[0]) % 12
        third_pc = (root_val + ct[1 % len(ct)]) % 12
        fifth_pc = (root_val + ct[2 % len(ct)]) % 12

        p_root  = _fit_to_register(root_pc,  53, 65)
        p_third = _fit_to_register(third_pc, 57, 69)
        p_fifth = _fit_to_register(fifth_pc, 60, 72)

        for beat in [0, 2]:
            t   = tick_start + beat * tpb
            dur = int(tpb * 1.5) - 15   # dotted quarter
            for note, vel in [(p_root, 118), (p_third, 108), (p_fifth, 112)]:
                events.append((t, 'on',  note, vel))
                events.append((t + dur, 'off', note, 0))
            # Answering eighth on the half-beat after
            t2 = t + int(tpb * 0.75)
            events.append((t2, 'on',  p_fifth, 95))
            events.append((t2 + int(tpb * 0.25) - 8, 'off', p_fifth, 0))
    return events

def generate_celesta_arpeggios(bars_data, root_val, tpb=480):
    """
    Celestial Lydian celesta sparkle — fast ascending arpeggio in the upper
    register (MIDI 72-90), soft velocity, 16th-note triplet feel.
    """
    events = []
    pattern_offsets = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75]
    for bar_idx, (ct, _) in enumerate(bars_data):
        bar_start = bar_idx * 4 * tpb
        # Build a 3-note upper arpeggio: root, third, fifth one octave up
        pitches_in_bar = []
        for offset in ct:
            pc = (root_val + offset) % 12
            p  = _fit_to_register(pc, 72, 84)
            pitches_in_bar.append(p)
            pitches_in_bar.append(p + 12)   # add upper octave for shimmer
        pitches_in_bar = sorted(set(p for p in pitches_in_bar if p <= 90))

        for half in range(2):
            start = bar_start + half * 2 * tpb
            for i, beat_off in enumerate(pattern_offsets):
                tick     = start + int(beat_off * tpb)
                dur      = int(0.24 * tpb)
                pitch    = pitches_in_bar[i % len(pitches_in_bar)]
                vel      = random.randint(52, 65)
                events.append((tick, 'on',  pitch, vel))
                events.append((tick + dur, 'off', pitch, 0))
    return events

def generate_woodwind_lead(bars_data, root_val, tpb=480):
    """
    Warm pastoral woodwind melody — one lyrical note per half-bar in the
    mid-high register (MIDI 65-79), soft-attack feel.
    """
    events = []
    prev_pitch = None
    for bar_idx, (ct, sc) in enumerate(bars_data):
        bar_start = bar_idx * 4 * tpb
        # Two half-bar notes per bar for a flowing melodic line
        for half in range(2):
            tick_on = bar_start + half * 2 * tpb + random.randint(0, 12)
            dur     = 2 * tpb - random.randint(30, 60)

            # Prefer scale tones; pick the one closest to prev pitch
            candidates = []
            for deg in sc:
                pc = (root_val + deg) % 12
                p  = _fit_to_register(pc, 65, 79)
                candidates.append(p)
            candidates = sorted(set(candidates))
            if prev_pitch is not None:
                pitch = min(candidates, key=lambda p: abs(p - prev_pitch))
            else:
                pitch = random.choice(candidates)
            prev_pitch = pitch

            vel = random.randint(68, 82)
            events.append((tick_on, 'on',  pitch, vel))
            events.append((tick_on + dur, 'off', pitch, 0))
    return events

# ── MIDI ASSEMBLY ───────────────────────────────────────────────────────────

def build_track(mid, name, program, channel, events, tpb=480):
    track = mido.MidiTrack()
    track.name = name
    mid.tracks.append(track)
    
    track.append(mido.Message('program_change', program=program, channel=channel, time=0))
    
    events.sort(key=lambda e: e[0])
    
    current_tick = 0
    for ev in events:
        tick = ev[0]
        msg_type = ev[1]
        note = ev[2]
        vel = ev[3]
        
        delta = max(0, tick - current_tick)
        if msg_type == 'on':
            track.append(mido.Message('note_on', note=note, velocity=vel, channel=channel, time=delta))
        else:
            track.append(mido.Message('note_off', note=note, velocity=0, channel=channel, time=delta))
        current_tick = tick

def compose_cinematic_track(mood_id, bpm, root_name, root_val):
    """
    Generates a 4-bar MIDI object dynamically composed of different tracks
    depending on the selected mood.
    """
    tpb = 480
    mid = mido.MidiFile(ticks_per_beat=tpb)
    
    # Setup Tempo Track
    tempo_track = mido.MidiTrack()
    tempo_track.name = "Tempo & Meta"
    mid.tracks.append(tempo_track)
    tempo_track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
    tempo_track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
    
    # Select Progression
    prog_raw = random.choice(CINEMATIC_PROGRESSIONS)
    
    bars_data = []
    for rn in prog_raw:
        ct_raw, scale = RN_ALL[rn]
        bars_data.append((ct_raw, scale))
        
    prog_label = "-".join(prog_raw)
        
    # Generate common foundation tracks
    sub_bass = generate_sub_bass(bars_data, root_val, tpb)
    staccato = generate_staccato_ostinato(bars_data, root_val, bpm, tpb)
    drone    = generate_drone(bars_data, root_val, tpb)
    melody   = generate_melody(bars_data, root_val, tpb)
    
    ch = 0
    build_track(mid, "Sub Bass", 43, ch, sub_bass); ch += 1
    build_track(mid, "High Drone", 48, ch, drone); ch += 1
    build_track(mid, "Staccato Strings", 48, ch, staccato); ch += 1
    build_track(mid, "Melody", 40, ch, melody); ch += 1
    
    # Generate Mood-Specific Tracks
    if mood_id == 1:
        # Ethereal Gothic Fantasy: Choir, Harp, Piano
        mood_name = "Ethereal Gothic Fantasy"
        choir_satb = generate_choir_satb(bars_data, root_val, tpb)
        harp  = generate_harp_arpeggios(bars_data, root_val, tpb)
        piano = generate_piano_melody(bars_data, root_val, tpb)
        
        for voice in ['bass', 'tenor', 'alto', 'soprano']:
            build_track(mid, f"Choir - {voice.capitalize()}", 52, ch, choir_satb[voice]); ch += 1
        build_track(mid, "Harp / Nylon Arps", 46, ch, harp); ch += 1
        build_track(mid, "Piano Melody", 0, ch, piano); ch += 1
        
    elif mood_id == 2:
        # Epic Heroic Action: Heavy Brass, Choir
        mood_name = "Epic Heroic Action"
        brass = generate_heavy_brass(bars_data, root_val, tpb)
        choir_satb = generate_choir_satb(bars_data, root_val, tpb)
        
        build_track(mid, "Heavy Brass", 61, ch, brass); ch += 1
        for voice in ['bass', 'tenor', 'alto', 'soprano']:
            build_track(mid, f"Choir - {voice.capitalize()}", 52, ch, choir_satb[voice]); ch += 1
        
    else:
        # Dark Assassin Stealth: Harp/Guitar, Sparse Piano
        mood_name = "Dark Assassin Stealth"
        harp  = generate_harp_arpeggios(bars_data, root_val, tpb)
        piano = generate_piano_melody(bars_data, root_val, tpb)
        
        build_track(mid, "Nylon Guitars", 24, ch, harp); ch += 1
        build_track(mid, "Dark Piano", 0, ch, piano); ch += 1
        
    return mid, mood_name, prog_label

def compose_cinematic_major_track(mood_id, bpm, root_name, root_val):
    """
    Generates a 4-bar major-key cinematic MIDI.
    Track counts mirror the minor engine exactly:
      Mood 1 (Triumphant Ascent)  — 10 tracks
      Mood 2 (Celestial Wonder)   —  9 tracks
      Mood 3 (Golden Pastoral)    —  6 tracks
    """
    tpb = 480
    mid = mido.MidiFile(ticks_per_beat=tpb)

    # Tempo track
    tempo_track = mido.MidiTrack()
    tempo_track.name = "Tempo & Meta"
    mid.tracks.append(tempo_track)
    tempo_track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
    tempo_track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))

    # Select a major progression
    prog_raw  = random.choice(CINEMATIC_MAJOR_PROGRESSIONS)
    bars_data = []
    for rn in prog_raw:
        ct_raw, scale = RN_MAJOR[rn]
        bars_data.append((ct_raw, scale))
    prog_label = "-".join(prog_raw)

    # ── Foundation tracks (all moods, same as minor engine) ──────────────────
    sub_bass = generate_sub_bass(bars_data, root_val, tpb)
    staccato = generate_staccato_ostinato(bars_data, root_val, bpm, tpb)
    drone    = generate_drone(bars_data, root_val, tpb)
    melody   = generate_melody(bars_data, root_val, tpb)   # DFS adapts to major ct

    ch = 0
    build_track(mid, "Sub Bass",        43, ch, sub_bass); ch += 1
    build_track(mid, "High Drone",      48, ch, drone);    ch += 1
    build_track(mid, "Staccato Strings",48, ch, staccato); ch += 1
    build_track(mid, "Melody",          40, ch, melody);   ch += 1

    # ── Mood-specific tracks ─────────────────────────────────────────────────
    if mood_id == 1:
        # Triumphant Ascent: Brass Fanfare + SATB Choir + Piano  (10 tracks)
        mood_name  = "Triumphant Ascent"
        brass      = generate_brass_fanfare(bars_data, root_val, tpb)
        choir_satb = generate_choir_satb(bars_data, root_val, tpb)
        piano      = generate_piano_melody(bars_data, root_val, tpb)

        build_track(mid, "Brass Fanfare", 61, ch, brass); ch += 1
        for voice in ['bass', 'tenor', 'alto', 'soprano']:
            build_track(mid, f"Choir - {voice.capitalize()}", 52, ch, choir_satb[voice]); ch += 1
        build_track(mid, "Piano Melody", 0, ch, piano); ch += 1

    elif mood_id == 2:
        # Celestial Wonder: Celesta Arps + SATB Choir  (9 tracks)
        mood_name  = "Celestial Wonder"
        celesta    = generate_celesta_arpeggios(bars_data, root_val, tpb)
        choir_satb = generate_choir_satb(bars_data, root_val, tpb)

        build_track(mid, "Celesta Arps", 8, ch, celesta); ch += 1   # GM 8 = Celesta
        for voice in ['bass', 'tenor', 'alto', 'soprano']:
            build_track(mid, f"Choir - {voice.capitalize()}", 52, ch, choir_satb[voice]); ch += 1

    else:
        # Golden Pastoral: Harp Arps + Woodwind Lead  (6 tracks)
        mood_name = "Golden Pastoral"
        harp      = generate_harp_arpeggios(bars_data, root_val, tpb)
        woodwind  = generate_woodwind_lead(bars_data, root_val, tpb)

        build_track(mid, "Pastoral Harp",   46, ch, harp);     ch += 1  # GM 46 = Harp
        build_track(mid, "Woodwind Lead",   73, ch, woodwind); ch += 1  # GM 73 = Flute

    return mid, mood_name, prog_label

# ── CLI APPLICATION ─────────────────────────────────────────────────────────

def main(out_dir='midi_files'):
    print("""
  ╔════════════════════════════════════════════════════════════╗
  ║    M O D E R N   C I N E M A T I C   T R A I L E R         ║
  ║    Ethereal · Gothic · Heroic · Lydian · Pastoral          ║
  ╚════════════════════════════════════════════════════════════╝
    """)

    # ── Word pools for evocative procedural project titles ──────────────────
    ADJECTIVES = [
        "Apex", "Infinite", "Midnight", "Titan", "Solar", "Gothic", "Ethereal", "Grim", "Silent",
        "Shadow", "Crimson", "Nebula", "Spectral", "Cosmic", "Lost", "Fallen", "Eternal", "Frozen",
        "Abyssal", "Radiant", "Iron", "Storm", "Phoenix", "Astral", "Mystic", "Ancient", "Vortex"
    ]
    NOUNS = [
        "Ascent", "Requiem", "Odyssey", "Eclipse", "Horizon", "Empire", "Sanctuary", "Vanguard",
        "Echo", "Whisper", "Rift", "Conquest", "Genesis", "Destiny", "Void", "Valhalla", "Covenant",
        "Chronicle", "Legacy", "Bastion", "Rebirth", "Summit", "Oracle", "Wasteland", "Mirage"
    ]

    ENHARMONICS = {
        'Db': 'C#', 'D#': 'Eb', 'Gb': 'F#', 'A#': 'Bb', 'Ab': 'G#',
    }

    # ── 1. Choose tonality ───────────────────────────────────────────────────
    print("  Select Tonality:")
    print("    1 -> Minor (Dark, Gothic, Ethereal, Action)")
    print("    2 -> Major (Triumphant, Celestial, Pastoral)")
    tonality_str = input("  --> ").strip()
    is_major = (tonality_str == '2')

    # ── 2. Choose mood ───────────────────────────────────────────────────────
    if is_major:
        print("\n  Select Major Cinematic Mood:")
        print("    1 -> Triumphant Ascent  (Full brass fanfare, SATB choir, piano — 10 tracks)")
        print("    2 -> Celestial Wonder   (Lydian celesta arps, SATB choir         —  9 tracks)")
        print("    3 -> Golden Pastoral    (Pastoral harp, flute woodwind            —  6 tracks)")
    else:
        print("\n  Select Minor Cinematic Mood:")
        print("    1 -> Ethereal Gothic Fantasy (Harps, SATB choir, piano    — 10 tracks)")
        print("    2 -> Epic Heroic Action      (Heavy brass, SATB choir     —  9 tracks)")
        print("    3 -> Dark Assassin Stealth   (Nylon guitars, dark piano   —  6 tracks)")
    mood_str = input("  --> ").strip()
    mood_id  = int(mood_str) if mood_str in ('1', '2', '3') else 1

    # ── 3. Choose key ────────────────────────────────────────────────────────
    available_keys = sorted(list(ROOTS.keys()))
    tonality_label = "Major" if is_major else "Minor"
    print(f"\n  Select {tonality_label} Key (Available: {', '.join(available_keys)}):")
    root_name_raw = input("  --> ").strip()

    if len(root_name_raw) >= 1:
        root_name = root_name_raw[0].upper() + root_name_raw[1:]
    else:
        root_name = 'C' if is_major else 'D'

    if root_name in ENHARMONICS:
        root_name = ENHARMONICS[root_name]
    if root_name not in ROOTS:
        root_name = 'C' if is_major else 'D'

    root_val = ROOTS[root_name]

    # ── 4. Tempo ─────────────────────────────────────────────────────────────
    print("\n  Select Tempo (BPM) [e.g. 100, 120, 140]:")
    bpm_str = input("  --> ").strip()
    try:
        bpm = int(bpm_str)
    except ValueError:
        bpm = 120 if is_major else 110

    # ── 5. Generate ──────────────────────────────────────────────────────────
    print("\n  [GENERATING] Composing 4-bar cinematic arrangement...")
    if is_major:
        mid, mood_name, prog_label = compose_cinematic_major_track(mood_id, bpm, root_name, root_val)
    else:
        mid, mood_name, prog_label = compose_cinematic_track(mood_id, bpm, root_name, root_val)

    project_title = f"{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}"
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
    print(f"  [SUCCESS] Generated {len(mid.tracks)-1} dynamic tracks!")
    print(f"  [SAVED]   {os.path.basename(fpath)}")
    print(f"  [PATH]    {fpath}\n")

if __name__ == '__main__':
    main()
