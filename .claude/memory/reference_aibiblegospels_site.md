---
name: aibiblegospels.com canonical website
description: aibiblegospels.com (apex) is the parent-brand site on Next.js 16/Vercel; use for ALL platform review Website URL fields
type: reference
originSessionId: d8307714-5c23-44bb-8e54-674ae9da6aae
---
`https://aibiblegospels.com` is the canonical parent-brand website for AI Bible Gospels. **Use APEX (no www) for all platform developer review Website URL fields** — TikTok, Meta, Google, etc. NOT the legal-pages GH Pages repo, NOT the YouTube channel URL.

## Stack + hosting

- **Next.js 16** (App Router, Turbopack) + TypeScript + Tailwind v4
- **Vercel deploy** — apex is primary/canonical (serves site directly); www 308's → apex
- **GoDaddy DNS** → Vercel
- **Repo**: `C:\Users\Owner\repos\aibiblegospelscom` — **READ-ONLY** per `feedback_repo_scope.md` (separate Claude instance owns it)

## Site content (as of 2026-04-22)

One-page site: Hero → Flagship case study (Faith Walk Live) → Services → YouTube credit → Work-with-us CTA → Footer with Privacy + Terms links + Colossians 3:23.

## Related URLs (separate hosting)

- **Legal pages** (GitHub Pages, separate repo `12tribesofisrael/aibiblegospels-legal`):
  - Privacy: `https://12tribesofisrael.github.io/aibiblegospels-legal/privacy.html`
  - Terms: `https://12tribesofisrael.github.io/aibiblegospels-legal/terms.html`
  - OAuth callback forwarder: `https://12tribesofisrael.github.io/aibiblegospels-legal/callback.html`
- **YouTube**: `https://www.youtube.com/@AIBIBLEGOSPELS`
- **Flagship project**: `https://faithwalklive.com`

## Windows curl gotcha

Local Windows curl may fail with `CRYPT_E_NO_REVOCATION_CHECK` (schannel quirk) — not a site problem. Add `--ssl-no-revoke` to bypass. Site IS live when the flag is used.

## Apex-primary rule (learned 2026-04-22)

Vercel originally had `www` as primary with apex → www 308. This broke TikTok's DNS TXT verification because www is a CNAME to Vercel (CNAMEs block TXT records per DNS spec). Fix was flipping Vercel domain settings so apex is primary, www redirects to apex. Keep it this way for any future platform verification (Google Search Console, Meta, etc.).
