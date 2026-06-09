"""One-off: pull YouTube traffic-source breakdown to see if external (TikTok) drives views.

Answers: "Is my TikTok bio link / mentions actually driving YouTube traffic?"
Queries last 28 days + last 90 days for:
  1. Views by traffic source TYPE (EXTERNAL vs SEARCH vs SUGGESTED vs SHORTS feed, etc.)
  2. Within EXTERNAL, the actual referring domains (tiktok.com, t.me, etc.)
"""
import sys
from datetime import date, timedelta

sys.path.insert(0, "src")
from youtube.client import YouTubeClient


def query(client, start, end, dimensions, filters=None, sort="-views"):
    params = {
        "ids": f"channel=={client.channel_id}",
        "startDate": start,
        "endDate": end,
        "metrics": "views,estimatedMinutesWatched",
        "dimensions": dimensions,
        "sort": sort,
        "maxResults": 25,
    }
    if filters:
        params["filters"] = filters
    return client.analytics.reports().query(**params).execute()


def show(title, resp):
    print(f"\n=== {title} ===")
    headers = [h["name"] for h in resp.get("columnHeaders", [])]
    rows = resp.get("rows", [])
    if not rows:
        print("  (no data)")
        return
    print("  " + " | ".join(headers))
    for r in rows:
        print("  " + " | ".join(str(c) for c in r))


def main():
    c = YouTubeClient()
    today = date.today()
    for window, days in [("LAST 28 DAYS", 28), ("LAST 90 DAYS", 90)]:
        start = (today - timedelta(days=days)).isoformat()
        end = today.isoformat()
        print(f"\n################ {window} ({start} -> {end}) ################")
        # 1. Views by traffic source type
        show("Views by traffic source TYPE",
             query(c, start, end, "insightTrafficSourceType"))
        # 2. External referrers only (the domains)
        show("EXT_URL referrer domains",
             query(c, start, end, "insightTrafficSourceDetail",
                   filters="insightTrafficSourceType==EXT_URL"))


if __name__ == "__main__":
    main()
