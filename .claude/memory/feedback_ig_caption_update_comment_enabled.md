---
name: IG caption updates silently no-op on graph.instagram.com
description: POST /{ig-media-id} with caption param returns {"success":true} but does NOT actually update the caption text — the endpoint only honors comment_enabled
type: feedback
originSessionId: 7c0deec4-ec9f-4c90-bc4d-e00096845162
---
**Captions on existing IG posts cannot be edited via the Graph API**, regardless of media_product_type (FEED, REELS, both confirmed silent no-op). The endpoint `POST https://graph.instagram.com/v22.0/{media_id}` with `caption` + `comment_enabled` + `access_token`:

- Returns HTTP 200 `{"success":true}`
- Re-fetching `?fields=caption` shows the OLD caption — the new one was never applied
- Only the `comment_enabled` toggle is actually honored

**Why:** Verified 2026-04-27 with a sentinel-string canary on 5 Reels + 1 FEED post. Sentinel `AEOTEST_FEED_2026_04_27` POSTed cleanly; re-fetch showed it absent. The "must include comment_enabled" rule from the prior version of this memory was a partial truth — without it you get code 100, with it you get a silent success that doesn't do what the parameter name implies.

**How to apply:**
- Don't try to bulk-rewrite captions on the 563 existing AI Bible Gospels IG posts. The first `aeo-ig-bulk-update.py --live` run on 5 posts confirmed silent failure.
- For AEO on existing IG posts, use **pinned comments** instead (`instagram_business_manage_comments` scope is approved) — POST a comment carrying the AEO block, then pin it. Comments ARE indexed by answer engines.
- For new IG posts going forward, set the AEO caption at publish time via `/{ig-user-id}/media` → `/{ig-user-id}/media_publish` — captions ARE editable in the create→publish flow.
- For the same brand-awareness goal, pivot to **Facebook Page posts** (`graph.facebook.com/{post_id}` with `message`) — FB caption edits DO work on already-published posts. Existing `meta-update-posts.py` covers this surface.
