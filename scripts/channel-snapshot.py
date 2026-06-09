"""One-off: concise channel health snapshot for an honest assessment."""
import sys
from datetime import date, timedelta

sys.path.insert(0, "src")
from youtube.client import YouTubeClient


def q(client, start, end, metrics, dimensions=None, sort=None, maxr=25, filters=None):
    params = {
        "ids": f"channel=={client.channel_id}",
        "startDate": start, "endDate": end,
        "metrics": metrics, "maxResults": maxr,
    }
    if dimensions: params["dimensions"] = dimensions
    if sort: params["sort"] = sort
    if filters: params["filters"] = filters
    return client.analytics.reports().query(**params).execute()


def line(resp):
    return resp.get("rows", [[]])


def main():
    c = YouTubeClient()
    info = c.get_channel_info()
    s = info["statistics"]
    print("=== LIFETIME ===")
    print(f"  Subs: {s.get('subscriberCount')}  Views: {s.get('viewCount')}  Videos: {s.get('videoCount')}")

    today = date.today()
    for label, days in [("28d", 28), ("90d", 90), ("365d", 365)]:
        start = (today - timedelta(days=days)).isoformat()
        r = q(c, start, today.isoformat(),
              "views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost,likes,comments")
        row = line(r)[0] if line(r) and line(r)[0] else []
        if row:
            v, w, avd, sg, sl, lk, cm = row
            net = int(sg) - int(sl)
            print(f"\n=== LAST {label} ===")
            print(f"  Views {v} | Watch {w} min | AvgDur {avd}s | Subs +{sg}/-{sl} (net {net:+d}) | Likes {lk} | Comments {cm}")

    # Top videos last 90d
    start = (today - timedelta(days=90)).isoformat()
    r = q(c, start, today.isoformat(), "views,estimatedMinutesWatched,averageViewDuration",
          dimensions="video", sort="-views", maxr=12)
    print("\n=== TOP 12 VIDEOS (last 90d) — videoId | views | watchMin | avgDurSec ===")
    for row in line(r):
        print("  " + " | ".join(str(x) for x in row))


if __name__ == "__main__":
    main()
