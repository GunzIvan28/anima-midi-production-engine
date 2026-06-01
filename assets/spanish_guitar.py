"""
ANIMA Spanish Guitar Engine
— Nylon Guitar Composer —
4-track arpeggiated guitar: Bajo · Rasgueado · Alzapua · Picado
Built from direct MIDI sample analysis (harmonic minor, phrygian dominant, phrygian).
"""

import os, sys, random, math
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage

assets_dir = os.path.dirname(os.path.abspath(__file__))
if assets_dir not in sys.path:
    sys.path.insert(0, assets_dir)
import specialist_styles

GENERATION_MODE = 'simple'

# ── GUITAR REGISTER BOUNDARIES (E2=40 .. E6=88) ─────────────────────────────
BAJO_LO,    BAJO_HI    = 40, 54   # E2–F#3  bass strings
RASGUEO_LO, RASGUEO_HI = 43, 66   # G2–F#4  mid-body arpeggio
ALZAPUA_LO, ALZAPUA_HI = 55, 72   # G3–C5   inner counter voice
PICADO_LO,  PICADO_HI  = 62, 81   # D4–A5   expressive lead
GM_NYLON = 24

# ── SCALES ───────────────────────────────────────────────────────────────────
SPANISH_SCALES = {
    'harmonic_minor':    [0,2,3,5,7,8,11],
    'phrygian_dominant': [0,1,4,5,7,8,10],
    'phrygian':          [0,1,3,5,7,8,10],
    'natural_minor':     [0,2,3,5,7,8,10],
    'dorian':            [0,2,3,5,7,9,10],
    'ionian':            [0,2,4,5,7,9,11],
    'mixolydian':        [0,2,4,5,7,9,10],
}

# ── ROMAN NUMERAL CHORD TABLES ────────────────────────────────────────────────
def _rn(chords, sc):
    return {s:(o,sc) for s,o in chords.items()}

SCALE_RN = {
    'harmonic_minor': _rn({
        'i':[0,3,7],'iidim':[2,5,8],'III':[3,7,11],
        'iv':[5,8,0],'V':[7,11,2],'VI':[8,0,3],'VII':[10,2,5]}, [0,2,3,5,7,8,11]),
    'phrygian_dominant': _rn({
        'I':[0,4,7],'bII':[1,5,8],'iii':[4,7,10],
        'iv':[5,8,0],'bVI':[8,0,4],'bVII':[10,1,4]}, [0,1,4,5,7,8,10]),
    'phrygian': _rn({
        'i':[0,3,7],'bII':[1,4,8],'bIII':[3,7,10],
        'iv':[5,8,0],'v':[7,10,1],'bVI':[8,0,3],'bVII':[10,1,5]}, [0,1,3,5,7,8,10]),
    'natural_minor': _rn({
        'i':[0,3,7],'iidim':[2,5,8],'bIII':[3,7,10],
        'iv':[5,8,0],'v':[7,10,2],'bVI':[8,0,3],'bVII':[10,2,5]}, [0,2,3,5,7,8,10]),
    'dorian': _rn({
        'i':[0,3,7],'ii':[2,5,9],'bIII':[3,7,10],
        'IV':[5,9,0],'v':[7,10,2],'vi':[9,0,3],'bVII':[10,2,5]}, [0,2,3,5,7,9,10]),
    'ionian': _rn({
        'I':[0,4,7],'ii':[2,5,9],'iii':[4,7,11],
        'IV':[5,9,0],'V':[7,11,2],'vi':[9,0,4],'viidim':[11,2,5]}, [0,2,4,5,7,9,11]),
    'mixolydian': _rn({
        'I':[0,4,7],'ii':[2,5,9],'iii':[4,7,10],
        'IV':[5,9,0],'v':[7,10,2],'vi':[9,0,4],'bVII':[10,2,5]}, [0,2,4,5,7,9,10]),
}

# ── CHARACTERISTIC PROGRESSIONS PER SCALE ────────────────────────────────────
SCALE_PROGRESSIONS = {
    'harmonic_minor':    [['i','VII','VI','V'],['i','iv','V','i'],
                          ['i','VI','III','VII'],['i','iv','VII','V']],
    'phrygian_dominant': [['I','bII','I','bVII'],['I','bVII','bVI','bII'],
                          ['I','iv','bVII','I'],['I','bII','bVII','bVI']],
    'phrygian':          [['i','bII','bVII','bVI'],['i','bVII','bVI','bII'],
                          ['i','iv','bVII','i'],['i','bII','bVII','i']],
    'natural_minor':     [['i','bVI','bVII','i'],['i','iv','v','i'],
                          ['i','bIII','bVII','i'],['i','bVI','bIII','bVII']],
    'dorian':            [['i','IV','i','IV'],['i','ii','bVII','i'],
                          ['i','IV','bVII','i'],['i','bIII','IV','i']],
    'ionian':            [['I','IV','V','I'],['I','vi','IV','V'],
                          ['I','V','vi','IV'],['I','ii','V','I']],
    'mixolydian':        [['I','bVII','IV','I'],['I','IV','bVII','I'],
                          ['I','v','IV','bVII'],['I','bVII','I','IV']],
}

