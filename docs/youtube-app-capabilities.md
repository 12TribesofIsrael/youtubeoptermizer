# YouTube App Capabilities — AI Bible Gospels

What the YouTube OAuth client can and cannot do as of 2026-04-29. This is the source of truth for "what API surfaces are unlocked" on the YT side.

Update it whenever scopes are added/removed, the OAuth client is regenerated, or quota is changed.

---

## Live status

| Item | Value |
|---|---|
| Google Cloud project | `youtube-optimizer-490415` |
| OAuth 2.0 client type | **Desktop** (Installed application) |
| Channel | AI Bible Gospels (`@AIBIBLEGOSPELS`) |
| Credential file | `credentials.json` (project root, gitignored) |
| Token cache | `token.json` (project root, gitignored) — has refresh token, persists indefinitely |
| Daily quota | **10,000 units/day** (default tier — raisable on request) |
| Last OAuth client refresh | 2026-04-27 (original client deleted in Cloud Console; replaced with fresh Desktop client) |

---

## Granted scopes (3 total)

- **`youtube.force-ssl`** — full read/write on the AI Bible Gospels channel. Covers everything in the API surface except uploads and analytics.
- **`youtube.upload`** — upload new videos (technically a subset of `force-ssl` but Google requires it explicitly for upload flows)
- **`yt-analytics.readonly`** — read-only analytics queries (impressions, retention, CTR, watch time, demographics, traffic sources)

Auth flow: first-run opens browser at `localhost:8080`, user signs into `aibiblegospels444@gmail.com` and approves all 3 scopes. Refresh token is cached and used silently on every subsequent run — no re-prompt unless Google forces it (typically every ~6 months idle, or when scopes change).

---

## What the app CAN do

### Videos
- List all videos on the channel (via uploads playlist — the source of truth, see [feedback memory on dedup](.claude/memory/feedback_yt_uploads_playlist_dedup.md))
- Read full metadata: title, description, tags, category, privacy, thumbnails, duration, statistics
- **Edit** title, description, tags, category, privacy (used by `aeo-bulk-update.py` for AEO description rollout, and by `yt-thomas-to-tommy.py` for the Tommy Lee scrub)
- **Delete** videos (used during the YPP cleanup pass)
- **Upload** new videos (not currently used — manual uploads via Studio)
- **Set thumbnails** (used during Phase 3 — 20 custom thumbnails)

### Playlists
- List all playlists
- Create new playlists
- Add videos to a playlist
- Remove videos from a playlist
- Reorder items (via PATCH on `playlistItems`)

### Channel
- Read channel metadata (subscriber count, total views, channel ID)
- Read + edit `brandingSettings.channel.description` (the About page)
- Read playlists owned by the channel

### Comments
- Read comments + replies on owned videos
- Reply to comments
- Moderate (mark as spam, remove, hold for review) — owned channel only
- Like / heart comments

### Analytics (`yt-analytics.readonly`)
- Daily-resolution queries on: views, watch time, retention curves, impressions, impressions CTR, subscribers gained/lost, traffic sources, demographics, geography, device type, playback location
- Per-video and channel-aggregate queries
- Date-range filters

### Search & discovery (public read)
- Search across all of YouTube
- Read public video data on any channel (used for competitor research)

---

## What the app CANNOT do

| Capability | Why blocked | Path to unblock |
|---|---|---|
| Manage Community posts | **Not exposed in YouTube Data API at all** | None — Google has never published this surface. Manual via Studio only. |
| Set / edit end screens | Not exposed in API | None — manual via Studio. |
| Set / edit info cards | Not exposed in API | None — manual via Studio. |
| Change channel name or handle | Not exposed in API | None — manual via Studio. |
| Manage subscribe watermark | Not exposed in API | None — manual via Studio. |
| Configure monetization settings (mid-rolls, ad breaks, monetization on/off) | Not exposed in API | None — manual via Studio. |
| Submit videos to YPP / appeal YPP suspensions | Not exposed in API | None — manual via Studio inbox. |
| Members-only / channel memberships management | Restricted partner API | Requires Google partner program enrollment, not on roadmap. |
| Live stream chat moderation | Possible via `youtube.force-ssl` but separate Live Streaming API surface | Build separately if needed. Not on roadmap. |
| Bulk-edit beyond ~166 description updates per day | Quota cap (50 units × 200 = 10,000) | Request quota raise via Google Cloud Console (free, ~1 week turnaround). Or pace updates across days. |

