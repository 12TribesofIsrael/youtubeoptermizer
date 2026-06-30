"""Source real public-domain artifact photos from the Met Museum Open Access API
for the Eden -> Timbuktu Part 1 artifact scenes (p11 Sumerian statue, p12 cuneiform
tablet, p14 Egyptian relief / Babylonian / Ethiopian).

Why real photos, not AI: these are the scenes where the narration puts "the receipts on
the table" (votive statues, cuneiform). Authentic museum images carry more weight with
viewers AND with YouTube reviewers than a generated illustration would.

Met API (public, no key): /search?q=...&hasImages=true  ->  /objects/{id} -> primaryImage.
We filter to isPublicDomain=true so the images are free to use.

Usage: python scripts/source-met-artifacts.py
Output: output/stills/eden-part1/<slug>_<objectID>.jpg
"""
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "stills" / "eden-part1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEARCH = "https://collectionapi.metmuseum.org/public/collection/v1/search"
OBJECT = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}"

# slug -> (search query, dept filter substring or None, how many to grab)
QUERIES = {
    "sumerian-statue": ("Sumerian votive figure", "Ancient Near Eastern Art", 2),
    "cuneiform-tablet": ("cuneiform tablet", "Ancient Near Eastern Art", 2),
    "babylonian-relief": ("Babylonian relief", "Ancient Near Eastern Art", 1),
    "egyptian-relief": ("Egyptian relief king", "Egyptian Art", 2),
    "nubian-kushite": ("Kushite Nubian", "Egyptian Art", 2),
}


def grab(slug: str, query: str, dept: str | None, n: int):
    print(f"[{slug}] searching '{query}'...")
    r = requests.get(SEARCH, params={"q": query, "hasImages": "true"}, timeout=60)
    r.raise_for_status()
    ids = r.json().get("objectIDs") or []
    if not ids:
        print("  no results")
        return 0
    got = 0
    for oid in ids[:60]:
        if got >= n:
            break
        try:
            o = requests.get(OBJECT.format(oid), timeout=60).json()
        except Exception as e:
            continue
        if not o.get("isPublicDomain"):
            continue
        img = o.get("primaryImage") or o.get("primaryImageSmall")
        if not img:
            continue
        if dept and dept.lower() not in (o.get("department", "").lower()):
            continue
        try:
            data = requests.get(img, timeout=120).content
        except Exception:
            continue
        if len(data) < 30_000:  # skip thumbnails / broken
            continue
        title = re.sub(r"[^a-z0-9]+", "-", (o.get("title") or "untitled").lower())[:40].strip("-")
        out = OUT_DIR / f"{slug}_{oid}_{title}.jpg"
        out.write_bytes(data)
        print(f"  + {out.name}  ({len(data)/1024:.0f} KB) — {o.get('objectDate','?')}, {o.get('department','?')}")
        got += 1
        time.sleep(0.3)
    if got == 0:
        print("  no public-domain image matched the dept filter")
    return got


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    total = 0
    for slug, (q, dept, n) in QUERIES.items():
        if only and slug != only:
            continue
        total += grab(slug, q, dept, n)
    print(f"\nDone: {total} artifact images -> {OUT_DIR.relative_to(ROOT)}")
