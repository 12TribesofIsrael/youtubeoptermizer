---
name: FB writes need a Page token, not User token
description: FB Graph /{post_id} edits and /{page_id}/feed creates reject User tokens under "new Pages experience" — must derive a Page token first
type: feedback
originSessionId: 5eb7f750-854c-4407-bd99-d48e87fa9b29
---
`graph.facebook.com/v25.0/{page_id}/feed` (post create) and `graph.facebook.com/v25.0/{post_id}` (caption edit) **reject User Access Tokens** even when they have `pages_manage_posts` and the user is Page Admin. Error:

```
{"message":"Invalid OAuth 2.0 Access Token","code":190,"error_subcode":2069032,
 "error_user_title":"User Access Token Is Not Supported",
 "error_user_msg":"A Page access token is required for this call for the new Pages experience."}
```

**Why:** Meta's "new Pages experience" tightened the auth model — Page-scoped writes require Page-scoped tokens. The migration is irreversible for any Page that has been migrated.

**How to apply:** When FB writes throw code 190 subcode 2069032, derive a Page token from the User token:

```python
url = f'https://graph.facebook.com/v25.0/{PAGE_ID}?fields=access_token&access_token={USER_TOKEN}'
page_token = json.loads(urllib.request.urlopen(url).read())['access_token']
```

Page token inherits the User token's scopes (so `pages_manage_posts` carries over) and inherits its TTL (so a 1h user token gives a 1h page token; long-lived user token gives a never-expiring page token).

**Verify** with `debug_token` — `type` field should return `PAGE`, not `USER`.

**Worth knowing:** The repo has `scripts/meta-token-refresh.py` that does the long-lived-user-token → never-expiring-page-token chain. Use it for any token you want to persist in `.env`. For one-shot bulk runs with a temp Graph Explorer token, just inline the derivation as above.
