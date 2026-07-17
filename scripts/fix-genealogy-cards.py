"""Rebuild the two genealogy cards (p5_1 chapter title, p5_6 the 42-name payoff) that
gpt-image-1 fabricated.

WHAT WENT WRONG (2026-07-17): both cards were model-generated and both are falsified.
  - p5_1's manifest "visual" says "...dissolve to a scroll listing name after name." The
    generator set that styling right after "set EXACTLY ... nothing else: V. The Lineage of
    the Messiah" — so the model drew the scroll of names it was describing and dropped the
    title. Description leaked into copy (the recurring root cause).
  - p5_6 (card_text empty) got its "three groups of fourteen names pulse" visual fed straight
    to the model, which invented 36 names.
  - The invented names are modern-translation spellings, not the 1611 KJV this channel reads
    (Uzziah/Shealtiel/Zerubbabel/Amos vs KJV Ozias/Salathiel/Zorobabel/Amon), one is
    misspelled ("Uziah"), and both lists run off the bottom edge.

THE FIX (project rule [[feedback_typeset_scripture_never_generate]]): the model renders only
the LIGHT (text-free background); PIL renders the WORDS. Names are pasted verbatim from
Matthew 1 in docs/1611KjvW_apocrypha - Copy.pdf — three groups of fourteen exactly as the
KJV enumerates them, culminating in Christ.

Usage:
  python scripts/fix-genealogy-cards.py --bg      # (re)generate the two text-free backgrounds
  python scripts/fix-genealogy-cards.py           # typeset over existing backgrounds
  python scripts/fix-genealogy-cards.py --bg --typeset   # both
"""
import argparse
import base64
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
API_KEY = os.environ.get("OPENAI_API_KEY")

OUT_DIR = ROOT / "output" / "cards" / "eden-full"
REJECT = OUT_DIR / "_rejected"

FONT = "C:/Windows/Fonts/constan.ttf"       # Constantia — documentary serif
FONT_B = "C:/Windows/Fonts/constanb.ttf"    # bold
GOLD = (232, 183, 90)
GOLD_DIM = (196, 150, 74)

# --- VERBATIM 1611 KJV, Matthew 1:2-16, in Matthew's own three groups of fourteen ---
GROUP_1 = ["Abraham", "Isaac", "Jacob", "Judas", "Phares", "Esrom", "Aram",
           "Aminadab", "Naasson", "Salmon", "Booz", "Obed", "Jesse", "David"]
GROUP_2 = ["Solomon", "Roboam", "Abia", "Asa", "Josaphat", "Joram", "Ozias",
           "Joatham", "Achaz", "Ezekias", "Manasses", "Amon", "Josias", "Jechonias"]
GROUP_3 = ["Salathiel", "Zorobabel", "Abiud", "Eliakim", "Azor", "Sadoc", "Achim",
           "Eliud", "Eleazar", "Matthan", "Jacob", "Joseph", "JESUS CHRIST"]

BG_PROMPTS = {
    "_bg_p5_1.png": (
        "Deep navy-black background with a subtle radial gradient slightly warmer toward the "
        "center, cinematic chiaroscuro, a soft vertical beam of golden light, sparse golden "
        "dust particles drifting in the beam, bronze-warm tones, sacred-but-modern documentary "
        "mood, elegant and reverent, high-end. 16:9. Generous empty dark negative space in the "
        "center for a title to be added later. NO text, NO letters, NO words, NO scroll, "
        "NO faces, NO figures anywhere in the image."
    ),
    "_bg_p5_6.png": (
        "Deep navy-black background with a warm golden radiance blooming softly from the upper "
        "center, as if light is breaking through, cinematic chiaroscuro, sparse golden dust "
        "particles, bronze-warm tones, sacred-but-modern documentary mood, reverent and "
        "high-end. 16:9. The glow is soft and even so overlaid text stays readable; large calm "
        "dark areas. NO text, NO letters, NO words, NO scroll, NO faces, NO figures anywhere."
    ),
}


