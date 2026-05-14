"""Top videos by views in the last 28 days, with traffic source + sub-gain split."""

import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient


def main():
    client = YouTubeClient()
    ch_id = client.channel_id

    end = date.today()
    start = end - timedelta(days=28)

    # Top 15 videos by views in last 28 days
    top = client.analytics.reports().query(
        ids=f"channel=={ch_id}",
        startDate=str(start),
        endDate=str(end),
        metrics="views,estimatedMinutesWatched,averageViewPercentage,subscribersGained,likes,comments",
        dimensions="video",
        sort="-views",
        maxResults=15,
    ).execute()

    rows = top.get("rows", [])
    if not rows:
        print("No analytics rows returned.")
        return

    # Resolve video IDs -> titles + publish dates
    ids = [r[0] for r in rows]
    details = client.youtube.videos().list(
        part="snippet,contentDetails",
        id=",".join(ids),
    ).execute()
    meta = {d["id"]: d for d in details.get("items", [])}

    print(f"\nTOP 15 VIDEOS (last 28 days: {start} -> {end})\n")
    print(f"  {'pub':<11}  {'views':>6}  {'wMin':>6}  {'avg%':>5}  {'subs':>4}  {'likes':>5}  title")
    for vid, views, mins, avg_pct, subs, likes, comments in rows:
        m = meta.get(vid, {})
        title = (m.get("snippet", {}).get("title") or vid)[:55]
        pub = (m.get("snippet", {}).get("publishedAt") or "")[:10]
        print(f"  {pub:<11}  {int(views):>6,}  {int(mins):>6,}  {avg_pct:>4.1f}%  {int(subs):>4}  {int(likes):>5}  {title}")

    # Traffic source breakdown
    print(f"\nTRAFFIC SOURCES (last 28 days):\n")
    src = client.analytics.reports().query(
        ids=f"channel=={ch_id}",
        startDate=str(start),
        endDate=str(end),
        metrics="views,estimatedMinutesWatched",
        dimensions="insightTrafficSourceType",
        sort="-views",
    ).execute()
    for row in src.get("rows", []):
        source, views, mins = row
        print(f"  {source:<30}  {int(views):>6,} views   {int(mins):>6,} min watched")

    # Day-by-day for trend
    print(f"\nDAILY VIEWS (last 14 days):\n")
    daily = client.analytics.reports().query(
        ids=f"channel=={ch_id}",
        startDate=str(end - timedelta(days=13)),
        endDate=str(end),
        metrics="views,subscribersGained,subscribersLost",
        dimensions="day",
    ).execute()
    for row in daily.get("rows", []):
        day, views, gained, lost = row
        net = gained - lost
        bar = "#" * min(60, int(views) // 20)
        print(f"  {day}  views={int(views):>4,}  net subs={net:+d}  {bar}")

    print()


if __name__ == "__main__":
    main()
