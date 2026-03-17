# -*- coding: utf-8 -*-
"""Identify top thumbnail optimization priorities by impressions and CTR."""

import csv
from pathlib import Path

post_csv = Path(__file__).resolve().parent.parent / "analytics" / "post-optimization" / "Table data.csv"

videos = []
with open(post_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row.get("Video title", "").strip()
        if not title or title == "Total" or row.get("Content", "").strip() == "Total":
            continue
        try:
            impressions = int(row.get("Impressions", "0") or 0)
            ctr = float(row.get("Impressions click-through rate (%)", "0") or 0)
            views = int(row.get("Views", "0") or 0)
            duration = int(row.get("Duration", "0") or 0)
            avg_pct = row.get("Average percentage viewed (%)", "0") or "0"
            avg_pct = float(avg_pct)
        except (ValueError, TypeError):
            continue

        if impressions < 500:
            continue

        videos.append({
            "id": row.get("Content", "").strip(),
            "title": title,
            "views": views,
            "impressions": impressions,
            "ctr": ctr,
            "duration": duration,
            "avg_pct": avg_pct,
        })

# Sort by impressions descending, then by CTR ascending (worst CTR first for high-impression videos)
videos.sort(key=lambda v: (-v["impressions"], v["ctr"]))

print("=" * 90)
print("TOP 30 THUMBNAIL PRIORITIES (Highest Impressions, Sorted by Impact)")
print("=" * 90)
print(f"{'#':<4} {'Impressions':<13} {'CTR':<7} {'Views':<8} {'Title'}")
print("-" * 90)

for i, v in enumerate(videos[:30], 1):
    flag = " <<<" if v["ctr"] < 3.5 else ""
    print(f"{i:<4} {v['impressions']:<13,} {v['ctr']:<7.2f} {v['views']:<8,} {v['title'][:60]}{flag}")

print("\n" + "=" * 90)
print("WORST CTR (Under 3% with 1000+ Impressions) — Biggest Thumbnail Opportunities")
print("=" * 90)

low_ctr = [v for v in videos if v["ctr"] < 3.0 and v["impressions"] >= 1000]
low_ctr.sort(key=lambda v: v["ctr"])

for i, v in enumerate(low_ctr[:20], 1):
    potential = int(v["impressions"] * 0.06) - v["views"]  # views if CTR hit 6%
    print(f"{i:<4} CTR: {v['ctr']:<6.2f} Imp: {v['impressions']:<8,} Views: {v['views']:<8,} Potential: +{max(0,potential):<6,} {v['title'][:55]}")
