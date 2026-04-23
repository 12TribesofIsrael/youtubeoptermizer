---
ended: 2026-04-22T22:00:00Z
project: youtubeoptermizer (AI Bible Gospels)
branch: main
originSessionId: d8307714-5c23-44bb-8e54-674ae9da6aae
---
# Last Session — 2026-04-22 (evening)

## What the user wanted
Verify whether TikTok had rejected the app a 2nd time, diagnose why, and get the Content Posting API app through a 3rd submission. Thomas came in frustrated ("i'm confuted") — needed a single linear path to passing review, not more options.

## What we did
- **Confirmed 2nd rejection via Gmail MCP.** Two rejection emails from `noreply@dev.tiktok.com` subject "Your app status update": Apr 20 02:18 UTC (name mismatch) and Apr 21 08:57 UTC (new). Email body is useless — real reason only visible in Dev Portal.
- **Parsed the Apr 21 rejection from a Thomas screenshot**: Website URL flagged (not a "fully developed website") + Demo video flagged (didn't show end-to-end flow, scopes not clearly demonstrated, must use sandbox).
- **Picked `aibiblegospels.com` as the canonical Website URL.** Thomas owns it (repo at `C:\Users\Owner\repos\aibiblegospelscom`, read-only to this instance). Confirmed it's live via curl (Windows schannel needs `--ssl-no-revoke` flag due to CRYPT_E_NO_REVOCATION_CHECK quirk — site is NOT actually broken).
- **Confirmed existing privacy/terms are already adequate** (fetched live pages from 12tribesofisrael.github.io/aibiblegospels-legal/). They name "AI Bible Gospels" by name and explicitly list TikTok in Sections 2 & 4. Talked Thomas out of writing new tiktok-privacy.html / tiktok-terms.html that the other Claude instance had suggested — would've been duplicated source of truth.
- **Had Thomas add Privacy + Terms footer links** to aibiblegospels.com via the other Claude instance owning the aibiblegospelscom repo. Verified live via curl HTML grep.
- **Chased the DNS TXT verification failure** through multiple rounds:
  1. First attempt: Thomas split `tiktok-developers-site-verification=<token>` at the `=` sign — put prefix as Name (subdomain) and token as Value. Wrong format. Fixed by putting entire string in Value at root (`@`).
  2. After fix, TikTok still rejected verification — error showed `www.aibiblegospels.com`. Root cause: Vercel had `www` as primary and apex 308'd to www. TikTok followed the redirect to www, but www is a CNAME to Vercel, which blocks TXT records per DNS spec.
  3. Final fix: flipped Vercel domain config — `aibiblegospels.com` set as primary (Connect to environment → Production), `www.aibiblegospels.com` set to 308 redirect → apex. Verified with curl: apex returns 200 with 0 redirects.
- **Updated TikTok Dev Portal** for 3rd submission: new sandbox demo video (replacing "Untitled design.mp4"), rewritten scope explanations (video.upload was 7 words — now specific), Website URL → aibiblegospels.com verified.
- **Thomas clicked Submit** on the 3rd submission late evening Apr 22 with the 101-char reason: "Fixed Website URL to aibiblegospels.com; new sandbox demo covers full OAuth + upload for both scopes."
- **Committed memory** (`e97cc4f`): updated `project_tiktok_app_review.md` with full timeline and gotchas, new `reference_aibiblegospels_site.md`, updated MEMORY.md index lines. Pushed to origin/main.

## Decisions worth remembering
- **Vercel apex-primary, www-redirect** is now the permanent rule for aibiblegospels.com. Locked because of the TXT-verification bug — don't flip back unless there's a strong reason. Documented in `reference_aibiblegospels_site.md`.
- **Don't write dedicated TikTok privacy/terms pages.** The existing generic-but-TikTok-aware pages at 12tribesofisrael.github.io/aibiblegospels-legal/ already pass the reviewer's "mention app by name + describe data" bar. Duplicating would create divergent sources of truth.
- **TikTok rejection emails are useless.** Subject "Your app status update" from `noreply@dev.tiktok.com` always has the same generic body. Always check the Dev Portal directly for the actual reason.
- **Memory edits can get silently reverted.** Near end-of-session, discovered my early memory writes (project_tiktok_app_review update, reference_aibiblegospels_site creation) had been overwritten — probably by the central memory backup sync picking up the stale version. Re-applied them before the final commit. If memory edits seem to disappear mid-session, just redo + commit.

## Open threads / next session starts here
- **Watch Gmail for 3rd TikTok verdict** on `aibiblegospels444@gmail.com`. Based on prior turnarounds (~24-30 hrs), expect the `noreply@dev.tiktok.com` "Your app status update" email by midday Apr 23 → early Apr 24. Claude can pull it via Gmail MCP (authenticated this session, persists).
- **If approved** → wire production client_key + client_secret into `scripts/tiktok-post.py` (currently using sandbox `sbawswnygychzo38lw`). Production creds are preserved as comments in .env.
- **If rejected AGAIN** → the rejection reason is ONLY in the Dev Portal, not email. Have Thomas screenshot the "See why" expansion on the rejection banner. Likely remaining risk areas: demo video quality (was recorded under time pressure), or some detail in the Apply Reason text.
- **YPP appeal still open** (from earlier this same calendar day's session) — watch for `yt-partner-support@google.com` reply. See `project_ypp_suspension_2026.md`.
- **TikTok Dev Portal Gmail MCP is now connected** — don't need to re-auth. Useful for polling any future platform-review emails (Meta, Google, etc.) without asking Thomas to screenshot.

## Uncommitted work
Clean working tree. Last commit `e97cc4f` pushed to origin/main.
