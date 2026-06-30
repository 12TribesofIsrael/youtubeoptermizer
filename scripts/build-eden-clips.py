"""Build the non-figure Part 1 clips (cards, maps, stills, Met artifacts) into
output/clips/eden-part1/<scene_id>.mp4 so they can be referenced as clip_path in the
assembler manifest.

This script also IS the canonical scene_id -> visual-asset + motion mapping for Part 1's
non-figure scenes (build-eden-manifest.py imports SCENE_ASSETS from here). Figure scenes
(co2, p3, p7, p9, p10, p15) come from Kling and live in output/clips/eden-part1-figures/.

Motion rule: text cards = static (a zoom would crop/destabilize the lettering); everything
else = slow ken-burns. Duration is long (90s) so the assembler's stream-loop never resets a
ken-burns mid-scene on the longest narration blocks.

Usage: python scripts/build-eden-clips.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "output" / "cards" / "eden-part1"
STILLS = ROOT / "output" / "stills" / "eden-part1"
OUT = ROOT / "output" / "clips" / "eden-part1"
OUT.mkdir(parents=True, exist_ok=True)

DUR = 90.0  # longer than any single Part-1 narration block

# scene_id -> (source image path, motion). "static" for text cards; ken-burns elsewhere.
SCENE_ASSETS = {
    # COLD OPEN
    "co1": (CARDS / "19_co1_ember.png",      "kenburns-in"),
    "co3": (CARDS / "01_title.png",          "static"),       # main title card
    "co4": (CARDS / "20_co4_journey.png",    "kenburns-in"),
    # INTRODUCTION
    "in1": (CARDS / "25_in1_scroll.png",     "kenburns-out"),
    "in2": (CARDS / "21_in2_trail.png",      "kenburns-in"),
    "in3": (CARDS / "22_in3_scatter.png",    "kenburns-out"),
    "in4": (CARDS / "26_in4_bible.png",      "kenburns-in"),
    "in5": (CARDS / "28_in5_bloom.png",      "kenburns-in"),
    # PART ONE
    "p1":  (CARDS / "02_chapter.png",        "static"),       # chapter card
    "p2":  (CARDS / "18_p2_aerial.png",      "kenburns-in"),
    "p4":  (CARDS / "03_gen210.png",         "static"),       # scripture card
    "p5":  (CARDS / "04_gen214.png",         "static"),       # scripture card
    "p6":  (CARDS / "05_gen213.png",         "static"),       # scripture card
    "p8":  (CARDS / "27_p8_genealogy.png",   "kenburns-in"),
    "p11": (STILLS / "sumerian-statue_323735_standing-male-worshiper.jpg", "kenburns-in"),
    "p12": (STILLS / "cuneiform-tablet_329081_proto-cuneiform.jpg",        "kenburns-in"),
    "p13": (CARDS / "23_p13_ur.png",         "kenburns-in"),
    "p14": (STILLS / "egyptian-relief_547705_relief-from-the-palace-of-apries-in-memp.jpg", "kenburns-out"),
    "p16": (CARDS / "24_p16_radiate.png",    "kenburns-in"),
    "p17": (CARDS / "19_co1_ember.png",      "kenburns-out"),  # bookend the cold-open ember
}

# Figure scenes -> already-rendered Kling clips (local). p7 added once re-rendered.
FIGURE_CLIPS = {
    "co2": ROOT / "output" / "clips" / "eden-part1-figures" / "co2.mp4",
    "p3":  ROOT / "output" / "clips" / "eden-part1-figures" / "p3.mp4",
    "p7":  ROOT / "output" / "clips" / "eden-part1-figures" / "p7.mp4",
    "p9":  ROOT / "output" / "clips" / "eden-part1-figures" / "p9.mp4",
    "p10": ROOT / "output" / "clips" / "eden-part1-figures" / "p10.mp4",
    "p15": ROOT / "output" / "clips" / "eden-part1-figures" / "p15.mp4",
}


def build():
    stills_to_clips = ROOT / "scripts" / "stills-to-clips.py"
    ok = 0
    for sid, (src, motion) in SCENE_ASSETS.items():
        if not src.exists():
            print(f"  MISSING source for {sid}: {src.name}")
            continue
        dst = OUT / f"{sid}.mp4"
        cmd = [sys.executable, str(stills_to_clips), str(src), str(dst),
               "--motion", motion, "--dur", str(DUR)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ERROR {sid}: {r.stdout.strip()} {r.stderr.strip()[-300:]}")
            continue
        print(f"  {sid:4s} <- {src.name[:42]:42s} ({motion})")
        ok += 1
    print(f"\nBuilt {ok}/{len(SCENE_ASSETS)} non-figure clips -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
