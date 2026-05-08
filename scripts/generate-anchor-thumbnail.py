"""Generate the YouTube thumbnail for the anchor doc using gpt-image-1.

Pulls the prompt from faith-walk-live/anchor-doc/publish-plan.md §3.
Output: 1280x720 PNG at faith-walk-live/anchor-doc/thumbnail.png
"""
import base64
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
API_KEY = os.environ["OPENAI_API_KEY"]
OUT = ROOT / "faith-walk-live" / "anchor-doc" / "thumbnail.png"

PROMPT = (
    "Create a 16:9 cinematic YouTube thumbnail. High-contrast composition.\n\n"
    "LEFT 60%: Close-up portrait of a determined Black man in his 30s, "
    "dark-brown to deep-brown skin, melanated African American complexion, "
    "wool-textured / coiled / tightly curled hair, weathered face showing "
    "fatigue and resolve, eyes locked on the viewer. He's wearing a backpack "
    "strap visible on shoulder. Warm golden-hour lighting on his face — "
    "bronze/amber tones, dramatic chiaroscuro. NOT Caucasian, NOT pale, "
    "NOT light-skinned, NOT European — explicitly Black/African American "
    "with the features described.\n\n"
    "RIGHT 40%: Bold gold serif text on a deep navy-black gradient background "
    "with sparse golden particles. Three-line stack:\n"
    "Line 1 (large, bold gold serif): 3000 MILES\n"
    "Line 2 (large, bold gold serif): TO BUILD\n"
    "Line 3 (large, bold gold serif, with subtle warm glow): A SCHOOL\n\n"
    "Background context (bottom-left, behind the figure): a faint road / "
    "highway shoulder with a yellow line suggesting forward motion. "
    "High contrast for mobile readability. Mood: documentary-cinematic, "
    "sacred-but-grounded, 'This is real.'"
)

print("Calling gpt-image-1 (1536x1024 quality=high)...")
r = requests.post(
    "https://api.openai.com/v1/images/generations",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": "gpt-image-1",
        "prompt": PROMPT,
        "size": "1536x1024",
        "quality": "high",
        "n": 1,
    },
    timeout=120,
)
r.raise_for_status()
data = r.json()["data"][0]

if "b64_json" in data:
    raw = base64.b64decode(data["b64_json"])
else:
    raw = requests.get(data["url"], timeout=60).content

# Resize 1536x1024 → 1280x720 (YT thumbnail spec)
img = Image.open(BytesIO(raw))
img_resized = img.resize((1280, 720), Image.Resampling.LANCZOS)
OUT.parent.mkdir(parents=True, exist_ok=True)
img_resized.save(OUT, "PNG", optimize=True)
size_kb = OUT.stat().st_size / 1024
print(f"Wrote {OUT.relative_to(ROOT)} ({size_kb:.1f} KB)")
if size_kb > 2048:
    print(f"  WARNING: YT thumbnail max is 2 MB. Current size: {size_kb/1024:.2f} MB")
