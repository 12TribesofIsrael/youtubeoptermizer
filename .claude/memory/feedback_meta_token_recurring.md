---
name: Meta token expiration is a recurring blocker
description: META_ACCESS_TOKEN has expired 5-6 times, blocking Instagram API work each time. Need a permanent fix — not just regenerating tokens.
type: feedback
originSessionId: f5cc844a-0b61-43d2-89c8-868b870f69c0
---
Meta access token keeps expiring and blocking all Instagram API work. User has regenerated the token ~6 times now and is frustrated.

**Why:** Short-lived tokens expire in 1-2 hours, long-lived tokens in 60 days. Each time it expires, all Instagram API calls fail silently, App Review test calls don't register, and work stalls until the user manually regenerates in Graph API Explorer.

**How to apply:** Next time this comes up, do NOT just tell the user to regenerate the token. Instead:
1. Build an automated token refresh flow (exchange short-lived → long-lived, and auto-refresh before expiry)
2. Investigate if there's a way to get a non-expiring Page Token (Page tokens derived from long-lived user tokens don't expire)
3. Also: user has TWO apps both named "AI Bible Gospels" — the Dev one (1505156764454804) and Live one (1452257036358754). Must always use the Live one. Dev app was renamed to "AI Bible Gospels (Dev)" on 2026-04-12.
