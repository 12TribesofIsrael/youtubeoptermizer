"""
AEO description bulk-update — skeleton mode (Option C).

Appends the canonical AEO constants block (Who-made-this-video Q&A + About + links + hashtag)
to every public video's description. Scrubs "Technology Gurus LLC" mentions on the way through.

Idempotent: skips videos that already have the marker. Resumable: checkpoints every 10 videos
to output/aeo-checkpoint.json. Stops cleanly on quota exhaustion.

Per-video AEO content (one_sentence_answer, expansion, timestamps, qa) is Phase B —
ramped up over the 90-day wait window with LLM generation from transcripts.
"""

import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "analytics/post-optimization/all-videos.csv"
CHECKPOINT = ROOT / "output/aeo-checkpoint.json"

# Videos deleted in delete-cull.py (2026-04-24) — exclude from update list
DELETED_IDS = {
    "3riiNCfzQ_g", "zQaLpyUFfNA", "wlRi_e-zzE4", "p0xBHbtk7CI", "2e_pe-3GpBI",
    "Ox_dozHLaaM", "CuNKO1aBdRM", "6lbjD5o_ulk", "puRpiE4KtXQ", "4-lwx45nL1A",
    "V1X-iqGgYls", "U9Odey7BrxE", "YZOq2NBT3d8", "w8fXqQPM26o", "FEkLq5XApX0",
    "TK82X4dOE7w", "Mo1wDJhH3d8", "EVXPdM8tGcQ", "hJZ3g3ThGik",
    "3ase0yJE_Xs", "ggAF28BvCqY", "sN_UHGSkArg", "dwd69b2G-gU",
}

MARKER = "— ABOUT AI BIBLE GOSPELS —"

CONSTANTS_BLOCK = """— Q&A —
Q: Who made this video?
A: AI Bible Gospels, a faith-tech project by Thomas Lee using AI to bring Scripture to life from a cultural perspective.

— ABOUT AI BIBLE GOSPELS —
AI Bible Gospels (@AIBIBLEGOSPELS) is a faith-tech brand founded by Thomas Lee that uses AI to narrate Scripture word-for-word from a cultural perspective underrepresented in biblical media. Flagship project: Faith Walk Live, the live tracker for Minister Zay's 3,000-mile walk from Philadelphia to California.

Website: https://aibiblegospels.com
Faith Walk Live: https://faithwalklive.com
YouTube: https://www.youtube.com/@AIBIBLEGOSPELS
LinkedIn: https://www.linkedin.com/in/ai-bible-gospels-049005353/
Contact: aibiblegospels444@gmail.com

#AIBibleGospels"""


def transform_description(current: str) -> str | None:
    """Return new description, or None if already has the marker (skip)."""
    if MARKER in current:
        return None
    cleaned = current
    # Scrub dissolved-entity refs
    for needle in ("Technology Gurus LLC", "technology gurus llc", "Technology Gurus, LLC"):
        cleaned = cleaned.replace(needle, "")
    cleaned = cleaned.replace("technologygurusllc@gmail.com", "aibiblegospels444@gmail.com")
    cleaned = cleaned.rstrip()
    if cleaned:
        return cleaned + "\n\n" + CONSTANTS_BLOCK
    return CONSTANTS_BLOCK


def load_checkpoint():
    if CHECKPOINT.exists():
        d = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        return set(d.get("completed", [])), set(d.get("skipped", [])), set(d.get("errored", []))
    return set(), set(), set()


def save_checkpoint(completed, skipped, errored):
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(
        json.dumps(
            {
                "completed": sorted(completed),
                "skipped": sorted(skipped),
                "errored": sorted(errored),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main():
    client = YouTubeClient()

    with CSV_PATH.open(encoding="utf-8") as f:
        all_video_ids = [r["video_id"] for r in csv.DictReader(f)]
    candidates = [v for v in all_video_ids if v not in DELETED_IDS]
    completed, skipped, errored = load_checkpoint()
    todo = [v for v in candidates if v not in completed and v not in skipped]

    print(f"Total candidates: {len(candidates)}")
    print(f"Completed prior: {len(completed)}  Skipped prior: {len(skipped)}  Errored prior: {len(errored)}")
    print(f"To process this run: {len(todo)}")
    print("=" * 70)

    if not todo:
        print("Nothing to do. All caught up.")
        return

    quota_hit = False
    for i, vid in enumerate(todo, 1):
        try:
            video = client.get_video(vid)
            if not video:
                skipped.add(vid)
                print(f"  [{i:>3}/{len(todo)}] SKIP    {vid}  (not found)")
                continue
            current_desc = video["snippet"].get("description", "") or ""
            new_desc = transform_description(current_desc)
            if new_desc is None:
                completed.add(vid)
                print(f"  [{i:>3}/{len(todo)}] ALREADY {vid}")
                continue
            if len(new_desc) > 4900:
                # YouTube hard-caps at 5000 chars. Truncate the original portion to fit.
                overhead = len(CONSTANTS_BLOCK) + 2
                budget = 4900 - overhead
                head = (current_desc.replace("Technology Gurus LLC", "")
                                    .replace("technologygurusllc@gmail.com", "aibiblegospels444@gmail.com"))
                head = head[:budget].rstrip()
                new_desc = head + "\n\n" + CONSTANTS_BLOCK if head else CONSTANTS_BLOCK

            client.update_video(vid, description=new_desc)
            completed.add(vid)
            title = video["snippet"]["title"][:55]
            print(f"  [{i:>3}/{len(todo)}] OK      {vid}  {title}")
            time.sleep(0.4)
        except Exception as e:
            err_str = str(e)
            if "quotaExceeded" in err_str or "rateLimitExceeded" in err_str or "userRateLimitExceeded" in err_str:
                print(f"  [{i:>3}/{len(todo)}] QUOTA HIT at {vid} — saving checkpoint and exiting.")
                quota_hit = True
                break
            errored.add(vid)
            print(f"  [{i:>3}/{len(todo)}] ERR     {vid}: {e}")

        if i % 10 == 0:
            save_checkpoint(completed, skipped, errored)

    save_checkpoint(completed, skipped, errored)

    print("=" * 70)
    print(f"Run summary:")
    print(f"  Completed (cumulative): {len(completed)} / {len(candidates)}")
    print(f"  Skipped (not found):    {len(skipped)}")
    print(f"  Errored:                {len(errored)}")
    remaining = [v for v in candidates if v not in completed and v not in skipped]
    print(f"  Remaining:              {len(remaining)}")
    if quota_hit:
        print(f"\n  Quota exhausted. Re-run tomorrow (PT midnight reset) to resume.")


if __name__ == "__main__":
    main()
