---
ended: 2026-04-20T20:00:00Z
project: youtubeoptermizer (AI Bible Gospels)
branch: main
originSessionId: 3f97120f-9e3e-4e35-89e8-cf5aa8126068
---
# Last Session — 2026-04-20

## What the user wanted
Execute the viral-formula replication plan: take the formula validated by the 2026-04-18 seed viral ("They don't teach this in church. Read [Scripture] slowly.") and ship 2-3 clones to ride the algorithmic momentum. Clone #1 had flopped — diagnose why, fix, ship Clone #2.

## What we did
- **Diagnosed Clone #1 flop** (14 likes / 4 shares / 0 comments at 18h vs seed's 447/361/31 at same age). Three structural issues:
  1. Voice mismatch — Modal pipeline defaulted to `NgBYGKDDq2Z8Hnhatgma` instead of the seed's Daniel voice
  2. Wrong aspect ratio — pipeline hardcoded `"full-hd"` (16:9 landscape) instead of `"instagram-story"` (9:16 vertical). Clone #1 uploaded to TikTok got pillar-boxed with black bars, ~33% screen coverage.
  3. Scene 1 thumbnail was scroll-on-table (no faces) — lost the scroll-stop signal.
- **Identified the Daniel voice ID** — `onwK4e9ZLuTAKqWW03F9` (Daniel - Steady Broadcaster). The Make.com seed template at `G:/My Drive/AI BIBLE GOSPELS/Make.com Master/Master Shorts/MasterCSV.json:1122` passes `"voice": "Daniel"` by name. JSON2Video exposes no GET-template API, so user confirmed the exact ID via their dashboard.
- **Attempted direct pipeline fix** — edited `ai-bible-gospels/workflows/custom-script/router.py:44`. **User stopped me**: the `ai-bible-gospels` repo has a separate Claude instance that owns it. The edit was reverted by that instance. New scope rule: from this session, `ai-bible-gospels` and other repos are read-only; only `youtubeoptermizer` accepts edits from here.
- **Produced [docs/aspect-ratios-reference.md](../../../../Users/Claude/youtubeoptermizer/docs/aspect-ratios-reference.md)** as a portable spec the other instance can consume via `git pull` (commit `c909ebf`).
- **Restructured Script 2** from 4 → 6 paragraphs for 1:1 scene mapping with Modal Claude's auto-split (commit `0ef47bc`).
- **Clone #2 shipped** — 1080×1920, Daniel voice (confirmed via ffprobe-equivalent MP4 header parse), face-forward thumbnail (melanated man on ship deck with chains), 1:13 duration. File at `clonevideos/he Tribe of Judah in North America.mp4`. Posted to https://www.tiktok.com/@aibiblegospels_/video/7630868334774390047.
- **Saved 3 durable memory records** — `feedback_repo_scope.md`, `reference_daniel_voice.md`, `reference_aspect_ratios.md`.

## Decisions worth remembering
- **Never edit `ai-bible-gospels/` from this session.** Separate Claude instance owns that repo. Cross-repo edits cause drift and were rejected. See `feedback_repo_scope.md`.
- **JSON2Video has NO public GET-template endpoint.** Template bodies are dashboard-only. Document voice/resolution settings externally if you need them cross-pipeline.
- **Modal Claude (custom-script endpoint) consistently paraphrases the hook and drops the CTA.** The 1-paragraph-per-scene pre-split helps but doesn't fully solve it — manual post-generation edits on Scene 1 narration and final-scene narration are mandatory. Lessons captured in [drafts/tiktok-scripts-batch-2026-04-19.md](../../../../Users/Claude/youtubeoptermizer/drafts/tiktok-scripts-batch-2026-04-19.md) "Lessons learned" section.
- **First-time "AI-generated content" label triggers TikTok review** which auto-sets privacy to "Only me" for minutes-to-hours. Don't manually override — wait for review to complete. See `feedback_tiktok_ai_label_review.md`.

## Open threads / next session starts here
- **Clone #2 day-1 metrics** — user is monitoring. At 7 min post-publish it was 0/0/0/0 (normal cold-start). Need paste of views/likes/shares/saves/comments at **30 min, 60 min, and 24 h** marks. Log each in the Updates section of [docs/viral-formula-deuteronomy-28.md](../../../../Users/Claude/youtubeoptermizer/docs/viral-formula-deuteronomy-28.md).
- **Script 3 (Smallest Nation) decision** — waits on Clone #2 day-1. If ≥5% share rate → ship Script 3 with same fixed pipeline. If flops again → deeper diagnosis (possibly account quality score damage from Clone #1's flop).
- **Clone #1 cleanup question** — consider deleting https://www.tiktok.com/@aibiblegospels_/video/7630560963900558622 (stuck at 14 likes after ~48h) to protect account quality score. User hasn't decided; flag next time.
- **Seed viral still growing** — +91 shares in last 24h as of 2026-04-20. Still in algorithmic push tier. Momentum preserved for Script 2-3 to piggyback on.
- **Duet/Stitch disabled on Clone #2** because duration is 1:13 (>60s threshold). For Script 3, target ≤60s to keep Duet/Stitch enabled as distribution amplifiers.
- **Untracked working-tree clutter** — `tmp_browser_actions.json`, `tmp_tiktok_compare.json`, `tmp_clone2_check.json`, `clonevideos/` (holds the 29.8MB Clone #2 MP4). Scratch files; safe to delete or leave.

## Uncommitted work
```
On branch main
Your branch is up to date with 'origin/main'.
Untracked files:
  .claude/
  clonevideos/
  tmp_browser_actions.json
  tmp_clone2_check.json
  tmp_tiktok_compare.json
```
No modified tracked files. All session work pushed through `0ef47bc`.
