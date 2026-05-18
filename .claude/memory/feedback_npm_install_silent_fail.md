---
name: npm-install-silent-fail
description: "`npm install` exit code 0 doesn't guarantee install completed. SSL cert errors (UNABLE_TO_VERIFY_LEAF_SIGNATURE) can fail mid-stream while cleanup script succeeds, yielding exit 0 with empty node_modules/. Verify before trusting."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 373f4945-6482-4d96-b023-f668cb24598b
---

`npm install` reporting exit code 0 is not sufficient evidence that dependencies actually installed. On this Windows machine (2026-05-16, `src/cta-overlay/`), an SSL cert verification error mid-stream (`UNABLE_TO_VERIFY_LEAF_SIGNATURE` on `registry.npmjs.org/undici-types/...`) halted the install partway, but the subsequent cleanup step (which mostly succeeded modulo a `EPERM rmdir` warning) returned exit 0. `node_modules/` was effectively empty — no `.bin/remotion`, no `@remotion/*`. The downstream `npx remotion render` then failed with "could not determine executable to run" with no obvious connection back to the install failure.

**Why:** The harness's task-completion notification trusts the wrapper script's exit code, which can mask sub-process errors that don't propagate.

**How to apply:**
- After any `npm install`, verify `ls node_modules/.bin/<expected-binary>` (e.g. `remotion`) before assuming success. Don't trust the exit code alone.
- If the install fails with cert errors on this Windows machine, retry with `NODE_OPTIONS=--use-system-ca npm install` — this lets Node use the Windows certificate store and resolves the leaf-signature error. Worked on 2026-05-16 (194 packages in 11 sec).
- For renders that depend on the install, gate them on a `[ -x node_modules/.bin/remotion ]` check or similar before invoking.
