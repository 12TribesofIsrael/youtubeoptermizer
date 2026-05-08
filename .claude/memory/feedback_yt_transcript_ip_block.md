---
name: youtube_transcript_api gets IP-blocked after ~12 fetches
description: YT rate-limits transcript scraping by IP; bulk transcript-driven scripts must treat transcript-unavailable as retryable, not permanent skip
type: feedback
originSessionId: 0734df78-6a4b-4eea-9432-c912278f58f1
---
The `youtube_transcript_api` Python library scrapes YouTube's transcript surface, which rate-limits per-IP. After ~12 successful fetches in a single run, subsequent calls return `IpBlocked` errors that look exactly like "transcript doesn't exist." The block typically clears in 24-48 hours.

**Why:** observed first time on 2026-05-07 during Phase B AEO rollout (`scripts/aeo-yt-phase-b.py --live --limit 100`). First 12 videos got transcripts and live writes, next 73 hit IP block. The block looks identical to "no captions on this video" — both raise generic exceptions in `api.fetch(vid)`.

**How to apply:**
- Bulk transcript-driven scripts must distinguish *permanent* skips (deleted, no captions) from *transient* skips (IP block). Don't persist transient skips to a checkpoint's `skipped` set — they need to retry on next run.
- Add an early-exit when 3+ transcript fetches fail in a row — don't burn through the queue for nothing.
- Pace post-write sleeps generously (1.5s+ between successful fetches; 0.5s tripped the limit at index 13).
- For permanent fix, options: WebshareProxyConfig in youtube-transcript-api ($1/mo residential proxies), or pivot to YouTube Data API v3 captions endpoint (200 quota/download — too expensive for bulk).
- Wait 24h between bulk runs; expect ~12 fresh transcript fetches per run.

Pattern in `scripts/aeo-yt-phase-b.py` (after fix in commit 2f30834): `transcript_block_streak` counter resets on success, breaks loop at 3.
