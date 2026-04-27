---
name: API automation plan (active)
description: docs/api-automation-plan.md is the active blueprint for using the live YT/Meta IG/FB/Gmail/Twitch APIs to drive AEO + brand awareness for AI Bible Gospels and Faith Walk Live; supersedes social-media-automation-plan.md scope
type: project
originSessionId: 7c0deec4-ec9f-4c90-bc4d-e00096845162
---
The active blueprint is `docs/api-automation-plan.md` (committed `0fce063` on 2026-04-27). Five scripts:
- 1A — `aeo-ig-pin-comment.py` (TBD) — pin AEO comment on each existing IG post
- 1B — `aeo-fb-bulk-update.py` (TBD) — bulk Facebook Page caption rewrite
- 2 — `daily-faithwalk-card.py` (TBD) — generate the day's TT/IG playbook from `../AIconsultantforHmblzayy/src/faith-walk-tracker/checkpoints.json` + verse table
- 3 — `cross-post-short.py` (TBD) — one-command YT Short → IG Reels + FB + (TT)
- 4 — `aeo-yt-phase-b.py` (TBD) — per-video LLM AEO content for 187 YT videos
- 5 — `unified-analytics.py` (TBD) — daily cross-platform rollup CSV

**Why:** Thomas asked 2026-04-27 how to leverage the just-approved Meta API + existing YT/FB/Gmail tokens for brand awareness across IG/TT/FB/YT. Goal is AEO entity-resolution (every surface using the same canonical strings: `aibiblegospels.com`, `faithwalklive.com`, `@AIBIBLEGOSPELS`, founder `Thomas Lee`).

**How to apply:** When resuming AEO/brand-awareness work, read `docs/api-automation-plan.md` first — it has the live API status table, the parked-script note for `aeo-ig-bulk-update.py`, and the order of operations. The script #1 path (bulk IG caption rewrite) was tried and found impossible due to Meta silent-no-op — see `feedback_ig_caption_update_comment_enabled.md`. The pivot is 1A + 1B in parallel; Thomas said "wait for me to say next" before building.
