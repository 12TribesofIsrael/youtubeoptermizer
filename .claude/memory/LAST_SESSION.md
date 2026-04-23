---
ended: 2026-04-22T23:59:00Z
project: youtubeoptermizer (AI Bible Gospels)
branch: main
originSessionId: 9ae7e17c-6ea6-40e7-8793-0bfa250ef5cf
---
# Last Session — 2026-04-22 (late)

## What the user wanted
Check the status of the Meta App Review (Instagram Business Login, submitted 2026-04-17) and resolve the recurring META_ACCESS_TOKEN expiration blocker so it stops derailing automation.

## What we did
- Built `scripts/meta-status-probe.py` — live read-only probe: debug_token, IG /me, recent media, app `/permissions` review state for both Meta app and IG app.
- First probe confirmed `META_ACCESS_TOKEN` was DEAD (error 190/subcode 460 — session invalidated). `IG_BUSINESS_TOKEN` still healthy (read access unaffected).
- Walked user through regenerating a short-lived user token in Graph API Explorer (Live app `1452257036358754`, 6 IG scopes). User pasted token; written to `.env`.
- Built `scripts/meta-token-refresh.py` — exchanges short-lived → long-lived (60d) user token, derives Page token, writes both back to `.env` as `META_ACCESS_TOKEN` + `META_PAGE_TOKEN`. Idempotent, re-runnable.
- Ran refresh: both tokens valid for **~59d** (expires ~2026-06-20). Discovered Page tokens under Business Manager do NOT become truly non-expiring — Meta caps them at user-token lifetime. Updated memory `feedback_meta_token_recurring.md` with this caveat + new usage instructions.
- Committed + pushed as `6cb21b8` to origin/main (2 files, 166 insertions).

## Decisions worth remembering
- Accepted 59d Page token expiry as the ceiling (not a bug) — truly non-expiring Page tokens only exist for personal/non-BM Pages. The refresh script is the permanent fix; user re-runs every ~50d.
- App Review submission state can't be cleanly introspected via API — `/permissions` on the Meta app shows only `email`+`public_profile` as live (baseline); the IG app `/permissions` endpoint rejects app-token auth. Dashboard is source of truth.

## Open threads / next session starts here
- **App Review decision expected by 2026-04-28** (Meta's 10-day window). If approved, run `python scripts/meta-update-posts.py instagram --live` to fix 538 IG captions. If rejected or no decision, check dashboard screenshot + resubmit.
- Scheduled Shorts still paused (15 "12 Tribes" drafts unscheduled 2026-04-22 during YPP appeal) — drip-release post-YPP resolution.
- YPP second appeal filed 2026-04-22; window closes 2026-04-30.
- TikTok 3rd app review submission live since 2026-04-22.

## Uncommitted work
Clean working tree.
