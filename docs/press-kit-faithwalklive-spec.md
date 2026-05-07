# Press Kit Spec — faithwalklive.com/press

**Owner of this spec:** youtubeoptermizer (Tommy Lee / AI Bible Gospels)
**Owner of the implementation:** sibling Claude on `faithwalklivecom` repo (READ-ONLY from here)
**Created:** 2026-05-07
**Status:** Ready to ship — spec is complete; no further input needed from this side.

---

## Why this page exists

No public press kit exists for "the walk." The 11 outlets that covered the Apr 28 strike (TMZ, Shade Room, 7 Fox affiliates, Daily Voice, Express Tribune, Lokmat) all wrote their stories without source assets — so each one used a still from Twitch and zero outbound links to faithwalklive.com.

A clean press kit at `faithwalklive.com/press` does three things at once:

1. **Owns the topic queries** "minister zay press kit", "faith walk live press kit", "3000 mile walk press kit", "humble zay media kit" — uncontested, low-volume but high-intent.
2. **Gives the journalist outreach play (`docs/journalist-outreach-apr28-followup.md`) a single URL to drop into every email.** Currently those emails point at `faithwalklive.com/updates/april-28-incident` (recovery timeline). Adding `faithwalklive.com/press` makes the email twice as useful — recovery beat + ready-to-use assets.
3. **Lowers the friction for journalists writing the next story.** Bio, fast facts, photos, logo, contact — all in one place, all free to use, no permission gate. Journalists who don't have a press kit go to Wikipedia. Journalists who have one go to the press kit.

**The win condition is not "press kit drives traffic."** It's "next time an outlet writes about the walk, they link to faithwalklive.com because the assets came from there."

---

## Page URL + meta

- **URL:** `https://faithwalklive.com/press` (canonical, indexable)
- **Page title:** `Press Kit — Faith Walk Live`
- **Meta description (~155 chars):**
  `Press assets, fast facts, and contact for Faith Walk Live — the live-tracker app following Minister Humble Zay's 3,000-mile walk from Philadelphia to California.`
- **Open Graph image:** Same brand identity as `/updates/april-28-incident` (gold-on-black, golden particles). Title text: "PRESS KIT — FAITH WALK LIVE".
- **`robots`:** index, follow (this is the opposite of the typical "press" intranet — we WANT crawlers).
- **Sitemap:** add `/press` to `sitemap.xml`.
- **Internal links:** link from site footer ("Press") on every page; link from `/updates/april-28-incident` ("Press kit"); link from homepage hero CTA bar (small text link, not a primary CTA).

---

## Page structure (copy-ready)

The page should read top-to-bottom in the order below. Journalists scan; don't make them hunt.

### 1. Hero (above the fold)

**H1:** `Press Kit — Faith Walk Live`

**Subhead (1 sentence):**
> Faith Walk Live is the live-tracker app following Minister Humble Zay's 3,000-mile walk from Philadelphia to California — live mileage, current location, and stream embed in one place.

**Hero CTA bar (3 inline links):**
- 📥 Download all assets (ZIP) → `/press/faith-walk-live-press-kit.zip`
- 📧 Press contact → `mailto:aibiblegospels444@gmail.com?subject=Press%20inquiry%20—%20Faith%20Walk%20Live`
- 📰 Latest update → `/updates/april-28-incident`

### 2. Fast facts (the part journalists copy/paste)

A two-column table, 8 rows. Every fact is a single line. No paragraph blocks.

