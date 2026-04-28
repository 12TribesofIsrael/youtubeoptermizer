---
ended: 2026-04-27T23:59:00Z
project: youtubeoptermizer (AI Bible Gospels)
branch: main
originSessionId: f722b886-dd9c-4fd1-bbd4-62cd81fc83ea
---
# Last Session — 2026-04-27 (late)

## What the user wanted
Tommy asked to build the IG comment-pin script (1A from `docs/api-automation-plan.md`) and run it across his 563 IG posts. Mid-session pivoted to a deeper privacy goal: scrub his legal name ("Thomas Lee") off every public surface — repo files, YT video descriptions, IG comments — replacing with the alias **Tommy Lee**. Wrap-up by night.

## What we did
- **Built `scripts/aeo-ig-pin-comment.py`** — posts + pins the AEO `CONSTANTS_BLOCK` as a comment on each IG post. Idempotent (marker check), checkpointed, dry-run by default. Lifted CONSTANTS + helpers verbatim from the parked `aeo-ig-bulk-update.py`.
- **Discovered IG pin endpoint quirk**: `POST /{ig-comment-id}` requires BOTH `is_pinned=true` AND `hide=false` together. First canary errored with code 100 ("hide is required"); patched with `hide=false`. Saved as feedback memory.
- **IG comment-pin progress: 256/563** posts pinned. Canary (latest Reel DXnbyvTDNbn, comment 18089952173590782) cleanly verified. Then `--limit 50` clean (5 sec/post pace). Then `--limit 200` clean. Stopped on attempt #257 with Meta code 368 ("action deemed abusive"). Saved as feedback memory.
- **Privacy scrub: Thomas Lee → Tommy Lee** across 9 tracked repo files (3 scripts, 2 docs, 4 memory files). Rewrote `user_thomas_profile.md` to drop legal-name callout. Added `feedback_use_tommy_not_legal.md` rule. Old IG canary comment (Thomas Lee) deleted, reposted with Tommy Lee, re-pinned, verified.
- **Built `scripts/aeo-fb-bulk-update.py`** for FB Page caption rewrite. Token refresh chain: user pasted new short-lived token → ran `meta-token-refresh.py` → got long-lived user token + non-expiring `META_PAGE_TOKEN` (now in `.env`). Read works (90 FB posts). **Write blocked on missing `pages_manage_posts` scope** (code 100/200 errors) — same blocker for both create and edit paths. Tommy can't add the scope in Graph Explorer; needs Meta App Review.
- **Built `scripts/yt-thomas-to-tommy.py`** — find-replace "Thomas Lee" → "Tommy Lee" across all live videos. First attempt failed: YT OAuth client was deleted in Google Cloud Console. Tommy generated a fresh Desktop OAuth client → swapped `credentials.json` → fresh OAuth flow → token cached. Refactored script to pull video IDs from the **uploads playlist** instead of the stale `analytics/post-optimization/all-videos.csv` (CSV had 679 stale rows).
- **YT scrub: 173/173 unique live videos done** in one pass. Most older videos had Phase A AEO block with "Thomas Lee" 2x → swapped both occurrences; the few newest FaithWalk videos had no AEO block at all (post-Phase A uploads, never blocked).
- **Discovered uploads-playlist dedup gotcha**: playlist returns 192 items but only 173 unique video IDs. Saved as feedback memory; script's `fetch_all_uploaded_video_ids` now dedupes.
- Committed `c6a6839` (17 files, 1310 inserts), pushed to origin/main. Hardened `.gitignore` against `*.client_secret*.json` and `*.old-deleted-oauth` patterns.

## Decisions worth remembering
- **Pivot away from FB caption-rewrite for now.** App Review for `pages_manage_posts` would unblock it but is multi-day. Skip-FB is the pragmatic call until Tommy explicitly wants to file the review.
- **Refactored YT script away from the CSV** because we deleted ~40 videos since the last analytics export. Uploads playlist is the only source of truth that stays current.
- **Used the script's `--retry-pin` and `--delete-comment-id` ops flags** for canary recovery rather than building separate one-off scripts. Worth the +20 lines of CLI plumbing.
- **Kept `scripts/aeo-ig-bulk-update.py` parked** even though its target endpoint is dead — it remains the canonical reference for `CONSTANTS_BLOCK` + transform pattern lifted by the new scripts.

## Open threads / next session starts here
1. **Resume IG comment-pin at 50/day pace.** Checkpoint at 256/563 (state in `output/aeo-ig-comment-checkpoint.json`). Wait at least 24h after the abuse flag (#257 timestamp ~2026-04-27 late). Re-run `python scripts/aeo-ig-pin-comment.py --live --limit 50`. Don't push past 50/day until Meta's heuristics cool.
2. **FB caption rewrite — decide on App Review.** `aeo-fb-bulk-update.py` is built and dry-run-clean. Submit Meta App Review for `pages_manage_posts` (same process as IG approval that landed 2026-04-27)? Or punt FB to manual via Meta Business Suite? Tommy left this open.
3. **Add AEO block to newest YT videos.** Tonight's scrub didn't add NEW blocks — it only replaced "Thomas Lee" in EXISTING blocks. The handful of post-Phase A uploads (Day 31 FaithWalk, etc.) have no AEO block at all. Quick run of `python scripts/aeo-bulk-update.py --live` would add it (script is idempotent — skips already-blocked).
4. **Revoke the user token Tommy pasted in chat.** It's already replaced in `.env` (long-lived user + non-expiring page token), but the original short-lived value sits in this conversation's transcript. Revoke at https://developers.facebook.com/tools/accesstoken/.
5. **Newer YT videos uploaded post-2026-04-26 don't have the AEO block.** Quick run of `aeo-bulk-update.py` (already pointed at the live uploads list via memory of the YT pattern) covers this. Or convert that script too to the uploads-playlist source-of-truth.

## Uncommitted work
Clean working tree.
