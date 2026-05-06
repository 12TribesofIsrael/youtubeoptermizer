---
name: Browser skill is a valid bypass for API App Review pain
description: When API access is gated behind painful App Review (TikTok analytics) and a working web dashboard exists, browser-skill scraping is a legitimate bridge — don't reflexively pursue API approval
type: feedback
originSessionId: 645b20fa-14d1-4900-82dc-30c1ba3a1d8e
---
When a piece of data lives behind a painful App Review process AND that data is freely viewable in a web dashboard, **propose browser-skill (Playwright) scraping as the bridge solution** before defaulting to "let's submit for API access."

**Why:** Decided 2026-05-06 for TikTok analytics. The Display API path (`video.list` + `user.info.stats` scopes) would mean another 2-4 week round of TikTok App Review after the 5-submission slog we just finished for `video.upload`. tiktok.com/tiktokstudio/analytics shows the same data for free. Tommy explicitly chose Option A (browser scrape) over Option B (API approval). Pragmatism wins when the manual route is automatable.

**How to apply:**
- When user wants metrics/data and asks "can we get this via API," check first whether (a) a web dashboard exposes it, and (b) the API path requires App Review. If both yes, lead with browser-skill scraping as the bridge.
- Tradeoffs to surface: scraper breaks if the platform redesigns the dashboard; runs on a schedule (weekly typical) instead of on-demand; needs a one-time login or persistent session cookie.
- Use cases this fits well: TikTok analytics, IG Insights (already burned by `instagram_business_manage_insights` review for limited metrics), Twitter/X analytics (free tier blocks API).
- Don't apply to write operations (posting, editing, deleting) — those need the real API and proper authentication.
- Don't apply when the API is easy to get (e.g. YouTube Data API — already approved, no scope-add needed).

The heuristic: **API approval is a means, not an end. If browser scraping delivers the data with less calendar time, do that.**
