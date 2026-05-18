"""
Rewrite LoRA training captions to prepend the channel trigger word + the
detected nationality archetype. Standardizes all .txt files in
training/lora-references/ so the LoRA learns a single coherent style
with archetype distinctions.

Detection is keyword-based against the existing caption text. Records that
match multiple nationalities (mixed scenes) get the dominant one or fall
back to `scene`. A dry-run mode lets you spot-check before writing.

Usage:
  python scripts/rewrite-lora-captions.py --dry-run     # preview, no writes
  python scripts/rewrite-lora-captions.py               # apply
  python scripts/rewrite-lora-captions.py --trigger-word aibgospels
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = REPO_ROOT / "training" / "lora-references"

# Detection rules — first match wins (ordered by specificity / theological priority).
# Each entry: (archetype_word, regex_pattern, hint)
DETECTION_RULES = [
    # Specific named Israelite figures
    ("israelite", r"\b(Black Hebrew Israelite|melanated|deeply melanated|wool[- ]textured|natural afro)\b", "explicit BHI markers"),
    ("israelite", r"\b(Jacob|Isaac|Rebekah|Joseph|Judah|Levi|Moses|Elijah|David|Solomon|Israelite|Hebrew patriarch|Hebrew prophet|Hebrew priest|tribe of [A-Z])\b", "Israelite named figure"),

    # Esau/Edomite — Caucasian per channel theology
    ("edomite", r"\b(Esau\b(?!.*newborn)|Edom\b|Edomite|Edomites)\b", "Edomite ref (note newborn-Esau exception)"),

    # Greek / Seleucid / Hellenistic
    ("greek", r"\b(Seleucid|Greek|Hellenistic|Demetrius|Alcimus|Antiochus|Eupolemus|olive[- ]skin|Macedonian)\b", "Greek/Seleucid ref"),

    # Egyptian
    ("egyptian", r"\b(Egyptian|Pharaoh|Cleopatra|Memphis|Thebes)\b", "Egyptian ref"),

    # Persian / Mede
    ("persian", r"\b(Persian|Mede\b|Medes|Cyrus|Darius)\b", "Persian ref"),

    # Roman
    ("roman", r"\b(Roman|centurion|legionnaire|toga|Caesar)\b", "Roman ref"),

    # Phoenician / Canaanite
    ("canaanite", r"\b(Canaanite|Phoenician|Philistine)\b", "Canaanite/Philistine ref"),
]

# Non-biblical content that should be flagged for likely deletion
NON_BIBLICAL_PATTERNS = [
    r"\b(entrepreneur|rowhome|coffee mug|kitchen table|laptop|office)\b",
    r"\b(modern|contemporary|2020|2023|2024|2025|2026)\b",
]


def detect_archetype(caption: str) -> tuple:
    """Returns (archetype, reason). archetype is 'israelite'/'greek'/etc or 'scene' fallback."""
    for archetype, pattern, reason in DETECTION_RULES:
        if re.search(pattern, caption, re.IGNORECASE):
            return archetype, reason
    return "scene", "no archetype keywords matched"


def is_likely_non_biblical(caption: str) -> bool:
    return any(re.search(p, caption, re.IGNORECASE) for p in NON_BIBLICAL_PATTERNS)


def rewrite_caption(caption: str, trigger: str, archetype: str) -> str:
    """Prepend trigger + archetype to caption. Strip any existing trigger prefix to avoid double-prefixing."""
    # If caption already starts with the trigger, leave it alone
    if caption.strip().lower().startswith(trigger.lower()):
        return caption
    return f"{trigger} {archetype}, {caption.strip()}"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", default=str(DEFAULT_DIR))
    parser.add_argument("--trigger-word", default="aibgospels")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would change, don't write")
    args = parser.parse_args()

    refs_dir = Path(args.dir).resolve()
    txt_files = sorted(refs_dir.glob("*.txt"))
    # Filter out the README
    txt_files = [t for t in txt_files if t.name.lower() != "readme.md"]
    if not txt_files:
        print(f"No .txt captions found in {refs_dir}", file=sys.stderr)
        sys.exit(1)

    archetype_counts = Counter()
    flagged_non_biblical = []
    samples_per_archetype = {}

    for txt in txt_files:
        caption = txt.read_text(encoding="utf-8").strip()
        archetype, reason = detect_archetype(caption)
        archetype_counts[archetype] += 1

        if is_likely_non_biblical(caption):
            flagged_non_biblical.append(txt.name)

        # Collect 2 samples per archetype for spot-check
        if len(samples_per_archetype.setdefault(archetype, [])) < 2:
            samples_per_archetype[archetype].append((txt.name, caption[:200]))

        new_caption = rewrite_caption(caption, args.trigger_word, archetype)
        if new_caption != caption and not args.dry_run:
            txt.write_text(new_caption, encoding="utf-8")

    print(f"{'(DRY RUN) ' if args.dry_run else ''}Processed {len(txt_files)} captions")
    print()
    print("Archetype distribution:")
    for archetype, count in sorted(archetype_counts.items(), key=lambda x: -x[1]):
        print(f"  {archetype:<12} {count:>4}")
    print()
    if flagged_non_biblical:
        print(f"FLAGGED as possibly non-biblical ({len(flagged_non_biblical)}):")
        for name in flagged_non_biblical[:15]:
            print(f"  {name}")
        if len(flagged_non_biblical) > 15:
            print(f"  ... and {len(flagged_non_biblical) - 15} more")
        print(f"  -> Consider deleting these before training.")
        print()

    print("Sample captions per archetype:")
    for archetype, samples in samples_per_archetype.items():
        print(f"\n  [{archetype}]")
        for name, snippet in samples:
            print(f"    {name}")
            print(f"      orig: {snippet[:150]}")
            print(f"      new:  {args.trigger_word} {archetype}, {snippet[:130]}")

    if args.dry_run:
        print(f"\n(Dry run — no files modified. Re-run without --dry-run to apply.)")


if __name__ == "__main__":
    main()
