---
name: Canary-test bulk API operations before scaling
description: For any bulk write across N>1 records (captions, comments, posts, descriptions), run a 5-record canary in --live mode and independently verify the change persisted before scaling — APIs sometimes return success without applying the write
type: feedback
originSessionId: 7c0deec4-ec9f-4c90-bc4d-e00096845162
---
Before running any bulk API write at scale (50, 100, 500+ records), do a 5-record `--live` canary AND independently verify the change persisted on the platform before scaling up. Both halves matter:

1. The `--live --limit 5` canary catches token/scope/permission errors the dry-run can't see.
2. The independent re-fetch (or visual check on the platform UI) catches **silent no-ops** — APIs that return `HTTP 200 success:true` without actually applying the write.

**Why:** 2026-04-27. Wrote `aeo-ig-bulk-update.py` to rewrite 563 IG captions, ran the live canary on 5, all returned `{"success":true}` HTTP 200. Thomas opened IG and said "I don't see the update." Re-fetch via API confirmed silent no-op — Meta accepts the `caption` parameter and ignores it on already-published posts, returning success either way. Without the visual + re-fetch verification, we would have "completed" all 563 and shipped nothing. See `feedback_ig_caption_update_comment_enabled.md` for the specific Meta finding.

**How to apply:** Build every bulk-write script with three modes:
- `--preview` (no API write, just print the transformed payload) — catches transform bugs
- `--live --limit 5` (writes 5, then stops) — catches API/auth issues at small blast radius
- `--live --limit N` (full run after canary verified) — only run AFTER step 2's writes are confirmed to have actually persisted on the platform side, not just to have returned success

The verification step is a re-GET against the same record, looking for a sentinel string or marker in the response body. If you can't re-GET to verify, ask the user to eyeball the records on the platform UI before scaling.
