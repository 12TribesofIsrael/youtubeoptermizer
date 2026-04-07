"""Analytics routes — charts, top videos, pre/post comparison."""

import asyncio
import csv
from pathlib import Path
from datetime import date, timedelta
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@router.get("/analytics/overview")
async def analytics_overview(start_date: str = None, end_date: str = None):
    """Time-series analytics data for charts."""
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        end = end_date or str(date.today())
        start = start_date or str(date.today() - timedelta(days=28))

        def _query():
            return client.analytics.reports().query(
                ids=f"channel=={client.channel_id}",
                startDate=start,
                endDate=end,
                metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained",
                dimensions="day",
                sort="day",
            ).execute()

        result = await asyncio.to_thread(_query)
        days = []
        for row in result.get("rows", []):
            days.append({
                "date": row[0],
                "views": row[1],
                "watch_time_minutes": row[2],
                "avg_view_duration": row[3],
                "subscribers_gained": row[4],
            })
        return {"days": days}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.get("/analytics/top-videos")
async def top_videos(start_date: str = None, end_date: str = None):
    """Top performing videos by views."""
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        end = end_date or str(date.today())
        start = start_date or str(date.today() - timedelta(days=28))

        def _query():
            return client.analytics.reports().query(
                ids=f"channel=={client.channel_id}",
                startDate=start,
                endDate=end,
                metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,likes,comments",
                dimensions="video",
                sort="-views",
                maxResults=20,
            ).execute()

        result = await asyncio.to_thread(_query)
        videos = []
        for row in result.get("rows", []):
            videos.append({
                "video_id": row[0],
                "title": row[0],  # Would need a separate lookup for title
                "views": row[1],
                "watch_time_minutes": row[2],
                "avg_view_duration": row[3],
                "subscribers_gained": row[4],
                "likes": row[5],
                "comments": row[6],
            })
        return {"videos": videos}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.get("/analytics/comparison")
async def comparison():
    """Compare pre and post optimization analytics from CSV files."""
    metrics = []

    pre_file = PROJECT_ROOT / "analytics" / "pre-optimization" / "Table data.csv"
    post_file = PROJECT_ROOT / "analytics" / "post-optimization" / "Table data.csv"

    def _read_csv(path):
        if not path.exists():
            return []
        with open(path, encoding="utf-8") as f:
            return list(csv.DictReader(f))

    try:
        pre_data = _read_csv(pre_file)
        post_data = _read_csv(post_file)

        if not pre_data or not post_data:
            return {"metrics": [], "note": "CSV files not found in analytics/ directory"}

        # Calculate aggregate metrics
        def _sum(data, col):
            total = 0
            for row in data:
                val = row.get(col, "0").replace(",", "").replace("%", "")
                try:
                    total += float(val)
                except ValueError:
                    pass
            return total

        def _avg(data, col):
            s = _sum(data, col)
            return round(s / len(data), 2) if data else 0

        comparisons = [
            ("Total Views", "Views"),
            ("Total Watch Time (hrs)", "Watch time (hours)"),
            ("Avg Impressions CTR", "Impressions click-through rate (%)"),
        ]

        for label, col in comparisons:
            pre_val = _sum(pre_data, col) if "Total" in label else _avg(pre_data, col)
            post_val = _sum(post_data, col) if "Total" in label else _avg(post_data, col)
            change = round((post_val - pre_val) / pre_val * 100, 1) if pre_val else 0
            metrics.append({
                "metric": label,
                "pre": f"{pre_val:,.0f}" if pre_val > 100 else f"{pre_val:.2f}",
                "post": f"{post_val:,.0f}" if post_val > 100 else f"{post_val:.2f}",
                "change_pct": change,
            })

        return {"metrics": metrics}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)
