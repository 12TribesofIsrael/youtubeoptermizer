# -*- coding: utf-8 -*-
"""Export current channel video data to CSV for post-optimization baseline."""

import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()

print("Fetching all videos...")
videos = client.list_videos(max_results=300)

output = Path(__file__).resolve().parent.parent / "analytics" / "post-optimization" / "all-videos.csv"

fields = [
    "video_id", "title", "published_at", "duration",
    "view_count", "like_count", "comment_count",
    "tags", "category_id", "description_preview"
]

with open(output, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for v in videos:
        snippet = v["snippet"]
        stats = v.get("statistics", {})
        details = v.get("contentDetails", {})
        writer.writerow({
            "video_id": v["id"],
            "title": snippet["title"],
            "published_at": snippet["publishedAt"],
            "duration": details.get("duration", ""),
            "view_count": stats.get("viewCount", 0),
            "like_count": stats.get("likeCount", 0),
            "comment_count": stats.get("commentCount", 0),
            "tags": "|".join(snippet.get("tags", [])),
            "category_id": snippet.get("categoryId", ""),
            "description_preview": snippet.get("description", "")[:150],
        })

print(f"Exported {len(videos)} videos to {output}")
