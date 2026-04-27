---
name: IG caption update requires comment_enabled param
description: graph.instagram.com /{media_id} POST for caption updates rejects calls missing comment_enabled — returns IGApiException code 100
type: feedback
originSessionId: 78449298-8e83-47d1-be46-fbc199ac1481
---
When updating an IG caption via POST `https://graph.instagram.com/v23.0/{media_id}`, the request MUST include `comment_enabled` (true or false) alongside `caption` and `access_token`. Without it, the call fails with:

```
{"error":{"message":"The parameter comment_enabled is required.","type":"IGApiException","code":100}}
```

**Why:** Discovered 2026-04-27 while probing scope-live status post-Meta-approval. First caption-write attempt failed; adding `comment_enabled=true` fixed it and returned `{"success":true}` HTTP 200.

**How to apply:** Before any bulk caption rollout (e.g. `meta-update-posts.py instagram --live` over the 538 IG posts), confirm the script passes `comment_enabled`. If it doesn't, every call will fail with code 100 and you'll be debugging a 538-post cascade. Be intentional about the value — passing `true` re-asserts comments-on; passing `false` disables comments. Probably want to read the post's current value first and round-trip it, not blanket `true`.
