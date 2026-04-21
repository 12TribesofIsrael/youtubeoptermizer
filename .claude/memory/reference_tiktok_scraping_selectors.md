---
name: TikTok public-page scraping selectors
description: DOM selectors for scraping TikTok video metrics via the browser skill — likes/shares/saves/comments are on the watch page, but views are only on the profile grid
type: reference
originSessionId: 5618946d-736d-4ccd-ab23-199943513a3f
---
# TikTok scraping via browser skill

Selectors and quirks for pulling public metrics from `tiktok.com/@<user>/video/<id>` and `tiktok.com/@<user>` profile pages using the `browser` skill's `evaluate` action.

## Engagement counters (on watch page)

The video watch page exposes four `data-e2e` attributes on `<strong>` elements in the right-side action rail:

| Metric | Selector |
|---|---|
| Likes | `[data-e2e="like-count"]` |
| Comments | `[data-e2e="comment-count"]` |
| Shares | `[data-e2e="share-count"]` |
| **Saves/bookmarks** | `[data-e2e="undefined-count"]` ← TikTok's own bug; they never renamed this |

**Watch out:** the "up next" video in the right carousel ALSO renders `like-count`/`share-count`/etc. strong elements, so `document.querySelectorAll('[data-e2e="like-count"]')` returns TWO matches. Use `document.querySelector(...)` (first match = current video).

## View count (NOT on watch page — profile grid only)

The public watch page at `tiktok.com/@user/video/<id>` does **not** render the view count anywhere. To get views, navigate to the profile page `tiktok.com/@user` and read the `<strong>` element inside each video thumbnail's container.

Pattern that worked (2026-04-21):
```js
const videos = Array.from(document.querySelectorAll('a[href*="/video/"]'));
const out = [];
for (const a of videos) {
  const m = a.href.match(/\/video\/(\d+)/);
  if (!m) continue;
  const container = a.closest('div[data-e2e]') || a.closest('div');
  const views = container?.querySelector('strong')?.textContent?.trim() || null;
  out.push({id: m[1], views});
}
const target = ['<id1>', '<id2>', ...];
return JSON.stringify(out.filter(v => target.includes(v.id)), null, 2);
```

Each video ID appears multiple times in the DOM (reposted-by notifications, sidebar, grid). Filter for the entry where `views` is non-null — that's the grid tile.

## Age / posted date

Not reliably exposed in public DOM. TikTok ID format is a Snowflake — extract timestamp from the first 32 bits if precision matters, otherwise infer from the "Pinned" badge or rely on the post log in [docs/viral-formula-deuteronomy-28.md](../../../../repos/youtubeoptermizer/docs/viral-formula-deuteronomy-28.md).

## Action sequence template

```json
[
  {"action": "goto", "url": "https://www.tiktok.com/@aibiblegospels_/video/<ID>"},
  {"action": "wait", "seconds": 6},
  {"action": "evaluate", "script": "const pick = (s) => document.querySelector(s)?.textContent?.trim() || null; return JSON.stringify({like: pick('[data-e2e=\"like-count\"]'), comment: pick('[data-e2e=\"comment-count\"]'), share: pick('[data-e2e=\"share-count\"]'), save: pick('[data-e2e=\"undefined-count\"]')}, null, 2);"}
]
```

Run with: `python ~/.claude/skills/browser/scripts/browser_pilot.py <actions.json>`

Public pages do not require login. The browser skill's persistent profile (`~/.meta-playwright-profile/`) will use whatever login state exists, but scraping public counters works either way.
