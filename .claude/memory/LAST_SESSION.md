---
ended: 2026-04-21T22:00:00Z
project: youtubeoptermizer (AI Bible Gospels)
branch: main
originSessionId: 5618946d-736d-4ccd-ab23-199943513a3f
---
# Last Session — 2026-04-21

## What the user wanted
Diagnose why the TikTok viral-formula replication was failing: Clone #2 (Tribe of Judah) had just landed and was flat like Clone #1. User wanted real numbers and the viral-formula doc updated with whatever rule was broken, so Script 3 doesn't repeat the mistake.

## What we did
- **Scraped live TikTok metrics** for all 3 posts via the `browser` skill (no login needed). Numbers at ~24–60h:
  - SEED (Deut 28) — 3,999 v / 511 l / **403 sh** / 181 sv / 34 c → share rate **10.08%** (seed still working but cooling).
  - CLONE #1 (Edom) — 255 v / 18 l / 6 sh → **2.35%** share rate. Dead.
  - CLONE #2 (Judah) — 176 v / 17 l / **1 sh** / 4 sv → **0.57%** share rate. Dead.
- **Diagnosed the failure mode** — both clones broke the hook formula, not the pipeline. Clone #1 dropped "in church" for "who Edom really is". Clone #2 dropped "in church" for "in American history" AND used a verse citation ("28:68") instead of a chapter AND ran 1:13 (>60s disables Duet/Stitch). Technical fixes in Clone #2 (Daniel voice ✓, 9:16 ✓, face thumbnail ✓) were correct but couldn't save the caption/duration mistakes.
- **Updated [docs/viral-formula-deuteronomy-28.md](../../../../Users/Claude/youtubeoptermizer/docs/viral-formula-deuteronomy-28.md)** — added a new "HARD RULES — LOCKED" section (6 non-negotiables: "in church" verbatim, chapter-not-verse, ≤55s, different chapter per clone, Daniel voice, 9:16). Rewrote the replication queue so priorities 1–5 all use compliant hooks (Genesis 49, Joel 3, Deut 7, Jeremiah 16, Deut 33). Logged day-2/day-3 actuals for seed + both clones in the Updates log. Meta-lesson added at bottom. Committed as `1e660e7` and pushed.
- **Enhanced the global `browser` SKILL.md** ([~/.claude/skills/browser/SKILL.md](~/.claude/skills/browser/SKILL.md)) with a new "`evaluate` action — critical gotchas" section. Pilot wraps scripts as `() => { <script> }` so you MUST use `return` (not IIFE). Added 5 concrete rules with before/after examples. This is in the GLOBAL skill dir, not in the repo.
- **Saved a project reference memory** `reference_tiktok_scraping_selectors.md` — `data-e2e` selectors for likes/comments/shares/saves (saves = the `undefined-count` quirk), view counts live only on profile grid not watch page, ready-to-paste action template. Committed as `371963d` and pushed.
- **Saved a feedback memory** `feedback_save_skill_learnings.md` — durable rule that skill gotchas go in the skill's SKILL.md, not session logs.

## Decisions worth remembering
- **Hook wording > pipeline technicals.** Clone #2 had every technical fix from LAST_SESSION 2026-04-20 (Daniel voice, 9:16, face thumbnail) and still flopped at 0.57% share rate. The winning lever is the literal phrase "They don't teach this in church. Read [Chapter] slowly." Voice/aspect/thumbnail are table stakes.
- **Cite chapter, not verse.** "Read Deuteronomy 28" is share-bait; "Read Deuteronomy 28:68" feels like a homework assignment and kills the share instinct.
- **Duration hard cap 55s.** Past 60s TikTok disables Duet/Stitch. Clone #2 at 1:13 proves the cost.
- **Don't use IIFEs with browser skill's evaluate.** The pilot already wraps your script in an arrow function; an inner IIFE becomes `() => { (()=>{...})() }` whose outer function doesn't return. Use a bare `return` at the end of a multi-statement script.

## Open threads / next session starts here
- **Script 3 (Smallest Nation) is not yet shipped.** The replication queue's priority-3 hook is now compliant: "They don't teach this in church. Read Deuteronomy 7 slowly. ☦️". Before posting: verify duration ≤55s, Daniel voice, 9:16, face-forward Scene 1 thumbnail. Do not deviate from the HARD RULES in [docs/viral-formula-deuteronomy-28.md](../../../../Users/Claude/youtubeoptermizer/docs/viral-formula-deuteronomy-28.md).
- **Clone #1 + Clone #2 cleanup decision is still open.** Both are dead on TikTok. User hasn't decided whether to delete. ⚠ The [YPP suspension memory](project_ypp_suspension_2026.md) says "do NOT delete videos until appeal resolves 2026-04-30" — that's YouTube-specific but flag the question explicitly before any TikTok delete.
- **Seed is cooling.** 2,700 → 3,999 views in ~48h (+1,300/day), won't hit the 20K–100K day-7 projection. Decision needed on whether to pin a fresh viral-formula-compliant clone to reactivate the algorithm push, or accept the cool-down.
- **Browser skill SKILL.md edit is not pushed anywhere.** The file lives in `~/.claude/skills/browser/SKILL.md`, which isn't in this repo. If the user wants it synced across machines, we need to find what git repo tracks `~/.claude/` (if any) or copy manually.
- **Untracked scratch files** — `scripts/tiktok-dashboard-check.json`, `scripts/tiktok-prod-authorize-check.json`, `scripts/tiktok-prod-consent-check.json`, `scripts/tiktok-rename-app.json` — pre-existing TikTok approval probes from an earlier session. Still safe to delete or leave.

## Uncommitted work
```
On branch main
Your branch is up to date with 'origin/main'.
Untracked files:
  scripts/tiktok-dashboard-check.json
  scripts/tiktok-prod-authorize-check.json
  scripts/tiktok-prod-consent-check.json
  scripts/tiktok-rename-app.json
```
No modified tracked files. Session work landed in commits `1e660e7` and `371963d`, both pushed to origin/main.
