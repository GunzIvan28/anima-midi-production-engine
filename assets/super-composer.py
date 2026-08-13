# -*- coding: utf-8 -*-
"""
ANIMA SUPER COMPOSER Specialist Style
-- Automated Orchestration Engine --
Parses an existing MIDI file, extracts key, scale, and tempo,
and generates a harmonically aligned 7-channel arrangement:
  Ch 0: Chord Pad (GM 89 Warm Pad)
  Ch 1: Rhythmic Bed (GM 49 String Ensemble 2)
  Ch 2: Lead Melody (GM 40 Violin)
  Ch 3: Counter Melody (GM 41 Viola)
  Ch 4: Arpeggio Bed (GM 46 Harp)
  Ch 5: Violin 1 (GM 40 Violin)
  Ch 6: Violin 2 (GM 40 Violin)
"""

import os
import sys
import math
import random
import mido

# Ensure assets directory is in path for imports
assets_dir = os.path.dirname(os.path.abspath(__file__))
if assets_dir not in sys.path:
    sys.path.append(assets_dir)

import VVC
import specialist_styles

def generate_lead_melody(root_pc, scale, chords, tension):
    """Generates an expressive main melody Snap-focused to chord tones and scale."""
    melody = []
    num_bars = len(chords)
    tpb = 480
    
    # Build scale notes in range 72 to 93 (Violin lead register)
    scale_notes = []
    for octave in [60, 72, 84]:
        for pitch_class in scale:
            scale_notes.append(octave + pitch_class)
    scale_notes = sorted(list(set(n for n in scale_notes if 69 <= n <= 93)))
    
    if not scale_notes:
        scale_notes = [72, 74, 76, 77, 79, 81, 83]
        
    cur_idx = len(scale_notes) // 2
    
    for bar in range(num_bars):
        # rest on some bars to create phrasing and room to breathe
        is_rest = (bar % 4 == 2 and random.random() < 0.4)
        if is_rest:
            melody.append((None, 4.0))
            continue
            
        chord_pcs = [n % 12 for n in chords[bar]]
        chord_pool = [n for n in scale_notes if n % 12 in chord_pcs]
        if not chord_pool:
            chord_pool = scale_notes
            
        beats_left = 4.0
        while beats_left > 0.01:
            pool = [0.5, 1.0, 1.5, 2.0]
            filtered = [d for d in pool if d <= beats_left]
            dur = random.choice(filtered) if filtered else beats_left
            
            strong = (beats_left % 2.0 < 0.01) or (beats_left % 1.0 < 0.01)
            if strong and random.random() < 0.7:
                pitch = random.choice(chord_pool)
                if pitch in scale_notes:
                    cur_idx = scale_notes.index(pitch)
            else:
                step = random.choice([-2, -1, 0, 1, 2])
                cur_idx = max(0, min(len(scale_notes) - 1, cur_idx + step))
                pitch = scale_notes[cur_idx]
                
            melody.append((pitch, dur))
            beats_left -= dur
            
    return melody


def generate_counter_melody(root_pc, scale, chords, tension):
    """Generates contrary and oblique counterpoint melody in the lower register."""
    counter = []
    num_bars = len(chords)
    tpb = 480
    
    # Viola Counter Register (48 to 72)
    scale_notes = []
    for octave in [48, 60]:
        for pitch_class in scale:
            scale_notes.append(octave + pitch_class)
    scale_notes = sorted(list(set(n for n in scale_notes if 48 <= n <= 72)))
    
    if not scale_notes:
        scale_notes = [48, 50, 52, 53, 55, 57, 59, 60]
        
    cur_idx = len(scale_notes) // 2
    
    for bar in range(num_bars):
        # Rest when lead plays complex parts or periodically
        is_rest = (bar % 4 == 0 and random.random() < 0.35)
        if is_rest:
            counter.append((None, 4.0))
            continue
            
        chord_pcs = [n % 12 for n in chords[bar]]
        chord_pool = [n for n in scale_notes if n % 12 in chord_pcs]
        if not chord_pool:
            chord_pool = scale_notes
            
        beats_left = 4.0
        while beats_left > 0.01:
            pool = [1.0, 2.0, 4.0]
            filtered = [d for d in pool if d <= beats_left]
            dur = random.choice(filtered) if filtered else beats_left
            
            pitch = random.choice(chord_pool)
            counter.append((pitch, dur))
            beats_left -= dur
            
    return counter


