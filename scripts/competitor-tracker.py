"""Weekly scorecard: what the top Bible channels are doing, and how far we drift from it.

Pulls each channel's public tabs with yt-dlp (no API quota, no login), measures the FRAMEWORK
rather than the content -- how often they post, how long, how they title, whether they go live,
how they use Shorts -- and puts our channel on the same ruler. The point is not to copy anyone;
it is to notice, in numbers, when we stop doing what the winners keep doing.

    python scripts/competitor-tracker.py              # full pull, writes the scorecard
    python scripts/competitor-tracker.py --quick      # 5 videos per tab (smoke test)
    python scripts/competitor-tracker.py --only bibleproject,HolyBibleChannel

Outputs
  analytics/competitors/YYYY-MM-DD.json   raw per-channel pull (kept forever; history)
  analytics/competitors/history.csv       one row per channel per run (trend lines)
  docs/competitor-scorecard.md            the read: benchmark table + our drift, rewritten each run

Watched by the notifier: task "BMB YouTube Competitor Tracker - weekly", heartbeat
analytics/competitors/.heartbeat (touched on every completed run), any exception mails via guard.
"""
import argparse
import csv
import json
import re
import statistics
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "analytics" / "competitors"
SCORECARD = ROOT / "docs" / "competitor-scorecard.md"
HEARTBEAT = OUT / ".heartbeat"
YTDLP = [sys.executable, "-m", "yt_dlp"]
SHORT_MAX = 180        # YouTube's Shorts ceiling (3 min) since 2024-10-15
WINDOW = 28            # days the cadence numbers are measured over

# Benchmarked 2026-09-30 (docs/competitor-scorecard.md has the numbers). "peer" = the set we
# measure ourselves against; "watch" = worth seeing but a different game (kids' church, 5M-sub
# donor-funded studio).
OURS = "AIBIBLEGOSPELS"
CHANNELS = {
    "HolyBibleChannel": "peer",            # full-book narration, the closest format match
    "DeepBibleStories": "peer",            # AI, near-daily long teaching
    "TheAIBibleOfficial": "peer",          # AI, Pray.com
    "TheSecretsOfTheBibleAIOfficial": "peer",
    "BibleNutshells": "peer",              # AI-assisted "full movie" cuts
    "AIBIBLESAGAS": "peer",                # one AI movie per book, premiere slots
    "bible.animations": "peer",
    "BibleChroniclesAnimation": "peer",
    "BibleStoriesinBlack": "peer",         # closest visual identity
    "IUICintheClassRoom": "peer",          # live teaching, our audience
    "aGATHERING144": "peer",
    "BenayahIsrael": "peer",
    "ScourbyYouBible": "peer",             # 24/7 KJV + Apocrypha streams
    "bibleproject": "watch",
    "SaddlebackKids": "watch",
    OURS: "ours",
}

HOOK_WORDS = re.compile(r"\b(WHY|SCARY|SECRET|HIDDEN|NO ONE|NOBODY|REALLY|SHOCKING|TRUTH|BANNED|FORBIDDEN)\b")


def ytdlp(url, n, flat=False):
    cmd = [*YTDLP, url, "--dump-json", "--skip-download", "--no-warnings", "--ignore-errors",
           "--playlist-end", str(n)]
    if flat:
        cmd.append("--flat-playlist")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    items = []
    for line in r.stdout.splitlines():
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return items


