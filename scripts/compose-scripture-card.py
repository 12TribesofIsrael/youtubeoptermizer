"""Typeset a scripture card: real font over a text-free generated background.

WHY THIS EXISTS: gpt-image-1 cannot be trusted to render scripture. On the Eden→Timbuktu
Deuteronomy 28:68 card (2026-07-16) it produced, across three attempts:
  - dropped "and bondwomen" entirely + no closing quote  (a truncated verse = a falsified verse)
  - "enemiess", "DEUTERONOMMY"
  - "ERING" for "BRING", "DEUTERONOMMY" again
The misspellings are systematic, not unlucky, and they look authoritative — gold serif on black
reads as scripture whether or not the words are right. On a scripture channel that is the one
error we must never ship.

So: the model renders only the LIGHT (background, book, ship, negative space) and Python renders
the WORDS. Typeset text is correct by construction.

Verse text MUST be pasted verbatim from `docs/1611KjvW_apocrypha - Copy.pdf` via pdftotext —
never from model memory. See memory [[feedback_card_copy_must_be_literal]].

Usage: python scripts/compose-scripture-card.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "cards" / "eden-full"

FONT = "C:/Windows/Fonts/constan.ttf"        # Constantia — documentary serif
FONT_SC = "C:/Windows/Fonts/constanb.ttf"    # bold, for the reference line
GOLD = (232, 183, 90)
GOLD_DIM = (196, 150, 74)

CARDS = [
    {
        "id": "p8_12",
        "bg": "_bg_p8_12.png",
        # VERBATIM 1611 KJV, Deut 28:68, elided exactly as the narration speaks it.
        "verse": ("“And the LORD shall bring thee into Egypt again with ships… "
                  "and there ye shall be sold unto your enemies for bondmen and bondwomen, "
                  "and no man shall buy you.”"),
        "ref": "DEUTERONOMY 28:68",
        "size": 62,
        "top": 0.10,      # verse block starts here (fraction of height)
    },
]


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def glow_text(img, xy, text, font, fill, passes=6):
    """Cheap warm glow: repeated faint offsets under the crisp glyph."""
    from PIL import ImageFilter
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, text, font=font, fill=fill + (255,))
    blur = layer.filter(ImageFilter.GaussianBlur(9))
    for _ in range(passes):
        img.alpha_composite(blur)
    img.alpha_composite(layer)


def compose(card):
    bg_path = OUT_DIR / card["bg"]
    if not bg_path.exists():
        raise SystemExit(f"missing background: {bg_path}")
    img = Image.open(bg_path).convert("RGBA")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    f_verse = ImageFont.truetype(FONT, card["size"])
    f_ref = ImageFont.truetype(FONT_SC, int(card["size"] * 0.42))

    lines = wrap(draw, card["verse"], f_verse, int(W * 0.78))
    lh = int(card["size"] * 1.38)
    y = int(H * card["top"])

    for ln in lines:
        w = draw.textlength(ln, font=f_verse)
        glow_text(img, ((W - w) / 2, y), ln, f_verse, GOLD)
        y += lh

    y += int(lh * 0.45)
    ref = " ".join(card["ref"])          # letter-spaced caps
    w = draw.textlength(ref, font=f_ref)
    glow_text(img, ((W - w) / 2, y), ref, f_ref, GOLD_DIM, passes=4)

    dest = OUT_DIR / f"{card['id']}.png"
    img.convert("RGB").save(dest)
    print(f"{card['id']}: {len(lines)} lines typeset -> {dest.relative_to(ROOT)}")
    print(f"  verse: {card['verse']}")


if __name__ == "__main__":
    for c in CARDS:
        compose(c)
