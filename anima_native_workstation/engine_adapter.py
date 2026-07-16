"""UI-independent bridge to the complete offline ANIMA engine suite."""

from __future__ import annotations

import importlib.util
import os
import random
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import mido

APP_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = Path(getattr(sys, "_MEIPASS", APP_DIR.parent))
ASSETS_DIR = REPOSITORY_ROOT / "assets"


def _load_module(name: str, filename: str):
    if name in sys.modules:
        return sys.modules[name]
    path = ASSETS_DIR / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load ANIMA engine: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _slug(value: str) -> str:
    return "_".join(part for part in re.sub(r"[^A-Za-z0-9#+-]+", "_", value).split("_") if part)


def _unique_path(directory: Path, stem: str) -> Path:
    path = directory / f"{stem}.mid"
    index = 1
    while path.exists():
        path = directory / f"{stem}_v{index}.mid"
        index += 1
    return path


@dataclass(slots=True)
class GenerationRequest:
    engine: str
    mood: str
    key: str
    bpm: int
    instrument: str
    seed: int
    output_directory: str
    bars: int = 4
    input_file: str = ""


@dataclass(slots=True)
class GenerationResult:
    file: str
    filename: str
    engine: str
    mood: str
    key: str
    bpm: int
    progression: list[str]
    seed: int
    tracks: list[dict[str, Any]]
    bars: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EngineAdapter:
    """Lazily loads legacy engines and exposes one stable native API."""

    INSTRUMENT_IDS = {"Violin": "1", "Viola": "2", "Cello": "3"}
    ROOTS = {"C": 60, "C#": 61, "D": 62, "Eb": 63, "E": 64, "F": 65,
             "F#": 66, "G": 67, "Ab": 68, "A": 69, "Bb": 70, "B": 71}

    def __init__(self) -> None:
        self._modules: dict[str, Any] = {}

    def _module(self, key: str, filename: str):
        if key not in self._modules:
            self._modules[key] = _load_module(f"anima_native_{key}", filename)
        return self._modules[key]

    @staticmethod
    def _moods(mapping, name_key="name"):
        return [{"name": value[name_key], "count": len(value.get("progressions", [1]))}
                for _, value in mapping.items()]

    @staticmethod
    def _cluster_moods(mapping):
        return [{"name": " / ".join(n.capitalize() for n in value["names"]),
                 "count": len(value["progressions"])} for value in mapping.values()]

    def catalog(self) -> list[dict[str, Any]]:
        minor_solo = self._module("solo_minor", "solo_performance_minor.py")
        major_solo = self._module("solo_major", "solo_performance_major.py")
        major = self._module("chords_major", "major-chord-generatory.py")
        minor = self._module("chords_minor", "minor-chord-generatory.py")
        spanish = self._module("spanish_family", "spanish_family.py")
        world = self._module("world", "world_composer.py")
        specialist = self._module("specialist", "specialist_styles.py")
        def item(id_, group, name, subtitle, accent, moods, bars=(4,), requires_input=False):
            return {"id": id_, "group": group, "name": name, "subtitle": subtitle,
                    "accent": accent, "moods": moods, "bars": list(bars),
                    "requiresInput": requires_input}
        minor_groups = minor_solo._progression_mood_groups()
        cinematic = self._module("cinematic", "cinematic.py")
        return [
            item("chords_major", "CORE HARMONY", "Major Chord Engine", "Harmony, lead, counter and arpeggio", "#d8aa4e", self._cluster_moods(major.STYLE_CLUSTERS)),
            item("chords_minor", "CORE HARMONY", "Minor Chord Engine", "Emotional minor harmony ensemble", "#8d73dc", self._cluster_moods(minor.STYLE_CLUSTERS)),
            item("solo_major", "SOLO PERFORMANCE", "Solo Major", "Memorable lead and seven-part performance", "#e0ae58", [{"name": n, "count": len(p)} for n, p in major_solo.MOOD_POOLS.items()]),
            item("solo_minor", "SOLO PERFORMANCE", "Solo Minor", "Intimate minor string performance", "#9b7cff", [{"name": n.replace("Solo Native - ", ""), "count": len(p)} for n, p in minor_groups.items()]),
            item("cinematic_major", "CINEMATIC", "Cinematic Major", "Solo Major moods with cinematic orchestration", "#e1bb63", [{"name": n, "count": len(cinematic.CINEMATIC_MAJOR_MOOD_POOLS[n])} for n in cinematic.CINEMATIC_MAJOR_MOOD_NAMES]),
            item("cinematic_minor", "CINEMATIC", "Cinematic Minor", "Minor Engine moods with cinematic orchestration", "#7e6fca", [{"name": n, "count": len(cinematic.CINEMATIC_MINOR_MOOD_POOLS[n])} for n in cinematic.CINEMATIC_MINOR_MOOD_NAMES]),
            item("spanish_family", "SPANISH", "Spanish Family", "Guitar, bass, trumpet and violin", "#df8952", self._moods(spanish.NATIVE_MOODS), bars=(4,)),
            item("world", "WORLD", "World Composer", "Regional melodic and rhythmic identities", "#42bca9", self._moods(world.WORLD_PRESETS, "region"), bars=(4, 8, 16)),
            item("flamenco", "SPECIALIST", "Flamenco Specialist", "Three-part expressive nylon guitar", "#c95e47", [{"name": k.title(), "count": len(v["progressions"])} for k, v in specialist.FLAMENCO_MOOD_DATA.items()], bars=(8,)),
            item("vvc_quartet", "IMPORT & ORCHESTRATE", "VVC Quartet Overlay", "Analyze a MIDI and add expressive strings", "#5fa7d5", [{"name": "Expressive Quartet", "count": 1}], bars=(4,), requires_input=True),
        ]

    def _inspect(self, path: Path) -> tuple[list[dict[str, Any]], int]:
        midi = mido.MidiFile(path)
        max_tick = 0
        tracks = []
        for index, track in enumerate(midi.tracks):
            tick = 0; notes = 0; name = track.name or f"Track {index + 1}"; channel = None
            for message in track:
                tick += message.time
                if message.type == "note_on" and message.velocity > 0:
                    notes += 1; channel = message.channel + 1
            max_tick = max(max_tick, tick)
            if notes:
                tracks.append({"name": name, "channel": channel or index + 1, "notes": notes})
        bars = max(1, round(max_tick / max(1, midi.ticks_per_beat * 4)))
        return tracks, bars

    def _save_chord_engine(self, engine, request, output: Path, tonality: str):
        cluster = next((v for v in engine.STYLE_CLUSTERS.values()
                        if v.get("name") == request.mood or " / ".join(n.capitalize() for n in v["names"]) == request.mood), None)
        if cluster is None:
            cluster = next((v for v in engine.STYLE_CLUSTERS.values() if v["names"][0].title() in request.mood), None)
        if cluster is None:
            raise ValueError(f"Unknown mood: {request.mood}")
        entry = random.choice(cluster["progressions"])
        progression = entry["chords"][:4]
        root = engine.roots[request.key]
        chords = engine.generate_chords(root, progression)
        melody = engine.generate_melody(root, progression, cluster["tension"])
        counter = engine.generate_counter(root, progression, cluster["tension"], lead_melody=melody)
        arpeggio = engine.generate_driving_arpeggio(root, progression, cluster["tension"])
        midi = engine.build_midi(chords, melody, counter, bpm=request.bpm, arpeggio=arpeggio)
        path = _unique_path(output, f"ANIMA_{tonality}_Harmony__{_slug(request.mood)}__{request.key}__{request.bpm}BPM__{'-'.join(progression)}")
        midi.save(path)
        return path, progression, f"{request.key} {tonality}"

    def generate(self, request: GenerationRequest) -> GenerationResult:
        output = Path(request.output_directory).expanduser().resolve()
        output.mkdir(parents=True, exist_ok=True)
        bpm = max(50, min(190, int(request.bpm)))
        random.seed(int(request.seed))
        root = self.ROOTS.get(request.key)
        if root is None:
            raise ValueError(f"Unsupported key: {request.key}")
        engine_name = request.engine; progression: list[str] = []; key_label = request.key

        if request.engine in ("solo_minor", "solo_major"):
            module = self._module(request.engine, f"solo_performance_{request.engine.split('_')[1]}.py")
            if request.engine == "solo_minor":
                groups = module._progression_mood_groups(); pools = {n.replace("Solo Native - ", ""): p for n, p in groups.items()}
                path, progression = module.compose_solo_performance(str(output), request.key, module.ROOTS[request.key], bpm, self.INSTRUMENT_IDS.get(request.instrument, "1"), pools[request.mood], request.mood)
                engine_name = "Solo Minor"; key_label += " Minor"
            else:
                path, progression = module.compose_major_solo_performance(str(output), request.key, module.ROOTS[request.key], bpm, self.INSTRUMENT_IDS.get(request.instrument, "1"), module.MOOD_POOLS[request.mood], request.mood)
                engine_name = "Solo Major"; key_label += " Major"
        elif request.engine in ("chords_major", "chords_minor"):
            tonal = "Major" if request.engine.endswith("major") else "Minor"
            module = self._module(request.engine, f"{tonal.lower()}-chord-generatory.py")
            path, progression, key_label = self._save_chord_engine(module, request, output, tonal)
            engine_name = f"{tonal} Chord Engine"
        elif request.engine.startswith("cinematic_"):
            module = self._module("cinematic", "cinematic.py")
            names = module.CINEMATIC_MAJOR_MOOD_NAMES if request.engine.endswith("major") else module.CINEMATIC_MINOR_MOOD_NAMES
            mood_id = names.index(request.mood) + 1
            midi, actual_mood, prog = (module.compose_cinematic_major_track(mood_id, bpm, request.key, root) if request.engine.endswith("major") else module.compose_cinematic_track(mood_id, bpm, request.key, root))
            progression = prog.split("-"); key_label += " " + ("Major" if request.engine.endswith("major") else "Minor")
            engine_name = "Cinematic " + key_label.split()[-1]
            path = _unique_path(output, f"ANIMA_{_slug(engine_name)}__{_slug(actual_mood)}__{request.key}__{bpm}BPM__{_slug(prog)}"); midi.save(path)
        elif request.engine == "spanish_family":
            module = self._module("spanish_family", "spanish_family.py")
            mood = next(v.copy() for v in module.NATIVE_MOODS.values() if v["name"] == request.mood)
            path, progression = module.compose_spanish_family(str(output), mood, request.key, root, bpm, request.bars); engine_name = "Spanish Family"; key_label += f" {mood['scale'].replace('_', ' ').title()}"
        elif request.engine == "world":
            module = self._module("world", "world_composer.py")
            preset = next(v.copy() for v in module.WORLD_PRESETS.values()
                          if v.get("name") == request.mood or v.get("region") == request.mood)
            path, progression = module.compose_world(str(output), preset, request.key, root, bpm, request.bars); engine_name = "World Composer"; key_label += f" {preset['scale'].replace('_', ' ').title()}"
        elif request.engine == "flamenco":
            module = self._module("specialist", "specialist_styles.py")
            mood_key = request.mood.lower(); before = set(output.glob("*.mid"))
            module.generate_flamenco_redone(str(output), root, request.key, bpm, 0.62, mood_key, request.mood, request.mood)
            created = list(set(output.glob("*.mid")) - before)
            if not created: raise RuntimeError("Flamenco engine did not produce a MIDI file.")
            path = max(created, key=lambda p: p.stat().st_mtime); engine_name = "Flamenco Specialist"; key_label += " Spanish"
        elif request.engine == "vvc_quartet":
            source = Path(request.input_file)
            if not source.is_file(): raise ValueError("Choose an existing MIDI file for the VVC workflow.")
            module = self._module("vvc", "VVC.py"); before = set(output.glob("*.mid")); module.generate_quartet_over_midi(str(source), str(output))
            created = list(set(output.glob("*.mid")) - before)
            if not created: raise RuntimeError("VVC could not detect a usable chord progression in that MIDI.")
            path = max(created, key=lambda p: p.stat().st_mtime); engine_name = "VVC Quartet Overlay"; key_label = "Auto-detected"
        else:
            raise ValueError(f"Unsupported engine: {request.engine}")

        path = Path(path).resolve(); tracks, actual_bars = self._inspect(path)
        return GenerationResult(str(path), path.name, engine_name, request.mood, key_label, bpm,
                                list(progression), int(request.seed), tracks, actual_bars)