# ── MOOD PRESETS ─────────────────────────────────────────────────────────────
MOOD_PRESETS = {
    'A': {'name':'Duende Oscuro',  'desc':'Dark passion, grief, the deep soul of Flamenco',
          'scale':'harmonic_minor',    'tension':0.75, 'bpm_range':(140,160), 'is_minor':True},
    'B': {'name':'Alma Flamenca',  'desc':'Fire, drama, the core Flamenco spirit',
          'scale':'phrygian_dominant', 'tension':0.70, 'bpm_range':(130,155), 'is_minor':True},
    'C': {'name':'Noche Española', 'desc':'Modal night, Spanish melancholy and mystery',
          'scale':'phrygian',          'tension':0.55, 'bpm_range':(140,160), 'is_minor':True},
    'D': {'name':'Serenata',       'desc':'Gentle longing, tender serenade',
          'scale':'natural_minor',     'tension':0.40, 'bpm_range':(100,125), 'is_minor':True},
    'E': {'name':'Romance Dorian', 'desc':'Soulful Dorian brightness, modal warmth',
          'scale':'dorian',            'tension':0.45, 'bpm_range':(110,135), 'is_minor':True},
    'F': {'name':'Alma Alegre',    'desc':'Bright joy, festive major energy',
          'scale':'ionian',            'tension':0.35, 'bpm_range':(115,145), 'is_minor':False},
    'G': {'name':'Pasión Mayor',   'desc':'Warm major with Spanish edge and drive',
          'scale':'mixolydian',        'tension':0.50, 'bpm_range':(130,155), 'is_minor':False},
}

ROOTS = {'C':60,'C#':61,'Db':61,'D':62,'D#':63,'Eb':63,'E':64,
         'F':65,'F#':66,'Gb':66,'G':67,'G#':68,'Ab':68,'A':69,'Bb':70,'B':71}

# ── MARKOV HELPERS ────────────────────────────────────────────────────────────
def _get_markov_matrix(scale):
    mat = [[0.0]*12 for _ in range(12)]
    sc = set(scale)
    for i in range(12):
        total = 0.0
        for j in range(12):
            if j % 12 in sc:
                d = min((j-i)%12, (i-j)%12)
                w = 1.0/(d+1) if d > 0 else 0.0
                mat[i][j] = w; total += w
        if total > 0:
            mat[i] = [x/total for x in mat[i]]
    return mat

def _markov_next(cur_pc, scale, mat):
    row = mat[cur_pc % 12]
    r = random.random(); cum = 0.0
    for j, w in enumerate(row):
        cum += w
        if r <= cum and j % 12 in set(scale):
            return j % 12
    return random.choice([s % 12 for s in scale])

def _build_progression(root_val, scale_name, tension, num_bars):
    """Return a flat list of RN symbols for num_bars."""
    global GENERATION_MODE
    rn_dict = SCALE_RN[scale_name]
    scale   = SPANISH_SCALES[scale_name]
    progs   = SCALE_PROGRESSIONS[scale_name]

    if GENERATION_MODE == 'decoupled':
        mat = _get_markov_matrix([(root_val + s) % 12 for s in scale])
        sym_roots = {sym: (root_val + offs[0]) % 12 for sym,(offs,_) in rn_dict.items()}
        syms = list(rn_dict.keys())
        cur = syms[0]
        result = []
        for _ in range(num_bars):
            result.append(cur)
            next_pc = _markov_next(sym_roots[cur], scale, mat)
            candidates = [s for s,r in sym_roots.items() if r == next_pc]
            cur = candidates[0] if candidates else random.choice(syms)
        return result
    else:
        base = random.choice(progs)
        result = [base[i % len(base)] for i in range(num_bars)]
        return result

# ── PITCH HELPERS ─────────────────────────────────────────────────────────────
def _in_range(pitch, lo, hi):
    while pitch < lo: pitch += 12
    while pitch > hi: pitch -= 12
    return pitch

