"""Build output/manifests/eden-full-doc.json — the assembler manifest for the ONE continuous
~86-minute cut: Part One (26 scenes) flowing straight into Parts Two–Eight + Conclusion + CTA
(103 scenes) = 129 scenes total.

Two sources, already in their final forms:
  - Part One: output/manifests/eden-part1.json — already the assembler shape, already narrated
    (its 26 mp3s are cached under output/audio/eden-part1/). Copied in verbatim so the fingerprint
    stays identical and the assembler reuses that audio for free.
  - Parts 2–8: output/manifests/eden-full-scenes.json — the planning shape. Converted here to the
    assembler shape (scene_id / clip_path / narration_text / sfx / is_figure).

Clip paths (used in place by the assembler, never copied):
  Part One  non-figure -> output/clips/eden-part1/<id>.mp4      figure -> output/clips/eden-part1-figures/<id>.mp4
  Parts 2-8 non-figure -> output/clips/eden-full/<id>.mp4       figure -> output/clips/eden-full-figures/<id>.mp4

Voice is Tommy's clone "Thomas Israel" (RKqAcMj3TkzJjyZpEbj0) @ 0.92 — the SAME voice Part One
was narrated in, so the two halves sound like one narrator. (Daniel is the Shorts voice, not this.)

Usage: python scripts/build-eden-full-manifest.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PART1 = ROOT / "output" / "manifests" / "eden-part1.json"
FULL = ROOT / "output" / "manifests" / "eden-full-scenes.json"
OUT = ROOT / "output" / "manifests" / "eden-full-doc.json"
SFX_MAP = ROOT / "scripts" / "assemble" / "sfx_map.json"

VOICE_ID = "RKqAcMj3TkzJjyZpEbj0"
VOICE_SPEED = 0.92
TOPIC = "eden-full-doc"
TITLE = "From Eden to Timbuktu: The Hidden History of the Black Hebrews"

FULL_NONFIG_DIR = "output/clips/eden-full"
FULL_FIG_DIR = "output/clips/eden-full-figures"


def strip_markdown(text: str) -> str:
    """Narration is authored with *italic* emphasis on scripture. The asterisks are for the
    reader, not the voice — strip them so the clone never voices a literal 'asterisk' and the
    character count (billing) reflects only spoken words. Everything else (em-dashes, quotes)
    is natural speech and stays."""
    text = text.replace("*", "")
    return re.sub(r"\s+", " ", text).strip()


def convert_full_scene(s, sfx_moods):
    sid = s["id"]
    is_fig = s["source"] == "KLING"
    clip_dir = FULL_FIG_DIR if is_fig else FULL_NONFIG_DIR
    mood = s["sfx_mood"]
    return {
        "scene_id": sid,
        "clip_path": f"{clip_dir}/{sid}.mp4",
        "narration_text": strip_markdown(s["narration"]),
        "sfx": {"file": sfx_moods.get(mood, {}).get("file"), "volume": 0.12, "mood": mood},
        "is_figure": is_fig,
    }


def build():
    sfx_moods = json.loads(SFX_MAP.read_text(encoding="utf-8"))["moods"]
    part1 = json.loads(PART1.read_text(encoding="utf-8"))
    full = json.loads(FULL.read_text(encoding="utf-8"))["scenes"]

    p1_scenes = part1["scenes"]                       # verbatim — preserves audio-cache fingerprint
    full_scenes = [convert_full_scene(s, sfx_moods) for s in full]

    # Guard: no scene_id may repeat across the join (would collide in the audio cache).
    ids = [s["scene_id"] for s in p1_scenes] + [s["scene_id"] for s in full_scenes]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"scene_id collision across Part One and Parts 2-8: {sorted(dupes)}")

    scenes = p1_scenes + full_scenes
    manifest = {
        "topic": TOPIC,
        "title": TITLE,
        "aspect": "16x9",
        "voice_id": VOICE_ID,
        "voice_speed": VOICE_SPEED,
        "scenes": scenes,
    }
    OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # Report cost of the NEW narration only (Part One is cached, re-costs nothing).
    new_chars = sum(len(s["narration_text"]) for s in full_scenes)
    p1_words = sum(len(s["narration_text"].split()) for s in p1_scenes)
    new_words = sum(len(s["narration_text"].split()) for s in full_scenes)
    total_words = p1_words + new_words
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"  {len(scenes)} scenes = {len(p1_scenes)} (Part One) + {len(full_scenes)} (Parts 2-8)")
    print(f"  narration ~{total_words} words (~{total_words/150:.1f} min @150wpm)")
    print(f"  NEW characters to synthesize: {new_chars:,}  ->  ~{round(new_chars*0.5):,} credits @0.5/char")
    print(f"  Part One's {len(p1_scenes)} scenes reuse cached audio (fingerprint match, $0).")


if __name__ == "__main__":
    build()
