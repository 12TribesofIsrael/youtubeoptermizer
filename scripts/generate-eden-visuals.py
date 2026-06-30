"""Generate Eden -> Timbuktu Part 1 non-figure visuals (maps + atmospheric stills)
via gpt-image-1, in the channel gold-on-navy brand.

These cover the ARCHIVAL/MAP/STILL scenes from drafts/eden-part1-scene-plan.md that
do NOT contain human figures (figures go through Kling for identity injection).

Design rule for MAPS: NO place-name text labels. gpt-image-1 garbles small map labels,
and the narration already speaks every place name. We render a glowing gold ROUTE / region
glow on an aged parchment-dark map so the geography reads as an intentional branded graphic,
not a mislabeled atlas. Stills are pure atmosphere (ember, scroll, Bible, vellum genealogy).

Usage: python scripts/generate-eden-visuals.py [id]   (default: all)
Output: output/cards/eden-part1/<NN>_<id>.png   (same folder as the text cards)
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
    "Brand identity: deep navy-black background, cinematic chiaroscuro, golden/amber light, "
    "sparse golden dust particles, bronze-warm tones, sacred-but-modern documentary mood, "
    "high-end and reverent. NO text, NO letters, NO words, NO labels, NO captions anywhere in the image. "
    "No faces, no people, no figures."
)

MAP_BASE = (
    f"{BRAND} 16:9 cinematic documentary MAP graphic. An aged dark parchment / antique map texture "
    "lit from within by warm gold, deep navy shadow at the edges. Geography is suggested by glowing "
    "gold coastlines and rivers, NOT by any written labels. Elegant, museum-exhibit quality. "
)

STILL_BASE = f"{BRAND} 16:9 cinematic atmospheric still, shallow depth of field, volumetric golden light. "

VISUALS = {
    # ---- MAPS (text-free, glowing gold route) ----
    "co4_journey": ("20", MAP_BASE +
        "A single glowing gold route line traveling across the ancient world: from the rivers of "
        "Mesopotamia in the east, westward to the Levant, down into the Nile valley and Ethiopia, "
        "across the vast Sahara, and ending at the West African coast. The route is one continuous "
        "luminous gold thread with soft glowing waypoint dots. Epic journey-of-a-people feeling."),
    "in2_trail": ("21", MAP_BASE +
        "A glowing gold trail winding from the Near East into Africa, the parchment edges curling, "
        "a soft scholarly reading-lamp glow as if studied on a desk. Continuation of a long journey route."),
    "in3_scatter": ("22", MAP_BASE +
        "From a single bright gold point in the eastern Mediterranean / Holy Land region, many gold "
        "arrows radiate outward in every direction across the map — a great scattering / diaspora. "
        "Dramatic, dispersal energy, gold arrows fading into the dark edges."),
    "p13_ur": ("23", MAP_BASE +
        "Southern Mesopotamia between two glowing gold rivers meeting near a gulf; one bright pulsing "
        "gold point of light marks a single great city in the river delta, a thin thread of light "
        "waiting to travel. Intimate, focused, the cradle of civilization."),
    "p16_radiate": ("24", MAP_BASE +
        "A brilliant gold point of light between two rivers in the Near East, with rays and ripples of "
        "golden light radiating outward across the whole world map — civilization spreading from one "
        "valley to every continent. Triumphant, foundational."),
    # ---- ATMOSPHERIC STILLS ----
    "co1_ember": ("19", STILL_BASE +
        "An almost entirely black frame, a single tiny golden ember / point of light suspended in the "
        "center of vast darkness, the faintest warm glow around it. Genesis-of-everything, the void before light."),
    "in1_scroll": ("25", STILL_BASE +
        "An ancient open scroll on a dark surface, warm golden light raking across the aged papyrus, "
        "soft particles in the air, a reverent study-table mood. The parchment is blank (no writing)."),
    "in4_bible": ("26", STILL_BASE +
        "An open ancient book / Bible on dark wood, pages glowing with warm gold light from above, "
        "deep shadow around it, dust motes in a single light beam. Pages blank of legible text. Sacred study."),
    "p8_genealogy": ("27", STILL_BASE +
        "An unfurled aged vellum scroll on dark vellum, faint abstract gold filigree lines branching "
        "like a family tree but with NO readable letters, lit by warm gold, deep navy shadow. "
        "An ancient genealogy / table of nations feeling, purely decorative branching lines."),
    "in5_bloom": ("28", STILL_BASE +
        "A bloom of warm golden light opening in darkness and dissolving toward a faint distant river "
        "valley at dawn, soft and dreamlike, a transition from light into landscape."),
    # ---- ARCHIVAL-style aerial (generated fallback; real stock preferred if sourced) ----
    "p2_aerial": ("18", STILL_BASE +
        "A sweeping cinematic aerial of two great rivers winding through a fertile green floodplain "
        "between tan deserts, dawn light glinting gold on the water, date palms, no buildings, no people. "
        "Epic establishing landscape, the cradle between two rivers."),
}


def generate(vid: str):
    num, prompt = VISUALS[vid]
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
    b64 = r.json()["data"][0]["b64_json"]
    out = OUT_DIR / f"{num}_{vid}.png"
    out.write_bytes(base64.b64decode(b64))
    print(f"  wrote {out.relative_to(ROOT)} ({out.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    ids = [sys.argv[1]] if len(sys.argv) > 1 else list(VISUALS)
    for vid in ids:
        generate(vid)
