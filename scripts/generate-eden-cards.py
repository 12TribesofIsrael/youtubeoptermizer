"""Generate Eden -> Timbuktu Part 1 text cards via gpt-image-1 (brand gold-on-navy).

Cards: title, chapter, and 3 scripture cards (Gen 2:10, 2:14, 2:13).
Reuses the proven approach from scripts/generate-title-cards.py (gpt-image-1 nails
multi-line scripture text at quality=high 1536x1024 — see memory gpt_image_1_for_title_cards).

Usage: python scripts/generate-eden-cards.py [card_id]   (default: all)
Output: output/cards/eden-part1/<NN>_<id>.png
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
OUT_DIR = ROOT / "output" / "cards" / "eden-part1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BRAND = (
    "Brand identity: deep navy-black background with a subtle radial gradient slightly warmer toward center, "
    "sparse golden particles floating like dust in a light beam, bold gold serif font with a subtle warm glow, "
    "cinematic chiaroscuro lighting, bronze-warm tones, sacred-but-modern documentary mood. "
    "Elegant, reverent, high-end. No crosses, doves, faces, or figures. Spell every word EXACTLY as given."
)

CARDS = {
    "title": ("01", f"{BRAND} 16:9 cinematic main title card. Centered, two stacked lines:\n"
              "Line 1 (VERY LARGE, BOLD GOLD SERIF, all caps): FROM EDEN TO TIMBUKTU\n"
              "Line 2 (smaller, refined gold serif): The Hidden History of the Black Hebrews\n"
              "Generous spacing, dramatic dark negative space around the text."),
    "chapter": ("02", f"{BRAND} 16:9 chapter card. Centered, two stacked lines:\n"
                "Line 1 (small gold serif, letter-spaced, all caps): PART ONE\n"
                "Line 2 (LARGE, BOLD GOLD SERIF): Ancient Black Civilization\n"
                "A thin gold divider rule between the two lines."),
    "gen210": ("03", f"{BRAND} 16:9 scripture card. Centered gold serif scripture quote, then a smaller "
               "reference beneath. The quote MUST be enclosed in curly double quotation marks (one opening at the "
               "very start, one closing at the very end). Spell the proper noun EDEN exactly as the four letters "
               "E-D-E-N (never 'den'). Quote (elegant gold serif, may wrap to 3-4 lines):\n"
               "“And a river went out of Eden to water the garden; and from thence it was parted, and became into four heads.”\n"
               "Reference beneath in smaller letter-spaced gold caps: GENESIS 2:10"),
    "gen214": ("04", f"{BRAND} 16:9 scripture card. Centered gold serif scripture quote, then a smaller "
               "reference beneath. Quote (elegant gold serif, may wrap to 3-4 lines):\n"
               "\"And the name of the third river is Hiddekel; that is it which goeth toward the east of Assyria. And the fourth river is Euphrates.\"\n"
               "Reference beneath in smaller letter-spaced gold caps: GENESIS 2:14"),
    "gen213": ("05", f"{BRAND} 16:9 scripture card. Centered gold serif scripture quote, then a smaller "
               "reference beneath. The quote MUST be enclosed in curly double quotation marks (one opening at the "
               "very start, one closing at the very end). Quote (elegant gold serif, may wrap to 2-3 lines):\n"
               "“And the name of the second river is Gihon: the same is it that compasseth the whole land of Ethiopia.”\n"
               "Reference beneath in smaller letter-spaced gold caps: GENESIS 2:13"),
}


def generate(card_id: str):
    num, prompt = CARDS[card_id]
    print(f"[{card_id}] generating...")
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "gpt-image-1", "prompt": prompt, "size": "1536x1024", "quality": "high", "n": 1},
        timeout=300,
    )
    if r.status_code != 200:
        print(f"  ERROR {r.status_code}: {r.text[:300]}")
        return
    b64 = r.json()["data"][0]["b64_json"]
    out = OUT_DIR / f"{num}_{card_id}.png"
    out.write_bytes(base64.b64decode(b64))
    print(f"  wrote {out.relative_to(ROOT)} ({out.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    ids = [sys.argv[1]] if len(sys.argv) > 1 else list(CARDS)
    for cid in ids:
        generate(cid)
