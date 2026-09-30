"""Track progress toward the YPP reapply gate and append one row per run.

The Reapply button is gated on eligibility (see
.claude/memory/project_ypp_suspension_2026.md): 500 subs, 3 public uploads in 90 days,
and EITHER 3,000 valid public watch hours in the trailing 365 days OR 3M Shorts views
in the trailing 90 days. Shorts watch time does not count toward the 3,000 hours, so
this splits watch time by creatorContentType and reports videoOnDemand + liveStream
separately from shorts.

Usage:
    python scripts/ypp-watch-hours.py            # print + append to analytics/ypp-tracker.csv
    python scripts/ypp-watch-hours.py --no-save  # print only
"""

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

ROOT = Path(__file__).resolve().parent.parent
TRACKER = ROOT / "analytics" / "ypp-tracker.csv"
WATCH_HOURS_GATE = 3000
SHORTS_VIEWS_GATE = 3_000_000
SUBS_GATE = 500

FIELDS = [
    "date", "subscribers",
    "vod_hours_365d", "live_hours_365d", "shorts_hours_365d", "qualifying_hours_365d",
    "hours_remaining", "hours_gained_28d", "months_to_gate_at_28d_pace",
    "shorts_views_90d", "top_video_id", "top_video_hours_365d",
]


def query(client, ch_id, start, end, metrics, dimensions=None, **kw):
    params = dict(ids=f"channel=={ch_id}", startDate=str(start), endDate=str(end), metrics=metrics)
    if dimensions:
        params["dimensions"] = dimensions
    params.update(kw)
    return client.analytics.reports().query(**params).execute().get("rows", [])


def hours_by_type(client, ch_id, start, end):
    out = {"videoOnDemand": 0.0, "liveStream": 0.0, "shorts": 0.0, "story": 0.0}
    for row in query(client, ch_id, start, end, "estimatedMinutesWatched", dimensions="creatorContentType"):
        out[row[0]] = row[1] / 60.0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-save", action="store_true")
    args = ap.parse_args()

    client = YouTubeClient()
    ch_id = client.channel_id
    today = date.today()
    y365 = today - timedelta(days=365)
    d90 = today - timedelta(days=90)
    d28 = today - timedelta(days=28)

    subs = int(client.youtube.channels().list(part="statistics", id=ch_id).execute()
               ["items"][0]["statistics"]["subscriberCount"])

    h365 = hours_by_type(client, ch_id, y365, today)
    # Same 365-day window as of 28 days ago, so the difference is the net change in the trailing year.
    h365_prev = hours_by_type(client, ch_id, y365 - timedelta(days=28), d28)
    qualifying = h365["videoOnDemand"] + h365["liveStream"]
    qualifying_prev = h365_prev["videoOnDemand"] + h365_prev["liveStream"]
    gained_28d = qualifying - qualifying_prev
    remaining = max(WATCH_HOURS_GATE - qualifying, 0.0)
    months = (remaining / gained_28d) * (28 / 30.4) if gained_28d > 0 else float("inf")

    shorts_views_90d = 0
    for row in query(client, ch_id, d90, today, "views", dimensions="creatorContentType"):
        if row[0] == "shorts":
            shorts_views_90d = row[1]

    top_id, top_hours = "", 0.0
    top = query(client, ch_id, y365, today, "estimatedMinutesWatched", dimensions="video",
                sort="-estimatedMinutesWatched", maxResults=1)
    if top:
        top_id, top_hours = top[0][0], top[0][1] / 60.0

    print(f"\nYPP eligibility as of {today}")
    print(f"  Subscribers            {subs:>9,}  (gate {SUBS_GATE})")
    print(f"  Watch hrs, long-form   {h365['videoOnDemand']:>9,.0f}")
    print(f"  Watch hrs, live        {h365['liveStream']:>9,.0f}")
    print(f"  Watch hrs, Shorts      {h365['shorts']:>9,.0f}  (does NOT count)")
    print(f"  Qualifying hrs (365d)  {qualifying:>9,.0f}  / {WATCH_HOURS_GATE:,}  -> {remaining:,.0f} to go")
    print(f"  Net change, last 28d   {gained_28d:>+9,.0f} hrs")
    if gained_28d > 0:
        print(f"  At that pace           {months:>9.1f} months to the gate")
    else:
        print(f"  At that pace           the gate is not being approached")
    print(f"  Shorts views (90d)     {shorts_views_90d:>9,}  / {SHORTS_VIEWS_GATE:,}")
    print(f"  Top video (365d)       {top_id}  {top_hours:,.0f} hrs\n")

    if args.no_save:
        return
    row = {
        "date": str(today), "subscribers": subs,
        "vod_hours_365d": round(h365["videoOnDemand"], 1),
        "live_hours_365d": round(h365["liveStream"], 1),
        "shorts_hours_365d": round(h365["shorts"], 1),
        "qualifying_hours_365d": round(qualifying, 1),
        "hours_remaining": round(remaining, 1),
        "hours_gained_28d": round(gained_28d, 1),
        "months_to_gate_at_28d_pace": "" if months == float("inf") else round(months, 1),
        "shorts_views_90d": shorts_views_90d,
        "top_video_id": top_id, "top_video_hours_365d": round(top_hours, 1),
    }
    new = not TRACKER.exists()
    with open(TRACKER, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)
    print(f"Appended to {TRACKER}")


if __name__ == "__main__":
    main()
