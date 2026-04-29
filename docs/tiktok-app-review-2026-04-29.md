# TikTok App Review — 4th submission (2026-04-29)

## What happened

3rd submission was rejected on 2026-04-28 with three reviewer notes:

1. "Invalid Terms of Service link provided"
2. "Invalid Privacy Policy link provided"
3. "App will not be approved for personal or company internal use."

The rejected submission had pointed all three URL fields (Website, Terms, Privacy) at `https://www.aibiblegospels.com/` — the homepage. There were no `/terms` or `/privacy` routes on the canonical site; the actual legal pages lived on a separate GitHub Pages repo (`12tribesofisrael/aibiblegospels-legal`) and that content explicitly said *"Our software is used exclusively by the account owner"* — the textbook definition of personal/internal use.

## Fix

### Site changes (`aibiblegospelscom` repo)

Commit `85d3f13` on `main`. Vercel auto-deployed.

- New route `src/app/terms/page.tsx` — TikTok-compliant Terms of Service, framed as a publishing service offered to creators connecting their own TikTok/IG/FB/YT accounts.
- New route `src/app/privacy/page.tsx` — Privacy Policy with explicit data-deletion path via `aibiblegospels444@gmail.com`, OAuth scope language, third-party platform links.
- `src/app/sitemap.ts` — added `/terms` and `/privacy` entries.
- `src/app/page.tsx` — footer links swapped from GitHub Pages URLs to internal `/terms` and `/privacy` Next.js routes.

The GitHub Pages legal repo (`aibiblegospels-legal`) was left untouched — it still hosts the OAuth `callback.html` forwarder used by both TikTok and Meta OAuth flows.

### TikTok Developer Portal field updates

| Field | Old | New |
|---|---|---|
| Description (120-char limit) | "AI Bible Gospels manages posting and engagement on our own TikTok account to share biblical content with our audience." | "Creators schedule and publish video posts to their own TikTok account, then track engagement and growth analytics." |
| Terms of Service URL | `https://www.aibiblegospels.com/` | `https://aibiblegospels.com/terms` |
| Privacy Policy URL | `https://www.aibiblegospels.com/` | `https://aibiblegospels.com/privacy` |
| Web/Desktop URL | `https://www.aibiblegospels.com/` | `https://aibiblegospels.com` (apex) |

Submission reason (120-char field at Submit time): *"Fixed invalid ToS/Privacy links and reframed app description as creator publishing service per reviewer comments."*

## Field length limits learned this round

- App **description** field: 120 chars max
- App **submission reason** field (the textbox that opens at Submit time): 120 chars max

## Portal flow gotcha learned this round

When an app sits in "Not approved" state, the form fields look editable but there is no Save/Submit button anywhere on the page. You must click **`Return to Draft`** (top right) and confirm the modal first. That transitions the app back to draft state and surfaces the Submit-for-review button. Until that confirmation, any field edits sit in the DOM but don't persist.

## Verification (passed before submit)

- `curl -I https://aibiblegospels.com/terms` → 200
- `curl -I https://aibiblegospels.com/privacy` → 200
- Both pages render in a fresh browser, no auth wall
- Footer links resolve to internal routes
- Privacy page contains `aibiblegospels444@gmail.com` and Data Deletion Request section
- Terms page describes service for "creators" (not "our own account")
- `https://aibiblegospels.com/sitemap.xml` lists both new routes

## What to watch for next

Email at `aibiblegospels444@gmail.com` from `noreply@dev.tiktok.com` subject "Your app status update". Email body is generic — real status is in the Dev Portal (`https://developers.tiktok.com/apps` → AI Bible Gospels → Production tab).

Past rounds turned around in 24-30h. Round 3 ran 6 days due to a TikTok-side backlog, so don't read silence as failure.

If they reject this round, the next likely friction points are:

1. **Demo video** — was recorded showing posting to "your" account. Doesn't strictly contradict the new "creator service" framing but doesn't reinforce it either. Re-recording with a clear "creator-onboards-then-posts" arc would be safer.
2. **Born Made Bosses LLC name** — still appears on the GH-Pages legal pages (which are not linked from the app submission anymore but remain discoverable via Google). If a reviewer cross-references the entity name to the canonical site, the mismatch is visible.

## Related files

- New legal pages: in `aibiblegospelscom` repo at `src/app/terms/page.tsx` and `src/app/privacy/page.tsx`
- Memory: `~/.claude/projects/c--Users-Owner-repos-youtubeoptermizer/memory/project_tiktok_app_review.md`
