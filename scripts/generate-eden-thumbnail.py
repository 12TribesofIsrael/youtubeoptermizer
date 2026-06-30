"""Generate Eden -> Timbuktu Part 1 thumbnail options via gpt-image-1 (brand gold-on-navy).

Three CTR-forward variants; Tommy picks one, then crop/export to 1280x720 for YouTube.
Figures MUST carry the Black Hebrew Israelite identity stack (locked brand rule) so the AI
does not default to Caucasian features.

Usage: python scripts/generate-eden-thumbnail.py [variant]   (default: all)
Output: output/thumbnails/eden-part1/<NN>_<variant>.png
"""
import base64
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import requests

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
API_KEY = os.environ["OPENAI_API_KEY"]
OUT_DIR = ROOT / "output" / "thumbnails" / "eden-part1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BRAND = (
    "Brand: deep navy-black background, dramatic cinematic chiaroscuro, divine golden/amber light "
    "breaking through darkness, warm bronze tones, sparse golden particles, bold gold serif title font "
    "with a subtle glow. Cinematic, revelatory, powerful, high-end YouTube documentary thumbnail. "
    "16:9. Spell every title word EXACTLY as given; large, crisp, legible at small size."
)
# The identity stack — required on any figure so it renders melanated, not Caucasian.
IDENTITY = (
    "The figure is a Black Hebrew Israelite man, dark-brown to deep-brown melanated African complexion, "
    "wool-textured tightly coiled hair and beard, regal and powerful. NOT white, NOT pale, NOT "
    "light-skinned, no Caucasian or European features."
)

VARIANTS = {
    "hebrews": ("01", f"{BRAND} {IDENTITY} Right third of frame: a regal melanated Black Hebrew Israelite "
                "king in earth-tone and gold robes, lit from behind by golden light, standing before a faint "
                "ancient ziggurat in deep shadow. Left two-thirds: bold gold serif title on dark negative space, "
                "two stacked lines, all caps: line 1 'THE BLACK' line 2 'HEBREWS'. Dramatic, mysterious."),
    "garden": ("02", f"{BRAND} No people. A sweeping golden river valley / primordial garden at dawn seen "
               "through parting clouds with a beam of divine light. Bold gold serif title centered lower third, "
               "two lines, all caps: line 1 'BEFORE EUROPE,' line 2 'A GARDEN'. Awe and scale."),
    "origin": ("03", f"{BRAND} {IDENTITY} Center: a powerful melanated Black Hebrew Israelite figure in profile "
               "looking toward a rising ziggurat wreathed in golden light and embers. Bold gold serif title across "
               "the top, all caps: 'FROM EDEN TO TIMBUKTU'. Small gold subtitle lower: 'THE HIDDEN HISTORY'. Epic."),
}


def generate(vid: str):
    num, prompt = VARIANTS[vid]
    print(f"[{vid}] generating...")
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "gpt-image-1", "prompt": prompt, "size": "1536x1024", "quality": "high", "n": 1},
        timeout=300,
    )
    if r.status_code != 200:
        print(f"  ERROR {r.status_code}: {r.text[:300]}")
        return
    out = OUT_DIR / f"{num}_{vid}.png"
    out.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"  wrote {out.relative_to(ROOT)} ({out.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    ids = [sys.argv[1]] if len(sys.argv) > 1 else list(VARIANTS)
    for vid in ids:
        generate(vid)
