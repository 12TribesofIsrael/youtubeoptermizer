---
name: Don't duplicate AIconsultantforHmblzayy work
description: youtubeoptermizer's lane is YT/IG/FB AEO + measurement; the sibling consulting repo already owns walk distribution, Twitch, X poster, HARO press, news-cycle response — recommending those is duplicate work
type: feedback
originSessionId: 544395dd-f971-4ead-9d62-b4c156bdab92
---
When discussing AI Bible Gospels / Faith Walk Live strategy, **do not recommend** any of these — they are owned by `../hblfaithwalk/AIconsultantforHmblzayy/` and either already shipped or actively running:

- Daily walk-themed content series (TT Stitch playbook on Zay's 2M-view post + first-comment camp + IG Story sticker — `docs/playbook-days-33-40.md`)
- Press pitches / inbound press (HARO/Qwoted daily routine — `docs/haro-playbook.md`)
- News-cycle response / comment-camp (`docs/comment-camp-apr28.md` — 11-outlet sweep + UTM scheme)
- X (Twitter) daily posts (`scripts/x-daily-post.js` — Premium + free-tier thread mode, idempotent log)
- Walk tracker / checkpoints / clip backfill / Twitch GQL queries (`src/faith-walk-tracker/` + `scripts/`)
- News-event JSON-LD on faithwalklive.com (`/updates/april-28-incident` — NewsArticle + FAQPage + SpeakableSpecification + BreadcrumbList shipped)
- Daily recovery appends (`npm run recovery:append` keeps `dateModified` fresh)
- RV route planning, Twitch chatbot, Discord scraper

**Why:** I burned ~6 turns on 2026-05-06 recommending things that were already done. User had to point me to the parent workspace. See `reference_hblfaithwalk_ecosystem.md` for the full topology.

**How to apply:** When the user asks about FWL strategy or "what should we do next," **first** check what the consulting repo already covers before recommending. The youtubeoptermizer lane is:

- YT description AEO (Phase A done, Phase B pending)
- IG bulk pinned comments (1A) + FB caption rewrite (1B) — autopilot
- YT-specific items in `faithwalklivecom/docs/seo-strategy.md` Phase B Week 1: end screens, channel banner clickable URL, pinned comments on top 3 videos
- Cross-platform measurement (`unified-analytics.py` script #5 — Vercel + YT + IG + FB + X attribution rollup, still missing)
- Channel cleanup / kill list / playlists / thumbnails / bulk metadata
- Anything that needs the YouTube Data API v3 token in this repo

Anything else: read the consulting repo's docs first, defer to that instance.
