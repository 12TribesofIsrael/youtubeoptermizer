#!/usr/bin/env node
/**
 * Memory sync — mirror Claude Code's auto-memory between:
 *   USER  (~/.claude/projects/<slug>/memory/)   ← per-machine Claude-native location
 *   REPO  (<repo>/.claude/memory/)              ← committed to git for cross-machine sync
 *
 * Usage:
 *   node scripts/memory-sync.js push   # USER -> REPO (session-end chain calls this)
 *   node scripts/memory-sync.js pull   # REPO -> USER (after `git pull` on a fresh machine)
 *
 * The slug is computed from the current working directory using Claude Code's
 * naming convention (lowercased drive letter, backslashes/colons become dashes).
 * If your repo lives at a different path on a second machine, override with the
 * CLAUDE_MEMORY_SLUG env var.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

function computeSlug(cwd) {
  if (process.env.CLAUDE_MEMORY_SLUG) return process.env.CLAUDE_MEMORY_SLUG;
  return cwd
    .replace(/^([A-Za-z]):/, (_, d) => d.toLowerCase() + ':')
    .replace(/\\/g, '-')
    .replace(/\//g, '-')
    .replace(/:/g, '-');
}

function copyDir(src, dst) {
  if (!fs.existsSync(src)) {
    console.log(`[skip] source does not exist: ${src}`);
    return { copied: 0 };
  }
  fs.mkdirSync(dst, { recursive: true });
  let copied = 0;
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dst, entry.name);
    if (entry.isDirectory()) {
      copied += copyDir(s, d).copied;
    } else {
      fs.copyFileSync(s, d);
      copied++;
    }
  }
  return { copied };
}

const CWD = process.cwd();
const SLUG = computeSlug(CWD);
const USER_MEMORY = path.join(os.homedir(), '.claude', 'projects', SLUG, 'memory');
const REPO_MEMORY = path.join(CWD, '.claude', 'memory');

const mode = process.argv[2];
if (mode === 'push') {
  console.log(`[memory-sync] PUSH`);
  console.log(`  source: ${USER_MEMORY}`);
  console.log(`  dest:   ${REPO_MEMORY}`);
  const r = copyDir(USER_MEMORY, REPO_MEMORY);
  console.log(`  copied ${r.copied} file(s)`);
} else if (mode === 'pull') {
  console.log(`[memory-sync] PULL`);
  console.log(`  source: ${REPO_MEMORY}`);
  console.log(`  dest:   ${USER_MEMORY}`);
  const r = copyDir(REPO_MEMORY, USER_MEMORY);
  console.log(`  copied ${r.copied} file(s)`);
} else {
  console.error('Usage: node scripts/memory-sync.js [push|pull]');
  console.error('');
  console.error(`Computed slug: ${SLUG}`);
  console.error('  (override with CLAUDE_MEMORY_SLUG env var if this is wrong on your machine)');
  console.error(`USER dir:      ${USER_MEMORY}`);
  console.error(`REPO dir:      ${REPO_MEMORY}`);
  process.exit(2);
}
