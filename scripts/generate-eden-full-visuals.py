"""Generate Eden -> Timbuktu FULL DOC visuals (Parts Two-Eight + Conclusion) via gpt-image-1.

Reads output/manifests/eden-full-scenes.json (built by scripts/parse-scene-plan.py) and
renders every CARD / MAP / STILL. KLING scenes are skipped here — this script produces their
source stills only when --kling-stills is passed (Kling v3 is image-to-video, so each figure
clip needs a still first).

Identity: the suffixes come from scripts/script-to-scenes.py, the canonical framework. They are
NOT re-declared here. The manifest's resolved `identity` field decides which suffix applies —
explicitly, so Part Two's European scenes cannot be melanated by keyword accident.

Usage:
    python scripts/generate-eden-full-visuals.py --canary        # 4 proof scenes, no bulk spend
    python scripts/generate-eden-full-visuals.py --ids p2_1,p3_5
    python scripts/generate-eden-full-visuals.py --all
Output: output/cards/eden-full/<id>.png
"""
import argparse
import base64
import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
import requests

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
API_KEY = os.environ["OPENAI_API_KEY"]
MANIFEST = ROOT / "output" / "manifests" / "eden-full-scenes.json"
OUT_DIR = ROOT / "output" / "cards" / "eden-full"