def super_compose_over_midi(filepath, out_dir, tension=0.65):
    """
    Core composition engine that takes an input MIDI file, detects its key/scale/BPM,
    and returns a beautifully orchestrated 7-track MidiFile object.
    """
    print(f"\n  Analyzing: {os.path.basename(filepath)} ...")
    
    # 1. Parse timeline and detect chords
    try:
        chord_groups, src_tpb = VVC.parse_midi_chords(filepath)
    except Exception as e:
        print(f"  [ERROR] Could not read file: {e}")
        return None, None

    if not chord_groups:
        print("  [ERROR] No chord progression detected in MIDI. Exiting.")
        return None, None

    # Detect key and tempo
    root_name, root_pc, scale, scale_name, is_minor = VVC.detect_key(chord_groups)
    bpm = VVC.detect_tempo(filepath)
    num_bars = len(chord_groups)

    print(f"  [DETECTED] Key   : {root_name} {scale_name}")
    print(f"  [DETECTED] Tempo : {bpm} BPM")
    print(f"  [DETECTED] Length: {num_bars} bars detected.")

    tpb = src_tpb
    tracks_events = [[] for _ in range(7)]

    # Setup track programs
    programs = [89, 49, 40, 41, 46, 40, 40]
    for ch, prog in enumerate(programs):
        tracks_events[ch].append((0, 'program', prog, 0, ch))
        tracks_events[ch].append((0, 'tempo', bpm, 0, ch))

    # 2. Voice-lead chord progression for pad/arpeggio references
    chords = []
    prev_voicing = []
    for bar in range(num_bars):
        pcs = chord_groups[bar]
        root_pc_bar = pcs[0]
        third_pc = pcs[1 % len(pcs)]
        fifth_pc = pcs[2 % len(pcs)] if len(pcs) > 2 else pcs[1 % len(pcs)]
        target_pcs = [root_pc_bar, third_pc, fifth_pc]
        
        if bar == 0 or not prev_voicing:
            voicing = sorted(list(set([
                48 + root_pc_bar, 48 + third_pc, 48 + fifth_pc,
                60 + root_pc_bar, 60 + third_pc, 60 + fifth_pc
            ])))
        else:
            voicing = VVC.voice_lead_chord(prev_voicing, target_pcs, register_min=48, register_max=72)
        prev_voicing = voicing
        chords.append(voicing)

    # --- 3. GENERATE TRACK EVENTS ---

    # Track 0: Chord Pad (GM 89 Warm Pad)
    for bar in range(num_bars):
        bar_start = bar * 4 * tpb
        voicing = chords[bar]
        vel_pad = int(48 + tension * 20)
        for note in voicing:
            tracks_events[0].append((bar_start, 'on', note, vel_pad, 0))
            tracks_events[0].append((bar_start + 4 * tpb - 15, 'off', note, 0, 0))
            
        specialist_styles.generate_cc_curve(tracks_events[0], 1, bar_start, 4 * tpb,
                                             start_val=50, end_val=int(60 + tension * 25), curve_type="sine", ch=0)
        specialist_styles.generate_cc_curve(tracks_events[0], 11, bar_start, 4 * tpb,
                                             start_val=45, end_val=int(55 + tension * 30), curve_type="linear", ch=0)

    # Track 1: Rhythmic Bed (GM 49 String Ensemble 2)
    for bar in range(num_bars):
        bar_start = bar * 4 * tpb
        voicing = chords[bar]
        low_note = voicing[0] - 12
        high_notes = [voicing[1], voicing[2], voicing[3 % len(voicing)]]
        
        # Bow-aware eighth note ostinato
        for step in range(8):
            beat_pos = step * 0.5
            tick = bar_start + int(beat_pos * tpb)
            is_downbeat = (step % 2 == 0)
            
            if is_downbeat:
                pitch = low_note
                vel = int(64 + tension * 20)
            else:
                pitch = high_notes[(step // 2) % len(high_notes)]
                vel = int(48 + tension * 15)
                
            vel += random.randint(-4, 4)
            vel = max(10, min(127, vel))
            
            tracks_events[1].append((tick, 'on', pitch, vel, 1))
            tracks_events[1].append((tick + int(0.35 * tpb), 'off', pitch, 0, 1))

        specialist_styles.generate_cc_curve(tracks_events[1], 11, bar_start, 4 * tpb,
                                             start_val=int(50 + tension * 18),
                                             end_val=int(70 + tension * 18),
                                             curve_type="sine", ch=1)

    # Track 2: Lead Melody (GM 40 Violin)
    melody_notes = generate_lead_melody(root_pc, scale, chords, tension)
    current_tick = 0
    for note, duration in melody_notes:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel = int(72 + tension * 25)
        stagger = random.randint(-4, 4)
        on_t = max(0, current_tick + stagger)
        tracks_events[2].append((on_t, 'on', note, min(127, vel), 2))
        tracks_events[2].append((current_tick + dur_ticks - 15, 'off', note, 0, 2))
        
        c_type = "crescendo" if duration >= 2.0 and random.random() < 0.5 else "sine"
        specialist_styles.generate_cc_curve(tracks_events[2], 1, current_tick, dur_ticks,
                                             start_val=55, end_val=int(75 + tension * 20), curve_type=c_type, ch=2)
        specialist_styles.generate_cc_curve(tracks_events[2], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=int(70 + tension * 25), curve_type="sine", ch=2)
        current_tick += dur_ticks

    # Track 3: Counter Melody (GM 41 Viola)
    counter_notes = generate_counter_melody(root_pc, scale, chords, tension)
    current_tick = 0
    for note, duration in counter_notes:
        dur_ticks = int(duration * tpb)
        if note is None:
            current_tick += dur_ticks
            continue
        vel = int(60 + tension * 20)
        stagger = random.randint(-4, 4)
        on_t = max(0, current_tick + stagger)
        tracks_events[3].append((on_t, 'on', note, min(127, vel), 3))
        tracks_events[3].append((current_tick + dur_ticks - 15, 'off', note, 0, 3))
        
        specialist_styles.generate_cc_curve(tracks_events[3], 11, current_tick, dur_ticks,
                                             start_val=50, end_val=int(66 + tension * 20), curve_type="sine", ch=3)
        current_tick += dur_ticks

    # Track 4: Arpeggio Bed (GM 46 Harp)
    for bar in range(num_bars):
        bar_start = bar * 4 * tpb
        voicing = chords[bar]
        sweep = voicing + list(reversed(voicing[1:-1]))
        if not sweep:
            sweep = [60]
            
        step_dur = tpb // 4
        for step in range(16):
            tick = bar_start + step * step_dur
            pitch = sweep[step % len(sweep)]
            vel = int(45 + tension * 15 + random.randint(-4, 4))
            vel = max(10, min(100, vel))
            
            tracks_events[4].append((tick, 'on', pitch, vel, 4))
            tracks_events[4].append((tick + step_dur - 10, 'off', pitch, 0, 4))

    # Track 5: Violin 1 (GM 40 Violin)
    for bar in range(num_bars):
        bar_start = bar * 4 * tpb
        voicing = chords[bar]
        
        reg_notes = [n for n in voicing if 72 <= n <= 84]
        if not reg_notes:
            reg_notes = [n + 12 for n in voicing if 60 <= n <= 72] or [72]
            
        for step in range(2):
            tick = bar_start + step * 2 * tpb
            pitch = reg_notes[step % len(reg_notes)]
            vel = int(60 + tension * 20)
            
            tracks_events[5].append((tick, 'on', pitch, vel, 5))
            tracks_events[5].append((tick + 2 * tpb - 15, 'off', pitch, 0, 5))
            
            specialist_styles.generate_cc_curve(tracks_events[5], 11, tick, 2 * tpb,
                                                 start_val=50, end_val=int(65 + tension * 15),
                                                 curve_type="sine", ch=5)

    # Track 6: Violin 2 (GM 40 Violin)
    for bar in range(num_bars):
        bar_start = bar * 4 * tpb
        voicing = chords[bar]
        
        reg_notes = [n for n in voicing if 72 <= n <= 84]
        if not reg_notes:
            reg_notes = [n + 12 for n in voicing if 60 <= n <= 72] or [72]
            
        lower_reg_notes = [n for n in voicing if 60 <= n <= 72]
        if not lower_reg_notes:
            lower_reg_notes = [n - 12 for n in reg_notes]
            
        for step in range(2):
            tick = bar_start + step * 2 * tpb
            v1_pitch = reg_notes[step % len(reg_notes)]
            
            candidates = [n for n in lower_reg_notes if n < v1_pitch]
            if candidates:
                pitch = candidates[-1]
            else:
                pitch = v1_pitch - 7
                
            vel = int(55 + tension * 18)
            
            tracks_events[6].append((tick, 'on', pitch, vel, 6))
            tracks_events[6].append((tick + 2 * tpb - 15, 'off', pitch, 0, 6))
            
            specialist_styles.generate_cc_curve(tracks_events[6], 11, tick, 2 * tpb,
                                                 start_val=48, end_val=int(60 + tension * 15),
                                                 curve_type="sine", ch=6)

    # 4. Build MIDI File
    mid = specialist_styles.build_midi_from_events(tracks_events, tpb)
    
    # Apply custom track names conforming to nomenclature
    names = [
        "Chord Pad",
        "Rhythmic Bed",
        "Lead Melody",
        "Counter Melody",
        "Arpeggio Bed",
        "Violin 1",
        "Violin 2"
    ]
    for idx, name in enumerate(names):
        if idx < len(mid.tracks):
            mid.tracks[idx].name = name
            
    # Save the output MIDI
    adjectives = [
        "Apex", "Infinite", "Midnight", "Titan", "Solar", "Gothic", "Ethereal", "Grim",
        "Silent", "Shadow", "Crimson", "Nebula", "Spectral", "Cosmic", "Lost", "Fallen",
        "Eternal", "Frozen", "Abyssal", "Radiant", "Iron", "Storm", "Phoenix", "Astral",
        "Mystic", "Ancient", "Vortex", "Golden", "Obsidian", "Celestial", "Wounded",
    ]
    nouns = [
        "Ascent", "Requiem", "Odyssey", "Eclipse", "Horizon", "Empire", "Sanctuary",
        "Vanguard", "Echo", "Whisper", "Rift", "Conquest", "Genesis", "Destiny", "Void",
        "Valhalla", "Covenant", "Chronicle", "Legacy", "Bastion", "Rebirth", "Summit",
        "Oracle", "Wasteland", "Mirage", "Lament", "Citadel", "Overture", "Pilgrimage",
    ]
    project_title = f"{random.choice(adjectives)}_{random.choice(nouns)}"
    
    # Progression label slug
    prog_label = VVC._vvc_progression_from_chord_groups(chord_groups, root_pc)
    key_label = f"{scale_name}_{'Minor' if is_minor else 'Major'}"
    
    fname = (
        f"{project_title}__Super_Composer__{root_name}_{key_label}__{bpm}BPM__{prog_label}"
    )
    
    fpath = VVC._vvc_unique_path(out_dir, fname)
    mid.save(fpath)
    
    print(f"\n  [SAVED]  {os.path.basename(fpath)}")
    print(f"  [PATH ]  {fpath}")
    print("       Tracks: [Chord Pad] + [Rhythmic Bed] + [Lead Melody] + [Counter Melody] + [Arpeggio Bed] + [Violin 1] + [Violin 2]\n")
    
    return fpath, chord_groups

def main(out_dir="midi_files"):
    os.makedirs(out_dir, exist_ok=True)
    print("""
+--------------------------------------------------------------+
|               S U P E R   C O M P O S E R                    |
|    Automated 7-Channel Harmony & Orchestration Engine       |
|    Accepts a MIDI file -> Analyzes -> Rich Arrangement       |
+--------------------------------------------------------------+""")
    
    filepath = input("  Enter path to existing MIDI file: ").strip().strip('"').strip("'")
    if not os.path.isfile(filepath):
        print(f"  [ERROR] File not found: {filepath}")
        return
        
    print("\n  Select Orchestration Intensity / Tension:")
    print("    1 -> Low (Tension 0.40) - Soft, reflective")
    print("    2 -> Medium (Tension 0.65) - Expressive, balanced")
    print("    3 -> High (Tension 0.85) - Dramatic, energetic")
    tc = input("  Choice (1-3, default 2): ").strip() or '2'
    tension = {'1': 0.40, '2': 0.65, '3': 0.85}.get(tc, 0.65)
    
    try:
        fpath, _ = super_compose_over_midi(filepath, out_dir, tension)
    except Exception as e:
        print(f"  [FATAL ERROR] Super composition failed: {e}")

if __name__ == "__main__":
    main()
