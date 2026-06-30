"""Pull top videos (28d + 90d) WITH titles, flag FaithWalkLive milestone clips."""
import sys
from datetime import date, timedelta

sys.path.insert(0, "src")
from youtube.client import YouTubeClient


def top_videos(c, start, end, n=20):
    r = c.analytics.reports().query(
        ids=f"channel=={c.channel_id}", startDate=start, endDate=end,
        metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained",
        dimensions="video", sort="-views", maxResults=n,
    ).execute()
    return r.get("rows", [])


def titles_for(c, ids):
    out = {}
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        resp = c.youtube.videos().list(part="snippet,contentDetails", id=",".join(batch)).execute()
        for it in resp.get("items", []):
            out[it["id"]] = {
                "title": it["snippet"]["title"],
                "published": it["snippet"]["publishedAt"][:10],
            }
    return out


def is_fwl(title):
    t = title.lower()
    return any(k in t for k in ["faithwalk", "walk", "miles", "minister zay", "3000"])


def report(c, label, days):
    today = date.today()
    start = (today - timedelta(days=days)).isoformat()
    rows = top_videos(c, start, today.isoformat(), 20)
    ids = [r[0] for r in rows]
    meta = titles_for(c, ids)
    print(f"\n################ TOP VIDEOS — LAST {label} ({start} -> {today}) ################")
    print(f"{'FWL':<4}{'views':>7}{'wMin':>7}{'avgS':>6}{'subs':>6}  title")
    fwl_v = fwl_s = tot_v = tot_s = 0
    for vid, views, wmin, avg, subs in rows:
        m = meta.get(vid, {})
        title = m.get("title", vid)
        flag = "FWL" if is_fwl(title) else ""
        if flag:
            fwl_v += int(views); fwl_s += int(subs)
        tot_v += int(views); tot_s += int(subs)
        print(f"{flag:<4}{views:>7}{wmin:>7}{avg:>6}{subs:>6}  {title[:60]}")
    print(f"\n  FWL clips: {fwl_v} views / {fwl_s} subs  |  Top-20 total: {tot_v} views / {tot_s} subs"
          f"  ->  FWL = {100*fwl_v//max(tot_v,1)}% of views, {100*fwl_s//max(tot_s,1)}% of subs")


def main():
    c = YouTubeClient()
    info = c.get_channel_info()
    s = info["statistics"]
    print(f"=== LIFETIME: {s['subscriberCount']} subs | {s['viewCount']} views | {s['videoCount']} videos ===")
    report(c, "28d", 28)
    report(c, "90d", 90)


if __name__ == "__main__":
    main()