| Fact | Value |
|---|---|
| **Walk** | Philadelphia, PA → California (3,000 miles, on foot) |
| **Started** | March 26, 2026 |
| **Current status** | In progress — Day 42 (~752 miles) as of May 7, 2026 *[update via shortcode/CMS — do NOT hardcode]* |
| **Apr 28 incident** | Struck by a vehicle on US-40 near Lewisville, IN. Resumed walking May 3. [Recovery timeline →](/updates/april-28-incident) |
| **Walker** | Isaiah "Humble Zay" Thomas, minister from Philadelphia |
| **Cause** | Fundraising to build a school for at-risk youth in Philadelphia |
| **Live tracker** | [faithwalklive.com](/) — built by AI Bible Gospels, supporter-built |
| **Live stream** | [twitch.tv/hmblzayy](https://www.twitch.tv/hmblzayy) (broadcasting daily) |

> **Note for the implementing Claude:** Day count + mileage MUST be CMS-driven or pulled from `AIconsultantforHmblzayy/src/faith-walk-tracker/checkpoints.json` at build time. Do NOT hardcode or this page goes stale in a week. If a CMS hookup adds friction, ship a static version with a visible "*Last updated: [date]*" stamp and a `[Refresh →]` link to whoever maintains it. A stale fact is worse than a missing one.

### 3. Boilerplate (the part editors paste into "About" sections)

Three lengths. Editors pick one based on word budget. Mark each with a copy-to-clipboard button if the design system has one.

**Short (40 words):**
> Faith Walk Live is the live-tracker app for Minister Humble Zay's 3,000-mile walk from Philadelphia to California, raising funds to build a school for at-risk Philly youth. Built by AI Bible Gospels, a faith-tech project by Tommy Lee.

**Medium (80 words):**
> Faith Walk Live is the public live-tracker app following Minister Isaiah "Humble Zay" Thomas's 3,000-mile walk on foot from Philadelphia to California. The walk, which began March 26, 2026, is a fundraiser to build a school for at-risk youth in Philadelphia. Faith Walk Live shows real-time mileage, current location, and the daily Twitch broadcast in one place. The app was built by AI Bible Gospels, a faith-tech project by Tommy Lee, as a supporter-side tool — not affiliated with HMBL.

**Long (160 words):**
> Faith Walk Live is the public live-tracker app following Minister Isaiah "Humble Zay" Thomas's 3,000-mile walk on foot from Philadelphia, Pennsylvania to California. The walk, which began March 26, 2026, is a self-funded fundraising mission: every mile raises money toward building a school for at-risk youth in Philadelphia, with eventual expansion to Baltimore and Washington, D.C. Zay broadcasts every step live on Twitch (twitch.tv/hmblzayy). On April 28, 2026 — Day 34 of the walk — Zay was struck by a vehicle on US-40 near Lewisville, Indiana. He resumed walking on May 3 and reached Indianapolis the following day. Faith Walk Live (faithwalklive.com) was built by AI Bible Gospels — a faith-tech project by Tommy Lee — to make the walk supportable in real time without scrolling Twitch. The tracker shows live mileage, current location, daily updates, and an embedded stream. Faith Walk Live is supporter-built and is not affiliated with HMBL.

### 4. Bio: Minister Humble Zay (~120 words)

Important: **third-party bio**, written in third person, factually conservative. Don't editorialize.

> Isaiah "Humble Zay" Thomas is a minister from Philadelphia, Pennsylvania. On March 26, 2026, he set out on foot to walk approximately 3,000 miles from Philadelphia to California — broadcasting every step live on Twitch (`twitch.tv/hmblzayy`) — to raise funds to build a school for at-risk youth in Philadelphia. He has, in his own words, framed the mission as a response to a generation of kids who "end up in the system or end up dead."
>
> On April 28, 2026, Zay was struck by a vehicle on US-40 in Indiana. He resumed walking five days later. As of [DATE], he is mid-walk, approximately [MILES] miles from Philadelphia.
>
> Zay's own platforms: Twitch [hmblzayy](https://www.twitch.tv/hmblzayy).

### 5. Bio: AI Bible Gospels / Tommy Lee (~100 words)

> AI Bible Gospels is a faith-tech project founded by Tommy Lee, building software in service of ministers, missionaries, and faith-driven creators — including live trackers, stream automation, ministry websites, and prayer walls. Faith Walk Live (`faithwalklive.com`) is its flagship app: a real-time tracker for Minister Humble Zay's 3,000-mile walk. AI Bible Gospels also operates the YouTube channel [@AIBIBLEGOSPELS](https://www.youtube.com/@AIBIBLEGOSPELS), which uses AI to narrate Scripture from a culturally underrepresented perspective. AI Bible Gospels built and maintains Faith Walk Live as a supporter-side tool. AI Bible Gospels is not affiliated with HMBL.

### 6. Downloadable assets

A grid of asset cards. Each card: thumbnail, label, file size, format, download link. All assets must be:
- Cleared for editorial use without further permission (state this explicitly under each).
- Hosted at stable URLs (`/press/assets/...`) that don't break across deploys.
- Available in **multiple sizes** where relevant (1080p + 4K for video; web + print resolution for stills).

**Required assets:**

| Asset | File | Format / size |
|---|---|---|
| Faith Walk Live logo (gold on black) | `faith-walk-live-logo-gold.png` | PNG, 2048x2048 transparent |
| Faith Walk Live logo (black on gold) | `faith-walk-live-logo-black.png` | PNG, 2048x2048 transparent |
| AI Bible Gospels brand mark | `aibiblegospels-mark.png` | PNG, 2048x2048 transparent |
| Hero photo — Zay walking (golden hour) | `zay-walking-hero.jpg` | JPG, 4000px wide, 300dpi |
| Portrait photo — Zay close-up | `zay-portrait.jpg` | JPG, 4000px wide, 300dpi |
| Community photo — auntie/Indiana support | `zay-community-indiana.jpg` | JPG, 4000px wide, 300dpi |
| Map — full route (Philly → California) | `route-map.png` | PNG, 2048x1152 |
| Map — current location (auto-updates) | `route-map-current.png` | PNG, 2048x1152 — generated from checkpoints.json |
| Stat card — fast facts visual | `fast-facts-card.png` | PNG, 1920x1080 (square + vertical variants) |
| B-roll reel | `faith-walk-live-broll-1080p.mp4` | MP4, 1080p, 60-90 sec, no music |
| Press release ZIP (everything above) | `faith-walk-live-press-kit.zip` | ZIP, ~50-100MB |

**Photo sourcing:** stills can be pulled from the existing Twitch clips library (see `youtubeoptermizer/faith-walk-live/anchor-doc/clips/` — those are pre-validated as compelling moments) and from the IG reel at `zay-monologue/`. Get explicit permission from Zay before publishing his portrait at full res — assume this is yes since he livestreams everything, but confirm.

**Caption rule under each photo:**
> Credit: AI Bible Gospels / Faith Walk Live. Cleared for editorial use. Please attribute as "Photo: faithwalklive.com" or "Photo: AI Bible Gospels".

### 7. Recent coverage (auto-updating list)

Reverse-chronological list of every outlet that has covered the walk. Initial seed list from Apr 28 incident:

- TMZ — [link]
- The Shade Room — [link]
- Fox 59 Indianapolis — [link]
- Fox 29 Philadelphia — [link]
- Fox 5 New York — [link]
- Fox 5 Atlanta — [link]
- KTVU (SF Bay) — [link]
- Fox 32 Chicago — [link]
- Fox 35 Orlando — [link]
- Daily Voice (PA) — [link]
- Express Tribune (PK) — [link]
- Lokmat Times (IN) — [link]

> **Implementation note:** make this CMS-managed. Every time a new outlet covers the walk, add a row. Journalists check who else has covered the story before pitching their editor — being on this list lowers the barrier for the next outlet.

### 8. Press contact

**One contact, one inbox, one expected response time.**

- **Name:** Tommy Lee
- **Role:** Founder, AI Bible Gospels / Builder, Faith Walk Live
- **Email:** [aibiblegospels444@gmail.com](mailto:aibiblegospels444@gmail.com?subject=Press%20inquiry%20—%20Faith%20Walk%20Live)
- **Response time:** Within 24 hours, weekdays.
- **Time zone:** Eastern (US).
- **For interviews with Minister Zay directly:** route through this same inbox; we'll coordinate.

### 9. What we're NOT

A short, plainspoken footer that pre-empts the most common journalistic confusion. **This section is non-negotiable** — every news outlet so far has either been unclear on or wrong about the relationship.

> **Faith Walk Live is supporter-built.** It is not owned, operated, or sponsored by Minister Humble Zay or HMBL. We built the tracker because the walk deserved one. All photos and copy on this page are cleared for editorial use; please credit "AI Bible Gospels / faithwalklive.com" or "Photo: faithwalklive.com." For Zay's own statements, route through his Twitch channel ([twitch.tv/hmblzayy](https://www.twitch.tv/hmblzayy)) or this press contact.

---

## Schema.org / structured data

Add `Organization` + `WebPage` JSON-LD blocks. Same pattern as `/updates/april-28-incident` (which uses `NewsArticle`).

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "Press Kit — Faith Walk Live",
  "description": "Press assets, fast facts, and contact for Faith Walk Live — the live-tracker app following Minister Humble Zay's 3,000-mile walk from Philadelphia to California.",
  "url": "https://faithwalklive.com/press",
  "publisher": {
    "@type": "Organization",
    "name": "AI Bible Gospels",
    "url": "https://aibiblegospels.com",
    "logo": {
      "@type": "ImageObject",
      "url": "https://faithwalklive.com/press/assets/aibiblegospels-mark.png"
    },
    "sameAs": [
      "https://www.youtube.com/@AIBIBLEGOSPELS",
      "https://x.com/aibiblegospels",
      "https://aibiblegospels.com",
      "https://t.me/aibiblegospels"
    ]
  },
  "about": {
    "@type": "Event",
    "name": "Faith Walk Live — 3,000-mile walk from Philadelphia to California",
    "startDate": "2026-03-26",
    "location": {
      "@type": "Place",
      "name": "Philadelphia, PA → California (on foot)"
    },
    "organizer": {
      "@type": "Person",
      "name": "Isaiah \"Humble Zay\" Thomas",
      "sameAs": "https://www.twitch.tv/hmblzayy"
    }
  }
}
```

---

## SEO targets

Pages that should rank for these queries within 30 days of ship (per the existing `seo-strategy.md` Phase B):

| Query | Intent | Expected position |
|---|---|---|
| `faith walk live press kit` | brand-direct | #1 |
| `minister zay press kit` | brand-direct | #1 |
| `humble zay media kit` | brand-direct | #1 |
| `humble zay bio` | brand-direct | #1-3 |
| `3000 mile walk press kit` | topic | #1-3 |
| `philly to california walk press` | topic | #1-3 |
| `faith walk live photos` | asset | #1-5 |
| `faith walk live logo` | asset | #1-5 |

These are all uncontested today. The window to own them is now.

---

## Cross-references (existing assets to link from this page)

- `/updates/april-28-incident` — recovery timeline (already shipped per `seo-strategy.md`)
- `/` (homepage tracker) — main funnel destination
- AI Bible Gospels YouTube → embed the upcoming anchor doc once published (`youtubeoptermizer/faith-walk-live/anchor-doc/`)
- Telegram channel → `t.me/aibiblegospels` (per `reference_telegram_channel.md`)

---

## Hand-off checklist (for sibling Claude on faithwalklivecom)

When the implementing Claude picks this up:

- [ ] Page lives at `https://faithwalklive.com/press`, returns 200, indexable
- [ ] Day count + mileage are dynamic (CMS or build-time pull from `checkpoints.json`)
- [ ] All asset URLs in §6 resolve; ZIP is generated at build time from the source assets
- [ ] OG image renders correctly when sharing the page on X/FB/iMessage
- [ ] Schema.org JSON-LD validates ([validator](https://validator.schema.org/))
- [ ] Footer link "Press" added to every page on the site
- [ ] `/updates/april-28-incident` cross-links to `/press`
- [ ] Sitemap updated, submitted to Search Console
- [ ] Once live: notify youtubeoptermizer Claude so the journalist outreach doc + YouTube publish plan can swap their placeholder references for the live URL

---

## Cross-doc updates required (after page goes live)

When `https://faithwalklive.com/press` is live, update these docs in `youtubeoptermizer`:

1. `docs/journalist-outreach-apr28-followup.md` master template — add a line:
   `Full press kit + assets: faithwalklive.com/press`
2. `faith-walk-live/anchor-doc/publish-plan.md` — flip the "Open item" note (already marked "verify live before upload") to "✅ live, link is hot."
3. `MEMORY.md` (auto-memory) — add a one-liner reference memory: *"faithwalklive.com/press is the canonical press kit URL — link from journalist outreach + YT descriptions."*

These are tracked here so this side knows what to do once sibling Claude reports back.
