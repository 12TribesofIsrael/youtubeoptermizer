"""Retention curves (audienceWatchRatio by elapsedVideoTimeRatio) for the FWL 6-pack."""

import sys
from pathlib import Path
from datetime import date, timedelta
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

PACK = json.loads((Path(__file__).resolve().parent.parent / "output" / "shorts-drop-schedule.json").read_text())


def fetch_curve(client, ch_id, video_id, pub_date):
    start = pub_date
    end = date.today()
    return client.analytics.reports().query(
        ids=f"channel=={ch_id}",
        startDate=str(start),
        endDate=str(end),
        metrics="audienceWatchRatio,relativeRetentionPerformance",
        dimensions="elapsedVideoTimeRatio",
        filters=f"video=={video_id}",
    ).execute()


def fmt_curve(rows, label, width=50):
    print(f"\n{label}")
    print(f"  {'time%':>5}  {'absRet':>6}  {'rel':>5}  bar")
    # 100 buckets in [0.00, 0.99] in 1% steps
    for r in rows:
        t_ratio, abs_ret, rel_ret = r
        t_pct = round(float(t_ratio) * 100)
        # Only show every 5% to keep it readable
        if t_pct % 5 != 0 and t_pct != 99:
            continue
        bar = "#" * min(width, int(float(abs_ret) * width))
        print(f"  {t_pct:>4}%  {float(abs_ret)*100:>5.1f}%  {float(rel_ret):>4.2f}  {bar}")


def main():
    client = YouTubeClient()
    ch_id = client.channel_id

    for entry in PACK:
        vid = entry["video_id"]
        title = entry["title"]
        pub = date.fromisoformat(entry["publishAt"][:10])

        try:
            data = fetch_curve(client, ch_id, vid, pub)
        except Exception as e:
            print(f"\n{title} ({vid}) — error: {e}")
            continue

        rows = data.get("rows", [])
        if not rows:
            print(f"\n{title} ({vid}) — no retention data yet")
            continue
        label = f"{vid} | pub {pub} | {title[:60]}"
        fmt_curve(rows, label)


if __name__ == "__main__":
    main()
