import mido
import random
import os
import math

def generate_cc_curve(track_events, control_no, start_tick, duration_ticks, start_val, end_val, curve_type="linear", ch=0):
    """
    Generates smooth CC events between start_tick and start_tick + duration_ticks
    and appends them to track_events.
    """
    step_size = 120
    steps = int(duration_ticks / step_size)
    if steps < 1:
        steps = 1
        step_size = duration_ticks
        
    for step in range(steps + 1):
        tick = start_tick + step * step_size
        if tick > start_tick + duration_ticks:
            tick = start_tick + duration_ticks
        pct = step / float(steps)
        
        if curve_type == "sine":
            value = int(start_val + (end_val - start_val) * math.sin(pct * math.pi))
        elif curve_type == "exp_decay":
            value = int(end_val + (start_val - end_val) * (1.0 - pct)**3)
        elif curve_type == "crescendo":
            value = int(start_val + (end_val - start_val) * pct**3)
        else:
            value = int(start_val + (end_val - start_val) * pct)
            
        value = max(0, min(127, value))
        track_events.append((tick, 'cc', control_no, value, ch))

# --- THEORY DATA & INSTRUMENTS ---
ROOTS = {'C':36,'C#':37,'D':38,'Eb':39,'E':40,'F':41,'F#':42,'G':43,'Ab':44,'A':45,'Bb':46,'B':47}

def get_flamenco_chord_voicing(notes):
    """
    Voice generated chord notes as an authentic Spanish nylon guitar chord shape.
    Features:
      - Standard low-bass note down an octave.
      - Open string resonances: E4 (64), B4 (71), E5 (76) added as modal drones
        when appropriate to capture the classic Flamenco resonance.
    """
    if not notes:
        return [40, 52, 57, 64, 71, 76] # Standard open E Phrygian shape
        
    sorted_notes = sorted(notes)
    base = sorted_notes[0]
    
    # Determine pitch classes in chord to see what key/vibe we have
    pcs = set(n % 12 for n in notes)
    
    voicing = [
        base - 12,  # Low bass string
        base,       # Root/tenor
        sorted_notes[1] if len(sorted_notes) > 1 else base + 4,
        sorted_notes[2] if len(sorted_notes) > 2 else base + 7,
    ]
    
    top_note = (sorted_notes[3] if len(sorted_notes) > 3 else base + 12)
    voicing.append(top_note)
    
    # Spanish Open String Resonances:
    # E.g., if chord has E (pc 4) or F (pc 5) or G (pc 7) or A (pc 9) or B (pc 11) or C (pc 0)
    # Adding 76 (E5) is signature for Phrygian dominant (e.g. F major chord, E major chord)
    if 4 in pcs or 5 in pcs or 11 in pcs:
        if 76 not in voicing:
            voicing.append(76) # Open high E string
    if 11 in pcs or 0 in pcs or 7 in pcs:
        if 71 not in voicing:
            voicing.append(71) # Open B string
            
    voicing = sorted(list(set(voicing)))
    return voicing[:6]

def get_templar_organum_voicing(notes):
    """
    Voice chord as parallel organum fifths and octaves (hollow sacred sound).
    """
    if not notes:
        return [48, 55, 60, 67]
    base = sorted(notes)[0]
    voicing = [
        base - 12,      # Deep drone root
        base,           # Tenor root
        base + 7,       # Tenor fifth
        base + 12,      # Alto root
        base + 19       # Soprano fifth
    ]
    return voicing

def get_tempo_and_velocity_modifiers(tension):
    """
    Music Theory adaptation:
    - Tension < 0.5 (Melancholy/Nostalgic): Adagio/Lento (64-76 BPM), piano/soft velocities (50-70).
    - 0.5 <= Tension < 0.7 (Romantic/Hopeful): Moderato/Andante (80-98 BPM), mezzo-forte velocities (70-90).
    - Tension >= 0.7 (Epic/Urgent/Ominous): Allegro/Presto (108-135 BPM), forte/fortissimo velocities (95-115).
    """
    if tension < 0.5:
        bpm = int(64 + (tension / 0.5) * 12)
        vel_chord = 60
        vel_lead = 72
        vel_perc = 62
    elif tension < 0.7:
        pct = (tension - 0.5) / 0.2
        bpm = int(80 + pct * 18)
        vel_chord = 75
        vel_lead = 85
        vel_perc = 78
    else:
        pct = min(1.0, (tension - 0.7) / 0.3)
        bpm = int(108 + pct * 27)
        vel_chord = 98
        vel_lead = 112
        vel_perc = 102
    return bpm, vel_chord, vel_lead, vel_perc

def build_midi_from_events(tracks_events, tpb=480):
    """
    Helper to convert absolute tick events to standard delta-time tracks.
    """
    mid = mido.MidiFile()
    mid.ticks_per_beat = tpb

    for te in tracks_events:
        # Sort by absolute tick. Handle programs and tempos first.
        te.sort(key=lambda x: (x[0], 0 if x[1] in ['program', 'tempo'] else 1))
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        last_tick = 0
        for ev in te:
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
                
    return mid

