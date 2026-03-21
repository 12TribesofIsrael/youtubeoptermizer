# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a YouTube channel optimization workspace for **AI Bible Gospels** (@AIBIBLEGOSPELS) — a Bible content channel focused on the 12 Tribes of Israel, Hebrew Israelite identity, and biblical prophecy. The channel has ~5,876 subscribers and 764K total views as of the analysis date.

The goal is for Claude to act as a **YouTube optimization assistant**, helping with content strategy, metadata optimization, analytics interpretation, and channel growth.

## Key Files

| File | Purpose |
|------|---------|
| `goal.md` | Full channel strategy report: strengths, weaknesses, competitor analysis, 90-day plan, content to remove/fix |
| `research.md` | Technical guide on using Claude + YouTube Data API v3, MCP servers, OAuth setup, and automation architecture |
| `analytics/Table data.csv` | Per-video analytics: views, retention, CTR, watch time, impressions, subscribers gained |
| `analytics/Chart data.csv` | Year-over-year average view duration trends per video |
| `analytics/Totals.csv` | Annual average view duration totals |
| `analytics/audit-results.json` | Full audit data from initial channel scan |
| `docs/changelog.md` | Living document: every change made, with dates, reasons, and measurement plan |
| `docs/competitors.md` | Competitor profiles, tactics to steal, title formulas, content gaps |
| `docs/project-plan.md` | Full project roadmap with phases, timelines, and priorities |
| `src/youtube/client.py` | Python API client — list/update/delete videos, playlists, analytics |
| `src/youtube/auth.py` | OAuth 2.0 authentication and token management |
| `scripts/` | Automation scripts for audits, bulk updates, deletions |

## Channel Context

- **Niche**: Biblical identity, 12 Tribes prophecy, Black Hebrew Israelite history — this specificity is the channel's unfair advantage
- **Content mix**: Primarily Shorts (30–60 sec), a long-running "Prophecy Revealed" part series (80+ parts), and a few long-form videos
- **Top performer**: "12 Tribes origins" Short — 115K views, 70% retention, 4.52% CTR
- **Retention**: 66–79% on Shorts (elite, top 5% for niche) — do NOT suggest changes to hook/pacing formula
- **CTR**: 4.06% channel average (target: 6–10%)
- **Competitors**: BibleProject (5.3M), AI Bible Stories (1.1M), AI Bible Sagas (110K), AI Bible Music (8.6K), The Bible in Black (47.5K)

## Brand Identity (Locked March 17, 2026)

All visual assets must follow this style:
- **Colors**: Deep navy/black backgrounds, golden/amber light, warm bronze skin tones
- **Lighting**: Dramatic chiaroscuro — divine golden light breaking through darkness
- **Mood**: Cinematic, revelatory, powerful
- **Font**: Bold gold serif with subtle glow
- **Figures**: Dark/brown-skinned biblical characters, Hebrew Israelite representation
- **Elements**: Parting clouds, light beams, ancient scrolls, stone tablets
- Apply this to: thumbnails, banners, profile pics, video intros, any image generation prompts

### Character Depiction Rule (MANDATORY)
All Israelite characters, Christ/Yashua, prophets, kings, and biblical Hebrew figures MUST be depicted as **melanated Black/African American men and women**. This is non-negotiable for every visual prompt, thumbnail prompt, video generation prompt (Kling, Runway, Sora, DALL-E, Midjourney, etc.).

**ALWAYS include in every AI image/video prompt:**
- "dark-brown to deep-brown skinned man/woman"
- "melanated African American complexion"
- "wool-textured / coiled / tightly curled hair"
- "NO Caucasian, European, or light-skinned depictions"
- "NOT white, NOT pale, NOT light-skinned"

**Why:** AI video generators (Kling, etc.) default to Caucasian features for biblical figures. You MUST explicitly override this in every prompt by specifying dark-brown/melanated skin, wool hair texture, and explicitly stating no Caucasian or European features. Without these negative prompts, the AI will insert white-presenting figures.

## Optimization Progress

| Phase | Status |
|-------|--------|
| Phase 1: Channel Cleanup | ✅ Done (30 deleted, 154 titles cleaned) |
| Phase 2: Title Optimization | ✅ Done (84 Part titles renamed, 50 em dash fixes) |
| Phase 3: Thumbnails | ✅ Done (20 custom thumbnails, brand guide applied) |
| Phase 4A: Playlists + Trailer | ✅ Playlists done (14/14), trailer script ready |
| Phase 4B: Long-form Content | Next |

## Current Priorities

1. **Channel trailer** — script written, video in production
2. **Manual tasks** — channel keywords, description, end screens, subscribe watermark
3. **Posting cadence**: 1 solid Short/day beats flooding then silence
4. **Long-form gap**: Need 4–6 animated explainer videos (10–20 min) for evergreen search traffic and ad revenue
5. **Missing formats**: Community posts, sleep/ambient audio, standalone discovery videos

## GitHub Repository

https://github.com/12TribesofIsrael/youtubeoptermizer

## YouTube API Integration (from research.md)

- **YouTube Data API v3**: Supports metadata updates (50 quota units), thumbnail uploads (50), video uploads (1,600), playlist management — daily limit 10,000 units
- **Recommended MCP server**: `eat-pray-ai/yutu` (Go, Apache-2.0) — full read-write YouTube control via OAuth 2.0
- **Analytics API**: Real-time queries for impressions, CTR, retention, demographics, traffic sources
- **OAuth requirement**: Service accounts don't work — must use interactive OAuth 2.0 with human auth at least once
- **Cannot automate**: Community posts, end screens, monetization settings, channel name changes

## When Analyzing Analytics Data

- CSV columns include: Video ID, title, publish time, duration (seconds), avg view duration, avg % viewed, engaged views, stayed to watch %, impressions, impressions CTR, subscribers gained, watch time hours
- Duration is in seconds for Shorts, longer values indicate long-form content
- Average view duration format is `H:MM:SS`; percentages over 100% indicate replay/rewatch behavior on Shorts
- Revenue columns are all zeros (channel likely not yet monetized or data not exported)
