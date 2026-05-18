"""
Move LoRA training files into archetype subdirectories for human pruning.

Reads each .txt caption in training/lora-references/, detects the archetype
from the `aibgospels [archetype], ...` prefix (set by rewrite-lora-captions.py),
and moves both the .jpg and .txt into training/lora-references/{archetype}/.

After organizing you can prune by archetype quickly (e.g., delete entire
`bad-renders/` subfolder, review `israelite/` for off-target images, etc).
The trainer (scripts/train-flux-lora.py) recursively walks subdirectories
and flattens them into the zip, so folder organization doesn't affect training.

Usage:
  python scripts/organize-lora-references.py
  python scripts/organize-lora-references.py --dry-run
"""

import argparse
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = REPO_ROOT / "training" / "lora-references"

# Match: "aibgospels {archetype}, ..." at the start of a caption
ARCHETYPE_RE = re.compile(r"^\s*aibgospels\s+([a-z]+)\s*,", re.IGNORECASE)


def detect_from_caption(caption: str) -> str:
    """Read the archetype tag set by rewrite-lora-captions.py."""
    m = ARCHETYPE_RE.match(caption)
    if m:
        return m.group(1).lower()
    return "untagged"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", default=str(DEFAULT_DIR))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    refs_dir = Path(args.dir).resolve()
    moves = []  # (src_jpg, src_txt, dest_dir)
    counts = Counter()
    no_caption = []

    # Only process top-level files — don't re-shuffle already-organized subdirs
    for jpg in sorted(refs_dir.glob("*.jpg")):
        txt = jpg.with_suffix(".txt")
        if not txt.exists():
            no_caption.append(jpg.name)
            archetype = "no-caption"
        else:
            caption = txt.read_text(encoding="utf-8").strip()
            archetype = detect_from_caption(caption)
        counts[archetype] += 1
        dest_dir = refs_dir / archetype
        moves.append((jpg, txt if txt.exists() else None, dest_dir))

    print(f"{'(DRY RUN) ' if args.dry_run else ''}Planning to organize {len(moves)} files:")
    for archetype, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {n:>4}  -> {refs_dir.name}/{archetype}/")
    if no_caption:
        print(f"\n  {len(no_caption)} files have no caption -> moved to no-caption/")

    if args.dry_run:
        print("\n(Dry run — nothing moved.)")
        return

    # Apply moves
    for jpg, txt, dest_dir in moves:
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(jpg), str(dest_dir / jpg.name))
        if txt:
            shutil.move(str(txt), str(dest_dir / txt.name))

    print(f"\nDone. Subdirs in {refs_dir}:")
    for sub in sorted(refs_dir.iterdir()):
        if sub.is_dir():
            n = len(list(sub.glob("*.jpg")))
            print(f"  {sub.name}/  ({n} images)")

    print()
    print("Next steps:")
    print("  1. Open each subfolder, delete bad/off-target images")
    print("  2. python scripts/train-flux-lora.py")
    print("     (trainer flattens subdirs into the zip automatically)")


if __name__ == "__main__":
    main()
