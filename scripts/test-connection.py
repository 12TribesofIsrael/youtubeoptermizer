"""Verify YouTube API connection by listing channel info and recent videos."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

print("Testing YouTube API Connection...")
print("=" * 50)

client = YouTubeClient()

# Channel info
channel = client.get_channel_info()
snippet = channel["snippet"]
stats = channel["statistics"]

print(f"\nChannel: {snippet['title']}")
print(f"Subscribers: {stats.get('subscriberCount', 'hidden')}")
print(f"Total videos: {stats['videoCount']}")
print(f"Total views: {stats['viewCount']}")

# Recent videos
print(f"\n{'─' * 50}")
print("10 Most Recent Videos:")
print(f"{'─' * 50}")

videos = client.list_videos(max_results=10)
for v in videos:
    title = v["snippet"]["title"]
    views = v["statistics"].get("viewCount", "N/A")
    print(f"  [{v['id']}] {title}")
    print(f"    Views: {views}")

print(f"\n{'─' * 50}")
print("Connection verified! API access is working.")
