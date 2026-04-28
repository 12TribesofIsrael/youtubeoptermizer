---
name: YT OAuth client recovered 2026-04-27
description: original Google Cloud OAuth client was deleted; replaced with fresh Desktop OAuth client; credentials.json + token.json now cached at project root; src/youtube/auth.py points there
type: project
originSessionId: f722b886-dd9c-4fd1-bbd4-62cd81fc83ea
---
On 2026-04-27, the YouTube OAuth client (originally in `credentials.json`) had been deleted in Google Cloud Console. First call to `client.get_video()` failed with `google.auth.exceptions.RefreshError: deleted_client: The OAuth client was deleted.`

**Recovery performed:**
1. Tommy created a fresh OAuth 2.0 Client ID (Desktop app) in Google Cloud Console
2. Downloaded the JSON to `src/youtube/client_secret.json` (his preferred staging location)
3. Copied to `credentials.json` at repo root (where `src/youtube/auth.py` reads from)
4. Old `credentials.json` and `token.json` backed up as `*.old-deleted-oauth` then deleted (dropped from disk; pre-emptively gitignored to prevent future leaks)
5. Triggered fresh OAuth flow via `flow.run_local_server(port=8080)` — Tommy approved consent in browser as `aibiblegospels444@gmail.com`
6. New `token.json` cached at repo root

**Verified:** `channels.list mine=true` returns "AI BIBLE GOSPELS" / `UCq6hz1xEEd9kL95Kcuof2wQ`.

**Why:** Don't recall exactly when/why the old OAuth client was deleted. Likely Google Cloud auto-cleanup for unused projects, or Tommy/Claude deleted it manually in a prior cleanup pass. Either way, OAuth re-creation is the established recovery path.

**How to apply:**
- If YT API calls start failing with `deleted_client` again, repeat the recovery: new Desktop OAuth client in Google Cloud Console → save as `credentials.json` at repo root → delete `token.json` to force fresh consent → run any YT script to trigger the local-server flow.
- `src/youtube/auth.py:12` reads from `credentials.json` at PROJECT_ROOT, NOT `src/youtube/client_secret.json`. Don't bother staging in src/.
- `.gitignore` now blocks `**/client_secret*.json` and `*.old-deleted-oauth` — these patterns prevent re-leaking through reflexive backup naming.
