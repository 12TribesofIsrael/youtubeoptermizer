"""Generate viral thumbnails for the full "From Eden to Timbuktu" documentary.

Two-stage, reliable-text pattern (see [[typeset_scripture_never_generate]]):
  1. fal FLUX-pro renders ONLY the image (melanated Black Hebrew Israelite figure +
     golden chiaroscuro + deliberate dark negative space for the title). No text baked in.
  2. PIL typesets the gold serif title with a dark stroke + warm glow so it is crisp and
     legible at small size. Correct-by-construction text.

OpenAI gpt-image-1 is billing-capped, so backgrounds go through fal FLUX-pro
(fal-ai/flux-pro/v1.1, 1280x720) like Part One. FAL_KEY is read from this repo's .env
or the sibling ai-bible-gospels/.env (read-only key reuse).

Three CTR-forward variants; Tommy picks one.
Output: output/thumbnails/eden-full/<NN>_<variant>.png  (1280x720, YouTube-ready)

Usage: python scripts/generate-eden-full-thumbnail.py [variant]   (default: all)
"""
import io
import sys
from pathlib import Path

import requests
from dotenv import dotenv_values
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "thumbnails" / "eden-full"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FAL_KEY = (dotenv_values(ROOT / ".env").get("FAL_KEY")
           or dotenv_values(ROOT.parent / "ai-bible-gospels" / ".env").get("FAL_KEY"))
FLUX_URL = "https://fal.run/fal-ai/flux-pro/v1.1"

W, H = 1280, 720
GOLD = (240, 194, 102)
GOLD_DIM = (206, 158, 82)
FONT = "C:/Windows/Fonts/constanb.ttf"     # Constantia Bold — brand documentary serif

# Identity stack — required so FLUX renders melanated figures, not Caucasian.
IDENTITY = (
    "a Black Hebrew Israelite man, dark-brown to deep-brown melanated African American "
    "complexion, wool-textured tightly coiled hair and beard, NOT white, NOT pale, NOT "
    "light-skinned, no Caucasian or European features"
)
BRAND = (
    "cinematic documentary key art, deep navy-black background, dramatic chiaroscuro, "
    "divine golden and amber light breaking through darkness, warm bronze tones, sparse "
    "golden embers, ultra sharp, high contrast, photorealistic, no text, no letters, no words"
)

# Each variant: (num, flux_prompt, [ (text, y_frac, size, kicker_bool), ... ], text_align)
VARIANTS = {
    # Regal king, right third; large dark negative space on the LEFT for the title.
    "hebrews": (
        "01",
        f"Right third of frame: a regal, powerful {IDENTITY}, a Hebrew Israelite king in "
        f"earth-tone and gold robes, direct intense eye contact with the camera, lit from "
        f"behind by golden light, a faint ancient ziggurat in deep shadow behind him. The LEFT "
        f"two-thirds of the frame is deep navy-black empty negative space with only faint golden "
        f"embers. {BRAND}",
        [("FROM EDEN TO TIMBUKTU", 0.16, 46, True),
         ("THE BLACK", 0.34, 132, False),
         ("HEBREWS", 0.55, 132, False)],
        "left",
    ),
    # Intense close-up face, right side; title stacked on the left.
    "erased": (
        "02",
        f"A tight dramatic close-up portrait on the RIGHT side of the frame of {IDENTITY}, "
        f"eyes locked directly on the camera with a solemn powerful expression, half his face "
        f"in golden rim light and half in shadow. The LEFT half of the frame is deep navy-black "
        f"negative space. {BRAND}",
        [("THE HISTORY", 0.30, 118, False),
         ("THEY ERASED", 0.52, 118, False)],
        "left",
    ),
    # Epic wide: lone figure walking toward golden light; centered lower title.
    "origin": (
        "03",
        f"Epic wide cinematic shot: a lone {IDENTITY} in flowing robes seen from behind and "
        f"slightly to the side, walking toward a monumental golden-lit horizon where an ancient "
        f"ziggurat and the mud-brick towers of Timbuktu rise through parting clouds and beams of "
        f"divine light. Vast scale, the sky filled with golden light, the lower third darker for "
        f"a title. {BRAND}",
        [("FROM EDEN TO TIMBUKTU", 0.60, 74, False),
         ("THE HIDDEN HISTORY OF THE BLACK HEBREWS", 0.76, 34, True)],
        "center",
    ),
}


def flux_bg(prompt: str) -> Image.Image:
    if not FAL_KEY:
        sys.exit("FAL_KEY not found in .env or ../ai-bible-gospels/.env")
    r = requests.post(
        FLUX_URL,
        headers={"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"},
        json={
            "prompt": prompt,
            "image_size": {"width": W, "height": H},
            "num_images": 1,
            "output_format": "png",
            "safety_tolerance": "5",
        },
        timeout=300,
    )
    if r.status_code != 200:
        sys.exit(f"FLUX error {r.status_code}: {r.text[:400]}")
    url = r.json()["images"][0]["url"]
    img = Image.open(io.BytesIO(requests.get(url, timeout=120).content)).convert("RGBA")
    return img.resize((W, H), Image.LANCZOS)


def scrim(img: Image.Image, align: str):
    """Darken the title side so gold text always reads."""
    grad = Image.new("L", (W, 1))
    for x in range(W):
        f = x / W
        if align == "left":
            a = int(200 * max(0.0, 1.0 - f * 1.7))      # dark on left, clears to the right
        else:
            a = 0
        grad.putpixel((x, 0), a)
    mask = grad.resize((W, H))
    if align == "center":
        # bottom vignette for the centered title
        vmask = Image.new("L", (1, H))
        for y in range(H):
            vmask.putpixel((0, y), int(210 * max(0.0, (y / H - 0.45) / 0.55)))
        mask = vmask.resize((W, H))
    black = Image.new("RGBA", (W, H), (4, 6, 14, 255))
    img.alpha_composite(Image.composite(black, Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                                        mask))


def glow(img, xy, text, font, fill, stroke=6):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, text, font=font, fill=fill + (255,))
    blur = layer.filter(ImageFilter.GaussianBlur(11))
    for _ in range(5):
        img.alpha_composite(blur)
    # crisp glyph with dark stroke for contrast at small size
    d2 = ImageDraw.Draw(img)
    d2.text(xy, text, font=font, fill=fill + (255,),
            stroke_width=stroke, stroke_fill=(10, 8, 4, 255))


def place(img, lines, align):
    draw = ImageDraw.Draw(img)
    margin = int(W * 0.05)
    for text, yf, size, kicker in lines:
        font = ImageFont.truetype(FONT, size)
        col = GOLD_DIM if kicker else GOLD
        disp = " ".join(text) if kicker else text     # letter-space the small kicker
        tw = draw.textlength(disp, font=font)
        if align == "center":
            x = (W - tw) / 2
        else:
            x = margin
        glow(img, (x, int(H * yf)), disp, font, col, stroke=3 if kicker else 6)


def build(vid):
    num, prompt, lines, align = VARIANTS[vid]
    print(f"[{vid}] FLUX background...")
    img = flux_bg(prompt)
    scrim(img, align)
    place(img, lines, align)
    out = OUT_DIR / f"{num}_{vid}.png"
    img.convert("RGB").save(out, quality=95)
    print(f"  wrote {out.relative_to(ROOT)} ({out.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    ids = [sys.argv[1]] if len(sys.argv) > 1 else list(VARIANTS)
    for vid in ids:
        build(vid)
