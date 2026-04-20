---
name: session-end
description: Capture the current session's state and hand it off to the next instance. Writes a rolling LAST_SESSION.md into the project's auto-memory dir so session-start (or a fresh Claude instance) can pick up exactly where we left off. Also extracts any durable user/feedback/project/reference memories and piggybacks on memory-sync if the project has it wired.
argument-hint: "[optional: one-line focus note, e.g. 'finished book sync, book/ still uncommitted']"
disable-model-invocation: false
---

# Session End

You are wrapping up the current session and preparing a context handoff for the next Claude instance (possibly on a different machine, possibly days later).

## Step 1 — Locate the auto-memory directory

Your system prompt contains an `# auto memory` section with a `C:\Users\Deskt\.claude\projects\...\memory\` path. That is the target directory. Do NOT guess or recompute it — read it directly from your system context. The session log goes at `<that-dir>/LAST_SESSION.md`.

If you cannot find the auto-memory path in your system prompt, tell the user and stop — do not write the session log somewhere else.

## Step 2 — Gather session state

Run these in parallel:

1. `git status` — what's modified/untracked
2. `git log --oneline -10` — recent commits (to distinguish pre-session vs. this-session commits)
3. `git diff --stat HEAD` — uncommitted change surface area

Also review the conversation in your own context:
- What the user asked for (their intent, not just the literal tasks)
- What decisions were made and why (especially non-obvious ones)
- What was completed vs. what's still open
- Any blockers, deferred questions, or threads you want to pick up next time
- Any files/paths/commands that matter for continuity

## Step 3 — Write LAST_SESSION.md

Overwrite (rolling, not append) `<auto-memory-dir>/LAST_SESSION.md` with this structure:

```markdown
---
ended: {{ISO timestamp, e.g. 2026-04-20T14:30:00Z — use the currentDate from your system prompt for the date}}
project: {{short project name from CLAUDE.md if present, else the repo folder name}}
branch: {{current git branch}}
version: {{if CLAUDE.md has a "Current Version: vX.Y.Z" line, capture it}}
---

# Last Session — {{date}}

## What the user wanted
{{One or two sentences on the user's actual goal this session — the why, not just the what.}}

## What we did
- {{Bullet per meaningful action or decision. Include file paths and commit hashes where relevant.}}
- {{Keep it factual; skip the small-talk turns.}}

## Decisions worth remembering
- {{Non-obvious choices — e.g. "chose rolling LAST_SESSION.md over timestamped history because simplicity won".}}
- {{Skip if none.}}

## Open threads / next session starts here
- {{What's NOT done. What you'd pick up first on resume. Be specific — name files, commands, questions.}}
- {{If the user left a thread dangling (e.g. "we'll deal with X tomorrow"), capture it here.}}

## Uncommitted work
{{Paste the short git status output. If nothing uncommitted, write "Clean working tree."}}

## Focus note
{{If the user passed arguments to this skill, put that verbatim here. Otherwise omit this section.}}
```

Rules:
- **Be specific, not generic.** "Fixed parser bug" is useless; "Fixed rollover promotion in scripts/tracker-from-title.js when rest-only archives shadow in-progress source (see commit 4dea653)" is useful.
- **Lead with what the next instance needs to act on.** The "Open threads" section is the most important — that's what the fresh Claude reads first.
- **Don't restate CLAUDE.md.** CLAUDE.md is always loaded. Don't duplicate project overview, commands, or file maps here.
- **Don't pad.** If the session was short, the log should be short.

## Step 4 — Extract durable memories

While reviewing the session, look for anything worth saving as a durable auto-memory (not just session state). These persist across sessions and are more valuable long-term than the session log:

- **user** — new facts about the user's role/preferences/knowledge
- **feedback** — corrections or confirmations on approach ("don't do X", "yes exactly like that")
- **project** — initiatives, decisions, deadlines, people
- **reference** — pointers to external systems

For each one found, save it following the normal auto-memory protocol (write a `<type>_<topic>.md` file in the auto-memory dir with frontmatter, then add a one-line pointer to `MEMORY.md`). See the `# auto memory` section of your system prompt for the exact format.

Do NOT duplicate session-log content into MEMORY.md. The session log is ephemeral handoff; MEMORY.md is the durable index.

## Step 5 — Cross-machine sync (if wired) — AUTOMATED

Check if the project has memory-sync wiring:

```bash
test -f scripts/memory-sync.js && grep -q '"memory:push"' package.json && echo HAS_SYNC || echo NO_SYNC
```

- If `NO_SYNC`: tell the user the log is local-only to this machine and mention they can wire memory-sync later if they want cross-machine continuity. Skip to Step 6.

- If `HAS_SYNC`: **run the full sync chain automatically** — this is the user's own memory on their own repo, syncing to their own other machine. No shared-state risk. Manual confirmation here is friction without payoff. Run these in order, one Bash call:

  ```bash
  npm run memory:push && \
    git add .claude/memory/ && \
    git diff --cached --quiet .claude/memory/ || \
    (git commit -m "Memory: session-end auto-sync $(date +%Y-%m-%d)" && git push origin main)
  ```

  Notes on this chain:
  - `npm run memory:push` copies `~/.claude/projects/.../memory/` into `.claude/memory/` in the repo.
  - `git diff --cached --quiet .claude/memory/` returns 0 (success, NO changes) if memory was already up-to-date — in that case the `||` branch is skipped and we don't make an empty commit. If there ARE changes, the diff returns non-zero and the commit + push runs.
  - Only `.claude/memory/` is staged — unrelated working-tree changes (book WIP, untracked files, etc.) stay out of the commit. Safe even on a dirty tree.
  - If `git push` fails (auth issue, behind upstream, network), report the failure clearly so the user can resolve manually. Do NOT use `--force` or skip hooks. The session log is already saved locally either way.

  When done, surface in the Step 6 summary: "Memory pushed to origin" (if a commit was made) OR "Memory already in sync, no commit needed" (if the diff was empty).

**Exception — when to NOT auto-sync:**
- If the working tree on `main` is in the middle of a rebase, merge, or detached HEAD. Detect with `git rev-parse --is-inside-work-tree` and check `.git/MERGE_HEAD` / `.git/rebase-merge`. If detected, fall back to the legacy behavior: tell the user manually, don't run.
- If the user passed an argument to `session-end` containing the word "no-sync" or "skip-sync", honor it.

## Step 6 — Confirm

Print a concise summary:

```
✓ Session log saved: <auto-memory-dir>/LAST_SESSION.md
✓ Durable memories added: {{count, or "none"}}
  {{list each new/updated memory file on its own line}}
{{if HAS_SYNC and commit made: ✓ Memory pushed to origin (commit <sha>)}}
{{if HAS_SYNC and no changes: ✓ Memory already in sync}}
{{if HAS_SYNC and push failed: ⚠ Memory committed locally but push failed — resolve manually}}
{{if NO_SYNC: log is local-only to this machine}}
Next session: run /session-start to resume.
```

Keep the final message under 10 lines. The user doesn't need to re-read the whole log — they just wrote it.
