---
name: Meta token expiration is a recurring blocker
description: META_ACCESS_TOKEN has expired 5-6 times, blocking Instagram API work each time. Need a permanent fix — not just regenerating tokens.
type: feedback
originSessionId: f5cc844a-0b61-43d2-89c8-868b870f69c0
---
Meta access token keeps expiring and blocking all Instagram API work. User has regenerated the token ~6 times now and is frustrated.

**Why:** Short-lived tokens expire in 1-2 hours, long-lived tokens in 60 days. Each time it expires, all Instagram API calls fail silently, App Review test calls don't register, and work stalls until the user manually regenerates in Graph API Explorer.

**How to apply:** Next time this comes up, do NOT just tell the user to regenerate the token. Instead:
1. Have them regen the short-lived user token in Graph API Explorer (Live app 1452257036358754, 6 IG scopes)
2. Run `python scripts/meta-token-refresh.py` — exchanges short-lived → long-lived (60d) user token AND derives a Page token, writes both to .env as META_ACCESS_TOKEN and META_PAGE_TOKEN
3. Caveat: Page tokens are NOT truly non-expiring when the Page is under Business Manager — Meta caps them at user-token lifetime (~59d). So user still needs to regen every ~50d. A non-expiring Page token only works for personal (non-BM) Pages.
4. Also: user has TWO apps both named "AI Bible Gospels" — Dev (1505156764454804) and Live (1452257036358754). Must always use the Live one. Dev was renamed "AI Bible Gospels (Dev)" on 2026-04-12.
