---
name: API capability reference docs
description: docs/meta-app-capabilities.md and docs/youtube-app-capabilities.md are the canonical source of truth for what each app can/cannot do
type: reference
originSessionId: 5eb7f750-854c-4407-bd99-d48e87fa9b29
---
Two reference docs in the repo capture exactly what scopes are granted, what each app CAN and CANNOT do, the App Review tier, and how to add new scopes:

- **`docs/meta-app-capabilities.md`** — Meta App `1452257036358754` (AI Bible Gospels). Covers all 10 granted scopes (5 IG Business + 4 FB Page + `public_profile`), what's blocked + why + how to unblock, App Review tier matrix, scope-add workflow.

- **`docs/youtube-app-capabilities.md`** — Google Cloud project `youtube-optimizer-490415`. Covers the 3 YouTube OAuth scopes, daily quota math (10K units/day → ~200 video edits or 6 uploads), auth flow, gotchas, scripts that consume the auth.

**When to read:** Before building any new IG/FB/YT script — check whether the required scope is granted. Before quoting "the API can do X" to the user — verify against the doc. Before submitting an App Review — check the tier matrix.

**Keep them updated:** Whenever scopes are added/removed, App Review status changes, OAuth client is regenerated, or quota tier changes. They're the single authoritative answer to "what can our apps do" — drift makes them worse than nothing.
