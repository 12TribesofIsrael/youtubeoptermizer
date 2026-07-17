"""Build the non-figure full-doc clips (cards, maps, stills, archival) into
output/clips/eden-full/<scene_id>.mp4 so they can be referenced as clip_path in the
assembler manifest.

Unlike Part 1's builder, the scene_id -> asset mapping is derived, not hand-written:
generate-eden-full-visuals.py names every card output/cards/eden-full/<scene_id>.png, and
render-eden-kling.py names every figure clip output/clips/eden-full-figures/<scene_id>.mp4.
Source-of-truth for the scene list is output/manifests/eden-full-scenes.json.

Motion rule (same as Part 1): text cards = static (a zoom crops/destabilizes the lettering);
everything else = slow ken-burns, alternating in/out so consecutive stills don't drift the
same direction.

Fit rule (differs from Part 1): static cards are built with --fit crop, not pad. Cards are 3:2
(1536x1024) and the frame is 16:9, so padding pillarboxes them 150px per side — which visibly
narrows the frame every time the cut lands on a card between full-bleed ken-burns stills and
the 1920x1080 Kling clips. The Kling clips are the fixed point (re-rendering costs fal credit),
so everything else matches them. Crop-safety was checked across all 19 text cards: the lost
strip is empty background on every one.

DUR is 150s — longer than the longest single narration block (257 words ~= 112s at speed
0.92) so the assembler's stream-loop never resets a ken-burns mid-scene.

Usage:
  python scripts/build-eden-full-clips.py --limit 10      # first 10, for a canary batch
  python scripts/build-eden-full-clips.py --offset 10 --limit 10
  python scripts/build-eden-full-clips.py                 # all of them
  python scripts/build-eden-full-clips.py --force         # rebuild existing
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "output" / "manifests" / "eden-full-scenes.json"
CARDS = ROOT / "output" / "cards" / "eden-full"
FIGURES = ROOT / "output" / "clips" / "eden-full-figures"
OUT = ROOT / "output" / "clips" / "eden-full"

DUR = 150.0

# Sources whose art is a text card -> hold still. Everything else gets ken-burns.
STATIC_SOURCES = {"CARD"}


def plan():
    """[(scene_id, src_png, motion)] for every non-KLING scene, in manifest order."""
    scenes = json.loads(MANIFEST.read_text(encoding="utf-8"))["scenes"]
    rows, kb = [], 0
    for s in scenes:
        if s["source"] == "KLING":
            continue  # already a real clip in eden-full-figures/
        if s["source"] in STATIC_SOURCES:
            motion = "static"
        else:
            motion = "kenburns-in" if kb % 2 == 0 else "kenburns-out"
            kb += 1
        rows.append((s["id"], CARDS / f"{s['id']}.png", motion))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="build at most N clips")
    ap.add_argument("--offset", type=int, default=0, help="skip the first N scenes")
    ap.add_argument("--force", action="store_true", help="rebuild clips that already exist")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    rows = plan()[args.offset:]
    if args.limit is not None:
        rows = rows[:args.limit]

    worker = ROOT / "scripts" / "stills-to-clips.py"
    ok = skipped = 0
    for sid, src, motion in rows:
        dst = OUT / f"{sid}.mp4"
        if dst.exists() and not args.force:
            print(f"  {sid:6s} exists, skipping")
            skipped += 1
            continue
        if not src.exists():
            print(f"  MISSING source for {sid}: {src.name}")
            continue
        fit = "crop" if motion == "static" else "pad"  # ken-burns already fills the frame
        r = subprocess.run(
            [sys.executable, str(worker), str(src), str(dst),
             "--motion", motion, "--dur", str(DUR), "--fit", fit],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"  ERROR {sid}: {r.stdout.strip()} {r.stderr.strip()[-300:]}")
            continue
        print(f"  {sid:6s} <- {src.name[:38]:38s} ({motion})")
        ok += 1

    total = len(plan())
    print(f"\nBuilt {ok}, skipped {skipped}, of {len(rows)} requested "
          f"({total} non-figure scenes total) -> {OUT.relative_to(ROOT)}")
    print(f"Figure scenes stay in {FIGURES.relative_to(ROOT)} (8 Kling clips).")


if __name__ == "__main__":
    main()
