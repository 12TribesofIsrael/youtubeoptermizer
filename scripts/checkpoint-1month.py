"""
1-Month Post-Optimization Checkpoint.

Compares current channel performance against the March 16, 2026 baseline
captured in analytics/Table data.csv (pre-optimization).

Pulls for the last 28 days:
- Channel totals: views, watch time, subs, CTR, impressions, avg view duration
- Per-video: views, impressions, CTR, avg view duration, subs gained
- Compares against baseline and flags meaningful deltas

YPP-suspension caveat: if the channel's in YPP suspension, expected impact
on impressions and reach is significant and independent of our optimization
work. Checkpoint data during suspension is useful as a "during-suspension"
baseline — re-run 2 weeks after YPP resolution for a clean optimization signal.

Run:
    python scripts/checkpoint-1month.py
"""

import csv
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient


def section(title: str) -> None:
    print()
    print("=" * 64)
    print(f"  {title}")
    print("=" * 64)


def load_baseline() -> dict:
    """Load pre-optimization per-video metrics from analytics/Table data.csv."""
    baseline_path = Path(__file__).resolve().parent.parent / "analytics" / "Table data.csv"
    if not baseline_path.exists():
        print(f"  WARN: baseline not found at {baseline_path}")
        return {}
    rows = {}
    with open(baseline_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            vid = r.get("Video") or r.get("Video ID")
            if vid:
                rows[vid] = r
    return rows


def pct_change(new: float, old: float) -> str:
    if not old:
        return "n/a"
    delta = (new - old) / old * 100
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.1f}%"


def main() -> int:
    client = YouTubeClient()
    ch_id = client.channel_id

    end = date.today()
    start = end - timedelta(days=28)

    section(f"1-Month Checkpoint  —  {start} to {end}")

    # ── Channel totals with CTR ────────────────────────────────
    totals = client.analytics.reports().query(
        ids=f"channel=={ch_id}",
        startDate=str(start),
        endDate=str(end),
        metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost,likes,comments,shares",
    ).execute()

    if totals.get("rows"):
        r = totals["rows"][0]
        print(f"  Views (28d):              {r[0]:>10,}")
        print(f"  Watch Time (min):         {r[1]:>10,}")
        print(f"  Avg View Duration (sec):  {r[2]:>10}")
        print(f"  Subs Gained:              {r[3]:>10,}")
        print(f"  Subs Lost:                {r[4]:>10,}")
        print(f"  Net Subs:                 {r[3]-r[4]:>10,}")
        print(f"  Likes:                    {r[5]:>10,}")
        print(f"  Comments:                 {r[6]:>10,}")
        print(f"  Shares:                   {r[7]:>10,}")

    # ── CTR/impressions (separate query — these metrics need traffic source) ─
    section("Impressions & CTR (28d)")
    try:
        imp_totals = client.analytics.reports().query(
            ids=f"channel=={ch_id}",
            startDate=str(start),
            endDate=str(end),
            metrics="cardImpressions,cardClicks,cardClickRate",
        ).execute()
        # cardImpressions != search/browse impressions. For thumbnail CTR we
        # need to query with dimensions=insightTrafficSourceType filtered to
        # YT_SEARCH or ADVERTISING, OR pull the GUI-level impressions via a
        # different metric key. The free API exposes this as:
        #   metrics="impressions,impressionsClickThroughRate"
        # but only in the v2 Analytics endpoint with specific dimensions.
        # Falling back to video-dimension query below.
        print(f"  Card impressions (weak proxy): {imp_totals.get('rows', [[0,0,0]])[0]}")
    except Exception as e:
        print(f"  Card impressions unavailable: {e}")

    # Real impressions+CTR (the YT Studio numbers) — dimension=video required
    try:
        vid_ctr = client.analytics.reports().query(
            ids=f"channel=={ch_id}",
            startDate=str(start),
            endDate=str(end),
            metrics="views,impressions,impressionsClickThroughRate,averageViewDuration",
            dimensions="video",
            sort="-impressions",
            maxResults=50,
        ).execute()

        if vid_ctr.get("rows"):
            total_imp = sum(r[1] for r in vid_ctr["rows"])
            total_views = sum(r[0] for r in vid_ctr["rows"])
            ctr_avg = (total_views / total_imp * 100) if total_imp else 0
            print(f"  Total impressions (top 50): {total_imp:,}")
            print(f"  Total views (top 50):       {total_views:,}")
            print(f"  Effective CTR:              {ctr_avg:.2f}%")
    except Exception as e:
        print(f"  Per-video impressions error: {e}")
        vid_ctr = {"rows": []}

    # ── Baseline comparison ───────────────────────────────────
    section("Baseline Comparison  (March 16, 2026 → today)")
    baseline = load_baseline()
    if not baseline:
        print("  No baseline file — skipping per-video comparison.")
        return 0

    print(f"  Baseline entries: {len(baseline)}")
    print()
    print(f"  {'Video':<12} {'Baseline V':>10} {'Now V':>10} {'Δ':>8}  Title")
    print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*8}  {'-'*40}")

    current_stats = {}
    videos = client.list_videos(max_results=300)
    for v in videos:
        current_stats[v["id"]] = int(v["statistics"].get("viewCount", 0))

    # Show top 15 by current views
    top = sorted(current_stats.items(), key=lambda x: x[1], reverse=True)[:15]
    for vid_id, cur_views in top:
        base = baseline.get(vid_id, {})
        title = next((v["snippet"]["title"] for v in videos if v["id"] == vid_id), vid_id)
        try:
            base_views = int(str(base.get("Views", "0")).replace(",", "") or 0)
        except ValueError:
            base_views = 0
        delta = pct_change(cur_views, base_views)
        print(f"  {vid_id:<12} {base_views:>10,} {cur_views:>10,} {delta:>8}  {title[:50]}")

    # ── Export fresh snapshot for this checkpoint ─────────────
    out_dir = Path(__file__).resolve().parent.parent / "analytics" / "checkpoint-2026-04-18"
    out_dir.mkdir(parents=True, exist_ok=True)

    snapshot = out_dir / "channel-snapshot.csv"
    with open(snapshot, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Metric", "Value"])
        if totals.get("rows"):
            r = totals["rows"][0]
            w.writerow(["Views (28d)", r[0]])
            w.writerow(["Watch time min (28d)", r[1]])
            w.writerow(["Avg view duration sec", r[2]])
            w.writerow(["Subs gained", r[3]])
            w.writerow(["Subs lost", r[4]])
            w.writerow(["Net subs", r[3] - r[4]])
            w.writerow(["Likes", r[5]])
            w.writerow(["Comments", r[6]])
            w.writerow(["Shares", r[7]])

    vid_csv = out_dir / "per-video-impressions.csv"
    with open(vid_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Video ID", "Views", "Impressions", "CTR %", "Avg view duration"])
        for r in vid_ctr.get("rows", []):
            w.writerow(r)

    print(f"\n  Saved snapshot → {snapshot}")
    print(f"  Saved per-video → {vid_csv}")
    print("\n  Next step: open docs/changelog.md and add impact notes for the 4/16-4/17 checkpoints.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
