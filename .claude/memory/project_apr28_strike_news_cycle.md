---
name: Apr 28 strike + 11-outlet news cycle
description: Day 34 vehicle strike on US-40 (Lewisville IN) generated an 11-outlet news cycle that's a permanent traffic asset for faithwalklive.com — none of the outlets link to the site, creating an outreach opportunity
type: project
originSessionId: 544395dd-f971-4ead-9d62-b4c156bdab92
---
**Date:** 2026-04-28 (Day 34 of the walk).
**Event:** Zay struck by a vehicle on US-40 between Richmond, IN → Lewisville, IN. Hospitalized, recovered, resumed walking 2026-05-03 (Day 39 from Greenfield, IN, 732 mi). Walk **never formally paused** in checkpoints (`paused: false` everywhere) — 5 days of `restOnly: true` between Day 34 and Day 39.

## The 11 outlets that covered it

| Tier | Outlet | Article URL |
|---|---|---|
| 1 | The Shade Room IG | https://www.instagram.com/p/DXsREFagUhr/ |
| 1 | TMZ TikTok | (URL not yet captured) |
| 2 | Fox 29 Philadelphia | https://www.fox29.com/news/twitch-streamer-minister-zay-hit-car-during-faith-walk-from-philadelphia-california |
| 2 | Fox 59 Indianapolis | https://fox59.com/news/indynews/streamer-hit-by-car-in-indiana-while-walking-across-country-to-raise-money-for-children/ |
| 2 | Fox 5 New York | (same wire story, fox5ny.com) |
| 2 | Fox 5 Atlanta | (same wire story, fox5atlanta.com) |
| 2 | KTVU Fox 2 (SF Bay) | (same wire story, ktvu.com) |
| 2 | Fox 32 Chicago | (same wire story, fox32chicago.com) |
| 2 | Fox 35 Orlando | (same wire story, fox35orlando.com) |
| 3 | Daily Voice (PA) | https://dailyvoice.com/pa/stewartstown-fawn-grove/twitch-streamer-hit-by-car-in-ohio-during-livestream-of-cross-country-walk-from-philly-to-cali/ |
| 3 | Express Tribune | https://tribune.com.pk/story/2605410/what-happened-to-hmblzayy-twitch-streamer-hit-during-3000-mile-faith-walk-in-indiana-crash |
| - | Lokmat Times | (Indian aggregator, low-priority) |

## What's been built around this

- `faithwalklivecom`: `/updates/april-28-incident` page with NewsArticle + FAQPage + SpeakableSpecification + BreadcrumbList JSON-LD; `/updates` index; `EventPostponed` schema in root layout when `isPaused`; dynamic sitemap with `lastModified` from recovery entries; llms.txt rewritten to route AI engines to the incident page
- `AIconsultantforHmblzayy`: daily `npm run recovery:append` keeps the page's `dateModified` fresh; `docs/comment-camp-apr28.md` (11-surface playbook); `docs/bio-link-audit-apr28.md`; `docs/roi-news-capture-apr28.md`; `docs/faithwalklive-utm-log.csv` with 16 apr28-campaign rows
- `youtubeoptermizer`: `docs/journalist-outreach-apr28-followup.md` (commit `9e3aeb9`) — cold email outreach playbook to earn news-domain backlinks from the 11 outlets

## Why it matters

**The 11 articles are indexed and getting search traffic right now from people Googling Zay** — but none of them link to faithwalklive.com. A single news-domain backlink from Fox 29 Philly or Fox 59 Indy outweighs weeks of social-surface AEO work for entity-resolution and SEO authority. This is a permanent asset (the articles will keep ranking for months).

## How to apply

- Don't try to redo the comment-camp (24-36h signal half-life — closed by 2026-04-30)
- DO ship journalist follow-up outreach using the "back walking May 3" beat (window closes ~2026-05-10)
- Reddit r/Twitch update post is still recoverable (longer signal life)
- Use the article URLs above as canonical citations in any future content (e.g. AEO Phase B descriptions for walk-related videos can cite `Fox 29 reported on April 28...`)
- Day 30 review of news-pivot impact = ~2026-05-28 per `baseline-metrics-2026-04-28.md`
