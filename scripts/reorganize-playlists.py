# -*- coding: utf-8 -*-
"""Create tribe-based playlists and organize videos into them."""

import sys
import csv
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()

post_csv = Path(__file__).resolve().parent.parent / "analytics" / "post-optimization" / "Table data.csv"

# Read all videos
videos = []
with open(post_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row.get("Video title", "").strip()
        vid = row.get("Content", "").strip()
        if not title or vid == "Total":
            continue
        videos.append({"id": vid, "title": title})

# Define playlist categories and their keyword matches
playlists_config = [
    ("The Tribe of Judah — Lions of Israel", ["Judah"], []),
    ("The Tribe of Benjamin — Wolves of the Last Days", ["Benjamin"], []),
    ("The Tribe of Ephraim — Fruitful in a Strange Land", ["Ephraim"], []),
    ("The Tribe of Manasseh — A Multitude of Nations", ["Manasseh"], []),
    ("The Tribe of Naphtali — A Hind Let Loose", ["Naphtali"], []),
    ("The Tribes of Zebulun & Issachar — Mayans and Aztecs", ["Zebulun", "Issachar"], []),
    ("The Tribe of Gad — Warriors of the Americas", ["Gad"], []),
    ("The Tribe of Reuben — Seminole Indians of Israel", ["Reuben"], []),
    ("The Tribe of Asher — Blessed Above Sons", ["Asher"], []),
    ("Simeon & Levi — Haiti, Dominican Republic, and Prophecy", ["Simeon", "Levi"], []),
    ("The Tribe of Dan — Judge of His People", ["Dan —", "Tribe of Dan"], []),
    ("The Lost Tribes — Where Did They Go?", ["Lost Tribe", "Scattered", "Where Did", "Missing", "10 Lost", "Crossed the Ocean", "Bering Strait", "Went Into Slavery on Ships", "Israelites Left the Heathen", "Esdras", "Euphrates", "Where the 10"], []),
    ("Deuteronomy 28 — Every Curse Fulfilled", ["Deuteronomy 28", "Curse", "Slave Ship", "Smitten", "Bondage", "Nation Swift as the Eagle", "Built Houses But Could Not"], []),
    ("The Blessings of Joseph", ["Joseph", "Blessings of Joseph"], []),
]

print("Creating tribe-based playlists...")
print("=" * 60)

created = 0
total_added = 0

for playlist_title, keywords, extra_ids in playlists_config:
    # Find matching videos
    matched = []
    for v in videos:
        if any(kw in v["title"] for kw in keywords):
            matched.append(v["id"])
    matched.extend(extra_ids)
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for vid in matched:
        if vid not in seen:
            seen.add(vid)
            unique.append(vid)
    matched = unique

    if not matched:
        print(f"  SKIP {playlist_title} — no videos matched")
        continue

    # Create playlist
    try:
        playlist = client.create_playlist(
            title=playlist_title,
            description=f"All videos about {playlist_title.split('—')[0].strip()} from AI Bible Gospels. Part of The Prophecy Revealed series.",
        )
        pid = playlist["id"]
        created += 1
        print(f"\n  [{created}] Created: {playlist_title} ({len(matched)} videos)")

        # Add videos to playlist
        for vid in matched:
            try:
                client.add_to_playlist(pid, vid)
                total_added += 1
                time.sleep(0.3)
            except Exception as e:
                print(f"    ERROR adding {vid}: {str(e)[:60]}")
                if "quotaExceeded" in str(e):
                    print("Quota hit!")
                    sys.exit(1)

        time.sleep(0.5)
    except Exception as e:
        print(f"  ERROR creating {playlist_title}: {str(e)[:80]}")
        if "quotaExceeded" in str(e):
            print("Quota hit!")
            break

print(f"\n{'=' * 60}")
print(f"Playlists created: {created}")
print(f"Videos added: {total_added}")
