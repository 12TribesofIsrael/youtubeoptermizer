"""Render the Eden→Timbuktu figure scenes through Kling v3 (fal.ai), image-to-video.

Kling v3 is IMAGE-to-video: each clip starts from its gpt-image-1 source still in
output/cards/eden-full/<id>.png, which is uploaded to fal storage first.

Calling convention mirrors ai-bible-gospels/workflows/custom-script/generate.py (the proven
caller): v3 standard, 15s, cfg_scale 0.5, network retries at 30/90/180s because fal's TCP
connections reset during long renders.

AUDIO OFF ($0.084/s vs $0.126/s). These clips play under Tommy's narration and the SFX library —
Kling audio would only fight it. 15s x $0.084 = ~$1.26/clip.

Resume-safe: an existing local mp4 is already-paid-for work and is skipped unless --redo.
Order is by narrative priority so a budget stop-out loses the least important clip, not the most.

Usage:
    python scripts/render-eden-kling.py --list
    python scripts/render-eden-kling.py --ids cn_3            # the payoff shot first
    python scripts/render-eden-kling.py --all
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "output" / "manifests" / "eden-full-scenes.json"
STILL_DIR = ROOT / "output" / "cards" / "eden-full"
OUT_DIR = ROOT / "output" / "clips" / "eden-full-figures"

# FAL_KEY lives in the sibling repo's .env (READ-ONLY from here — we only read the key).
FAL_KEY = (dotenv_values(ROOT / ".env").get("FAL_KEY")
           or dotenv_values(ROOT.parent / "ai-bible-gospels" / ".env").get("FAL_KEY"))

# Standard caps at 720p even with a 1920x1080 16:9 input (measured 2026-07-16: 3:2 in -> 1176x784,
# 16:9 in -> 1280x720). Part One's six Kling clips are all 1920x1080, so mixing standard output
# into the same documentary would be visibly soft against them. Pro is the default for that
# reason; --standard is available when resolution doesn't matter.
KLING_TIERS = {
    "pro":      {"url": "https://fal.run/fal-ai/kling-video/v3/pro/image-to-video",      "rate": 0.112},
    "standard": {"url": "https://fal.run/fal-ai/kling-video/v3/standard/image-to-video", "rate": 0.084},
}
DURATION = "15"
TIER = "pro"                  # set in main() from --standard
KLING_URL = KLING_TIERS[TIER]["url"]
RATE_PER_SEC = KLING_TIERS[TIER]["rate"]     # audio off
COST_PER_CLIP = RATE_PER_SEC * int(DURATION)

# Narrative priority — if credits run short, the tail is what we lose.
PRIORITY = ["cn_3", "p4_4", "p7_6", "cn_5", "p4_2", "p5_4", "p7_5", "p8_8"]

# Camera move per scene. Kling's prompt field drives motion; the identity/content already
# lives in the source still, so keep these about the CAMERA, not the subject.
MOTION = {
    "p4_2": "Very slow cinematic push-in on the lone standing figure; dust drifting in golden dawn light.",
    "p4_4": "Slow, stately dolly forward down the hall toward the throne; torch flames flicker; the kneeling men stay still.",
    "p5_4": "Slow push-in on the enthroned king; shafts of light shift gently; regal stillness.",
    "p7_5": "The kneeling young man rises onto his feet in one continuous motion as the camera slowly cranes up with him; firelight flares.",
    "p7_6": "Slow sweeping aerial track alongside the immense procession crossing the desert; endless glinting gold; heat haze.",
    "p8_8": "Very slow, still, reverent drift; the ship barely moves on the dark water; the figures stand motionless looking back at the land.",
    # The source still already shows the host STANDING. Kling animates forward from frame 1, so
    # asking a standing crowd to "rise to their feet" would just produce mush. Crane over the
    # risen host instead and let the light do the work — the narration carries the resurrection.
    "cn_3": "Slow majestic crane upward and back over the vast standing host as dawn light spreads across the valley; dust and breath drifting in the golden air; the people hold still and hold the camera's gaze.",
    "cn_5": "Slow push-in on the faces; recognition dawning; warm golden light; the subjects hold the camera's gaze.",
}


def fal_headers():
    return {"Authorization": f"Key {FAL_KEY}"}


def prep_16x9(path):
    """Crop the 3:2 still to 16:9 and upscale to 1920x1080 before upload.

    Kling matches its output resolution to the INPUT aspect. Feeding gpt-image-1's native
    1536x1024 (3:2) yielded 1176x784 — visibly soft beside Part One's clips, which are all
    1920x1080 because that pipeline fed Kling 16:9 FLUX images (measured 2026-07-16).

    Cropping costs nothing real: the finished documentary is 16:9, so a 3:2 still gets cropped
    by the assembler regardless. Centre-crop keeps the subject, which every figure still frames
    centrally.
    """
    from PIL import Image
    im = Image.open(path).convert("RGB")
    target = 16 / 9
    w, h = im.size
    if w / h > target:                      # too wide — trim sides
        new_w = int(h * target)
        box = ((w - new_w) // 2, 0, (w - new_w) // 2 + new_w, h)
    else:                                   # too tall — trim top/bottom
        new_h = int(w / target)
        box = (0, (h - new_h) // 2, w, (h - new_h) // 2 + new_h)
    im = im.crop(box).resize((1920, 1080), Image.LANCZOS)

    prepped = OUT_DIR / "_kling_src"
    prepped.mkdir(parents=True, exist_ok=True)
    dest = prepped / Path(path).name
    im.save(dest)
    return dest


def upload_still(path):
    """Upload the local still to fal storage; Kling needs a URL, not bytes."""
    import fal_client
    os.environ["FAL_KEY"] = FAL_KEY
    return fal_client.upload_file(str(prep_16x9(path)))


def render(sid, index, total):
    still = STILL_DIR / f"{sid}.png"
    if not still.exists():
        return None, f"missing source still: {still.name} (Kling is image-to-video)"

    dest = OUT_DIR / f"{sid}.mp4"
    print(f"[{index}/{total}] {sid}: uploading still…")
    image_url = upload_still(still)

    payload = {
        "image_url": image_url,
        "prompt": MOTION.get(sid, "Slow cinematic camera movement."),
        "duration": DURATION,
        "cfg_scale": 0.5,
        # MUST be explicit: fal defaults generate_audio=true. Omitting it on 2026-07-16 billed
        # every clip at the audio-ON rate ($2.52 vs $1.68 on pro, +50%) for tracks that measured
        # -55.9 dB — i.e. we paid a premium for silence the narration overwrites anyway.
        # The RATE_PER_SEC table below assumes this flag is set. Never let them drift apart.
        "generate_audio": False,
    }

    backoff = [30, 90, 180]
    for attempt, sleep_for in enumerate(backoff + [None], start=1):
        try:
            print(f"[{index}/{total}] {sid}: Kling v3 render (attempt {attempt}) ~${COST_PER_CLIP:.2f}…")
            r = requests.post(KLING_URL, headers=fal_headers(), json=payload, timeout=1800)
            r.raise_for_status()
            break
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError) as e:
            if sleep_for is None:
                return None, f"network failure after {attempt} attempts: {e}"
            print(f"[{index}/{total}] {sid}: {type(e).__name__} — retrying in {sleep_for}s")
            time.sleep(sleep_for)
        except requests.exceptions.HTTPError as e:
            return None, f"HTTP {r.status_code}: {r.text[:200]}"

    data = r.json()
    url = (data.get("video") or {}).get("url") or data.get("data", {}).get("video", {}).get("url")
    if not url:
        return None, f"no video url in response: {json.dumps(data)[:200]}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    vid = requests.get(url, timeout=600)
    dest.write_bytes(vid.content)
    return dest, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", help="comma-separated scene ids")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--redo", action="store_true", help="re-render even if the mp4 exists")
    ap.add_argument("--standard", action="store_true",
                    help="use the cheaper standard tier (720p — softer than Part One's 1080p clips)")
    args = ap.parse_args()

    global TIER, KLING_URL, RATE_PER_SEC, COST_PER_CLIP
    TIER = "standard" if args.standard else "pro"
    KLING_URL = KLING_TIERS[TIER]["url"]
    RATE_PER_SEC = KLING_TIERS[TIER]["rate"]
    COST_PER_CLIP = RATE_PER_SEC * int(DURATION)
    print(f"tier: kling v3 {TIER} | ${COST_PER_CLIP:.2f}/clip (15s, audio off)\n")

    if not FAL_KEY:
        sys.exit("FAL_KEY not found in .env or ../ai-bible-gospels/.env")

    scenes = json.loads(MANIFEST.read_text(encoding="utf-8"))["scenes"]
    kling = [s["id"] for s in scenes if s["source"] == "KLING"]
    ordered = [i for i in PRIORITY if i in kling] + [i for i in kling if i not in PRIORITY]

    if args.list:
        bal = requests.get("https://rest.alpha.fal.ai/billing/user_balance",
                           headers=fal_headers(), timeout=20).text
        print(f"fal balance: ${float(bal):.2f} | ${COST_PER_CLIP:.2f}/clip (15s, audio off)\n")
        print("priority order:")
        for i, sid in enumerate(ordered, 1):
            has_still = (STILL_DIR / f"{sid}.png").exists()
            done = (OUT_DIR / f"{sid}.mp4").exists()
            print(f"  {i}. {sid:6s} still:{'yes' if has_still else 'MISSING':7s} clip:{'done' if done else '-'}")
        return

    picks = [i.strip() for i in args.ids.split(",")] if args.ids else (ordered if args.all else None)
    if not picks:
        ap.error("pass --list, --ids, or --all")

    if not args.redo:
        picks = [p for p in picks if not (OUT_DIR / f"{p}.mp4").exists()]
    if not picks:
        print("nothing to do — all requested clips already rendered")
        return

    print(f"{len(picks)} clip(s) — est ${len(picks)*COST_PER_CLIP:.2f}\n")
    ok = fail = 0
    for i, sid in enumerate(picks, 1):
        dest, err = render(sid, i, len(picks))
        if dest:
            print(f"[{i}/{len(picks)}] {sid} -> {dest.name} ({dest.stat().st_size/1e6:.1f} MB)\n")
            ok += 1
        else:
            print(f"[{i}/{len(picks)}] {sid} FAILED: {err}\n")
            fail += 1
    print(f"done: {ok} ok, {fail} failed | spent ~${ok*COST_PER_CLIP:.2f}")


if __name__ == "__main__":
    main()