---

## Quota math (10,000 units/day default)

| Operation | Cost | Daily ceiling at default quota |
|---|---|---|
| `videos.list` (read) | 1 | 10,000 calls |
| `playlistItems.list` (read) | 1 | 10,000 calls |
| `videos.update` (edit metadata) | 50 | 200 videos/day |
| `videos.delete` | 50 | 200/day |
| `thumbnails.set` | 50 | 200/day |
| `playlists.insert` | 50 | 200/day |
| `playlistItems.insert` | 50 | 200/day |
| `channels.update` (About description) | 50 | 200/day |
| `search.list` | **100** | 100 calls/day |
| `videos.insert` (upload) | **1,600** | 6 uploads/day |
| Analytics queries (`youtubeAnalytics.v2`) | separate quota tier | not counted against Data API |

Practical impact:
- Bulk metadata rollouts (descriptions, tag updates) are gated at ~166–200 videos/day. The 187-video catalog fits in 1 day cleanly.
- Uploads are the most expensive — daily cap is 6 if you also do nothing else.
- `search.list` is heavy (100 units) — avoid in loops; prefer `playlistItems.list` (1 unit) when listing your own channel.

---

## Authentication notes

### First-run flow
1. Place `credentials.json` (Desktop OAuth client JSON downloaded from Google Cloud Console) in project root.
2. Run any script that calls [src/youtube/auth.py](../src/youtube/auth.py) `get_credentials()`.
3. Browser opens to Google sign-in. Use `aibiblegospels444@gmail.com` (the channel's canonical OAuth account — not any other personal dev account that may also be signed in to the same browser).
4. Approve all 3 scopes.
5. `token.json` is written. Done — no re-auth needed unless Google revokes.

### Refresh handling
The `Credentials` object auto-refreshes when expired, as long as `refresh_token` is present in `token.json`. No manual intervention.

### When re-auth IS needed
- OAuth client deleted/regenerated in Cloud Console (happened 2026-04-27)
- User revokes app access at https://myaccount.google.com/permissions
- Scopes change in `src/youtube/auth.py` `SCOPES` list — Google invalidates the cached token
- 6+ months of idleness (rare)

If `token.json` becomes invalid, just delete it and re-run any script — the auth flow will re-prompt.

### Gotchas
- `credentials.json` is gitignored. Do not commit. The `.gitignore` blocks `*.client_secret*.json` and `*.old-deleted-oauth` patterns as of 2026-04-27.
- The OAuth project (`youtube-optimizer-490415`) is in publishing status "Testing" — only listed test users can authenticate. `aibiblegospels444@gmail.com` is the sole test user. If you ever add another user, add them in Cloud Console → OAuth consent screen → Test users.
- Service accounts DO NOT work for YouTube. Must use interactive OAuth at least once.

---

## Scripts that use this auth

| Script | What it does |
|---|---|
| [scripts/aeo-bulk-update.py](../scripts/aeo-bulk-update.py) | Append AEO `CONSTANTS_BLOCK` to every video description (Phase A — done 2026-04-26) |
| [scripts/yt-thomas-to-tommy.py](../scripts/yt-thomas-to-tommy.py) | Privacy scrub — normalize creator name across every live video description to the public alias (done 2026-04-27, 173/173) |
| [src/youtube/client.py](../src/youtube/client.py) | The wrapper: list/get/update/delete videos, playlists, thumbnails, analytics, channel branding |

---

## Related docs
- [api-automation-plan.md](api-automation-plan.md) — Script 4 (`aeo-yt-phase-b.py`) and Script 5 (`unified-analytics.py`) both consume this auth
- [meta-app-capabilities.md](meta-app-capabilities.md) — sister doc for FB/IG side
- [research.md](../research.md) — original research on the YouTube Data API surface
