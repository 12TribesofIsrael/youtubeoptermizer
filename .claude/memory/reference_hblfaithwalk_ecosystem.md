---
name: hblfaithwalk parent workspace
description: Pointer to the parent workspace at C:\Users\Claude\hblfaithwalk with 5 sibling repos that own different layers of the AI Bible Gospels / Faith Walk Live ecosystem
type: reference
originSessionId: 544395dd-f971-4ead-9d62-b4c156bdab92
---
`C:\Users\Claude\hblfaithwalk` is the parent workspace for the AI Bible Gospels / Faith Walk Live ecosystem. **READ-ONLY from youtubeoptermizer** — separate Claude instances own each subrepo.

## Subrepos and what each owns

| Path | Owns |
|---|---|
| `AIconsultantforHmblzayy/` | The walk tracker (`src/faith-walk-tracker/checkpoints.json` is source-of-truth), Twitch clipper/chatbot/Discord scraper, X daily poster (`scripts/x-daily-post.js`), HARO press lane, distribution playbooks (TT Stitch / first-comment camp / IG Story sticker), comment-camp on news cycles, Twitch GQL clip queries |
| `aibiblegospelscom/` | Parent brand site at aibiblegospels.com (Next.js) |
| `faithwalklivecom/` | Faith Walk Live site at faithwalklive.com (Next.js + Leaflet). Has `/updates/april-28-incident` page with NewsArticle JSON-LD + FAQPage + SpeakableSpecification + BreadcrumbList + EventPostponed schema. `npm run recovery:append` for daily updates. SEO infrastructure shipped (sitemap, robots, OG, JSON-LD WebSite + Event) |
| `faithwalkbook/` | Private book project (mirror via `npm run book:sync` from AIconsultantforHmblzayy) |
| `claude-memory-backup/` | Cross-machine memory backup |

## Key docs to cross-reference (READ-ONLY)

- `AIconsultantforHmblzayy/CLAUDE.md` — full version history + the consulting strategy
- `AIconsultantforHmblzayy/docs/aeo-youtube-description-spec.md` — the hand-off spec for THIS Claude instance (youtubeoptermizer); defines YT description AEO template + identity strings
- `AIconsultantforHmblzayy/docs/comment-camp-apr28.md` — news-cycle traffic capture playbook (Tier 1-5 surfaces, UTM scheme)
- `AIconsultantforHmblzayy/docs/bio-link-audit-apr28.md` — surface audit + ShuggC backchannel rule
- `AIconsultantforHmblzayy/docs/baseline-metrics-2026-04-28.md` — Day 30 review baseline (~2026-05-28)
- `AIconsultantforHmblzayy/docs/playbook-days-33-40.md` — active distribution playbook
- `AIconsultantforHmblzayy/docs/haro-playbook.md` + `docs/haro-response-template.md` — daily inbound press routine
- `faithwalklivecom/CLAUDE.md` — FWL site rules, voice/writing rules, "supporter-built not official" positioning
- `faithwalklivecom/docs/faith-tech-pivot-strategy.md` — the FWL thesis (positioning rules non-negotiable)
- `faithwalklivecom/docs/seo-strategy.md` — SEO checklist with Phase B Week 1 YT items that are MY lane

## Use this reference when

- User asks about FWL strategy, the walk, the news cycle, distribution
- Before recommending content/distribution work — check what the consulting repo already does (don't duplicate)
- For tracker state: read `AIconsultantforHmblzayy/src/faith-walk-tracker/checkpoints.json` directly
- For Twitch clip slugs: GQL query (Client-ID `kimne78kx3ncx6brgo4mv6wki5h1ko`) per the consulting repo's pattern
