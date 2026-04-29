# Meta App Capabilities — AI Bible Gospels

What the Meta App (`AI Bible Gospels`, App ID `1452257036358754`) can and cannot do as of 2026-04-29, after adding `pages_manage_posts` for FB caption rewrites.

This doc is the source of truth for "what API surfaces are unlocked." Update it whenever scopes are added/removed or App Review status changes.

---

## Live status

| Item | Value |
|---|---|
| Meta App | AI Bible Gospels (`1452257036358754`) |
| Facebook Page | AI Bible Gospels (`601690023018873`) |
| Instagram Business account | `17841454335324028` |
| App Review status | IG Business — **APPROVED 2026-04-27** (5 IG scopes live in production). FB — no review submitted; running in dev mode (App Admin can use scopes on own assets). |
| Permanent page token | `META_PAGE_TOKEN` in `.env` — never expires, 8 scopes (no `pages_manage_posts`) |
| Temporary user/page tokens | Minted from Graph Explorer when `pages_manage_posts` is needed; ~1h TTL |

---

## Granted scopes (10 total)

### Instagram (5 — approved via App Review 2026-04-27)
- **`instagram_basic`** — read IG profile + post metadata
- **`instagram_manage_comments`** — post comments, reply, pin (used by `aeo-ig-pin-comment.py`)
- **`instagram_content_publish`** — upload new IG posts/Reels
- **`instagram_manage_messages`** — read & send IG DMs
- **`business_management`** — Business Manager assets (cross-platform)

### Facebook Page (4)
- **`pages_show_list`** — list Pages the user admins
- **`pages_read_engagement`** — read Page metadata, posts, followers, basic stats
- **`pages_read_user_content`** — read user-generated comments on Page posts (added as dependency of `pages_manage_posts` consent flow)
- **`pages_manage_posts`** ← **added 2026-04-29** — create/edit/delete Page posts. Unblocks `aeo-fb-bulk-update.py`.

### Identity (1)
- **`public_profile`** — basic identity (auto-granted to every app)

---

## What the app CAN do

### Instagram
- Read all posts/Reels metadata + comments
- Post comments on existing posts and pin them (the AEO pin play — 306/563 done as of 2026-04-29)
- Publish new posts/Reels
- Read insights for `reach`, `follower_count`, `profile_views` (NOT `impressions` — that metric is unsupported on `graph.instagram.com`)
- Read & send DMs

### Facebook Page
- Read all Page posts and engagement
- **Create new Page posts**
- **Edit `message` field on existing Page posts** (used by `aeo-fb-bulk-update.py`)
- **Delete Page posts**
- Read user-generated comments on Page posts

### Business
- View Business Manager assets (Pages, IG accounts, ad accounts owned by the Business)

---

## What the app CANNOT do

| Capability | Why blocked | Path to unblock |
|---|---|---|
| Edit IG captions on existing posts | `graph.instagram.com /{media_id}` silently no-ops `caption` writes (confirmed via canary). Endpoint only honors `comment_enabled`. | None — Meta architectural limitation, not a scope issue. Pinned comments are the workaround. |
| Pin / edit / delete comments on FB Page posts | `pages_manage_engagement` not granted (dropped to avoid `pages_read_user_content` dependency conflict in Graph Explorer) | Add `pages_manage_engagement` at App Dashboard → re-mint token |
| Read FB Page Insights (analytics) | `read_insights` not granted | Add `read_insights` at App Dashboard → re-mint token. Needed for Script 5 (`unified-analytics.py`). |
| Read user emails | `email` not granted | Add at App Dashboard. Not needed by current roadmap. |
| Manage Live Video, Branded Content, Creator Marketplace | Scopes not granted | Add when/if the use case appears. Not on roadmap. |
| Update Page settings or webhooks | `pages_manage_metadata` not granted | Add when settings/webhook automation becomes useful. |
| Post to TikTok | Different platform (TikTok Developer App, not Meta) | TikTok App Review still in queue (5+ days as of 2026-04-27). |
| Post to YouTube | Different platform (Google OAuth, not Meta) | Already wired via separate `credentials.json` / `token.json`. |

---

## How to add a new scope

1. **App Dashboard** — open https://developers.facebook.com/apps/1452257036358754/use_cases/ → relevant Use Case → Permissions tab → click `+ Add` next to the scope. Status flips to "Ready for testing."
2. **Graph Explorer** — open https://developers.facebook.com/tools/explorer/ in a fresh tab (or hard-refresh to clear cached config) → set Meta App = AI Bible Gospels, User or Page = "AI Bible Gospels" (Page Token, not User Token) → click "Add a Permission" → search and select the new scope → click **Generate Access Token** → approve consent dialog.
3. **Verify** — paste token through `debug_token` (`https://graph.facebook.com/debug_token?input_token=TOKEN&access_token=APPID|SECRET`) to confirm scope is actually granted.
4. **Use** — for one-time runs, prefix the script with `META_PAGE_TOKEN='...' python scripts/foo.py`. For permanent integration, run `meta-token-refresh.py` to derive a never-expiring page token, then update `.env`.

### Gotchas learned the hard way
- Adding a scope at App Dashboard alone is not enough — Graph Explorer also needs to request it on the next token generation.
- "+ Add" status in App Dashboard ≠ scope is on the token. Always verify with `debug_token`.
- Scopes pulled in as dependencies (e.g. `pages_manage_engagement` requires `pages_read_user_content`) must also be added at App Dashboard or consent fails with "Invalid Scopes."
- A regenerated token may be silently stale if "Generate Access Token" wasn't clicked after the scope change — always re-click after editing permissions.
- User tokens with the right scopes work for Page-post edits when the user is Page Admin, but cleaner to derive a Page token via `GET /{PAGE_ID}?fields=access_token`.

---

## App Review status by scope tier

**Standard Access** (in dev mode, App Admin only — what we have today for FB):
- All current FB scopes work for Tommy Lee's own AI Bible Gospels Page

**Advanced Access** (production-grade — required for non-admin users):
- Only the 5 IG scopes are at this tier (approved 2026-04-27)
- FB scopes would need a separate App Review submission to reach this tier
- For the AEO automation (where only Tommy Lee runs the scripts on his own assets), Advanced Access is **not needed** — Standard Access is sufficient indefinitely

---

## Related docs
- [api-automation-plan.md](api-automation-plan.md) — 5-script blueprint that consumes these scopes
- [meta-instagram-api-guide.md](meta-instagram-api-guide.md) — IG-specific API patterns
- [scripts/meta-token-refresh.py](../scripts/meta-token-refresh.py) — derive long-lived tokens
