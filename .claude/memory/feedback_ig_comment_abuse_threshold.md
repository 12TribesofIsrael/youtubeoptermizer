---
name: IG comment-posting hits Meta abuse flag around 256/session
description: Meta's anti-spam triggers (code 368, "action deemed abusive") after ~256 rapid comments via API in one session; pace at 50/day to stay under threshold
type: feedback
originSessionId: f722b886-dd9c-4fd1-bbd4-62cd81fc83ea
---
On 2026-04-27, `scripts/aeo-ig-pin-comment.py` ran cleanly through 256 IG posts (1 canary + 5 + 50 + 200 batches, ~3 sec/post pace) then hit Meta error code 368 / subcode 4928002:

```
"The action attempted has been deemed abusive or is otherwise disallowed"
```

This is Meta's anti-spam flag — same templated comment text across many posts in rapid succession trips a heuristic. The 257th attempt was the first IMAGE post in the queue (prior 256 were mostly VIDEO/Reel), but the more likely cause is cumulative session count, not media type.

**Why:** The original `docs/api-automation-plan.md` paced 1A at 50/day specifically to avoid this. We blew past the limit testing batch sizes (the script worked so cleanly on 50 then 200 that scaling further felt safe — it wasn't).

**How to apply:**
- For any bulk same-text comment/caption operation across IG: cap at **50/day** per the original plan, even when individual batches feel fine.
- The flag triggers per app/page, not per IP — switching machines/networks won't reset it.
- Cooldown: ~24h+ before retrying. Don't retry on the same day after seeing code 368.
- Don't conflate this with rate-limit errors (which are transient and recover in minutes). 368 is content/behavioral; longer cooldown.
- Checkpoint pattern in `aeo-ig-pin-comment.py` makes resume safe — saved state = 256/563 in `output/aeo-ig-comment-checkpoint.json`.
