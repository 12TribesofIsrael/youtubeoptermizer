"""Quick channel status check — pulls key metrics from YouTube API."""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient


def main():
    client = YouTubeClient()
    ch_id = client.channel_id

    # Channel info
    ch = client.youtube.channels().list(
        part="snippet,statistics,brandingSettings",
        id=ch_id,
    ).execute()["items"][0]

    stats = ch["statistics"]
    print(f"\n{'='*55}")
    print(f"  AI BIBLE GOSPELS — Channel Status")
    print(f"{'='*55}")
    print(f"  Subscribers:    {int(stats['subscriberCount']):,}")
    print(f"  Total Views:    {int(stats['viewCount']):,}")
    print(f"  Total Videos:   {stats['videoCount']}")
    print(f"{'='*55}\n")

    # Recent videos (last 10)
    print("RECENT UPLOADS (last 10):\n")
    videos = client.list_videos(max_results=10)
    for v in videos:
        title = v["snippet"]["title"][:55]
        views = int(v["statistics"].get("viewCount", 0))
        likes = int(v["statistics"].get("likeCount", 0))
        published = v["snippet"]["publishedAt"][:10]
        print(f"  {published}  {views:>7,} views  {likes:>4} likes  {title}")

    # Analytics — last 28 days
    print(f"\nLAST 28 DAYS ANALYTICS:\n")
    end = date.today()
    start = end - timedelta(days=28)
    try:
        analytics = client.analytics.reports().query(
            ids=f"channel=={ch_id}",
            startDate=str(start),
            endDate=str(end),
            metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost,likes,comments",
        ).execute()

        if analytics.get("rows"):
            row = analytics["rows"][0]
            headers = [h["name"] for h in analytics["columnHeaders"]]
            for h, v in zip(headers, row):
                label = h.replace("estimated", "").replace("Minutes", " Min").replace("Watched", " Watched")
                print(f"  {label:<25} {v:>10,}" if isinstance(v, int) else f"  {label:<25} {v:>10}")
    except Exception as e:
        print(f"  Analytics API error: {e}")
        print("  (Analytics API may need separate enablement in Google Cloud Console)")

    print()


if __name__ == "__main__":
    main()