def _chord_pitches_in_range(root_val, chord_offsets, lo, hi):
    """Get all chord-tone pitches available in [lo, hi]."""
    pitches = []
    for offset in chord_offsets:
        pc = (root_val + offset) % 12
        p = pc + 48  # start from C3
        while p < lo: p += 12
        while p > hi: p -= 12
        if lo <= p <= hi and p not in pitches:
            pitches.append(p)
        # also one octave up
        if lo <= p+12 <= hi and p+12 not in pitches:
            pitches.append(p+12)
    return sorted(pitches)

def _scale_pitches_in_range(root_val, scale, lo, hi):
    pitches = []
    for s in scale:
        pc = (root_val + s) % 12
        p = pc + 48
        while p < lo: p += 12
        while p > hi: p -= 12
        if lo <= p <= hi and p not in pitches:
            pitches.append(p)
        if lo <= p+12 <= hi and p+12 not in pitches:
            pitches.append(p+12)
    return sorted(pitches)

# ── TRACK 0: BAJO ─────────────────────────────────────────────────────────────
def generate_bajo(root_val, progression, rn_dict, tension, num_bars, tpb):
    """Bass: root on beat 1, optional 5th on beat 3. Half/whole note values."""
    events = []  # (abs_beat, pitch, dur_beats, velocity)
    for bar, sym in enumerate(progression):
        offsets, _ = rn_dict[sym]
        root_pc = (root_val + offsets[0]) % 12
        fifth_pc = (root_val + offsets[2]) % 12 if len(offsets) > 2 else root_pc

        root_p = _in_range(root_pc + 48, BAJO_LO, BAJO_HI)
        fifth_p = _in_range(fifth_pc + 48, BAJO_LO, BAJO_HI)

        beat_base = bar * 4.0
        vel = random.randint(62, 78)

        if tension > 0.55:
            # Root on 1, 5th on 3
            events.append((beat_base,       root_p,  2.0, vel))
            events.append((beat_base + 2.0, fifth_p, 2.0, max(50, vel-8)))
        else:
            # Whole note root
            events.append((beat_base, root_p, 4.0, vel))
    return events

