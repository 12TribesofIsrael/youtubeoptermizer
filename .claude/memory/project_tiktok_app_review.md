---
name: TikTok App Review status
description: Third submission 2026-04-22 after 2 rejections; all 5 fixes applied (apex redirect, DNS verify, new demo, scope rewrite, URL update)
type: project
originSessionId: 3f97120f-9e3e-4e35-89e8-cf5aa8126068
---
TikTok Content Posting API app review — **3rd submission live 2026-04-22** after fixing all flagged issues from the 2nd rejection.

## Timeline

- **2026-04-18** — 1st submission as "Ai-Bible-Gospels"
- **2026-04-20 02:18 UTC** — 1st rejection: name mismatch (app "Ai-Bible-Gospels" vs website/legal "AI Bible Gospels")
- **2026-04-20** — renamed app to "AI Bible Gospels" (spaces), resubmitted
- **2026-04-21 08:57 UTC** — 2nd rejection: Website URL + Demo video
- **2026-04-22** — 3rd submission after full fix pass (see below)

## 2nd rejection reasons (verbatim, 2026-04-21)

- **Website URL** — "cannot be a landing page or login page. You must have an externally facing fully developed website."
- **Demo video** — "must show the complete end-to-end flow... all selected products and scopes must be clearly demonstrated... required to use sandbox."

## Apr 22 fix pass (what changed before 3rd submit)

1. **Website URL** → `https://aibiblegospels.com` (live Next.js/Vercel site, verified via TikTok DNS TXT after flipping apex as primary). Replaced the legal-pages GH URL.
2. **Apex as primary in Vercel** — previously `aibiblegospels.com` 308'd to `www.aibiblegospels.com`; reversed so apex serves directly, www→apex. Fixed DNS TXT verification failure (www is CNAME to Vercel, blocks TXT per spec).
3. **DNS TXT at root** — `tiktok-developers-site-verification=KwMOkEST8r3pyyR2bg2YFuveU8x88zEX` at `@` in GoDaddy. Prior attempt split the string wrong (put prefix as Name, token as Value at subdomain) — TikTok's actual format is full string in Value at root.
4. **Privacy + Terms footer links** on aibiblegospels.com (pointing to existing legal URLs on GH Pages). Added via aibiblegospelscom repo (separate Claude instance).
5. **Re-recorded sandbox demo** showing: site tour → OAuth consent (both scopes visible) → user info call → video upload → inbox confirmation.
6. **Scope explanation** rewritten to be specific (prior was 7 words for video.upload — reviewer flagged as vague).

## Key facts (locked)

- **App name**: "AI Bible Gospels" (Organization: Born Made Bosses LLC)
- **Website URL**: `https://aibiblegospels.com` (apex canonical, live, verified)
- **Target user** (sandbox tester): aibiblegospels_
- **Active credentials in .env**: SANDBOX (sbawswnygychzo38lw) — production creds preserved as comments
- **Scopes**: user.info.basic + video.upload (no video.publish)
- **Products**: Login Kit + Content Posting API (Direct Post OFF, inbox/drafts only)
- **Redirect URI**: https://12tribesofisrael.github.io/aibiblegospels-legal/callback.html
- **Privacy Policy URL**: https://12tribesofisrael.github.io/aibiblegospels-legal/privacy.html
- **Terms URL**: https://12tribesofisrael.github.io/aibiblegospels-legal/terms.html

## Gotchas (still true — don't re-learn)

- Email from `noreply@dev.tiktok.com` subject "Your app status update" is GENERIC — real rejection reason ONLY visible in Dev Portal, not email body.
- TikTok **follows redirects** during DNS verification. If Website URL is apex but apex redirects to www, TikTok looks for TXT at www — which may be a CNAME (blocks TXT). Fix: make apex the non-redirected canonical.
- TikTok TXT verification format: **entire string** (`tiktok-developers-site-verification=<token>`) goes in the **Value** field at **root** (`@`). NOT subdomain, NOT split at the `=`.
- TikTok rejects localhost redirect URIs. Use GH Pages forwarder (`callback.html`).
- Pre-approval OAuth requires Sandbox mode — production creds return `client_key` error until approved.
- Dev Portal won't save app config without a placeholder demo video first. Upload any mp4, save, swap real demo later.
- Sandbox video processing is slow (5-15 min for PROCESSING_UPLOAD → SEND_TO_USER_INBOX); production <30s.

## Expected turnaround

Based on prior 2 rounds: ~24-30 hours. Watch `aibiblegospels444@gmail.com` for `noreply@dev.tiktok.com` email subject "Your app status update".