def _load_converter():
    spec = importlib.util.spec_from_file_location("s2s", ROOT / "scripts" / "script-to-scenes.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S2S = _load_converter()
IDENTITY_SUFFIX = {
    "melanated": S2S.MELANATED_SUFFIX,
    "light": S2S.LIGHT_MELANATED_SUFFIX,
    # EUROPEAN_SUFFIX, not EDOM_SUFFIX: this doc's Europeans are post-biblical (Blumenbach's
    # 1795 study, Granada 1492). EDOM_SUFFIX would put them in ancient Edomite robes.
    "european": S2S.EUROPEAN_SUFFIX,
    "none": "",
}

# Brand constants mirror scripts/generate-eden-cards.py / generate-eden-visuals.py so Parts
# Two-Eight sit seamlessly beside Part One's already-rendered assets.
BRAND_TEXT = (
    "Brand identity: deep navy-black background with a subtle radial gradient slightly warmer toward center, "
    "sparse golden particles floating like dust in a light beam, bold gold serif font with a subtle warm glow, "
    "cinematic chiaroscuro lighting, bronze-warm tones, sacred-but-modern documentary mood. "
    "Elegant, reverent, high-end. No crosses, doves, faces, or figures. Spell every word EXACTLY as given."
)
BRAND_IMAGE = (
    "Brand identity: deep navy-black background, cinematic chiaroscuro, golden/amber light, "
    "sparse golden dust particles, bronze-warm tones, sacred-but-modern documentary mood, high-end and reverent."
)
# Maps get NO written labels — gpt-image-1 garbles small map text and the narration already
# speaks every place name (inherited from generate-eden-visuals.py).
MAP_BASE = (
    f"{BRAND_IMAGE} 16:9 cinematic documentary MAP graphic. An aged dark parchment / antique map texture "
    "lit from within by warm gold, deep navy shadow at the edges. Geography is suggested by glowing gold "
    "coastlines, rivers and routes, NOT by any written labels. Museum-exhibit quality. "
    "NO text, NO letters, NO words, NO labels, NO captions anywhere in the image."
)
NO_TEXT = " NO text, NO letters, NO words, NO captions anywhere in the image."

# Opt-in marker for the handful of stills that must carry words (the p4_3 family tree's
# per-medallion captions). Everything else stays text-free: the narration speaks every name,
# and gpt-image-1 garbles unspecified labels.
ALLOW_TEXT_RE = re.compile(r"\bALLOW TEXT\b", re.I)

# Scenes that must use a REAL public-domain artifact, never a generated one. The narration
# presents these as primary evidence ("on the maps the Europeans drew, there appeared..."), so a
# generated stand-in is a forged source — the exact "inauthentic content" charge that cost the
# channel monetization. On 2026-07-16 the generator silently invented a Catalan Atlas (p7_7).
# Refuse to generate these; they must be sourced by hand and dropped in.
MUST_SOURCE_RE = re.compile(r"source it, do not generate|genuine PD", re.I)


def sanitize(visual):
    """Strip authoring notation so only visual description reaches the model.

    The plan is written for humans: markdown bold, and bracketed directives aimed at us
    ("[EDOM/JAPHETH RULE — renders Caucasian European]", "[FIGURE → identity stack]").
    Those are instructions ABOUT the render, not content OF it — feeding them to
    gpt-image-1 invites it to draw a rulebook. Identity is applied via the resolved
    suffix instead, which is why stripping the marker here is safe.
    """
    # Authoring notes are written TO US and often name the exact thing a scene must avoid
    # (e.g. p6_5's note explains why Islam's founder must never appear). Letting one reach the
    # model would inject that subject into the prompt — the same backfire the note warns about.
    # Cut everything from the marker onward.
    v = re.split(r"\*{0,2}Authoring note", visual, flags=re.I)[0]
    v = re.sub(r"\[[^\]]*\]", " ", v)           # bracketed internal directives
    v = v.replace("**", "").replace("⭐", " ")   # markdown bold / flags
    v = re.sub(r"\s+", " ", v).strip()
    return v


def build_prompt(scene):
    src, ident = scene["source"], scene["identity"]
    visual = sanitize(scene["visual"])

    if src == "CARD":
        # Chapter cards carry their copy in the header note ("Chapter card: II. ...").
        # The Visual line is a transition/styling direction, not the words to set — feeding
        # it alone made the canary print "MOUNT ARARAT" instead of the chapter title.
        card_text = sanitize(scene.get("card_text", ""))
        if card_text:
            return (
                f"{BRAND_TEXT} 16:9 cinematic documentary card. Set EXACTLY this text and "
                f"nothing else: {card_text} "
                f"Styling: {visual}"
            )
        return f"{BRAND_TEXT} 16:9 cinematic documentary card. {visual}"

    if src == "MAP":
        return f"{MAP_BASE} Scene: {visual}"

    # STILL / ARCHIVAL-substitute / Kling source still.
    prompt = f"{BRAND_IMAGE} 16:9 cinematic documentary still. {visual}"
    prompt += IDENTITY_SUFFIX[ident]

    # SAFETY_SUFFIX ends with "no text, no letters, no symbols" — correct for almost every
    # still, but it CONTRADICTS a scene that needs captions, and the model resolves the
    # contradiction by garbling. The p4_3 family tree printed ISHMAEL twice and dropped Abraham
    # entirely because it was told to label a tree and render no letters in the same breath.
    # Scenes that genuinely need words opt in with "ALLOW TEXT"; they keep the photoreal/camera
    # half of the suffix and drop the no-text half.
    if ALLOW_TEXT_RE.search(visual):
        prompt += S2S.SAFETY_SUFFIX.replace(", no text, no letters, no symbols", "")
    else:
        prompt += S2S.SAFETY_SUFFIX
        if ident == "none":
            prompt += NO_TEXT
    return prompt


def generate(scene, retries=2):
    prompt = build_prompt(scene)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUT_DIR / f"{scene['id']}.png"

    for attempt in range(1, retries + 2):
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "gpt-image-1",
                "prompt": prompt,
                "size": "1536x1024",
                "quality": "high",
                "n": 1,
            },
            timeout=300,
        )
        if r.status_code == 200:
            b64 = r.json()["data"][0]["b64_json"]
            dest.write_bytes(base64.b64decode(b64))
            return dest, None
        if r.status_code in (429, 500, 502, 503) and attempt <= retries:
            time.sleep(8 * attempt)
            continue
        return None, f"HTTP {r.status_code}: {r.text[:200]}"
    return None, "retries exhausted"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canary", action="store_true",
                    help="4 proof scenes: card, map, melanated still, european still")
    ap.add_argument("--ids", help="comma-separated scene ids")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--kling-stills", action="store_true", help="include KLING source stills")
    ap.add_argument("--dry-run", action="store_true", help="print prompts, generate nothing")
    ap.add_argument("--limit", type=int, help="stop after N scenes (review in batches)")
    ap.add_argument("--redo", action="store_true",
                    help="regenerate even if the png already exists (default: skip, never re-pay)")
    args = ap.parse_args()

    scenes = json.loads(MANIFEST.read_text(encoding="utf-8"))["scenes"]
    by_id = {s["id"]: s for s in scenes}

    if args.canary:
        # Deliberately spans every code path — especially european, which must render
        # Caucasian. If that one comes back melanated the identity wiring is inverted.
        picks = ["p2_1", "p2_3", "p3_5", "p2_9"]
    elif args.ids:
        picks = [i.strip() for i in args.ids.split(",")]
    elif args.all:
        picks = [s["id"] for s in scenes
                 if s["source"] != "KLING" or args.kling_stills]
    else:
        ap.error("pass --canary, --ids, or --all")

    missing = [p for p in picks if p not in by_id]
    if missing:
        sys.exit(f"unknown scene ids: {missing}")

    # Resume-safe: an existing png is already-paid-for work. Skipping by default means a
    # batch can be re-run after an interruption without burning the quota twice.
    if not args.redo:
        already = [p for p in picks if (OUT_DIR / f"{p}.png").exists()]
        picks = [p for p in picks if p not in already]
        if already:
            print(f"skipping {len(already)} already rendered: {', '.join(already[:8])}"
                  f"{' …' if len(already) > 8 else ''}")

    if args.limit:
        remaining = len(picks) - args.limit
        picks = picks[:args.limit]
        if remaining > 0:
            print(f"--limit {args.limit}: {remaining} scene(s) left for the next batch")

    if not picks:
        print("nothing to do — all requested scenes already rendered")
        return

    # Hard refusal, not a warning: generating a stand-in for a real primary source would put a
    # forged artifact on screen while the narration calls it evidence.
    blocked = [p for p in picks if MUST_SOURCE_RE.search(by_id[p]["visual"])]
    if blocked:
        picks = [p for p in picks if p not in blocked]
        print(f"REFUSING to generate {len(blocked)} must-source scene(s): {', '.join(blocked)}")
        print("  These need a real public-domain artifact sourced by hand. Drop the file in as")
        print(f"  {OUT_DIR.relative_to(ROOT)}/<id>.png. A generated stand-in would be a forged source.\n")

    print(f"{len(picks)} scene(s) -> {OUT_DIR.relative_to(ROOT)}\n")
    ok = fail = 0
    for i, sid in enumerate(picks, 1):
        s = by_id[sid]
        tag = f"[{i}/{len(picks)}] {sid} ({s['source']}/{s['identity']})"
        if args.dry_run:
            print(f"{tag}\n  {build_prompt(s)[:400]}...\n")
            continue
        dest, err = generate(s)
        if dest:
            print(f"{tag} -> {dest.name} ({dest.stat().st_size/1024:.0f} KB)")
            ok += 1
        else:
            print(f"{tag} -> FAILED: {err}")
            fail += 1

    if not args.dry_run:
        print(f"\ndone: {ok} ok, {fail} failed")
        if fail:
            sys.exit(1)


if __name__ == "__main__":
    main()
