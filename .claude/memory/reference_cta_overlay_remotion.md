---
name: cta-overlay-remotion-project
description: "src/cta-overlay/ is a sibling Remotion project that renders 3 transparent-BG FOLLOW CTA variants (reward/curiosity/social) for drop-in over any TT/Short export. 1080x1920, 60 frames, ProRes 4444."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 373f4945-6482-4d96-b023-f668cb24598b
---

`src/cta-overlay/` is a sibling Remotion project to `src/anchor-doc/` and `src/shorts/`, dedicated to rendering 2-second branded FOLLOW CTA overlays with transparent backgrounds (alpha channel via `yuva444p10le` pixel format). Built 2026-05-16.

**Compositions (`src/cta-overlay/src/Root.tsx`):**
| ID | Subtext | Best for |
|---|---|---|
| `cta-reward` | "for daily 12 Tribes drops 🔱" | Default CTA on standalone Shorts |
| `cta-curiosity` | "there's more →" | Part-of-series Shorts (Deut 28 parts, lost-tribes-per-tribe, etc.) |
| `cta-social` | "1K+ walking with us" | Stronger on credibility plays; ages as the number changes |

**Animation spec (`src/cta-overlay/src/FollowCTA.tsx`):**
- Spring-entry FOLLOW headline (220px Cinzel, gold), breathing glow via sine wave
- Variant subtext slides up 8 frames behind the headline
- Pulsing 👆🏿 emoji at top pointing to profile area
- Drifting gold particle field (14 particles, noise-driven)
- Brand backdrop = radial navy-to-warm gradient

**Brand theme** (`src/cta-overlay/src/theme.ts`) is identical to `src/shorts/src/theme.ts` — gold (#D4A857), cream (#F4ECD7), deep navy (#0A0E1A), Georgia serif. Copy from shorts/ if you ever fork it.

**Render command** (run from `src/cta-overlay/` dir):
```bash
npx remotion render src/index.ts cta-reward out/cta-reward.mov --codec=prores --prores-profile=4444
# Or all 3:
npm run render:all
```

Output = transparent-BG MOV per variant, drop into CapCut at the tail of any Short.

**Gotchas:**
- npm scripts use `npx remotion` (NOT bare `remotion`) — matches the shorts/ pattern, otherwise the binary isn't on PATH.
- Install requires `NODE_OPTIONS=--use-system-ca npm install` on this Windows machine — see [[feedback_npm_install_silent_fail]].
- As of 2026-05-18 the project is **built + deps installed but renders not yet executed**. First render will validate the spec works end-to-end.
