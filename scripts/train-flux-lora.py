"""
Train a FLUX LoRA on Black Hebrew Israelite reference stills.

Bundles images from training/lora-references/, uploads to fal.ai storage,
submits a training job, polls until done, and writes the resulting LoRA URL
to training/lora-config.json for use by render-via-pipeline.py.

Usage:
  python scripts/train-flux-lora.py
  python scripts/train-flux-lora.py --trigger-word aibgospels --steps 1500

Requires FAL_KEY env var. Reuses the one already in
C:/Users/Claude/ai-bible-gospels/.env if not set in this shell.
"""

import argparse
import json
import os
import sys
import time
import zipfile
from pathlib import Path

import requests

# Reuse FAL_KEY from sibling repo if not set in this shell
if not os.getenv("FAL_KEY"):
    from dotenv import load_dotenv
    sibling_env = Path("C:/Users/Claude/ai-bible-gospels/.env")
    if sibling_env.exists():
        load_dotenv(sibling_env)

FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("ERROR: FAL_KEY not set. Source it from .env or shell.", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
REFS_DIR = REPO_ROOT / "training" / "lora-references"
CONFIG_PATH = REPO_ROOT / "training" / "lora-config.json"

# fal.ai endpoints
STORAGE_URL = "https://rest.alpha.fal.ai/storage/upload/initiate"
TRAINING_URL = "https://queue.fal.run/fal-ai/flux-lora-fast-training"


def fal_headers():
    return {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}


def bundle_references(refs_dir: Path) -> Path:
    """Zip all image files in refs_dir (recursively), plus matching caption .txt files.

    Walks subdirectories so the user can organize images into folders by
    archetype (israelite/, greek/, edomite/, etc.) for visual curation —
    the trainer doesn't care about folder structure, so we FLATTEN
    everything to the zip root using the basename.

    Caption convention: an image at `judah-warrior-01.jpg` is paired with
    `judah-warrior-01.txt` (same stem). fal-ai/flux-lora-fast-training
    auto-detects these caption pairs.

    If two images in different subfolders happen to share a basename, the
    second one is renamed `{stem}__{parent-folder}{ext}` to avoid collisions.
    """
    image_exts = {".jpg", ".jpeg", ".png", ".webp"}
    images = sorted([p for p in refs_dir.rglob("*")
                    if p.is_file() and p.suffix.lower() in image_exts])
    if not images:
        print(f"ERROR: no image files (jpg/png/webp) found in {refs_dir}", file=sys.stderr)
        sys.exit(1)
    if len(images) < 10:
        print(f"WARN: only {len(images)} images. Recommended: 20-30 for a strong LoRA.",
              file=sys.stderr)

    # Detect folder structure for friendly log output
    subdirs = {p.parent.name for p in images if p.parent != refs_dir}
    if subdirs:
        print(f"  Walking subdirs: {sorted(subdirs)}")

    captioned = 0
    used_arcnames = set()
    zip_path = refs_dir.parent / "lora-dataset.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for img in images:
            # Flatten: collision-safe basename
            arcname = img.name
            if arcname in used_arcnames:
                arcname = f"{img.stem}__{img.parent.name}{img.suffix}"
            used_arcnames.add(arcname)
            zf.write(img, arcname=arcname)
            caption_path = img.with_suffix(".txt")
            if caption_path.exists():
                # Caption arcname follows the (possibly renamed) image arcname
                caption_arcname = Path(arcname).with_suffix(".txt").name
                zf.write(caption_path, arcname=caption_arcname)
                captioned += 1
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  Bundled {len(images)} images ({captioned} captioned) -> {zip_path} ({size_mb:.1f} MB)")
    if captioned == 0:
        print(f"  WARN: no .txt caption files found. Trainer will auto-caption — "
              f"lower quality for character LoRAs.")
    elif captioned < len(images):
        print(f"  WARN: {len(images) - captioned} images have no caption. "
              f"Consider adding matching .txt files.")
    return zip_path


def upload_to_fal_storage(zip_path: Path) -> str:
    """Upload a file to fal.ai storage. Returns the public URL.

    Uses the two-step protocol: POST /storage/upload/initiate returns a signed
    PUT URL, then we PUT the file body, and the original signed-URL response
    includes the final access URL.
    """
    print(f"  Uploading {zip_path.name} to fal.ai storage...")

    # Step 1 — request a signed upload URL
    resp = requests.post(
        STORAGE_URL,
        headers={"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"},
        json={"file_name": zip_path.name, "content_type": "application/zip"},
        timeout=30,
    )
    resp.raise_for_status()
    init_data = resp.json()
    upload_url = init_data.get("upload_url") or init_data.get("uploadUrl")
    file_url = init_data.get("file_url") or init_data.get("fileUrl") or init_data.get("access_url")
    if not upload_url or not file_url:
        print(f"  Unexpected initiate response: {init_data}", file=sys.stderr)
        sys.exit(1)

    # Step 2 — PUT the file body to the signed URL
    with zip_path.open("rb") as f:
        put_resp = requests.put(
            upload_url,
            data=f,
            headers={"Content-Type": "application/zip"},
            timeout=300,
        )
    put_resp.raise_for_status()
    print(f"  Upload complete: {file_url}")
    return file_url


def submit_training(images_zip_url: str, trigger_word: str, steps: int) -> str:
    """Submit training job to fal-ai/flux-lora-fast-training. Returns request_id."""
    print(f"  Submitting training (trigger='{trigger_word}', steps={steps})...")
    resp = requests.post(
        TRAINING_URL,
        headers=fal_headers(),
        json={
            "images_data_url": images_zip_url,
            "trigger_word": trigger_word,
            "steps": steps,
            "is_style": False,  # this is a subject/character LoRA, not pure style
            "create_masks": False,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    request_id = data.get("request_id")
    if not request_id:
        print(f"  Unexpected submit response: {data}", file=sys.stderr)
        sys.exit(1)
    print(f"  Training queued: request_id={request_id}")
    return request_id


def poll_training(request_id: str, poll_seconds: int = 30, max_wait_seconds: int = 3600) -> dict:
    """Poll training status until done or error."""
    status_url = f"https://queue.fal.run/fal-ai/flux-lora-fast-training/requests/{request_id}/status"
    result_url = f"https://queue.fal.run/fal-ai/flux-lora-fast-training/requests/{request_id}"

    start = time.time()
    while True:
        elapsed = int(time.time() - start)
        if elapsed > max_wait_seconds:
            print(f"  ERROR: timed out after {elapsed}s", file=sys.stderr)
            sys.exit(1)

        resp = requests.get(status_url, headers={"Authorization": f"Key {FAL_KEY}"}, timeout=30)
        resp.raise_for_status()
        status_data = resp.json()
        status = status_data.get("status", "unknown")
        print(f"  [{elapsed:>5}s] Status: {status}")

        if status == "COMPLETED":
            # Fetch the final result
            result_resp = requests.get(result_url, headers={"Authorization": f"Key {FAL_KEY}"}, timeout=30)
            result_resp.raise_for_status()
            return result_resp.json()
        elif status in ("FAILED", "CANCELLED", "ERROR"):
            print(f"  ERROR: training {status} — full status: {status_data}", file=sys.stderr)
            sys.exit(1)

        time.sleep(poll_seconds)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--trigger-word", default="aibgospels",
                        help="Word that activates the LoRA in prompts (default: aibgospels)")
    parser.add_argument("--steps", type=int, default=1500,
                        help="Training steps (default: 1500; range 1000-2500)")
    parser.add_argument("--refs-dir", default=str(REFS_DIR),
                        help="Directory of reference images")
    args = parser.parse_args()

    refs_dir = Path(args.refs_dir).resolve()
    if not refs_dir.exists():
        print(f"ERROR: {refs_dir} not found. Create it and drop reference images.", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print(f"FLUX LoRA Training — trigger='{args.trigger_word}'")
    print("=" * 60)

    # 1. Bundle references
    zip_path = bundle_references(refs_dir)

    # 2. Upload to fal storage
    zip_url = upload_to_fal_storage(zip_path)

    # 3. Submit training
    request_id = submit_training(zip_url, args.trigger_word, args.steps)

    # 4. Poll until done
    print("  Polling for completion (~10-30 min)...")
    result = poll_training(request_id)

    # 5. Extract LoRA URL
    diffusers_lora = result.get("diffusers_lora_file", {})
    lora_url = diffusers_lora.get("url") if isinstance(diffusers_lora, dict) else None
    if not lora_url:
        # Try alternate result schemas
        lora_url = result.get("lora_url") or result.get("file_url")
    if not lora_url:
        print(f"  Could not extract LoRA URL from result: {result}", file=sys.stderr)
        sys.exit(1)

    # 6. Write config for downstream consumers
    CONFIG_PATH.write_text(json.dumps({
        "lora_url": lora_url,
        "trigger_word": args.trigger_word,
        "training_steps": args.steps,
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "request_id": request_id,
        "image_count": len(list(refs_dir.glob("*.jpg")) + list(refs_dir.glob("*.png"))),
    }, indent=2), encoding="utf-8")

    print()
    print("=" * 60)
    print(f"DONE — LoRA trained.")
    print(f"  URL: {lora_url}")
    print(f"  Trigger word: {args.trigger_word}")
    print(f"  Config saved to: {CONFIG_PATH}")
    print("=" * 60)
    print()
    print("Next step: render with the LoRA via:")
    print(f"  python scripts/render-via-pipeline.py output/scenes/<file>.json --lora-url '{lora_url}'")
    print("(or the wrapper will auto-load from training/lora-config.json if --lora-url omitted)")


if __name__ == "__main__":
    main()
