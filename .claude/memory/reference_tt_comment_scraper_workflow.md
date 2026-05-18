---
name: tt-comment-scraper-workflow
description: "End-to-end TT comment scrape + classify + reply-queue workflow. Scraper at analytics/_tiktok-comments-actions-v4.json, classifier at scripts/tt-comments-classify.py, output at output/tt-comments-to-reply.md."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 373f4945-6482-4d96-b023-f668cb24598b
---

When a TT post hits high comment volume and Tommy wants a triage queue, use this pipeline (built 2026-05-16):

**Step 1 — Scrape** (`analytics/_tiktok-comments-actions-v4.json`):
- Replace the `goto` URL with the target post
- Navigates → clicks Comments tab → scrolls 8 pages → extracts each commenter wrapper as `{i, h:handle, d:displayName, l:likes, c:comment}`
- Dumps payload to `window._dump` then slices in 1200-char chunks (browser_pilot.py truncates results at 2000 chars, so smaller slices = survives the cap)
- Hits TT's lazy-load ceiling around 50 comments per post — nested "View N replies" not expanded
- Run: `python ~/.claude/skills/browser/scripts/browser_pilot.py analytics/_tiktok-comments-actions-v4.json > analytics/_tt-scrape.log 2>&1`
- **Always re-encode the JSON with `ensure_ascii=True`** before running, or Python on Windows cp1252 chokes on emoji bytes.

**Step 2 — Classify** (`scripts/tt-comments-classify.py`):
- Reads the log, reconstructs the JSON payload from sliced `Result:` lines (markers after `built N items, payload=B bytes`)
- 6 buckets ranked by leverage: `identity` > `intent` > `tribe_claim` > `skeptic` > `faithwalk` > `scripture_quoter` > `affirmer` (hate ignored)
- 5 reply templates per bucket, rotated by handle hash to vary phrasing
- Filters: own replies (`aibiblegospels_`), display-name-echoes, "· Friend"/"· Creator" pseudo-comments
- Output: `output/tt-comments-to-reply.md` — priority-sorted with paste-ready replies + profile links

**Step 3 — Post** (manual or semi-supervised, NOT auto-reply):
- Per [[feedback_tt_comment_auto_reply_silent_fail]], browser auto-reply has silent-failure mode.
- Default = Tommy copy-pastes from the queue file. ~20 min for 30 comments.

**Maintenance notes:**
- Reply templates live inline in `scripts/tt-comments-classify.py` — edit there if Tommy's voice shifts.
- Scraper caps at ~50 comments per post. For longer threads, need to add "View N replies" expansion + multiple-pass scrolling.
- TT's `DivCommentObjectWrapper` and `DivCommentMain` class prefixes are the load-bearing selectors — TT obfuscates inner classes but those structural names have been stable since 2026-04.
