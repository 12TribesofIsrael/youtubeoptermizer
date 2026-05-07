"""Generate title cards via OpenAI image API.

Tries gpt-image-1 first (best text rendering, 2025+ release), falls back to
dall-e-3 if the newer endpoint is unavailable on the account.

Usage:
    python scripts/generate-title-cards.py [card_id]

card_id: card1 | card2 | card3 | card4 (default: all 4)
Output: faith-walk-live/anchor-doc/cards/<NN>_<id>.png
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
OUT_DIR = ROOT / "faith-walk-live/anchor-doc/cards"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BRAND = (
    "Brand identity: deep navy-black background with subtle radial gradient slightly warmer toward center, "
    "sparse golden particles floating like dust in light, gold serif font with subtle warm glow, "
    "cinematic chiaroscuro lighting, bronze-warm tones, sacred-but-modern documentary mood. "
    "No crosses, doves, or other religious graphic elements."
)

CARDS = {
    "card1": (
        "01",
        "Main Title",
        f"{BRAND} 16:9 cinematic title card. Center the following text in bold gold serif on a "
        f"deep navy-black background with golden particles. Two stacked lines, the first much larger:\n"
        f"Line 1 (LARGE, BOLD GOLD SERIF): 3000 MILES FOR THE KIDS\n"
        f"Line 2 (smaller, gold serif): PHILADELPHIA — CALIFORNIA\n"
        f"Faint golden light beam descending from above-center behind the text. Render the text clearly and accurately.",
    ),
    "card2": (
        "02",
        "James 1:27 Scripture Card",
        f"{BRAND} 16:9 scripture card. Center the following italicized quote in elegant gold serif on a "
        f"deep navy-black background with sparse golden particles. Render the text clearly and accurately:\n\n"
        f'"Pure religion and undefiled before God and the Father is this: To visit the fatherless and widows in their affliction."\n'
        f"— James 1:27\n\n"
        f"The quote is in italic gold serif. The citation '— James 1:27' is in regular weight gold serif, smaller. "
        f"Beneath the citation is a thin horizontal golden divider line, like in an ancient text. "
        f"Faint warm radiance behind the text.",
    ),
    "card3": (
        "03",
        "Matthew 25:40 Scripture Card",
        f"{BRAND} 16:9 scripture card. Center the following italicized quote in elegant gold serif on a "
        f"deep navy-black background with sparse golden particles. Render the text clearly and accurately:\n\n"
        f'"Inasmuch as ye have done it unto one of the least of these my brethren, ye have done it unto me."\n'
        f"— Matthew 25:40\n\n"
        f"The quote is in italic gold serif. The citation '— Matthew 25:40' is in regular weight gold serif, smaller. "
        f"Beneath the citation is a thin horizontal golden divider line. Faint warm radiance behind the text.",
    ),
    "card4": (
        "04",
        "CTA / Closing Card",
        f"{BRAND} 16:9 cinematic closing card. Three stacked CTAs in bold gold serif on a deep navy-black background "
        f"with golden particles, separated by thin golden horizontal divider lines. Render all text clearly and accurately:\n\n"
        f"Top section (large bold gold serif): TRACK THE WALK LIVE\n"
        f"   subtitle (smaller gold): faithwalklive.com\n"
        f"--- thin golden divider line ---\n"
        f"Middle section (large bold gold serif): DONATE TO THE SCHOOL\n"
        f"   subtitle (smaller gold): Link in description\n"
        f"--- thin golden divider line ---\n"
        f"Bottom section (large bold gold serif): SUBSCRIBE\n"
        f"   subtitle (smaller gold): @AIBIBLEGOSPELS\n\n"
        f"Mood: invitation, sacred, modern. Strong center alignment. Equal vertical spacing between sections.",
    ),
}


def generate(card_id: str):
    num, label, prompt = CARDS[card_id]
    print(f"[{num}] {label} — {len(prompt)} char prompt")

    # Try gpt-image-1 first (best text rendering)
    payload = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1536x1024",
        "quality": "high",
        "n": 1,
    }
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )

    if r.status_code != 200:
        print(f"  gpt-image-1 returned {r.status_code}; falling back to dall-e-3")
        try:
            print(f"  detail: {r.json()}")
        except Exception:
            print(f"  detail: {r.text[:300]}")
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": "1792x1024",
            "quality": "hd",
            "style": "vivid",
            "n": 1,
        }
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=120,
        )
        if r.status_code != 200:
            print(f"  dall-e-3 also failed: {r.status_code}: {r.text[:400]}")
            return None
        used_model = "dall-e-3"
    else:
        used_model = "gpt-image-1"

    data = r.json()["data"][0]
    out_path = OUT_DIR / f"{num}_{card_id}.png"

    if "b64_json" in data:
        out_path.write_bytes(base64.b64decode(data["b64_json"]))
    elif "url" in data:
        img = requests.get(data["url"], timeout=60)
        img.raise_for_status()
        out_path.write_bytes(img.content)
    else:
        print(f"  unexpected response shape: {data.keys()}")
        return None

    print(f"  wrote {out_path.name} via {used_model} ({out_path.stat().st_size/1024:.1f} KB)")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) > 1:
        targets = [sys.argv[1]]
        if targets[0] not in CARDS:
            print(f"Unknown card: {targets[0]}. Available: {list(CARDS.keys())}")
            sys.exit(1)
    else:
        targets = list(CARDS.keys())

    print(f"Generating {len(targets)} card(s)\n")
    for t in targets:
        generate(t)
        print()
    print(f"Done. Cards in {OUT_DIR}")
