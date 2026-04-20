---
name: session-start
description: Resume from the previous session. Reads LAST_SESSION.md from the project's auto-memory dir, checks current git state, and delivers a concise catch-up so work can continue without the user having to re-explain. Use at the start of a fresh Claude instance or whenever you want to re-ground on where things stand.
argument-hint: "(no arguments)"
disable-model-invocation: false
---

# Session Start

You are resuming work on this project. The previous session (possibly on a different machine) wrote a handoff file. Your job: read it, cross-check it against current reality, and give the user a tight catch-up so you can get back to work.

## Step 1 — Locate the auto-memory directory

Your system prompt contains an `# auto memory` section with a `C:\Users\Deskt\.claude\projects\...\memory\` path. That is where `LAST_SESSION.md` lives. Do NOT guess or recompute it — read it directly from your system context.

## Step 2 — Pull cross-machine updates (if wired)

If the project has `scripts/memory-sync.js` and a `memory:pull` npm script, the user may have pushed a session log from another machine. Check:

```bash
test -f scripts/memory-sync.js && grep -q '"memory:pull"' package.json && echo HAS_SYNC || echo NO_SYNC
```

If `HAS_SYNC`, tell the user: "This project supports cross-machine memory sync. If you ended the last session on a different machine, run `git pull && npm run memory:pull` before continuing." Do NOT run it for them — that touches git state. Let them decide.

## Step 3 — Read the session log

```bash
cat <auto-memory-dir>/LAST_SESSION.md
```

If the file does not exist: tell the user "No previous session log found — this is either a fresh project or the last session wasn't closed with `/session-end`. Proceeding with a clean-slate catch-up." Then skip to Step 4 and give the normal git-based catch-up only.

If the file exists but is older than ~2 weeks (check the `ended:` frontmatter): mention the staleness. The log is still useful but the "open threads" may be cold — verify before acting on them.

## Step 4 — Cross-check against current state

Run in parallel:

1. `git status` — what's in the working tree NOW
2. `git log --oneline -10` — recent commits (compare against the session log's mentions — are there new commits since?)
3. `git branch --show-current` — confirm branch matches the log

Reconcile:
- If the log's "Uncommitted work" section doesn't match reality, that means work continued outside Claude (user committed manually, pulled new changes, switched branches, etc.) — note this in your catch-up.
- If there are new commits since the log was written that weren't in the "What we did" section, mention them so the user knows you see them.

## Step 5 — Deliver the catch-up

Give the user a concise status brief. Target: under 15 lines, scannable. Structure:

```
**{{project name}} — {{version if known}} — {{branch}}**

**Where we left off** ({{date of last session}}):
{{2-3 bullets from "What we did" — only the highlights that matter now}}

**Open threads** (what to pick up):
{{verbatim or tightened from "Open threads" section of the log — this is the key part}}

**Current state:**
- Working tree: {{clean | N files modified, M untracked}}
- New commits since last session: {{list them, or "none"}}
- {{any reconciliation notes — e.g. "Log mentioned book/ as untracked; still untracked."}}

**Ready to continue.** What's next?
```

Rules:
- **Don't re-explain the project.** CLAUDE.md is already loaded. Focus on what's *changed* or *pending*.
- **Don't dump the whole log.** The log is context for YOU; the user wrote it and doesn't need it read back verbatim. Synthesize.
- **If open threads conflict with what the user now says they want, flag it.** E.g. "Log says next step is X, but you're asking about Y — want to park X?"
- **Don't proactively start work.** End with "What's next?" and let the user direct. Exception: if the user invoked `/session-start` with a clear follow-up intent in the same turn ("session-start and keep going on the book"), then roll straight into that work after the catch-up.

## Step 6 — Do NOT auto-invoke session-end

`session-end` is triggered by the user, not by you. Don't schedule it, suggest it at every turn, or auto-run it. Mention it once in the final line of the catch-up ("Run `/session-end` when you're ready to wrap.") and then drop it.