# ── TRACK 1: RASGUEADO ────────────────────────────────────────────────────────
def generate_rasgueado(root_val, progression, rn_dict, tension, num_bars, tpb):
    """
    Single-note ascending/descending arpeggio outlining chord tones.
    Intervals of 7-15 semitones simulate cross-string guitar voicing.
    """
    events = []
    for bar, sym in enumerate(progression):
        offsets, _ = rn_dict[sym]
        pitches = _chord_pitches_in_range(root_val, offsets, RASGUEO_LO, RASGUEO_HI)
        if not pitches:
            continue

        beat_base = bar * 4.0

        # Choose note duration based on tension
        if tension > 0.65:
            dur = 0.5   # 8th notes — fast rasgueo (puelo/hermosa style)
        elif tension > 0.40:
            dur = random.choice([0.5, 0.5, 1.0])   # mixed
        else:
            dur = 1.0   # quarter notes — slower (tango/spanish-night style)

        count = int(4.0 / dur)

        # Direction per bar
        direction = random.choice(['up', 'down', 'bounce', 'bounce'])
        if direction == 'up':
            seq = pitches
        elif direction == 'down':
            seq = list(reversed(pitches))
        else:  # bounce: low-high-low-high pattern
            lo = pitches[0]; hi = pitches[-1]
            mid = pitches[len(pitches)//2] if len(pitches) > 2 else lo
            seq = [lo, hi, mid, hi, lo, hi]

        # Cycle to fill count
        full = []
        while len(full) < count:
            full.extend(seq)
        full = full[:count]

        for i, pitch in enumerate(full):
            vel = random.randint(58, 82)
            vel = min(95, vel + int(i * 1.5))
            events.append((beat_base + i * dur, pitch, dur * 0.92, vel))

    return events

# ── TRACK 2: ALZAPUA ──────────────────────────────────────────────────────────
def generate_alzapua(root_val, progression, rn_dict, tension, num_bars, tpb, lead_events=None):
    events = []
    prev_pitch = None
    for bar, sym in enumerate(progression):
        if random.random() > 0.60 + tension * 0.15:
            continue
        offsets, scale = rn_dict[sym]
        scale_pitches = _scale_pitches_in_range(root_val, scale, ALZAPUA_LO, ALZAPUA_HI)
        chord_pitches = _chord_pitches_in_range(root_val, offsets, ALZAPUA_LO, ALZAPUA_HI)
        if not scale_pitches:
            continue
        beat_base = bar * 4.0
        num_notes = random.randint(2, 4)
        beat = beat_base
        for _ in range(num_notes):
            if beat >= beat_base + 4.0:
                break
            if prev_pitch is None:
                pitch = random.choice(chord_pitches or scale_pitches)
            else:
                candidates = [p for p in scale_pitches if abs(p - prev_pitch) <= 5]
                pitch = random.choice(candidates) if candidates else random.choice(scale_pitches)
            dur = random.choice([0.5, 1.0, 1.0, 2.0])
            if beat + dur > beat_base + 4.0:
                dur = beat_base + 4.0 - beat
            vel = random.randint(52, 72)
            events.append((beat, pitch, dur * 0.88, vel))
            prev_pitch = pitch
            beat += dur
    return events

# ── TRACK 3: PICADO ───────────────────────────────────────────────────────────
def generate_picado(root_val, progression, rn_dict, tension, num_bars, tpb):
    events = []
    prev_pitch = None
    for bar, sym in enumerate(progression):
        offsets, scale = rn_dict[sym]
        scale_pitches = _scale_pitches_in_range(root_val, scale, PICADO_LO, PICADO_HI)
        chord_pitches = _chord_pitches_in_range(root_val, offsets, PICADO_LO, PICADO_HI)
        if not scale_pitches:
            continue
        beat_base = bar * 4.0
        beat = beat_base
        run_prob = 0.25 + tension * 0.55

        while beat < beat_base + 4.0:
            remaining = beat_base + 4.0 - beat
            if random.random() < run_prob and remaining >= 0.75:
                # Picado run: 3-6 16th notes stepwise
                run_len = random.randint(3, min(6, int(remaining / 0.25)))
                if prev_pitch is None:
                    prev_pitch = random.choice(chord_pitches or scale_pitches)
                for _ in range(run_len):
                    if beat >= beat_base + 4.0:
                        break
                    step = random.choice([-2,-1,-1,1,1,2])
                    candidates = [p for p in scale_pitches if 0 < abs(p - prev_pitch) <= 3]
                    if candidates:
                        pitch = min(candidates, key=lambda p: abs(p-(prev_pitch+step)))
                    else:
                        pitch = prev_pitch
                    vel = random.randint(72, 100)
                    events.append((beat, pitch, 0.22, vel))
                    prev_pitch = pitch
                    beat += 0.25
            else:
                # Statement phrase: quarter or half note
                if prev_pitch is None:
                    pitch = random.choice(chord_pitches or scale_pitches)
                else:
                    candidates = [p for p in scale_pitches if abs(p - prev_pitch) <= 7]
                    pitch = random.choice(candidates) if candidates else random.choice(scale_pitches)
                dur = random.choice([0.5, 1.0, 1.0, 2.0, 2.0] if tension > 0.5 else [1.0, 2.0, 2.0, 4.0])
                dur = min(dur, remaining)
                vel = random.randint(65, 95)
                events.append((beat, pitch, dur * 0.90, vel))
                prev_pitch = pitch
                beat += dur
    return events

# ── MIDI ASSEMBLY ─────────────────────────────────────────────────────────────
def _events_to_track(events, channel, program, bpm, tpb):
    track = MidiTrack()
    us_per_beat = int(60_000_000 / bpm)
    track.append(MetaMessage('set_tempo', tempo=us_per_beat, time=0))
    track.append(Message('program_change', channel=channel, program=program, time=0))

    msgs = []
    for (beat, pitch, dur_beats, vel) in events:
        start = int(beat * tpb)
        end   = int((beat + dur_beats) * tpb)
        hvel  = max(1, min(127, vel + random.randint(-4, 4)))
        stagger = random.randint(-4, 4)
        msgs.append((max(0, start + stagger), 'on',  pitch, hvel,  channel))
        msgs.append((max(0, end   + stagger), 'off', pitch, 0,     channel))

    msgs.sort(key=lambda x: (x[0], 0 if x[1]=='off' else 1))
    prev_tick = 0
    for tick, kind, pitch, vel, ch in msgs:
        delta = max(0, tick - prev_tick)
        if kind == 'on':
            track.append(Message('note_on',  channel=ch, note=pitch, velocity=vel, time=delta))
        else:
            track.append(Message('note_off', channel=ch, note=pitch, velocity=0,   time=delta))
        prev_tick = tick
    return track

def build_spanish_guitar_midi(bpm, root_val, root_name, scale_name, mood_name,
                               tension, num_bars=4):
    rn_dict    = SCALE_RN[scale_name]
    progression = _build_progression(root_val, scale_name, tension, num_bars)
    tpb = 480

    bajo    = generate_bajo(root_val, progression, rn_dict, tension, num_bars, tpb)
    rasgueo = generate_rasgueado(root_val, progression, rn_dict, tension, num_bars, tpb)
    alzapua = generate_alzapua(root_val, progression, rn_dict, tension, num_bars, tpb)
    picado  = generate_picado(root_val, progression, rn_dict, tension, num_bars, tpb)

    mid = MidiFile(ticks_per_beat=tpb)
    mid.tracks.append(_events_to_track(bajo,    0, GM_NYLON, bpm, tpb))
    mid.tracks.append(_events_to_track(rasgueo, 1, GM_NYLON, bpm, tpb))
    mid.tracks.append(_events_to_track(alzapua, 2, GM_NYLON, bpm, tpb))
    mid.tracks.append(_events_to_track(picado,  3, GM_NYLON, bpm, tpb))
    return mid, progression

# ── CLI HELPERS ───────────────────────────────────────────────────────────────
def _div(c='-', w=62): print(c * w)

def _select_mood():
    print("""
  Select a mood:
  ____________________________________________________________
    A  →  Duende Oscuro      Dark passion, grief            [Harmonic Min]
    B  →  Alma Flamenca      Fire, drama, Flamenco core     [Phrygian Dom]
    C  →  Noche Española     Modal night, Spanish mystery   [Phrygian]
    D  →  Serenata           Gentle longing, tender night   [Natural Min]
    E  →  Romance Dorian     Soulful warmth, modal glow     [Dorian]
    F  →  Alma Alegre        Bright joy, festive major      [Ionian]
    G  →  Pasión Mayor       Warm major with Spanish edge   [Mixolydian]
  ____________________________________________________________""")
    while True:
        choice = input("  --> ").strip().upper()
        if choice in MOOD_PRESETS:
            m = MOOD_PRESETS[choice]
            print(f"  [{m['name']}] — {m['desc']}")
            return m
        print("  Enter A-G.")

def _select_key():
    print(f"\n  Select root key: {' · '.join(ROOTS.keys())}")
    while True:
        k = input("  --> ").strip()
        if k in ROOTS:
            return k, ROOTS[k]
        print("  Invalid key.")

def _select_tempo(lo, hi):
    print(f"\n  Select BPM ({lo}–{hi}) or press Enter for default:")
    val = input("  --> ").strip()
    if val.isdigit():
        return max(lo, min(hi, int(val)))
    return random.randint(lo, hi)

def _save(mid, fname_base, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, fname_base + '.mid')
    idx = 1
    while os.path.exists(path):
        path = os.path.join(out_dir, f"{fname_base}_v{idx}.mid")
        idx += 1
    mid.save(path)
    return path

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main(out_dir='midi_files'):
    os.makedirs(out_dir, exist_ok=True)
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║       S P A N I S H   G U I T A R   C O M P O S E R       ║
║      Bajo · Rasgueado · Alzapua · Picado — 4 Tracks       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝""")

    while True:
        mood   = _select_mood()
        key_name, root_val = _select_key()
        bpm_lo, bpm_hi = mood['bpm_range']
        bpm    = _select_tempo(80, 160)

        scale_name = mood['scale']
        tension    = mood['tension']
        mood_name  = mood['name']

        _div()
        print(f"""
  ── Composition Summary ──────────────────────────────
    Mood    : {mood_name}
    Scale   : {scale_name.replace('_',' ').title()}
    Key     : {key_name}
    BPM     : {bpm}
    Tension : {'#'*int(tension*10)}{'.'*(10-int(tension*10))} {int(tension*100)}%
    Mode    : {GENERATION_MODE.upper()}
  ─────────────────────────────────────────────────────
""")
        mid, prog = build_spanish_guitar_midi(bpm, root_val, key_name,
                                               scale_name, mood_name, tension)
        prog_str = '-'.join(prog)
        sc_short = scale_name.replace('_','')[:8]
        fname = f"SpanishGuitar_4Bar_{mood_name.replace(' ','_')}__{key_name}_{sc_short}__{bpm}BPM"
        path  = _save(mid, fname, out_dir)
        print(f"  [SAVED]  {os.path.basename(path)}")
        print(f"  [PATH ]  {path}")
        print(f"  [PROG ]  {prog_str}\n")

        print("  [G] Generate again  [B] Back  [Q] Quit")
        sub = input("  --> ").strip().lower()
        if sub == 'q':
            break
        elif sub == 'b':
            return

if __name__ == '__main__':
    main()
