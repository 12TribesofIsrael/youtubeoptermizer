---
name: Vercel env vars don't apply to existing deployments — redeploy required
description: Adding env vars in Vercel dashboard AFTER a deployment was built doesn't retroactively apply them; the running deployment still sees them as undefined until a fresh build runs
type: feedback
---
Adding `KEY=value` pairs in Vercel → Project → Settings → Environment Variables does NOT affect an already-running deployment. The currently-deployed bundle still reads `process.env.KEY` as `undefined` until a new build runs.

**Why:** On 2026-05-01, after pushing the `/api/tiktok/start` route to `aibiblegospelscom`, hitting it returned a 307 to `/connect/tiktok/error?reason=server_misconfigured` — which is the explicit branch fired when `process.env.TIKTOK_CLIENT_KEY` is undefined. Tommy had added the env vars in Vercel, but the deploy from my push had completed beforehand. Redeploying via the Vercel dashboard's `⋯` → Redeploy fixed it; the next probe correctly issued the TikTok OAuth redirect with the client_key embedded in the Location header.

**How to apply** — when wiring secrets/env into a Vercel app:
- After adding env vars in dashboard, ALWAYS trigger a fresh deploy. Two options: (a) Deployments tab → `⋯` → Redeploy on the latest production deploy, or (b) push a no-op commit to trigger a new build.
- Confirm scope: env vars added to the `Production` environment apply only to production deploys; `Preview` is separate; `Development` is for `vercel dev` locally. If your prod deploy still sees `undefined`, double-check the env var is scoped to Production not just Preview.
- Verification: probe the route that uses the env var — if it errors with the "missing env" branch you wrote, redeploy didn't take effect; if it produces the expected output, you're good.
- Common naming traps: `NEXT_PUBLIC_` prefix exposes the var to the client (use only for non-secrets); without the prefix it's server-only. TikTok client_secret should be server-only.
