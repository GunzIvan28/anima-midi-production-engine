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
    'F#': 54, 'G': 55, 'G#': 56, 'A': 57, 'Bb': 58, 'B': 59
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

def _nearest_short_string_pitch(pc, prev_pitch=None, reg_min=55, reg_max=72):
    """Resolve a pitch class into a tight professional short-string register."""
    candidates = [p for p in range(reg_min, reg_max + 1) if p % 12 == pc % 12]
    if not candidates:
        return _fit_to_register(pc, reg_min, reg_max)
    target = prev_pitch if prev_pitch is not None else (reg_min + reg_max) // 2
    return min(candidates, key=lambda p: (abs(p - target), abs(p - ((reg_min + reg_max) // 2))))


def _short_string_cell_pool(bpm, tension):
    """Return playable 1-beat spiccato/staccato cells for the current tempo."""
    if bpm < 100:
        cells = [
            [(0.0, 0.50, 'root', 'staccato'), (0.5, 0.50, 'fifth', 'staccato')],
            [(0.0, 0.75, 'root', 'marcato'), (0.75, 0.25, 'third', 'spiccato')],
            [(0.0, 0.50, 'root', 'staccato'), (0.5, 0.25, 'third', 'spiccato'), (0.75, 0.25, 'fifth', 'spiccato')],
        ]
    elif bpm < 132:
        cells = [
            [(0.0, 0.50, 'root', 'staccato'), (0.5, 0.25, 'fifth', 'spiccato'), (0.75, 0.25, 'third', 'spiccato')],
            [(0.0, 0.25, 'root', 'spiccato'), (0.25, 0.25, 'third', 'spiccato'), (0.5, 0.50, 'fifth', 'staccato')],
            [(0.0, 0.25, 'root', 'spiccato'), (0.25, 0.25, 'fifth', 'spiccato'), (0.5, 0.25, 'root', 'spiccato'), (0.75, 0.25, 'third', 'spiccato')],
            [(0.0, 0.50, 'root', 'staccato'), (0.5, 0.50, 'root', 'staccato')],
        ]
    else:
        cells = [
            [(0.0, 0.50, 'root', 'staccato'), (0.5, 0.50, 'fifth', 'staccato')],
            [(0.0, 0.25, 'root', 'spiccato'), (0.25, 0.25, 'fifth', 'spiccato'), (0.5, 0.50, 'root', 'staccato')],
            [(0.0, 0.50, 'root', 'staccato'), (0.5, 0.25, 'third', 'spiccato'), (0.75, 0.25, 'fifth', 'spiccato')],
        ]
    if tension > 0.72 and bpm < 146:
        cells.append([(0.0, 0.25, 'root', 'spiccato'), (0.25, 0.25, 'fifth', 'spiccato'),
                      (0.5, 0.25, 'octave', 'spiccato'), (0.75, 0.25, 'fifth', 'spiccato')])
    return cells


def generate_staccato_ostinato(bars_data, root_val, bpm, tpb=480):
    """
    Professional short-string ostinato using BPM-aware density, phrase arcs,
    tight register voice-leading, bow-aware accents, and per-render variation.
    """
    events = []
    cell_pool = _short_string_cell_pool(bpm, tension=0.72)
    phrase_arcs = random.choice([
        [0.72, 0.88, 1.06, 0.82],
        [0.66, 0.92, 0.96, 1.10],
        [0.78, 0.84, 1.12, 0.74],
    ])
    motif = [random.choice(cell_pool) for _ in range(4)]
    prev_pitch = None

    for bar_idx, (ct, sc) in enumerate(bars_data):
        bar_start = bar_idx * 4 * tpb
        ct_pcs = [(root_val + tone) % 12 for tone in ct]
        scale_pcs = [(root_val + tone) % 12 for tone in sc]
        phrase_energy = phrase_arcs[bar_idx % len(phrase_arcs)]

        for beat in range(4):
            if beat == 0:
                cell = motif[0]
            elif beat == 3 and phrase_energy < 0.85 and random.random() < 0.55:
                cell = [(0.0, 0.50, 'root', 'staccato')]
            else:
                cell = random.choice([motif[beat % 4], random.choice(cell_pool)])

            if phrase_energy > 1.0 and random.random() < 0.22:
                cell = random.choice(cell_pool)

            for step_idx, (offset, dur, role, articulation) in enumerate(cell):
                if phrase_energy < 0.78 and beat in (1, 3) and random.random() < 0.35:
                    continue

                if role == 'root':
                    pc = ct_pcs[0]
                elif role == 'third':
                    pc = ct_pcs[1 % len(ct_pcs)]
                elif role == 'fifth':
                    pc = ct_pcs[2 % len(ct_pcs)]
                elif role == 'octave':
                    pc = ct_pcs[0]
                else:
                    pc = random.choice(scale_pcs)

                pitch = _nearest_short_string_pitch(pc, prev_pitch, 55, 72)
                if prev_pitch is not None and abs(pitch - prev_pitch) > 7:
                    pitch = _nearest_short_string_pitch(pc, prev_pitch, 55, 67 if prev_pitch < 67 else 72)
                prev_pitch = pitch

                tick = bar_start + beat * tpb + int(offset * tpb)
                jitter = 0 if beat == 0 and offset == 0.0 else random.randint(-6, 7)
                tick = max(bar_start, tick + jitter)
                dur_ticks = int(dur * tpb)
                gate = {'spiccato': 0.42, 'staccato': 0.58, 'marcato': 0.76}.get(articulation, 0.52)
                off_tick = tick + max(18, int(dur_ticks * gate) - random.randint(0, 8))

                bow_is_down = (beat * 4 + step_idx) % 2 == 0
                vel = int(70 + 28 * phrase_energy)
                if beat in (0, 2) and offset == 0.0:
                    vel += 12 if bow_is_down else 7
                elif offset == 0.0:
                    vel += 5
                else:
                    vel += -8 if not bow_is_down else -3
                vel += random.randint(-5, 5)
                vel = max(48, min(118, vel))

                events.append((tick, 'on', pitch, vel))
                events.append((off_tick, 'off', pitch, 0))
    return events

def generate_harp_arpeggios(bars_data, root_val, tpb=480):
    """
    Impressionist harp figure -- sparse, breath-driven, harmonically clear.

    Design principles:
      * 8th-note / dotted-8th grid -- no relentless 16th-note waterfalls.
      * Each beat gets a 3-note ascending figure (root -> 3rd -> 5th) in a
        sigh shape: long onset, short middle, short tail  (offsets 0, 0.5, 0.75).
      * Beats 2 and 4 have a 40 % chance of being silent (breathing room).
      * Single warm register MIDI 60-79 (C4-G5) -- no random octave hops.
      * Gentle velocity arch per bar: soft open -> peak on beat 3 -> soft close.
      * Small human jitter +/- 8 ticks per note-on.
    """
    HAR_MIN = 60   # C4
    HAR_MAX = 79   # G5

    # Offsets within a beat for the 3-note sigh figure (in beat fractions)
    #  0.0  = downbeat of the beat  (long)
    #  0.5  = halfway through       (short)
    #  0.75 = three-quarter         (short tail)
    FIGURE_OFFSETS   = [0.0, 0.5, 0.75]
    FIGURE_CT_IDX    = [0,   1,   2   ]   # root, 3rd, 5th
    FIGURE_DURATIONS = [int(0.45 * tpb),
                        int(0.22 * tpb),
                        int(0.20 * tpb)]

    # Velocity envelope shape across the 4 beats of a bar
    # [beat0, beat1, beat2, beat3]  --  peak on beat 2 (0-indexed)
    VEL_SHAPE = [62, 58, 74, 60]

    events = []

    for bar_idx, (ct, _) in enumerate(bars_data):
        bar_start = bar_idx * 4 * tpb

        for beat in range(4):
            # Skip beat (40 % chance) on the weaker beats 1 and 3 (0-indexed)
            if beat in (1, 3) and random.random() < 0.40:
                continue

            beat_tick  = bar_start + beat * tpb
            base_vel   = VEL_SHAPE[beat]

            for fig_i, (frac_off, ct_idx, dur_ticks) in enumerate(
                    zip(FIGURE_OFFSETS, FIGURE_CT_IDX, FIGURE_DURATIONS)):

                # Human jitter: +/- 8 ticks
                jitter   = random.randint(-8, 8)
                tick_on  = beat_tick + int(frac_off * tpb) + jitter
                tick_off = tick_on + dur_ticks

                # Resolve pitch class into the warm register
                pc    = (root_val + ct[ct_idx % len(ct)]) % 12
                pitch = _fit_to_register(pc, HAR_MIN, HAR_MAX)

                # Slight velocity variation around the beat's base level
                vel = max(40, min(110, base_vel + random.randint(-6, 6)))

                events.append((tick_on,  'on',  pitch, vel))
                events.append((tick_off, 'off', pitch, 0))

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

def generate_chord_pad(bars_data, root_val, tpb=480):
    """
    Lush sustained chord pad with voice-leading through inversions.

    Algorithm per bar:
      1. Compute all pitch classes for the bar's chord.
      2. Build every inversion (rotate PC list so each chord tone can be bass).
      3. For each inversion, stack voices upward within MIDI 52–76
         (E3–E5 — the warm orchestral mid-range) using the smallest
         ascending interval to the next PC, avoiding unisons.
      4. Pick the inversion whose total voice-movement from the
         previous bar's voicing is smallest (nearest-pitch globally).
      5. Emit sustained whole-bar notes with a 25-tick breath gap.
    """
    PAD_MIN = 52   # E3  — bottom of the warm orchestral range
    PAD_MAX = 76   # E5  — top of the comfortable pad range

    events     = []
    prev_voicing = None

    for bar_idx, (ct, _) in enumerate(bars_data):
        bar_start = bar_idx * 4 * tpb
        ct_pcs    = [(root_val + offset) % 12 for offset in ct]

        # ── Build one voicing per inversion ──────────────────────────────
        voicing_candidates = []
        for inv in range(len(ct_pcs)):
            rotated = ct_pcs[inv:] + ct_pcs[:inv]   # rotate so inv-th PC is bass

            bass_pc = rotated[0]
            bass_p  = PAD_MIN + ((bass_pc - PAD_MIN) % 12)
            if bass_p > PAD_MAX:
                continue

            voicing = [bass_p]
            for pc in rotated[1:]:
                prev_p = voicing[-1]
                step   = (pc - prev_p) % 12
                if step == 0:
                    step = 12          # avoid unison — go up one octave
                next_p = prev_p + step
                if next_p > PAD_MAX:
                    break
                voicing.append(next_p)

            if len(voicing) >= 2:
                voicing_candidates.append(voicing)

        # Fallback: place each PC in register, take lowest three
        if not voicing_candidates:
            fb = sorted(set(
                PAD_MIN + ((pc - PAD_MIN) % 12)
                for pc in ct_pcs
            ))
            voicing_candidates = [fb[:3]]

        # ── Select inversion with minimum total voice movement ───────────────
        if prev_voicing is None:
            best = voicing_candidates[0]   # root position for bar 1
        else:
            def cost(v):
                return sum(min(abs(p - q) for q in prev_voicing) for p in v)
            best = min(voicing_candidates, key=cost)

        prev_voicing = best

        # ── Emit sustained notes ───────────────────────────────────────
        dur_ticks = 4 * tpb - 25      # full bar with 25-tick breath gap
        vel       = random.randint(72, 82)
        for pitch in best:
            events.append((bar_start,              'on',  pitch, vel))
            events.append((bar_start + dur_ticks,  'off', pitch, 0))

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
    chord_pad = generate_chord_pad(bars_data, root_val, tpb)
    
    ch = 0
    build_track(mid, "Chord Pad", 89, ch, chord_pad); ch += 1
    build_track(mid, "Sub Bass", 43, ch, sub_bass); ch += 1
    build_track(mid, "High Drone", 48, ch, drone); ch += 1
    build_track(mid, "Staccato / Spiccato Strings", 48, ch, staccato); ch += 1
    
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
        # Epic Heroic Action: Heavy Brass, Choir, Piano
        mood_name = "Epic Heroic Action"
        brass = generate_heavy_brass(bars_data, root_val, tpb)
        choir_satb = generate_choir_satb(bars_data, root_val, tpb)
        piano = generate_piano_melody(bars_data, root_val, tpb)
        
        build_track(mid, "Heavy Brass", 61, ch, brass); ch += 1
        for voice in ['bass', 'tenor', 'alto', 'soprano']:
            build_track(mid, f"Choir - {voice.capitalize()}", 52, ch, choir_satb[voice]); ch += 1
        build_track(mid, "Piano Melody", 0, ch, piano); ch += 1
        
    else:
        # Dark Assassin Stealth: Harp/Guitar, Sparse Piano, Choir, Piano Melody
        mood_name = "Dark Assassin Stealth"
        harp  = generate_harp_arpeggios(bars_data, root_val, tpb)
        dark_piano = generate_piano_melody(bars_data, root_val, tpb)
        choir_satb = generate_choir_satb(bars_data, root_val, tpb)
        piano = generate_piano_melody(bars_data, root_val, tpb)
        
        build_track(mid, "Nylon Guitars", 24, ch, harp); ch += 1
        build_track(mid, "Dark Piano", 0, ch, dark_piano); ch += 1
        for voice in ['bass', 'tenor', 'alto', 'soprano']:
            build_track(mid, f"Choir - {voice.capitalize()}", 52, ch, choir_satb[voice]); ch += 1
        build_track(mid, "Piano Melody", 0, ch, piano); ch += 1
        
    return mid, mood_name, prog_label

def compose_cinematic_major_track(mood_id, bpm, root_name, root_val):
    """
    Generates a 4-bar major-key cinematic MIDI.
    Track counts mirror the minor engine exactly:
      Mood 1 (Triumphant Ascent)  — 10 tracks
      Mood 2 (Celestial Wonder)   — 10 tracks
      Mood 3 (Golden Pastoral)    — 11 tracks
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
    chord_pad = generate_chord_pad(bars_data, root_val, tpb)   # DFS adapts to major ct

    ch = 0
    build_track(mid, "Chord Pad",        89, ch, chord_pad); ch += 1
    build_track(mid, "Sub Bass",         43, ch, sub_bass); ch += 1
    build_track(mid, "High Drone",       48, ch, drone);    ch += 1
    build_track(mid, "Staccato / Spiccato Strings", 48, ch, staccato); ch += 1

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
        # Celestial Wonder: Celesta Arps + SATB Choir + Piano  (10 tracks)
        mood_name  = "Celestial Wonder"
        celesta    = generate_celesta_arpeggios(bars_data, root_val, tpb)
        choir_satb = generate_choir_satb(bars_data, root_val, tpb)
        piano      = generate_piano_melody(bars_data, root_val, tpb)

        build_track(mid, "Celesta Arps", 8, ch, celesta); ch += 1   # GM 8 = Celesta
        for voice in ['bass', 'tenor', 'alto', 'soprano']:
            build_track(mid, f"Choir - {voice.capitalize()}", 52, ch, choir_satb[voice]); ch += 1
        build_track(mid, "Piano Melody", 0, ch, piano); ch += 1

    else:
        # Golden Pastoral: Harp Arps + Woodwind Lead + Choir + Piano  (11 tracks)
        mood_name = "Golden Pastoral"
        harp      = generate_harp_arpeggios(bars_data, root_val, tpb)
        woodwind  = generate_woodwind_lead(bars_data, root_val, tpb)
        choir_satb = generate_choir_satb(bars_data, root_val, tpb)
        piano     = generate_piano_melody(bars_data, root_val, tpb)

        build_track(mid, "Pastoral Harp",   46, ch, harp);     ch += 1  # GM 46 = Harp
        build_track(mid, "Woodwind Lead",   73, ch, woodwind); ch += 1  # GM 73 = Flute
        for voice in ['bass', 'tenor', 'alto', 'soprano']:
            build_track(mid, f"Choir - {voice.capitalize()}", 52, ch, choir_satb[voice]); ch += 1
        build_track(mid, "Piano Melody", 0, ch, piano); ch += 1

    return mid, mood_name, prog_label

# ── CLI APPLICATION ─────────────────────────────────────────────────────────

def main(out_dir='midi_files'):
    os.makedirs(out_dir, exist_ok=True)
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

    while True:
        # ── 1. Choose tonality ───────────────────────────────────────────────
        print("  Select Tonality:")
        print("    1 -> Minor (Dark, Gothic, Ethereal, Action)")
        print("    2 -> Major (Triumphant, Celestial, Pastoral)")
        tonality_str = input("  --> ").strip()
        is_major = (tonality_str == '2')

        # ── 2. Choose mood ───────────────────────────────────────────────────
        if is_major:
            print("\n  Select Major Cinematic Mood:")
            print("    1 -> Triumphant Ascent  (Full brass fanfare, SATB choir, piano — 10 tracks)")
            print("    2 -> Celestial Wonder   (Lydian celesta arps, SATB choir, piano — 10 tracks)")
            print("    3 -> Golden Pastoral    (Harp, flute, SATB choir, piano         — 11 tracks)")
        else:
            print("\n  Select Minor Cinematic Mood:")
            print("    1 -> Ethereal Gothic Fantasy (Harps, SATB choir, piano    — 10 tracks)")
            print("    2 -> Epic Heroic Action      (Heavy brass, SATB choir, piano — 10 tracks)")
            print("    3 -> Dark Assassin Stealth   (Nylon guitars, dark piano, SATB choir, piano — 11 tracks)")
        mood_str = input("  --> ").strip()
        mood_id  = int(mood_str) if mood_str in ('1', '2', '3') else 1

        # ── 3. Choose key ────────────────────────────────────────────────────
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

        # ── 4. Tempo ─────────────────────────────────────────────────────────
        print("\n  Select Tempo (BPM) [e.g. 100, 120, 140]:")
        bpm_str = input("  --> ").strip()
        try:
            bpm = int(bpm_str)
        except ValueError:
            bpm = 120 if is_major else 110

        # ── 5. Generate ──────────────────────────────────────────────────────
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

        print("  [G] Generate again  [B] Back  [Q] Quit")
        sub = input("  --> ").strip().lower()
        if sub in ("b", "q"):
            return

if __name__ == '__main__':
    main()