def gen_bg(name, prompt, retries=2):
    if not API_KEY:
        raise SystemExit("OPENAI_API_KEY not set — cannot generate backgrounds")
    dest = OUT_DIR / name
    for attempt in range(1, retries + 2):
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": "gpt-image-1", "prompt": prompt,
                  "size": "1536x1024", "quality": "high", "n": 1},
            timeout=300,
        )
        if r.status_code == 200:
            dest.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
            print(f"  bg -> {dest.relative_to(ROOT)}")
            return dest
        if r.status_code in (429, 500, 502, 503) and attempt <= retries:
            time.sleep(8 * attempt)
            continue
        raise SystemExit(f"bg {name}: HTTP {r.status_code}: {r.text[:200]}")


def glow_text(img, xy, text, font, fill, passes=6, blur=9):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(xy, text, font=font, fill=fill + (255,))
    blurred = layer.filter(ImageFilter.GaussianBlur(blur))
    for _ in range(passes):
        img.alpha_composite(blurred)
    img.alpha_composite(layer)


def _open_bg(name):
    p = OUT_DIR / name
    if not p.exists():
        raise SystemExit(f"missing background {p} — run with --bg first")
    return Image.open(p).convert("RGBA")


def typeset_title():
    """p5_1 — chapter title card: 'V.' over 'THE LINEAGE OF THE MESSIAH'."""
    img = _open_bg("_bg_p5_1.png")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    f_num = ImageFont.truetype(FONT, int(H * 0.085))
    f_ttl = ImageFont.truetype(FONT_B, int(H * 0.11))

    num = "V."
    title_lines = ["THE LINEAGE", "OF THE MESSIAH"]
    line_h = int(H * 0.135)
    block_h = int(H * 0.10) + line_h * len(title_lines)
    y = (H - block_h) / 2 - int(H * 0.02)

    w = draw.textlength(num, font=f_num)
    glow_text(img, ((W - w) / 2, y), num, f_num, GOLD_DIM, passes=4)
    y += int(H * 0.11)
    for ln in title_lines:
        w = draw.textlength(ln, font=f_ttl)
        glow_text(img, ((W - w) / 2, y), ln, f_ttl, GOLD)
        y += line_h

    dest = OUT_DIR / "p5_1.png"
    img.convert("RGB").save(dest)
    print(f"p5_1: chapter title typeset -> {dest.relative_to(ROOT)}")


def typeset_names():
    """p5_6 — three columns of 14 KJV names, JESUS CHRIST as the culmination."""
    img = _open_bg("_bg_p5_6.png")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    f_name = ImageFont.truetype(FONT, int(H * 0.040))
    f_last = ImageFont.truetype(FONT_B, int(H * 0.044))

    cols = [GROUP_1, GROUP_2, GROUP_3]
    col_x = [W * 0.22, W * 0.50, W * 0.78]     # column centers
    row_h = int(H * 0.058)
    top = H * 0.13
    n_rows = max(len(c) for c in cols)
    block_h = row_h * (n_rows - 1)
    start_y = (H - block_h) / 2 - int(H * 0.04)

    for cx, col in zip(col_x, cols):
        y = start_y
        for name in col:
            culmination = name == "JESUS CHRIST"
            font = f_last if culmination else f_name
            fill = GOLD if culmination else GOLD_DIM
            passes = 7 if culmination else 3
            w = draw.textlength(name, font=font)
            glow_text(img, (cx - w / 2, y), name, font, fill, passes=passes)
            y += row_h

    dest = OUT_DIR / "p5_6.png"
    img.convert("RGB").save(dest)
    print(f"p5_6: {sum(len(c) for c in cols)} KJV names typeset (3 groups) -> {dest.relative_to(ROOT)}")


def quarantine_originals():
    REJECT.mkdir(parents=True, exist_ok=True)
    for sid in ("p5_1", "p5_6"):
        src = OUT_DIR / f"{sid}.png"
        if src.exists():
            dst = REJECT / f"{sid}_FABRICATED_gptimage.png"
            if not dst.exists():           # keep the first evidence copy only
                src.replace(dst)
                print(f"  quarantined original {sid}.png -> {dst.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", action="store_true", help="(re)generate the two text-free backgrounds")
    ap.add_argument("--typeset", action="store_true", help="typeset the cards (default if no flags)")
    args = ap.parse_args()
    do_bg = args.bg
    do_typeset = args.typeset or not args.bg

    if do_typeset:
        quarantine_originals()
    if do_bg:
        for name, prompt in BG_PROMPTS.items():
            gen_bg(name, prompt)
    if do_typeset:
        typeset_title()
        typeset_names()


if __name__ == "__main__":
    main()
