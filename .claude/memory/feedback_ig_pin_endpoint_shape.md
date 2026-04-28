---
name: IG comment pin endpoint requires hide=false
description: API quirk — POST graph.instagram.com/{comment_id} for pinning needs is_pinned=true AND hide=false together; sending is_pinned alone fails with code 100
type: feedback
originSessionId: f722b886-dd9c-4fd1-bbd4-62cd81fc83ea
---
The Instagram Graph API endpoint for pinning a comment is `POST graph.instagram.com/v22.0/{comment-id}` — but it expects BOTH `is_pinned` AND `hide` parameters in the same request. Sending `is_pinned=true` alone returns:

```
{"message": "The parameter hide is required.", "type": "IGApiException", "code": 100}
```

The fix: always send `{"is_pinned": "true", "hide": "false", "access_token": ...}`. The `hide` parameter is the moderation toggle for the comment; passing `false` keeps it visible.

**Why:** Discovered 2026-04-27 during the first live canary of `scripts/aeo-ig-pin-comment.py`. POST landed cleanly (200 OK, comment_id returned), pin failed with code 100. Without the canary discipline, the entire 563-post bulk would have left every comment unpinned.

**How to apply:**
- Any IG comment-state mutation goes through this endpoint with both flags. The script's `pin_comment` helper at `scripts/aeo-ig-pin-comment.py` is the working reference.
- If the API ever returns "is_pinned is required" or similar reciprocal errors, send the missing flag — Meta bundles moderation flags together at this endpoint.
- This is undocumented behavior — Meta's docs show pinning as `is_pinned=true` only.
