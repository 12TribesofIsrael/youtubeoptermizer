"""Export fresh YouTube analytics to analytics/post-optimization/ for comparison."""

import csv
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()
ch_id = client.channel_id
out_dir = Path(__file__).resolve().parent.parent / "analytics" / "post-optimization"
out_dir.mkdir(parents=True, exist_ok=True)

# 1. Channel status
ch = client.youtube.channels().list(part="snippet,statistics", id=ch_id).execute()["items"][0]
stats = ch["statistics"]
print(f"Channel: {ch['snippet']['title']}")
print(f"Subscribers: {int(stats['subscriberCount']):,}")
print(f"Total Views: {int(stats['viewCount']):,}")
print(f"Total Videos: {stats['videoCount']}")
print()

# 2. Pull all videos
print("Fetching all videos...")
videos = client.list_videos(max_results=300)
print(f"Found {len(videos)} videos")

# 3. Pull 28-day analytics
print("\nPulling 28-day analytics...")
end = date.today()
start = end - timedelta(days=28)
analytics = client.analytics.reports().query(
    ids=f"channel=={ch_id}",
    startDate=str(start),
    endDate=str(end),
    metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost,likes,comments",
).execute()

if analytics.get("rows"):
    row = analytics["rows"][0]
    print(f"Views (28d):              {row[0]:,}")
    print(f"Watch Time (min):         {row[1]:,}")
    print(f"Avg View Duration (sec):  {row[2]}")
    print(f"Subscribers Gained:       {row[3]:,}")
    print(f"Subscribers Lost:         {row[4]:,}")
    print(f"Net Subscribers:          {row[3]-row[4]:,}")
    print(f"Likes:                    {row[5]:,}")
    print(f"Comments:                 {row[6]:,}")

# 4. Pull per-video analytics (views, watch time, avg duration, subs)
print("\nPulling per-video analytics...")
imp_map = {}
try:
    vid_data = client.analytics.reports().query(
        ids=f"channel=={ch_id}",
        startDate=str(start),
        endDate=str(end),
        metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,likes",
        dimensions="video",
        sort="-views",
        maxResults=200,
    ).execute()
    if vid_data.get("rows"):
        for r in vid_data["rows"]:
            imp_map[r[0]] = {"views_28d": r[1], "watch_min": r[2], "avg_dur": r[3], "subs_gained": r[4], "likes_28d": r[5]}
        print(f"Got analytics for {len(imp_map)} videos")
except Exception as e:
    print(f"Per-video analytics error: {e}")


# 5. Parse duration helper
def parse_duration(dur_iso):
    dur = dur_iso.replace("PT", "")
    secs = 0
    if "H" in dur:
        h, dur = dur.split("H")
        secs += int(h) * 3600
    if "M" in dur:
        m, dur = dur.split("M")
        secs += int(m) * 60
    if "S" in dur:
        secs += int(dur.replace("S", ""))
    return secs


# 6. Export Table data.csv
table_path = out_dir / "Table data.csv"
with open(table_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Video", "Video title", "Video publish time", "Duration (sec)",
        "Views", "Likes", "Comments", "Average view duration (28d)",
        "Views (28d)", "Watch time minutes (28d)",
    ])
    for v in videos:
        vid = v["id"]
        title = v["snippet"]["title"]
        published = v["snippet"]["publishedAt"]
        secs = parse_duration(v.get("contentDetails", {}).get("duration", "PT0S"))
        views = v["statistics"].get("viewCount", "0")
        likes = v["statistics"].get("likeCount", "0")
        comments = v["statistics"].get("commentCount", "0")
        imp = imp_map.get(vid, {})
        avg_dur = imp.get("avg_dur", "")
        views_28d = imp.get("views_28d", "")
        watch_min = imp.get("watch_min", "")
        subs_gained = imp.get("subs_gained", "")
        writer.writerow([vid, title, published, secs, views, likes, comments, avg_dur, views_28d, watch_min])

print(f"\nExported {len(videos)} videos to {table_path}")

# 7. Show top 10 by views (28d)
if imp_map:
    print("\nTOP 10 BY VIEWS (last 28 days):")
    sorted_vids = sorted(imp_map.items(), key=lambda x: x[1]["views_28d"], reverse=True)[:10]
    for vid_id, data in sorted_vids:
        title = next((v["snippet"]["title"] for v in videos if v["id"] == vid_id), vid_id)
        print(f"  {data['views_28d']:>6,} views | {data['avg_dur']:>4}s avg | {data['watch_min']:>6,} min | {title[:50]}")

# 9. Daily time-series
print("\nPulling daily time-series...")
daily = client.analytics.reports().query(
    ids=f"channel=={ch_id}",
    startDate=str(start),
    endDate=str(end),
    metrics="views,estimatedMinutesWatched,subscribersGained",
    dimensions="day",
    sort="day",
).execute()

chart_path = out_dir / "Chart data.csv"
with open(chart_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Date", "Views", "Watch time (minutes)", "Subscribers gained"])
    for row in daily.get("rows", []):
        writer.writerow(row)
print(f"Exported {len(daily.get('rows', []))} days to {chart_path}")

# 10. Totals
totals_path = out_dir / "Totals.csv"
with open(totals_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Metric", "Value"])
    if analytics.get("rows"):
        row = analytics["rows"][0]
        writer.writerow(["Views (28d)", row[0]])
        writer.writerow(["Watch time (min)", row[1]])
        writer.writerow(["Avg view duration (sec)", row[2]])
        writer.writerow(["Subscribers gained", row[3]])
        writer.writerow(["Subscribers lost", row[4]])
        writer.writerow(["Net subscribers", row[3] - row[4]])
        writer.writerow(["Likes", row[5]])
        writer.writerow(["Comments", row[6]])
    writer.writerow(["Total subscribers", stats["subscriberCount"]])
    writer.writerow(["Total views", stats["viewCount"]])
    writer.writerow(["Total videos", stats["videoCount"]])
    writer.writerow(["Export date", str(date.today())])
print(f"Exported totals to {totals_path}")

print("\n" + "=" * 60)
print("  DONE — All fresh analytics exported to analytics/post-optimization/")
print("=" * 60)
