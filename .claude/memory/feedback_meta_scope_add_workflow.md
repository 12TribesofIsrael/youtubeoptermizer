---
name: Meta scope-add workflow + 4 gotchas
description: Adding a new permission scope to the Meta App is a 3-step App-Dashboard → Graph-Explorer → debug_token chain with 4 specific gotchas that cost multiple round-trips on 2026-04-29
type: feedback
originSessionId: 5eb7f750-854c-4407-bd99-d48e87fa9b29
---
When the Meta App needs a new scope (e.g. `pages_manage_posts` for FB writes, `read_insights` for analytics):

**Step 1 — App Dashboard:** https://developers.facebook.com/apps/{APP_ID}/use_cases/ → relevant Use Case → Permissions tab → click `+ Add` next to the scope. Status flips from `+ Add` to "Ready for testing".

**Step 2 — Graph Explorer:** https://developers.facebook.com/tools/explorer/ — open in a fresh tab (or hard-refresh) → set Meta App → set User or Page = "Page Access Token" with the actual Page selected → "Add a Permission" → search/select new scope → click **Generate Access Token** → approve consent dialog.

**Step 3 — Verify:** run debug_token (`https://graph.facebook.com/debug_token?input_token=TOKEN&access_token=APPID|SECRET`). Confirm scope is in the returned `scopes` list AND `type=PAGE`.

**Why:** Without all three steps, the script will hit code 100/200 errors silently. Verification step is critical — Graph Explorer can SHOW a scope as selected without it actually being on the issued token.

**How to apply:** When the user reports "FB/IG write blocked" or "we need scope X", follow this exact sequence. Don't shortcut. Don't trust visual confirmation in Graph Explorer alone.

**The four gotchas, in order they bit on 2026-04-29:**

1. **Stale displayed token.** After adding a scope in App Dashboard, the token already showing in Graph Explorer's text field is from the PREVIOUS scope set. **Must re-click "Generate Access Token"** to mint a new one with the new scopes. Test with debug_token before proceeding.

2. **Dependency injection.** Some scopes pull in dependencies the user didn't ask for. `pages_manage_engagement` requires `pages_read_user_content` to be added at App Dashboard, otherwise consent fails with "Invalid Scopes: pages_read_user_content". Either add the dependency at App Dashboard, or drop the dependency-heavy scope.

3. **Wrong-token-type write reject.** Once `pages_manage_posts` is granted on a User Token, FB still rejects `/feed` writes with "A Page access token is required for this call for the new Pages experience" (code 190, subcode 2069032). Solution: derive a Page token from the user token via `GET /{PAGE_ID}?fields=access_token&access_token={USER_TOKEN}`. Page token inherits user-token scopes. See `feedback_fb_page_token_required.md`.

4. **Wrong x click in scope removal.** When trying to remove a scope-with-dependency by clicking its `x` in Graph Explorer, easy to accidentally click the wrong scope's `x`. Lost `pages_manage_posts` once and had to re-add. Always verify the active permission list AFTER removal, before regenerating.

**Worth knowing:** App Admin in dev mode can use Standard Access scopes on their own assets without App Review. Tommy is the App Admin and the AI Bible Gospels Page is his — so Standard Access is sufficient indefinitely. Only Advanced Access (= App Review submission) is needed when other Meta users will use the scope.

Full reference: `docs/meta-app-capabilities.md` (in repo).
