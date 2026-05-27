# AI Bible Gospels — Master Status Doc
**Last Updated:** May 27, 2026
**Channel:** @AIBIBLEGOSPELS

---

## YPP (Monetization)

- **SUSPENDED** — both appeals rejected (Apr 15 + Apr 23), reason: "inauthentic content"
- **Reapply date: July 8, 2026** (~6 weeks out)
- Catalog cleanup and AEO work is allowed during the wait — old "do not edit" rules retired post-denial

---

## YouTube Channel Work

| Phase | Status |
|---|---|
| Phase 1 — Cleanup (30 deleted, 154 titles cleaned) | ✅ Done |
| Phase 2 — Title optimization (84 Part titles, 50 em dash fixes) | ✅ Done |
| Phase 3 — Thumbnails (20 custom, brand guide applied) | ✅ Done |
| Phase 4A — Playlists (14/14), trailer, end screens, keywords | ✅ Done |
| AEO descriptions — all 213 videos, constants block on every video | ✅ Done Apr 26 |
| Phase 4B — Long-form content (4–6 animated explainers, 10–20 min) | 🔲 Not started |

---

## Platform API Status

| Platform | Status | Notes |
|---|---|---|
| YouTube API | 🟢 Live | OAuth recovered Apr 27 with fresh Desktop client |
| Instagram API | 🟢 Approved | App Review approved Apr 27; IG silently no-ops caption edits on existing posts — use pinned comments instead |
| Facebook API | 🟢 Live | FB Page token required for writes (User token rejected) |
| TikTok API | 🟢 Approved | Content Posting API live May 6 — drafts/inbox mode; re-OAuth required once on prod creds |
| Meta access token | 🔴 Recurring issue | Expires every ~60 days; has broken ~6 times; needs automated refresh |

---

## Video Production Pipeline

### Custom Script 2.0 (BUILT)
Verbatim-preserving Bible video pipeline — bypasses the AI scene generator.

```
drafts/X.txt
  → scripts/script-to-scenes.py   (verse → scenes JSON, injects identity stacks)
  → output/scenes/X.json
  → scripts/render-via-pipeline.py (Kling + ElevenLabs + JSON2Video)
  → MP4
```

- LoRA auto-loaded from `training/lora-config.json` (`aibgospels` trigger)
- Identity stacks (MELANATED_SUFFIX / EDOM_SUFFIX) inject on every scene
- Daniel voice: `onwK4e9ZLuTAKqWW03F9` (locked — proven viral)

### Local FFmpeg Assembler (PLANNED — NOT BUILT)
Replaces JSON2Video as the last-mile assembly step. ~$1–2/video savings + removes external dependency.

- Full spec: [`docs/local-ffmpeg-assembler.md`](local-ffmpeg-assembler.md)
- **Task zero: FFmpeg not on PATH** — install first
- Estimated build time: ~1 full day
- Key complexity: ASS karaoke needs Approach B (per-word `\1c` color overrides), not just `\k` clock advance

---

## TikTok / Social

| Item | Status |
|---|---|
| TT comment scraper | ✅ Built — `analytics/_tiktok-comments-actions-v4.json` |
| TT comment classifier | ✅ Built — `scripts/tt-comments-classify.py` (6 buckets × 5 reply templates) |
| TT comment reply queue | 🔲 4 of 6 levers remaining — `output/tt-comments-to-reply.md` (manual paste) |
| CTA overlay Remotion (3 variants) | ✅ Built — `src/cta-overlay/` — **not yet rendered** |
| TikTok bio → Telegram funnel | ✅ Live — bio sends to t.me/aibiblegospels |
| Telegram channel | ✅ Live — t.me/aibiblegospels |

---

## Community / Funnel

- **Funnel:** TikTok hook → Telegram (primary) → email (aibiblegospels.com) → YouTube
- **FB Group** is hub #2
- Skip Discord, X community, TT community features

---

## What To Do Next (Priority Order)

1. **Build the FFmpeg assembler** — single-day build, unblocks video production from JSON2Video. [`docs/local-ffmpeg-assembler.md`](local-ffmpeg-assembler.md) is the spec. Start: install FFmpeg.
2. **Render the CTA overlay** — `src/cta-overlay/` is built, 3 FOLLOW CTA variants at 1080×1920 ProRes 4444, drop into CapCut tail of any Short.
3. **TT comment replies** — 4 levers left in priority queue (manual paste, not auto-reply).
4. **Phase 4B long-form** — 4–6 animated explainer videos before July 8 YPP reapply. Watch time from long-form directly supports the appeal.
5. **Meta token rotation** — automate the 60-day refresh cycle so it stops breaking.

---

## Key Files Reference

| File | Purpose |
|---|---|
| `docs/status.md` | This file — master current state |
| `docs/project-plan.md` | Full original roadmap with phases (reference only — some phases now complete) |
| `docs/local-ffmpeg-assembler.md` | FFmpeg assembler spec (module layout, commands, risk list) |
| `docs/api-automation-plan.md` | 5-script blueprint for AEO+brand-awareness across IG/FB/YT/TT |
| `analytics/post-optimization/Table data.csv` | Per-video metrics (latest export) |
| `docs/changelog.md` | Every change with dates and measurement plan |
| `src/youtube/client.py` | YouTube API client |
| `scripts/script-to-scenes.py` | Custom Script 2.0 converter |
| `scripts/render-via-pipeline.py` | Custom Script 2.0 renderer |
| `src/cta-overlay/` | Remotion CTA overlay project |
| `output/tt-comments-to-reply.md` | TikTok comment reply priority queue |
