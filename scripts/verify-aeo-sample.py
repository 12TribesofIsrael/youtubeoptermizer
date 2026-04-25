"""Verify AEO descriptions on a 5-video sample per the spec's section 7."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

# 5 sample IDs spanning the run
SAMPLE = [
    "mYbLS7to7iM",  # first updated
    "TxO-08eVvVw",  # mid-batch (Matthew 6 top performer)
    "hNt6alQiIVE",  # tribe top performer (33K views)
    "EWksyIbaImo",  # Zebulun top (22K)
    "9H4yPDLobmw",  # near end of today's batch
]

client = YouTubeClient()

required = [
    ("https://aibiblegospels.com", "canonical website URL"),
    ("— ABOUT AI BIBLE GOSPELS —", "About marker"),
    ("Q: Who made this video?", "Who-made Q&A"),
    ("aibiblegospels444@gmail.com", "channel email"),
    ("https://faithwalklive.com", "Faith Walk Live URL"),
    ("#AIBibleGospels", "primary hashtag"),
]
forbidden = [
    ("Technology Gurus LLC", "dissolved entity"),
    ("technologygurusllc@gmail.com", "old contact email"),
]

print(f"Verifying {len(SAMPLE)} sample videos...")
print("=" * 70)

all_pass = True
for vid in SAMPLE:
    video = client.get_video(vid)
    if not video:
        print(f"\n[{vid}] NOT FOUND")
        all_pass = False
        continue
    desc = video["snippet"].get("description", "") or ""
    title = video["snippet"]["title"][:60]
    print(f"\n[{vid}] {title}")
    print(f"  desc length: {len(desc)} chars")
    for needle, label in required:
        ok = needle in desc
        print(f"  {'PASS' if ok else 'FAIL'} contains  {label}")
        if not ok:
            all_pass = False
    for needle, label in forbidden:
        absent = needle not in desc
        print(f"  {'PASS' if absent else 'FAIL'} excludes  {label}")
        if not absent:
            all_pass = False

print("=" * 70)
print(f"Overall: {'PASS' if all_pass else 'FAIL'}")