def generate_flamenco(mode, out_dir, root_val, root_name, chords, melody, counter, tension, label_name, mood_prefix):
    """
    Generates Spanish Nylon Guitar and Flamenco Percussion using authentic ornaments.
    Adopts generated chords, melody, and counter-melody.
    """
    tpb = 480
    bpm, vel_chord, vel_lead, vel_perc = get_tempo_and_velocity_modifiers(tension)
    
    # 5 tracks: Chords (Ch 0), Lead (Ch 1), Counter/Alzapua (Ch 2), Bass (Ch 3), Percussion (Ch 9)
    tr_chords = [(0, 'program', 24, 0, 0), (0, 'tempo', bpm, 0, 0)]  # Nylon Guitar
    tr_lead   = [(0, 'program', 24, 0, 1)]                          # Nylon Guitar
    tr_cnt    = [(0, 'program', 24, 0, 2)]                          # Nylon Guitar
    tr_bass   = [(0, 'program', 32, 0, 3)]                          # Acoustic Bass
    tr_perc   = []                                                  # Drum track
    
    num_bars = len(chords)
    
    # --- 1. RENDER GUITAR CHORDS (Strumming, Rasgueados, and Arpeggios) ---
    for bar in range(num_bars):
        voicing = get_flamenco_chord_voicing(chords[bar])
        bar_start_tick = bar * 4 * tpb
        
        # Section properties for 32-bar songs
        is_intro = (mode == "song" and bar < 4)
        is_outro = (mode == "song" and bar >= 28)
        is_verse = (mode == "song" and ((4 <= bar < 12) or (20 <= bar < 28)))
        is_chorus = (mode == "song" and (12 <= bar < 20))
        
        if is_intro:
            # Soft arpeggio on downbeat
            step_dur = tpb
            for step, note in enumerate(voicing[:4]):
                tick = bar_start_tick + step * step_dur
                tr_chords.append((tick, 'on', note, vel_chord - 12, 0))
                tr_chords.append((tick + step_dur - 10, 'off', note, 0, 0))
        elif is_outro:
            # Single slow strum (Rasgueado style roll)
            stagger = 25
            for i, note in enumerate(voicing):
                on_t = bar_start_tick + i * stagger
                off_t = bar_start_tick + 3 * tpb
                tr_chords.append((on_t, 'on', note, vel_chord - 15, 0))
                tr_chords.append((off_t, 'off', note, 0, 0))
        elif is_verse or (mode == "loop" and tension < 0.5):
            # Syncopated flamenco triplet arpeggiation (0.0, 0.333, 0.667 beats)
            # This replicates the hermoso/la guitara hand-picked organic style.
            triplet_pattern = [
                (0, [0], 160, -4),           # Beat 0.0: Low Bass string
                (160, [1], 160, -8),         # Beat 0.333: Tenor string
                (320, [2], 160, -6),         # Beat 0.667: Mid string
                # Beat 1.0: skip
                (640, [1], 160, -8),         # Beat 1.333: Tenor string
                (800, [3 % len(voicing)], 160, -6), # Beat 1.667: High string
                (960, [0], 160, -2),         # Beat 2.0: Low Bass string
                (1120, [2], 160, -8),        # Beat 2.333: Tenor string
                (1280, [4 % len(voicing)], 160, -4), # Beat 2.667: High string
                (1440, [1, 2, 3], 240, -10), # Beat 3.0: Soft strum
                (1680, [5 % len(voicing)], 240, -4)  # Beat 3.5: Highest open drone accent
            ]
            for tick_off, note_indices, dur_ticks, vel_mod in triplet_pattern:
                for idx in note_indices:
                    note = voicing[idx]
                    # Add micro-stagger humanization
                    stagger = random.randint(-6, 6)
                    on_t = max(0, bar_start_tick + tick_off + stagger)
                    tr_chords.append((on_t, 'on', note, vel_chord + vel_mod, 0))
                    tr_chords.append((on_t + dur_ticks - 10, 'off', note, 0, 0))
        else:
            # Chorus / High Tension Strumming, Rasgueados, & Golpe Taps
            for beat in range(4):
                beat_tick = bar_start_tick + beat * tpb
                
                # Wood knock (Golpe) on upbeat of beat 2 and 4
                if beat in [1, 3] and tension >= 0.5:
                    golpe_tick = beat_tick + tpb // 2
                    tr_perc.append((golpe_tick, 'on', 37, vel_perc + 12, 9)) # Side stick knock
                    tr_perc.append((golpe_tick + 60, 'off', 37, 0, 9))
                    
                if beat == 0:
                    # Downstrum Rasgueado: quick staggered roll low-to-high
                    stagger = 15 if tension >= 0.7 else 22
                    for i, note in enumerate(voicing):
                        on_t = beat_tick + i * stagger
                        off_t = beat_tick + tpb - 30
                        tr_chords.append((on_t, 'on', note, vel_chord - i * 3, 0))
                        tr_chords.append((off_t, 'off', note, 0, 0))
                elif beat == 2:
                    # Upstrum Rasgueado: quick staggered roll high-to-low
                    stagger = 15 if tension >= 0.7 else 22
                    for i, note in enumerate(reversed(voicing)):
                        on_t = beat_tick + i * stagger
                        off_t = beat_tick + tpb - 30
                        tr_chords.append((on_t, 'on', note, vel_chord - i * 3, 0))
                        tr_chords.append((off_t, 'off', note, 0, 0))
                elif beat == 1:
                    # Triplet strum (three quick strums)
                    triplet_dur = tpb // 3
                    for trip in range(3):
                        trip_tick = beat_tick + trip * triplet_dur
                        # alternate down/up sweep of top 3 notes
                        notes_to_play = voicing[:3] if trip % 2 == 0 else voicing[-3:]
                        for note in notes_to_play:
                            tr_chords.append((trip_tick, 'on', note, vel_chord - 10, 0))
                            tr_chords.append((trip_tick + triplet_dur - 10, 'off', note, 0, 0))
                elif beat == 3:
                    # Staccato accent strum
                    for note in voicing:
                        tr_chords.append((beat_tick, 'on', note, vel_chord + 10, 0))
                        tr_chords.append((beat_tick + 120, 'off', note, 0, 0))
                        
    # --- 2. RENDER TOP MELODY (Tremolo picking, Ligados, and Picado) ---
    current_tick = 0
    for note, duration in melody:
        dur_ticks = int(duration * tpb)
        
        if note is None:
            current_tick += dur_ticks
            continue
            
        # Mute logic based on song section
        bar_idx = current_tick // (4 * tpb)
        is_intro = (mode == "song" and bar_idx < 4)
        
        if is_intro:
            current_tick += dur_ticks
            continue
            
        # Ornamentations based on tension & duration
        if tension >= 0.5 and duration >= 1.0:
            # Crescendo Tremolo picking: rapid repetitions repeating the note
            num_repeats = int(duration * 6) if tension >= 0.7 else int(duration * 4)
            if num_repeats > 0:
                repeat_dur = dur_ticks // num_repeats
                for r in range(num_repeats):
                    r_tick = current_tick + r * repeat_dur
                    # Smooth crescendo ramp from vel_lead-35 to vel_lead+15
                    progress = r / float(num_repeats)
                    vel = int((vel_lead - 35) + progress * 50)
                    vel = max(10, min(127, vel))
                    
                    # Add micro-stagger humanization
                    stagger = random.randint(-5, 5)
                    tr_lead.append((max(0, r_tick + stagger), 'on', note, vel, 1))
                    tr_lead.append((max(0, r_tick + stagger + repeat_dur - 5), 'off', note, 0, 1))
        elif tension >= 0.4 and duration >= 0.5 and random.random() < 0.6:
            # Ligado (grace note hammer-on/slide)
            grace_dur = tpb // 6 # extremely rapid grace note (32nd note equivalent)
            grace_note = note - 1 if random.random() < 0.7 else note + 1
            tr_lead.append((current_tick, 'on', grace_note, vel_lead - 15, 1))
            tr_lead.append((current_tick + grace_dur, 'off', grace_note, 0, 1))
            
            # Main note strike
            stagger = random.randint(-4, 4)
            tr_lead.append((max(0, current_tick + grace_dur + stagger), 'on', note, vel_lead + 5, 1))
            tr_lead.append((current_tick + dur_ticks - 10, 'off', note, 0, 1))
        else:
            # Sharp humanized Picado picking: crisp alternate strokes
            stagger = random.randint(-6, 6)
            alt_vel = vel_lead + random.choice([-8, -4, 0, 4, 8])
            tr_lead.append((max(0, current_tick + stagger), 'on', note, alt_vel, 1))
            tr_lead.append((current_tick + dur_ticks - 15, 'off', note, 0, 1))
            
        current_tick += dur_ticks
        
    # --- 3. RENDER COUNTER-MELODY (Alzapúa & Fingerstyle Support) ---
    current_tick = 0
    for note, duration in counter:
        dur_ticks = int(duration * tpb)
        
        if note is None:
            current_tick += dur_ticks
            continue
            
        bar_idx = current_tick // (4 * tpb)
        is_muted = (mode == "song" and (bar_idx < 12 or bar_idx >= 28))
        if mode == "loop" and tension < 0.4:
            is_muted = True
            
        if is_muted:
            current_tick += dur_ticks
            continue
            
        # Play counter-melody with clean alzapúa/fingerpicking performance
        safe_note = note
        while safe_note > 64:
            safe_note -= 12
            
        # Alzapúa velocity modeling: downbeats are heavy thumb strokes, offbeats are light sweeps
        is_downbeat = (current_tick % tpb == 0)
        alt_vel = (vel_lead - 5) if is_downbeat else (vel_lead - 16)
        alt_vel = max(10, min(127, alt_vel + random.randint(-5, 5)))
        
        # Add micro-stagger
        stagger = random.randint(-6, 6)
        tr_cnt.append((max(0, current_tick + stagger), 'on', safe_note, alt_vel, 2))
        tr_cnt.append((max(0, current_tick + stagger + dur_ticks - 10), 'off', safe_note, 0, 2))
        current_tick += dur_ticks
        
    # --- 4. RENDER BASS ---
    for bar in range(num_bars):
        bar_start_tick = bar * 4 * tpb
        voicing = get_flamenco_chord_voicing(chords[bar])
        root_note = voicing[0]  # Low bass note from chord
        fifth_note = voicing[1]
        
        is_intro = (mode == "song" and bar < 4)
        is_outro = (mode == "song" and bar >= 28)
        
        if is_intro or is_outro or tension < 0.5:
            # Simple sustained bass on beat 1
            tr_bass.append((bar_start_tick, 'on', root_note, vel_chord - 8, 3))
            tr_bass.append((bar_start_tick + 4 * tpb - 30, 'off', root_note, 0, 3))
        else:
            # Dynamic flamenco bassline: root on beat 1, fifth on beat 3
            tr_bass.append((bar_start_tick, 'on', root_note, vel_chord - 5, 3))
            tr_bass.append((bar_start_tick + 2 * tpb - 20, 'off', root_note, 0, 3))
            tr_bass.append((bar_start_tick + 2 * tpb, 'on', fifth_note, vel_chord, 3))
            tr_bass.append((bar_start_tick + 4 * tpb - 20, 'off', fifth_note, 0, 3))
            
    # --- 5. RENDER PERCUSSION (Palmas, Cajon, Castanets) ---
    for bar in range(num_bars):
        bar_start_tick = bar * 4 * tpb
        
        # Percussion section mutes
        is_silent = (mode == "song" and (bar < 4 or bar >= 28))
        if is_silent:
            continue
            
        is_verse = (mode == "song" and ((4 <= bar < 12) or (20 <= bar < 28)))
        
        if is_verse or (mode == "loop" and tension < 0.5):
            # Light Cajon beat: Kick on beat 1, Snare on beat 3, soft Palmas clap on upbeat
            for beat in range(4):
                b_tick = bar_start_tick + beat * tpb
                if beat == 0:
                    tr_perc.append((b_tick, 'on', 36, vel_perc - 10, 9))
                    tr_perc.append((b_tick + 100, 'off', 36, 0, 9))
                if beat == 2:
                    tr_perc.append((b_tick, 'on', 38, vel_perc - 15, 9))
                    tr_perc.append((b_tick + 100, 'off', 38, 0, 9))
                # Soft Handclap (Palmas) on upbeat of beat 2 and 4
                if beat in [1, 3]:
                    tr_perc.append((b_tick + tpb // 2, 'on', 39, vel_perc - 20, 9))
                    tr_perc.append((b_tick + tpb // 2 + 100, 'off', 39, 0, 9))
        else:
            # Full Chorus dynamic: heavy Cajon, fast Palmas, and Castanet rolls
            for beat in range(4):
                b_tick = bar_start_tick + beat * tpb
                # Cajon Kick on 1 and 3
                if beat in [0, 2]:
                    tr_perc.append((b_tick, 'on', 36, vel_perc, 9))
                    tr_perc.append((b_tick + 100, 'off', 36, 0, 9))
                # Cajon Snare on 2 and 4
                if beat in [1, 3]:
                    tr_perc.append((b_tick, 'on', 38, vel_perc - 5, 9))
                    tr_perc.append((b_tick + 100, 'off', 38, 0, 9))
                # Continuous Palmas claps on upbeat
                tr_perc.append((b_tick + tpb // 2, 'on', 39, vel_perc - 12, 9))
                tr_perc.append((b_tick + tpb // 2 + 100, 'off', 39, 0, 9))
                
                # Castanet rolls on last beat
                if beat == 3:
                    for r in range(4):
                        r_tick = b_tick + r * (tpb // 4)
                        tr_perc.append((r_tick, 'on', 85, vel_perc - 18, 9))
                        tr_perc.append((r_tick + 50, 'off', 85, 0, 9))
                        
    mid = build_midi_from_events([tr_chords, tr_lead, tr_cnt, tr_bass, tr_perc], tpb)
    
    m_clean = mood_prefix.replace(' ','_').replace('&','and').replace(',','')
    l_clean = label_name.replace(' ','_').replace('(','').replace(')','').replace('/','_')
    fname = f"Flamenco_{mode.capitalize()}_{m_clean}__{l_clean}__{root_name}_Minor"
    
    # Save file
    fpath = os.path.join(out_dir, fname + ".mid")
    idx = 1
    while os.path.exists(fpath):
        fpath = os.path.join(out_dir, f"{fname}_v{idx}.mid")
        idx += 1
        
    mid.save(fpath)
    print(f"\n  [SAVED]  {os.path.basename(fpath)}")
    print(f"  [PATH ]  {fpath}\n")
    return fname

# ── SPANISH FLAMENCO REDONE ──────────────────────────────────────────────────
# Authentic Spanish scales
SCALE_PHRYGIAN_DOMINANT = [0, 1, 4, 5, 7, 8, 10]   # Spanish Gypsy / Freygish
SCALE_DOUBLE_HARMONIC   = [0, 1, 4, 5, 7, 8, 11]   # Byzantine / Arabic
SCALE_PHRYGIAN_MODE     = [0, 1, 3, 5, 7, 8, 10]   # Classic Phrygian
SCALE_HARMONIC_MINOR    = [0, 2, 3, 5, 7, 8, 11]   # Mournful
SCALE_DORIAN_MODE       = [0, 2, 3, 5, 7, 9, 10]   # Passionate

# Map mood keys to suited Spanish scales and progressions
# Chord intervals are semitone offsets from root for triads
FLAMENCO_MOOD_DATA = {
    'melancholy': {
        'scales': [SCALE_PHRYGIAN_DOMINANT, SCALE_HARMONIC_MINOR],
        'progressions': [
            {'intervals': [(0,3,7), (8,12,15), (1,5,8), (7,11,14)], 'label': 'Soleá Lament'},
            {'intervals': [(0,3,7), (7,10,14), (8,12,15), (7,11,14)], 'label': 'Andalusian Tears'},
            {'intervals': [(0,3,7), (5,8,12), (1,5,8), (7,11,14)], 'label': 'Siguiriyas Grief'},
            {'intervals': [(0,3,7), (8,12,15), (5,8,12), (7,11,14)], 'label': 'Fado Tristeza'},
            {'intervals': [(0,3,7), (1,5,8), (0,3,7), (7,11,14)], 'label': 'Phrygian Weeping'},
            {'intervals': [(0,3,7), (5,8,12), (7,10,14), (0,3,7)], 'label': 'Austere Sorrow'},
        ],
    },
    'epic': {
        'scales': [SCALE_DOUBLE_HARMONIC, SCALE_PHRYGIAN_DOMINANT],
        'progressions': [
            {'intervals': [(0,3,7), (8,12,15), (3,7,10), (10,14,17)], 'label': 'Heroic Phrygian'},
            {'intervals': [(0,3,7), (7,10,14), (8,12,15), (10,14,17)], 'label': 'Battle March'},
            {'intervals': [(0,3,7), (5,8,12), (8,12,15), (10,14,17)], 'label': 'Epic Castilian'},
            {'intervals': [(0,3,7), (3,7,10), (10,14,17), (8,12,15)], 'label': 'Warrior Ballad'},
            {'intervals': [(0,3,7), (10,14,17), (8,12,15), (7,11,14)], 'label': 'Conquest Theme'},
            {'intervals': [(8,12,15), (3,7,10), (10,14,17), (0,3,7)], 'label': 'Triumphant Return'},
        ],
    },
    'nostalgic': {
        'scales': [SCALE_HARMONIC_MINOR, SCALE_DORIAN_MODE],
        'progressions': [
            {'intervals': [(0,3,7), (3,7,10), (8,12,15), (10,14,17)], 'label': 'Granadinas Memory'},
            {'intervals': [(0,3,7), (10,14,17), (3,7,10), (8,12,15)], 'label': 'Wistful Malagueña'},
            {'intervals': [(0,3,7), (8,12,15), (10,14,17), (3,7,10)], 'label': 'Faded Summer'},
            {'intervals': [(8,12,15), (10,14,17), (0,3,7), (7,10,14)], 'label': 'Golden Haze'},
            {'intervals': [(0,3,7), (5,8,12), (3,7,10), (10,14,17)], 'label': 'Childhood Echo'},
            {'intervals': [(0,3,7), (10,14,17), (8,12,15), (5,8,12)], 'label': 'Soft Reverie'},
        ],
    },
    'dark': {
        'scales': [SCALE_PHRYGIAN_MODE, SCALE_DOUBLE_HARMONIC],
        'progressions': [
            {'intervals': [(0,3,7), (1,5,8), (0,3,7), (10,14,17)], 'label': 'Templar Phrygian'},
            {'intervals': [(0,3,7), (8,12,15), (1,5,8), (0,3,7)], 'label': 'Dark Descent'},
            {'intervals': [(0,3,7), (5,8,12), (1,5,8), (7,11,14)], 'label': 'Gothic Thriller'},
            {'intervals': [(0,3,7), (1,5,8), (10,14,17), (0,3,7)], 'label': 'Assassin Theme'},
            {'intervals': [(0,3,7), (7,10,14), (1,5,8), (10,14,17)], 'label': 'Inquisition'},
            {'intervals': [(1,5,8), (0,3,7), (1,5,8), (10,14,17)], 'label': 'Gregorian Doom'},
        ],
    },
    'romantic': {
        'scales': [SCALE_HARMONIC_MINOR, SCALE_PHRYGIAN_DOMINANT],
        'progressions': [
            {'intervals': [(0,3,7), (8,12,15), (3,7,10), (10,14,17)], 'label': 'Lush Romance'},
            {'intervals': [(0,3,7), (3,7,10), (10,14,17), (8,12,15)], 'label': 'Emotional Sweep'},
            {'intervals': [(8,12,15), (10,14,17), (0,3,7), (3,7,10)], 'label': 'Anticipation'},
            {'intervals': [(0,3,7), (5,8,12), (8,12,15), (10,14,17)], 'label': 'Stirring Passion'},
            {'intervals': [(0,3,7), (8,12,15), (10,14,17), (5,8,12)], 'label': 'Tender Ache'},
            {'intervals': [(0,3,7), (8,12,15), (5,8,12), (3,7,10)], 'label': 'Moonlit Serenade'},
        ],
    },
    'hopeful': {
        'scales': [SCALE_DORIAN_MODE, SCALE_HARMONIC_MINOR],
        'progressions': [
            {'intervals': [(0,3,7), (3,7,10), (10,14,17), (8,12,15)], 'label': 'Rising Hope'},
            {'intervals': [(8,12,15), (3,7,10), (10,14,17), (0,3,7)], 'label': 'Victorious Resolve'},
            {'intervals': [(0,3,7), (10,14,17), (3,7,10), (8,12,15)], 'label': 'Lifting Spirits'},
            {'intervals': [(0,3,7), (5,8,12), (3,7,10), (10,14,17)], 'label': 'Cautious Hope'},
            {'intervals': [(3,7,10), (10,14,17), (8,12,15), (0,3,7)], 'label': 'Anthem of Light'},
            {'intervals': [(0,3,7), (8,12,15), (3,7,10), (5,8,12)], 'label': 'Morning Glow'},
        ],
    },
    'tragic': {
        'scales': [SCALE_DOUBLE_HARMONIC, SCALE_PHRYGIAN_DOMINANT],
        'progressions': [
            {'intervals': [(0,3,7), (7,10,14), (8,12,15), (10,14,17)], 'label': 'Tragic Climax'},
            {'intervals': [(0,3,7), (8,12,15), (3,7,10), (10,14,17)], 'label': 'Orchestral Tragedy'},
            {'intervals': [(0,3,7), (10,14,17), (1,5,8), (0,3,7)], 'label': 'Dark Fate'},
            {'intervals': [(0,3,7), (5,8,12), (7,10,14), (8,12,15)], 'label': 'Tragic Ascent'},
            {'intervals': [(0,3,7), (1,5,8), (7,10,14), (0,3,7)], 'label': 'Doomed Hero'},
            {'intervals': [(8,12,15), (0,3,7), (7,10,14), (10,14,17)], 'label': 'Last Stand'},
        ],
    },
}

# Map Quick Mood letters and Blend cluster keys to flamenco mood keys
_FLAMENCO_QUICK_MAP = {
    'a': 'dark',        # Dark & Ominous
    'b': 'melancholy',  # Melancholy & Deep Sorrow
    'c': 'nostalgic',   # Bittersweet & Nostalgic
    'd': 'epic',        # Epic & Heroic
}
_FLAMENCO_BLEND_MAP = {
    'A': 'melancholy',  # Sorrowful / Sad / Heartbreaking
    'B': 'romantic',    # Romantic / Emotional
    'C': 'nostalgic',   # Yearning / Nostalgic
    'D': 'hopeful',     # Hopeful / Uplifting
    'E': 'tragic',      # Tragic / Epic
}

def _flamenco_voice_chord(root_val, intervals):
    """Voice a chord as an authentic 6-string nylon guitar shape."""
    notes = sorted([root_val + iv for iv in intervals])
    base = notes[0]
    voicing = [base - 12, base]
    for n in notes[1:]:
        voicing.append(n)
    # Add high octave root drone
    voicing.append(base + 12)
    voicing = sorted(list(set(voicing)))
    return voicing[:6]

def _flamenco_generate_melody(root_val, scale, chord_intervals_seq, num_bars, tension, active_bars=None):
    """Generate an expressive Spanish lead melody biased toward chord tones.
    active_bars: set of bar indices where this track plays; None = all bars.
    """
    melody = []
    base = root_val + 36  # C5 register
    scale_notes = []
    for oct_off in [-24, -12, 0, 12, 24]:
        for t in scale:
            scale_notes.append(base + oct_off + t)
    scale_notes = sorted(list(set(n for n in scale_notes if 48 <= n <= 100)))
    if not scale_notes:
        scale_notes = [root_val + 48 + t for t in scale]

    cur_idx = len(scale_notes) // 2

    for bar in range(num_bars):
        # Call-and-response: rest on inactive bars
        if active_bars is not None and bar not in active_bars:
            melody.append((None, 4.0))
            continue

        chord_ivs = chord_intervals_seq[bar % len(chord_intervals_seq)]
        # Chord tones in the lead register
        chord_tones = set()
        for oct_off in [-12, 0, 12, 24]:
            for iv in chord_ivs:
                ct = root_val + iv + oct_off
                if 48 <= ct <= 100:
                    chord_tones.add(ct)
        chord_pool = [n for n in scale_notes if n in chord_tones]
        if not chord_pool:
            chord_pool = scale_notes

        beats_left = 4.0
        beat_pos = 0.0

        # Every 4th bar: dramatic sustained chord-tone with optional grace note
        if bar % 4 == 0:
            target = random.choice(chord_pool)
            if random.random() < 0.4:
                grace = target - 1
                melody.append((grace, 0.167))
                melody.append((target, 3.833))
            else:
                melody.append((target, 4.0))
            cur_idx = scale_notes.index(target) if target in scale_notes else cur_idx
            continue

        while beats_left > 0.01:
            # Descending run under high tension — stay near chord tones
            if tension >= 0.5 and beats_left >= 2.0 and random.random() < 0.5:
                step_dur = 0.167 if tension >= 0.7 else 0.333
                run_beats = min(2.0, beats_left)
                num_steps = int(run_beats / step_dur)
                start_idx = min(cur_idx + random.randint(2, 5), len(scale_notes) - 1)
                for s in range(num_steps):
                    idx = max(0, start_idx - s)
                    melody.append((scale_notes[idx], step_dur))
                    cur_idx = idx
                beats_left -= run_beats
                beat_pos += run_beats
            else:
                pool = [0.5, 0.5, 1.0, 1.0, 1.5, 2.0]
                filtered = [d for d in pool if d <= beats_left]
                dur = random.choice(filtered) if filtered else beats_left

                # 65% chance: snap to a chord tone; otherwise step-wise
                if random.random() < 0.65 and chord_pool:
                    pitch = random.choice(chord_pool)
                    new_idx = min(range(len(scale_notes)), key=lambda i: abs(scale_notes[i] - pitch))
                    cur_idx = new_idx
                else:
                    step = random.choice([-2, -1, -1, 0, 1, 1, 2])
                    if random.random() < 0.15:
                        step = random.choice([-4, -3, 3, 4])
                    cur_idx = max(0, min(len(scale_notes) - 1, cur_idx + step))
                    pitch = scale_notes[cur_idx]

                # Grace note ornament
                if dur >= 0.5 and random.random() < 0.25:
                    grace = pitch - 1
                    melody.append((grace, 0.125))
                    melody.append((pitch, dur - 0.125))
                else:
                    melody.append((pitch, dur))

                beats_left -= dur
                beat_pos += dur

    return melody

def _flamenco_generate_counter(root_val, chord_intervals_seq, scale, num_bars, tension, active_bars=None):
    """Generate supporting counter-melody with alzapua bass runs.
    active_bars: set of bar indices where this track plays; None = all bars.
    """
    counter = []
    base = root_val + 12  # C3 register
    scale_notes = []
    for oct_off in [-24, -12, 0, 12, 24]:
        for t in scale:
            scale_notes.append(base + oct_off + t)
    scale_notes = sorted(list(set(n for n in scale_notes if 28 <= n <= 72)))
    if not scale_notes:
        scale_notes = [root_val + t for t in scale]

    cur_idx = len(scale_notes) // 3

    for bar in range(num_bars):
        # Call-and-response: rest on inactive bars
        if active_bars is not None and bar not in active_bars:
            counter.append((None, 4.0))
            continue

        chord_ivs = chord_intervals_seq[bar % len(chord_intervals_seq)]
        root_note = root_val + chord_ivs[0]
        while root_note < 36:
            root_note += 12
        while root_note > 60:
            root_note -= 12
        
        beats_left = 4.0
        
        if tension >= 0.55 and random.random() < 0.6:
            # Alzapua thumb sweep pattern
            fifth_note = root_note + 7
            if fifth_note > 64:
                fifth_note -= 12
            while beats_left > 0.01:
                step_dur = 0.333
                if beats_left >= step_dur * 3:
                    counter.append((root_note, step_dur))
                    counter.append((fifth_note, step_dur))
                    counter.append((root_note + 12, step_dur))
                    beats_left -= step_dur * 3
                else:
                    counter.append((root_note, beats_left))
                    beats_left = 0.0
        else:
            # Fingerstyle counterpoint
            while beats_left > 0.01:
                pool = [0.5, 1.0, 1.5, 2.0]
                filtered = [d for d in pool if d <= beats_left]
                dur = random.choice(filtered) if filtered else beats_left
                
                step = random.choice([-2, -1, 0, 1, 1, 2])
                cur_idx = max(0, min(len(scale_notes) - 1, cur_idx + step))
                pitch = scale_notes[cur_idx]
                counter.append((pitch, dur))
                beats_left -= dur
    
    return counter

def generate_flamenco_redone(out_dir, root_val, root_name, bpm, tension,
                              mood_key, label_name, mood_prefix):
    """
    Re-engineered Spanish Flamenco Nylon Guitar generator.
    Outputs exactly 3 tracks: Chords, Counter Melody, Lead Melody.
    """
    tpb = 480
    num_bars = 8  # 8-bar compositions
    
    # Select mood data
    mood_data = FLAMENCO_MOOD_DATA.get(mood_key, FLAMENCO_MOOD_DATA['melancholy'])
    scale = random.choice(mood_data['scales'])
    prog_entry = random.choice(mood_data['progressions'])
    prog_label = prog_entry['label']
    chord_intervals_seq = prog_entry['intervals']
    
    # Velocity from tension
    vel_chord = int(65 + tension * 40)
    vel_lead = int(75 + tension * 35)
    vel_cnt = int(55 + tension * 30)

    # --- Call-and-Response bar assignment ---
    # Counter ("call") plays bars 0,1,4,5 — lower register, anchoring phrases
    # Lead ("response") plays bars 2,3,6,7 — upper register, answering phrases
    # Bar 7 is the climax: BOTH play together for maximum emotion
    counter_bars = {0, 1, 4, 5, 7}   # call + climax
    lead_bars    = {2, 3, 6, 7}       # response + climax
    
    # --- Build 3 tracks ---
    tr_chords = [(0, 'program', 24, 0, 0), (0, 'tempo', bpm, 0, 0)]  # Nylon Guitar
    tr_counter = [(0, 'program', 24, 0, 1)]   # Nylon Guitar
    tr_lead = [(0, 'program', 24, 0, 2)]      # Nylon Guitar
    
    # --- TRACK 1: CHORDS (Strumming, Rasgueados, Syncopated Triplets) ---
    for bar in range(num_bars):
        bar_start = bar * 4 * tpb
        chord_ivs = chord_intervals_seq[bar % len(chord_intervals_seq)]
        voicing = _flamenco_voice_chord(root_val, chord_ivs)
        
        pattern = random.choice(['strum', 'rasgueado', 'triplet_strum'])
        if tension >= 0.7:
            pattern = random.choice(['rasgueado', 'rasgueado', 'triplet_strum'])
        elif tension < 0.4:
            pattern = random.choice(['strum', 'strum', 'triplet_strum'])

        if pattern == 'strum':
            # Full chord strum on every beat — all voicing notes, slight downward stagger
            for beat in range(4):
                beat_tick = bar_start + beat * tpb
                stagger_step = random.randint(8, 18)
                sustain = tpb - 20
                for i, note in enumerate(voicing):
                    on_t = beat_tick + i * stagger_step
                    tr_chords.append((max(0, on_t), 'on', note, vel_chord - i * 2 + random.randint(-4, 4), 0))
                    tr_chords.append((beat_tick + sustain, 'off', note, 0, 0))
        elif pattern == 'rasgueado':
            # Aggressive strum rolls on beats 1 and 3 — all notes sustain 2 beats
            for beat in [0, 2]:
                beat_tick = bar_start + beat * tpb
                stagger_step = random.randint(12, 22)
                sustain = 2 * tpb - 30
                for i, note in enumerate(voicing):
                    on_t = beat_tick + i * stagger_step + random.randint(-3, 3)
                    tr_chords.append((max(0, on_t), 'on', note, vel_chord - i * 2 + random.randint(-3, 3), 0))
                    tr_chords.append((beat_tick + sustain, 'off', note, 0, 0))
            generate_cc_curve(tr_chords, 11, bar_start, 2 * tpb, start_val=100, end_val=55, curve_type="exp_decay", ch=0)
        else:
            # Syncopated triplet strums — ALL chord notes at every hit
            triplet_offsets = [0, 160, 320, 640, 800, 960, 1280, 1440, 1680]
            bar_end = bar_start + 4 * tpb
            for t_off in triplet_offsets:
                tick = bar_start + t_off
                stagger_step = random.randint(6, 14)
                vel_base = vel_chord - 6 + random.randint(-5, 5)
                for i, note in enumerate(voicing):
                    on_t = tick + i * stagger_step
                    if on_t < bar_end:
                        vel = max(10, min(127, vel_base - i))
                        tr_chords.append((max(0, on_t), 'on', note, vel, 0))
                        tr_chords.append((on_t + 130, 'off', note, 0, 0))
    
    # --- TRACK 2: COUNTER MELODY ---
    counter_notes = _flamenco_generate_counter(root_val, chord_intervals_seq, scale, num_bars, tension, active_bars=counter_bars)
    current_tick = 0
    for note, duration in counter_notes:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        stagger = random.randint(-5, 5)
        vel = vel_cnt + random.randint(-6, 6)
        vel = max(10, min(127, vel))
        tr_counter.append((max(0, current_tick + stagger), 'on', note, vel, 1))
        tr_counter.append((current_tick + dur_ticks - 12, 'off', note, 0, 1))
        current_tick += dur_ticks
    
    # --- TRACK 3: LEAD / TOP MELODY ---
    melody_notes = _flamenco_generate_melody(root_val, scale, chord_intervals_seq, num_bars, tension, active_bars=lead_bars)
    current_tick = 0
    for note, duration in melody_notes:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        
        # Tremolo picking on long notes under high tension
        if tension >= 0.5 and duration >= 1.5:
            num_repeats = int(duration * 5)
            if num_repeats > 0:
                repeat_dur = dur_ticks // num_repeats
                for r in range(num_repeats):
                    r_tick = current_tick + r * repeat_dur
                    progress = r / float(num_repeats)
                    vel = int((vel_lead - 30) + progress * 45)
                    vel = max(10, min(127, vel))
                    stagger = random.randint(-4, 4)
                    tr_lead.append((max(0, r_tick + stagger), 'on', note, vel, 2))
                    tr_lead.append((r_tick + repeat_dur - 8, 'off', note, 0, 2))
                # Crescendo swell
                generate_cc_curve(tr_lead, 11, current_tick, dur_ticks, start_val=50, end_val=vel_lead, curve_type="crescendo", ch=2)
        else:
            stagger = random.randint(-5, 5)
            vel = vel_lead + random.randint(-6, 6)
            vel = max(10, min(127, vel))
            tr_lead.append((max(0, current_tick + stagger), 'on', note, vel, 2))
            tr_lead.append((current_tick + dur_ticks - 10, 'off', note, 0, 2))
        
        current_tick += dur_ticks
    
    # --- BUILD AND SAVE ---
    mid = build_midi_from_events([tr_chords, tr_counter, tr_lead], tpb)
    
    # Determine scale name for filename
    scale_name = "Spanish"
    if scale == SCALE_PHRYGIAN_DOMINANT:
        scale_name = "PhrygianDominant"
    elif scale == SCALE_DOUBLE_HARMONIC:
        scale_name = "DoubleHarmonic"
    elif scale == SCALE_PHRYGIAN_MODE:
        scale_name = "Phrygian"
    elif scale == SCALE_HARMONIC_MINOR:
        scale_name = "HarmonicMinor"
    elif scale == SCALE_DORIAN_MODE:
        scale_name = "Dorian"
    
    m_clean = mood_prefix.replace(' ','_').replace('&','and').replace(',','')
    l_clean = prog_label.replace(' ','_').replace('(','').replace(')','').replace('/','_')
    fname = f"Flamenco_{m_clean}__{l_clean}__{root_name}_{scale_name}__{bpm}BPM"
    
    fpath = os.path.join(out_dir, fname + ".mid")
    idx = 1
    while os.path.exists(fpath):
        fpath = os.path.join(out_dir, f"{fname}_v{idx}.mid")
        idx += 1
    
    mid.save(fpath)
    print(f"\n  [SAVED]  {os.path.basename(fpath)}")
    print(f"  [PATH ]  {fpath}\n")
    return fname

def generate_templar_chants(mode, out_dir, root_val, root_name, chords, melody, counter, tension, label_name, mood_prefix):
    """
    Generates Sacred Liturgical Choirs using authentic organum fifth beds,
    cathedral organ drones, tubular bells, and orchestral timpani.
    """
    tpb = 480
    bpm, vel_chord, vel_lead, vel_perc = get_tempo_and_velocity_modifiers(tension)
    
    # 6 tracks: Choir Bed (Ch 0), Choir Lead (Ch 1), Choir Counter (Ch 2), Organ Pedal (Ch 3), Bells (Ch 4), Timpani (Ch 9)
    tr_choir = [(0, 'program', 52, 0, 0), (0, 'tempo', bpm, 0, 0)]  # Choir Aahs
    tr_lead  = [(0, 'program', 53, 0, 1)]                          # Voice Oohs
    tr_cnt   = [(0, 'program', 54, 0, 2)]                          # Synth Voice
    tr_organ = [(0, 'program', 19, 0, 3)]                          # Church Organ
    tr_bells = [(0, 'program', 14, 0, 4)]                          # Tubular Bells
    tr_perc  = []                                                  # Orchestral Drums
    
    num_bars = len(chords)
    
    # --- 1. RENDER CHORAL BED (Organum Fifths & Octaves) ---
    for bar in range(num_bars):
        bar_start_tick = bar * 4 * tpb
        voicing = get_templar_organum_voicing(chords[bar])
        
        # Whole note sustained chords
        for note in voicing:
            tr_choir.append((bar_start_tick, 'on', note, vel_chord, 0))
            tr_choir.append((bar_start_tick + 4 * tpb - 30, 'off', note, 0, 0))
            
        # Slow cathedral choir breath swells
        generate_cc_curve(tr_choir, 11, bar_start_tick, 4 * tpb, start_val=60, end_val=85, curve_type="sine", ch=0)
        generate_cc_curve(tr_choir, 1, bar_start_tick, 4 * tpb, start_val=55, end_val=80, curve_type="sine", ch=0)
            
    # --- 2. RENDER CHORAL LEAD (Legato Melismatic Chant) ---
    current_tick = 0
    for note, duration in melody:
        dur_ticks = int(duration * tpb)
        
        if note is None:
            current_tick += dur_ticks
            continue
            
        bar_idx = current_tick // (4 * tpb)
        is_muted = (mode == "song" and bar_idx >= 28) # Mute lead in outro
        
        if is_muted:
            current_tick += dur_ticks
            continue
            
        # Gregorian chants are sustained, legato lines.
        tr_lead.append((current_tick, 'on', note, vel_lead, 1))
        tr_lead.append((current_tick + dur_ticks - 20, 'off', note, 0, 1))
        
        # Legato melismatic swells
        generate_cc_curve(tr_lead, 11, current_tick, dur_ticks, start_val=50, end_val=vel_lead, curve_type="sine", ch=1)
        generate_cc_curve(tr_lead, 1, current_tick, dur_ticks, start_val=45, end_val=vel_lead + 5, curve_type="sine", ch=1)
        
        current_tick += dur_ticks
        
    # --- 3. RENDER CHORAL COUNTER (Synth Voice Counterpoint) ---
    current_tick = 0
    for note, duration in counter:
        dur_ticks = int(duration * tpb)
        
        if note is None:
            current_tick += dur_ticks
            continue
            
        bar_idx = current_tick // (4 * tpb)
        # Counter-melody only enters in Chorus (12-20) and Verse 2 (20-28)
        is_muted = (mode == "song" and (bar_idx < 12 or bar_idx >= 28))
        if mode == "loop" and tension < 0.4:
            is_muted = True
            
        if not is_muted:
            # Shift down to alto register
            safe_note = note
            while safe_note > 69:
                safe_note -= 12
                
            tr_cnt.append((current_tick, 'on', safe_note, vel_lead - 15, 2))
            tr_cnt.append((current_tick + dur_ticks - 25, 'off', safe_note, 0, 2))
            
            # Counterpoint voice swells
            generate_cc_curve(tr_cnt, 11, current_tick, dur_ticks, start_val=45, end_val=vel_lead - 10, curve_type="sine", ch=2)
            
        current_tick += dur_ticks
        
    # --- 4. RENDER ORGAN PEDAL DRONE ---
    for bar in range(num_bars):
        bar_start_tick = bar * 4 * tpb
        voicing = get_templar_organum_voicing(chords[bar])
        pedal_note = voicing[0] - 12  # Very low sub-bass drone
        
        tr_organ.append((bar_start_tick, 'on', pedal_note, vel_chord - 8, 3))
        tr_organ.append((bar_start_tick + 4 * tpb - 30, 'off', pedal_note, 0, 3))
        
        # Sub-bass organ dynamic swells
        generate_cc_curve(tr_organ, 11, bar_start_tick, 4 * tpb, start_val=60, end_val=80, curve_type="sine", ch=3)
        
    # --- 5. RENDER TUBULAR BELLS (Downbeat Accents) ---
    for bar in range(num_bars):
        bar_start_tick = bar * 4 * tpb
        
        # Bells play on beat 1 of every 2nd bar in Verse, and every bar in Chorus
        is_verse = (mode == "song" and ((4 <= bar < 12) or (20 <= bar < 28)))
        is_chorus = (mode == "song" and (12 <= bar < 20))
        
        is_bell = True
        if is_verse and (bar % 2 != 0):
            is_bell = False
        if mode == "song" and (bar < 4 or bar >= 28): # mute in intro/outro
            is_bell = False
            
        if is_bell:
            voicing = get_templar_organum_voicing(chords[bar])
            bell_note = voicing[3]  # Accent high octave root
            tr_bells.append((bar_start_tick, 'on', bell_note, vel_chord + 15, 4))
            tr_bells.append((bar_start_tick + 3 * tpb, 'off', bell_note, 0, 4))
            
            # Tubular bells decay envelope
            generate_cc_curve(tr_bells, 11, bar_start_tick, 3 * tpb, start_val=105, end_val=50, curve_type="exp_decay", ch=4)
            
    # --- 6. RENDER ORCHESTRAL TIMPANI & BASS DRUM ---
    for bar in range(num_bars):
        bar_start_tick = bar * 4 * tpb
        
        is_silent = (mode == "song" and (bar < 4 or bar >= 28))
        if is_silent:
            continue
            
        # Heavy downbeat concert drum (note 35)
        tr_perc.append((bar_start_tick, 'on', 35, vel_perc, 9))
        tr_perc.append((bar_start_tick + 200, 'off', 35, 0, 9))
        
        # Timpani roll (note 47) into beat 3 for high tension / chorus
        is_chorus = (mode == "song" and (12 <= bar < 20))
        if is_chorus or (mode == "loop" and tension >= 0.5):
            roll_start = bar_start_tick + 2 * tpb - 240
            for r in range(4):
                r_tick = roll_start + r * 60
                tr_perc.append((r_tick, 'on', 47, vel_perc - 20 + r * 8, 9))
                tr_perc.append((r_tick + 50, 'off', 47, 0, 9))
                
            generate_cc_curve(tr_perc, 11, roll_start, 240, start_val=40, end_val=90, curve_type="crescendo", ch=9)
                
            # Heavy Timpani accent on beat 3
            tr_perc.append((bar_start_tick + 2 * tpb, 'on', 47, vel_perc + 5, 9))
            tr_perc.append((bar_start_tick + 2 * tpb + 200, 'off', 47, 0, 9))
            
    mid = build_midi_from_events([tr_choir, tr_lead, tr_cnt, tr_organ, tr_bells, tr_perc], tpb)
    
    m_clean = mood_prefix.replace(' ','_').replace('&','and').replace(',','')
    l_clean = label_name.replace(' ','_').replace('(','').replace(')','').replace('/','_')
    fname = f"Sacred_Liturgical_{mode.capitalize()}_{m_clean}__{l_clean}__{root_name}_Minor"
    
    # Save file
    fpath = os.path.join(out_dir, fname + ".mid")
    idx = 1
    while os.path.exists(fpath):
        fpath = os.path.join(out_dir, f"{fname}_v{idx}.mid")
        idx += 1
        
    mid.save(fpath)
    print(f"\n  [SAVED]  {os.path.basename(fpath)}")
    print(f"  [PATH ]  {fpath}\n")
    return fname


def generate_symphonic_choir(mode, out_dir, root_val, root_name, chords, melody, counter, tension, label_name, mood_prefix):
    tpb = 480
    
    # Tracks:
    # 0 = Soprano (52)
    # 1 = Alto (52)
    # 2 = Tenor (52)
    # 3 = Bass (52)
    # 4 = High Strings (48)
    # 5 = Low Strings (43)
    # 6 = Woodwinds (73)
    # 7 = Epic Brass (56)
    # 8 = Timpani (47)
    # 9 = Percussion (Ch 9)
    
    tracks = [[] for _ in range(10)]
    programs = [(0, 52), (1, 52), (2, 52), (3, 52), (4, 48), (5, 43), (6, 73), (7, 56), (8, 47), (9, 0)]
    
    for i, (ch, prog) in enumerate(programs):
        if i == 9: continue # Ch 9 is percussion
        tracks[i].append((0, 'program', prog, 0, ch))
        
    num_bars = len(chords)
    
    # 1. RENDER CHORDS (SATB + Brass + Low Strings)
    for bar_idx in range(num_bars):
        bar_start_tick = bar_idx * 4 * tpb
        chord = chords[bar_idx]
        
        pcs = sorted(list(set(n % 12 for n in chord)))
        root_pc = pcs[0]
        
        bass = 36 + root_pc
        tenor = 48 + pcs[1 % len(pcs)]
        alto = 55 + pcs[2 % len(pcs)]
        soprano = 60 + root_pc
        if soprano <= alto: soprano += 12
        if alto <= tenor: alto += 12
        
        vel_choir = int(70 + tension * 30)
        vel_choir = min(127, vel_choir)
        
        for i, pitch in enumerate([soprano, alto, tenor, bass]):
            tracks[i].append((bar_start_tick, 'on', pitch, vel_choir, i))
            tracks[i].append((bar_start_tick + 4 * tpb - 20, 'off', pitch, 0, i))
            
        tracks[5].append((bar_start_tick, 'on', bass, min(127, vel_choir + 10), 5))
        tracks[5].append((bar_start_tick + 4 * tpb - 20, 'off', bass, 0, 5))
        tracks[5].append((bar_start_tick, 'on', bass - 12, min(127, vel_choir + 10), 5))
        tracks[5].append((bar_start_tick + 4 * tpb - 20, 'off', bass - 12, 0, 5))
        
        if tension > 0.5:
            fifth_pc = pcs[2 % len(pcs)] if len(pcs) > 2 else pcs[1 % len(pcs)]
            brass_notes = [bass, bass + 12, bass + 12 + ((fifth_pc - root_pc) % 12)]
            for bn in brass_notes:
                tracks[7].append((bar_start_tick, 'on', bn, min(127, vel_choir + 15), 7))
                tracks[7].append((bar_start_tick + 4 * tpb - 20, 'off', bn, 0, 7))
                
        if bar_idx % 2 == 0 or tension > 0.6:
            tracks[8].append((bar_start_tick, 'on', 47, min(127, vel_choir + 20), 8))
            tracks[8].append((bar_start_tick + 240, 'off', 47, 0, 8))
            
        if tension > 0.4:
            for beat in range(4):
                tick = bar_start_tick + beat * tpb
                vel_drum = vel_choir if beat == 0 else vel_choir - 20
                tracks[9].append((tick, 'on', 41, max(1, vel_drum), 9))
                tracks[9].append((tick + 120, 'off', 41, 0, 9))
                if tension > 0.7:
                    tracks[9].append((tick + tpb//2, 'on', 43, max(1, vel_drum - 10), 9))
                    tracks[9].append((tick + tpb//2 + 120, 'off', 43, 0, 9))
                    
    # 2. RENDER MELODY
    current_tick = 0
    for note, duration in melody:
        dur_ticks = int(duration * tpb)
        if note is not None:
            pitch = note
            while pitch < 72: pitch += 12
            while pitch > 84: pitch -= 12
            
            vel = int(80 + tension * 30)
            vel = min(127, vel)
            
            tracks[4].append((current_tick, 'on', pitch, vel, 4))
            tracks[4].append((current_tick + dur_ticks - 10, 'off', pitch, 0, 4))
            tracks[4].append((current_tick, 'on', pitch - 12, max(1, vel - 10), 4))
            tracks[4].append((current_tick + dur_ticks - 10, 'off', pitch - 12, 0, 4))
            
            if tension > 0.3:
                tracks[6].append((current_tick, 'on', pitch + 12, max(1, vel - 5), 6))
                tracks[6].append((current_tick + dur_ticks - 10, 'off', pitch + 12, 0, 6))
                
            tracks[0].append((current_tick, 'on', pitch, vel, 0))
            tracks[0].append((current_tick + dur_ticks - 10, 'off', pitch, 0, 0))
            
        current_tick += dur_ticks
        
    # 3. RENDER COUNTER MELODY
    current_tick = 0
    for note, duration in counter:
        dur_ticks = int(duration * tpb)
        if note is not None:
            pitch = note
            while pitch < 55: pitch += 12
            while pitch > 67: pitch -= 12
            
            vel = int(70 + tension * 20)
            vel = min(127, vel)
            
            tracks[1].append((current_tick, 'on', pitch, vel, 1))
            tracks[1].append((current_tick + dur_ticks - 10, 'off', pitch, 0, 1))
            tracks[2].append((current_tick, 'on', pitch - 12, vel, 2))
            tracks[2].append((current_tick + dur_ticks - 10, 'off', pitch - 12, 0, 2))
            
            tracks[4].append((current_tick, 'on', pitch, vel, 4))
            tracks[4].append((current_tick + dur_ticks - 10, 'off', pitch, 0, 4))
            
        current_tick += dur_ticks

    mid = build_midi_from_events(tracks, tpb)
    
    m_clean = mood_prefix.replace(' ','_').replace('&','and').replace(',','')
    l_clean = label_name.replace(' ','_').replace('(','').replace(')','').replace('/','_')
    fname = f"Symphonic_Choir_{mode.capitalize()}_{m_clean}__{l_clean}__{root_name}_Minor"
    
    fpath = os.path.join(out_dir, fname + ".mid")
    idx = 1
    while os.path.exists(fpath):
        fpath = os.path.join(out_dir, f"{fname}_v{idx}.mid")
        idx += 1
        
    mid.save(fpath)
    print(f"\n  [SAVED]  {os.path.basename(fpath)}")
    print(f"  [PATH ]  {fpath}\n")
    return fname
