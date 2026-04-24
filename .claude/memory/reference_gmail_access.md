---
name: Gmail API access wired for aibiblegospels444@gmail.com
description: Gmail Data API is authenticated for aibiblegospels444@gmail.com; token + registry live in C:/Users/Owner/.claude/skills/gmail-inbox/; use the /gmail-inbox skill or call gmail_unified.py directly to read/label/search inbox
type: reference
originSessionId: 23f60aef-a5cf-4bb6-b791-d4575ab1ee73
---
**Gmail is wired and working for `aibiblegospels444@gmail.com` as of 2026-04-24.**

**Files:**
- Credentials: `C:/Users/Owner/.claude/skills/gmail-inbox/credentials.json` (OAuth installed-app client, GCP project `youtube-optimizer-490415` / number `596363097778`)
- Token: `C:/Users/Owner/.claude/skills/gmail-inbox/token_aibiblegospels444.json` (gmail.modify + gmail.labels + gmail.settings.basic + spreadsheets + drive scopes; auto-refreshes via refresh_token)
- Registry: `C:/Users/Owner/.claude/skills/gmail-inbox/gmail_accounts.json` (single entry: `aibiblegospels444`)
- Helper scripts (custom, written 2026-04-24): `fetch_relevant.py` (TikTok/YouTube body extractor), `fetch_tiktok_html.py` (HTML→text)

**How to use:**
- Preferred: invoke the `/gmail-inbox` skill — it knows the registry pattern.
- Direct CLI from the skill dir:
  ```
  cd C:/Users/Owner/.claude/skills/gmail-inbox
  PYTHONIOENCODING=utf-8 python scripts/gmail_unified.py --query "newer_than:7d" --account aibiblegospels444
  ```
- ⚠ Always set `PYTHONIOENCODING=utf-8` — the script's print loop crashes on emoji subjects under Windows cp1252.

**Gotchas:**
- Gmail API must stay enabled on GCP project `youtube-optimizer-490415`. If it gets disabled, calls fail with `accessNotConfigured 403`. Re-enable at https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=596363097778
- The credentials.json was originally for YouTube API auth (token.json in `repos/youtubeoptermizer/` is YouTube-only). The Gmail token uses the same OAuth client but different scopes.
- Do NOT commit `token_*.json` or `gmail_accounts.json` to any public repo — the skill dir is private (in `~/.claude/skills/`) so it's safe by default.

**Quick search query templates:**
- Last 14d from a vendor: `newer_than:14d from:noreply@dev.tiktok.com`
- App-review responses: `(from:facebookmail.com OR from:meta.com OR from:noreply@dev.tiktok.com OR from:yt-partner-support@google.com) newer_than:14d`
- All unread: `is:unread newer_than:7d`
