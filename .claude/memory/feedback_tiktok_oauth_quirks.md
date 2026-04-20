---
name: TikTok OAuth quirks
description: TikTok rejects localhost redirect URIs and requires Sandbox mode before app review — use public callback forwarder + sandbox creds
type: feedback
originSessionId: 3f97120f-9e3e-4e35-89e8-cf5aa8126068
---
TikTok OAuth integration has two non-obvious gotchas that will waste an hour if you hit them blind.

**Why:** Burned ~90 min on 2026-04-18 fighting both issues (localhost rejection + client_key error from unreviewed production app). Documented so we never lose that time again.

**How to apply:** Whenever building a NEW TikTok integration or re-adding Content Posting API to another account:

1. **Never use `localhost` in the TikTok redirect URI field.** TikTok's Dev Portal hard-rejects it with "Enter a valid URL beginning with https://". Instead, host a public forwarder page (see `callback.html` in the aibiblegospels-legal GH Pages repo) that captures `?code=...` and redirects via JS to `https://localhost:9876/callback?code=...`. Meta/Instagram allow localhost — TikTok does not.

2. **Production credentials don't work for OAuth until the app is reviewed.** Trying OAuth with unreviewed production `client_key` returns a cryptic `client_key` error with no useful detail. Fix: create a Sandbox (top-right toggle on the app page), Clone from Production (copies products/scopes/redirect), add the TikTok username as a Target User, then use the Sandbox `client_key` + `client_secret` in .env. Sandbox OAuth works immediately for target users.

3. **TikTok won't let you save the app config without a demo video first.** Upload any placeholder mp4 to unblock "Save" — swap in the real demo later before hitting "Submit for review."

4. **`video.publish` scope is NOT in the default Content Posting API scope list** — only `video.upload` (drafts/inbox mode). `video.publish` (direct post to feed) requires additional approval and should not be requested on first submission.
