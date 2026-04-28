---
name: YT uploads playlist returns duplicate items across pages
description: channels.list mine=true → uploads playlist can return the same video_id multiple times across pagination boundaries; always dedupe by video_id
type: feedback
originSessionId: f722b886-dd9c-4fd1-bbd4-62cd81fc83ea
---
The YouTube Data v3 uploads playlist (fetched via `channels.list mine=true` → `relatedPlaylists.uploads` → `playlistItems.list`) does NOT guarantee unique items across pages.

Observed 2026-04-27: AI Bible Gospels uploads playlist returned **192 items** but only **173 unique video IDs**. 19 duplicate entries spread across pages.

**Why:** Likely a YouTube quirk where pagination cursors aren't perfectly stable when the playlist is being modified, or the uploads playlist tracks every upload event (including reuploads/edits) as a separate playlist item even though they share a video_id. Either way, the API does not guarantee uniqueness.

**How to apply:**
- Always dedupe playlist results by `videoId` before iterating. The fetcher in `scripts/yt-thomas-to-tommy.py` (`fetch_all_uploaded_video_ids`) is the working reference — uses a `seen: set` to filter dups while preserving order.
- Don't trust `len(items)` from pagination as a video count — use `len(set(video_ids))`.
- Same pattern likely applies to other YT playlists. Always dedupe.

Related: the analytics CSV (`analytics/post-optimization/all-videos.csv`) is also unreliable as a video-ID source — it's a manual export that goes stale fast (679 rows when the live count was 173). The uploads playlist is the only durable source-of-truth for "what videos exist on this channel right now."