def channel_subs(base):
    """Subscriber count from the channel page itself. Video entries carry the same field but on
    the first run one channel's came back as 203 for a 203K channel; the channel page is the
    figure YouTube shows."""
    r = subprocess.run([*YTDLP, base, "--dump-single-json", "--flat-playlist", "--playlist-items", "0",
                        "--no-warnings"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return json.loads(r.stdout).get("channel_follower_count")
    except json.JSONDecodeError:
        return None


def pull(handle, n):
    base = f"https://www.youtube.com/@{handle}"
    vids = ytdlp(base + "/videos", n)
    streams = ytdlp(base + "/streams", max(3, n // 3))
    shorts = ytdlp(base + "/shorts", n, flat=True)
    subs = channel_subs(base) or next(
        (v.get("channel_follower_count") for v in vids + streams if v.get("channel_follower_count")), None)
    return {"handle": handle, "subs": subs, "videos": vids, "streams": streams, "shorts": shorts}


def parse_date(s):
    return datetime.strptime(s, "%Y%m%d").date() if s else None


def title_pattern(title):
    t = title or ""
    return {
        "subtitle": bool(re.search(r"\s[|:\u2014\u2013-]\s|:\s", t)),   # "Book — subtitle" / "Book: subtitle"
        "hook": bool(HOOK_WORDS.search(t.upper())) or any(w.isupper() and len(w) > 3 for w in re.findall(r"[A-Za-z]+", t)),
        "question": t.strip().endswith("?") or t.lower().startswith(("why ", "what ", "who ", "how ")),
        "full": bool(re.search(r"\bfull\b|\bmovie\b|\bcomplete\b|\bentire\b", t, re.I)),
    }


def measure(raw, today):
    cutoff = today - timedelta(days=WINDOW)
    longform = [v for v in raw["videos"] if (v.get("duration") or 0) > SHORT_MAX]
    recent = [v for v in longform if parse_date(v.get("upload_date")) and parse_date(v["upload_date"]) >= cutoff]
    recent_streams = [v for v in raw["streams"] if parse_date(v.get("upload_date")) and parse_date(v["upload_date"]) >= cutoff]
    live_now = sum(1 for v in raw["streams"] if v.get("is_live"))
    durs = [v["duration"] / 60 for v in longform if v.get("duration")]
    views = [v["view_count"] for v in longform[:10] if v.get("view_count") is not None]
    pats = [title_pattern(v.get("title")) for v in longform[:10]]
    n = max(len(pats), 1)
    return {
        "handle": raw["handle"], "role": CHANNELS[raw["handle"]], "subs": raw["subs"],
        "uploads_28d": len(recent),
        "uploads_per_week": round(len(recent) * 7 / WINDOW, 2),
        "median_len_min": round(statistics.median(durs), 1) if durs else None,
        "median_views_last10": int(statistics.median(views)) if views else None,
        "views_per_sub": round(statistics.median(views) / raw["subs"], 4) if views and raw["subs"] else None,
        "streams_28d": len(recent_streams), "live_now": live_now,
        "shorts_listed": len(raw["shorts"]),
        "shorts_median_views": int(statistics.median([s["view_count"] for s in raw["shorts"] if s.get("view_count")])) if any(s.get("view_count") for s in raw["shorts"]) else None,
        "title_subtitle_pct": round(100 * sum(p["subtitle"] for p in pats) / n),
        "title_hook_pct": round(100 * sum(p["hook"] for p in pats) / n),
        "title_question_pct": round(100 * sum(p["question"] for p in pats) / n),
        "title_full_pct": round(100 * sum(p["full"] for p in pats) / n),
        "latest_upload": max((v.get("upload_date") or "" for v in raw["videos"]), default=""),
        "top_recent": [{"title": v.get("title"), "views": v.get("view_count"), "min": round((v.get("duration") or 0) / 60)}
                       for v in sorted(longform[:10], key=lambda v: v.get("view_count") or 0, reverse=True)[:3]],
    }


def med(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return statistics.median(vals) if vals else None


def fmt(v, pct=False):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:,.1f}"
    return f"{v:,}{'%' if pct else ''}"


def scorecard(rows, today):
    peers = [r for r in rows if r["role"] == "peer"]
    ours = next((r for r in rows if r["role"] == "ours"), None)
    bench = {k: med(peers, k) for k in ("uploads_per_week", "median_len_min", "streams_28d", "shorts_listed",
                                         "title_subtitle_pct", "title_hook_pct", "views_per_sub")}
    L = [f"# Competitor scorecard — {today}", "",
         f"Weekly pull (`scripts/competitor-tracker.py`, yt-dlp, public tabs). Cadence is measured over the last "
         f"{WINDOW} days; lengths and title patterns over each channel's last 10 long-form uploads (> {SHORT_MAX // 60} min). "
         "Subscriber counts are YouTube's rounded public figure.", "",
         "## The ruler", "",
         "| Channel | Subs | Long-form / wk | Median len (min) | Median views (last 10) | Views per sub | Streams (28d) | Live now | Shorts listed | Subtitle titles | Hook titles |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["role"] != "ours", -(r["subs"] or 0))):
        tag = " **(us)**" if r["role"] == "ours" else (" *(watch)*" if r["role"] == "watch" else "")
        L.append(f"| @{r['handle']}{tag} | {fmt(r['subs'])} | {fmt(r['uploads_per_week'])} | {fmt(r['median_len_min'])} | "
                 f"{fmt(r['median_views_last10'])} | {fmt(r['views_per_sub'])} | {r['streams_28d']} | {r['live_now']} | "
                 f"{r['shorts_listed']} | {fmt(r['title_subtitle_pct'], True)} | {fmt(r['title_hook_pct'], True)} |")
    L += ["", f"**Peer median** ({len(peers)} channels): "
              f"{fmt(bench['uploads_per_week'])} long-form/wk · {fmt(bench['median_len_min'])} min · "
              f"{fmt(bench['streams_28d'])} streams/28d · {fmt(bench['title_subtitle_pct'], True)} subtitle titles · "
              f"{fmt(bench['title_hook_pct'], True)} hook titles · {fmt(bench['views_per_sub'])} views per sub", ""]
    if ours:
        L += ["## Our drift", "",
              "Where we sit against the peer median. A line is flagged when we are below the median on something "
              "the peers all do, or above it on something none of them do.", ""]
        checks = [
            ("Long-form uploads per week", ours["uploads_per_week"], bench["uploads_per_week"], "below"),
            ("Median long-form length (min)", ours["median_len_min"], bench["median_len_min"], "below"),
            ("Live streams in 28 days", ours["streams_28d"], bench["streams_28d"], "below"),
            ("Titles with a subtitle", ours["title_subtitle_pct"], bench["title_subtitle_pct"], "below"),
            ("Titles with a hook word", ours["title_hook_pct"], bench["title_hook_pct"], "below"),
            ("Median views per subscriber", ours["views_per_sub"], bench["views_per_sub"], "below"),
        ]
        for label, mine, theirs, bad in checks:
            if mine is None or theirs is None:
                L.append(f"- {label}: us {fmt(mine)}, peers {fmt(theirs)} (not enough data)")
                continue
            flag = "**OFF TRACK**" if (bad == "below" and mine < theirs) else "on track"
            L.append(f"- {label}: us {fmt(mine)}, peer median {fmt(theirs)} — {flag}")
        L.append("")
    L += ["## What is working for them right now (top of the last 10 uploads)", ""]
    for r in sorted(peers, key=lambda r: -(r["median_views_last10"] or 0)):
        for t in r["top_recent"][:1]:
            L.append(f"- @{r['handle']}: \"{t['title']}\" — {fmt(t['views'])} views, {t['min']} min")
    L += ["", "*Numbers are YouTube's public figures at pull time. This file is rewritten every run; history is in "
              "`analytics/competitors/history.csv`.*"]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="5 videos per tab")
    ap.add_argument("--only", help="comma-separated handles")
    ap.add_argument("--no-notify", action="store_true", help="skip the notifier guard (manual runs)")
    args = ap.parse_args()
    n = 5 if args.quick else 15
    handles = [h for h in CHANNELS if not args.only or h in args.only.split(",")]
    if OURS not in handles:
        handles.append(OURS)

    def run():
        today = date.today()
        OUT.mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(max_workers=6) as ex:
            raws = list(ex.map(lambda h: pull(h, n), handles))
        rows = [measure(r, today) for r in raws]
        empty = [r["handle"] for r in raws if not r["videos"]]
        if len(empty) > len(handles) // 2:
            raise RuntimeError(f"yt-dlp returned nothing for {len(empty)}/{len(handles)} channels: {empty}")
        (OUT / f"{today}.json").write_text(json.dumps({"date": str(today), "channels": rows}, indent=1, ensure_ascii=False), encoding="utf-8")
        hist = OUT / "history.csv"
        fields = ["date"] + [k for k in rows[0] if k != "top_recent"]
        new = not hist.exists()
        with hist.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            if new:
                w.writeheader()
            for r in rows:
                w.writerow({"date": str(today), **r})
        SCORECARD.write_text(scorecard(rows, today), encoding="utf-8")
        HEARTBEAT.touch()
        print(f"{len(rows)} channels ({len(empty)} empty: {empty}) -> {SCORECARD}")
        if empty:
            print("   empty pulls are kept out of the medians but recorded; if the same handle is empty two weeks running, its URL changed")

    if args.no_notify:
        run()
        return
    sys.path.insert(0, r"C:\Users\Claude\ecosystem\notify")
    from notify import guard
    with guard("youtube competitor tracker"):
        run()


if __name__ == "__main__":
    main()
