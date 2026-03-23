# Social Media Audit Tool

A full-stack web app that generates comprehensive social media audit reports for YouTube creators. Powered by Claude AI — runs 3 parallel research agents, benchmarks against competitors, and delivers an actionable optimization report.

---

## What It Does

Paste in a YouTube channel + social media URLs, and the app:

1. **Researches platform best practices** — current 2026 algorithm tips, posting frequency, bio optimization, content formats, best times to post for each platform
2. **Audits a competitor** — finds (or uses your provided) a top-performing creator in the same niche and analyzes their social strategy across all platforms
3. **Researches niche hashtags & trends** — trending hashtags, winning content formats, content gaps in your niche
4. **Generates a full audit report** — synthesizes all research into a branded, actionable report

All 3 research phases run **in parallel** using the Claude API for speed.

---

## Features

### 1. Multi-Platform Audit
Supports: **Instagram, TikTok, X/Twitter, Facebook, LinkedIn, Threads**

For each platform, the report includes:
- Profile setup recommendations (account type, pic/banner dimensions)
- Copy-paste bio (character-counted, ready to paste)
- Content strategy (frequency, formats, best times, CTAs)
- Platform-specific fixes checklist

### 2. Competitor Benchmarking
- Provide a competitor or let the AI find one
- Per-platform comparison: "What [Competitor] Does That You Don't"
- Tactics to steal, gaps to exploit

### 3. Hashtag Bank
- Core hashtags (evergreen)
- Sub-niche hashtags
- Platform-specific hashtags (#bibletok, etc.)
- Trending hashtags (rotate weekly)

### 4. Priority Action List
- **Immediate** (today) — highest impact first
- **This Week** — medium priority
- **This Month** — lower priority, still important

### 5. PDF Download
- Download the full report as a styled PDF
- Branded with dark navy/gold theme
- Print-friendly fallback if WeasyPrint isn't installed

### 6. Copy Markdown
- Copy the raw markdown report to clipboard
- Paste into Notion, Google Docs, or any markdown editor

---

## How to Run Locally

### Prerequisites
- Python 3.10+
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Setup

```bash
cd src/audit-app
pip install -r requirements.txt
```

### Set your API key

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Run

```bash
uvicorn app:app --reload --port 8000
```

Open **http://localhost:8000** in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web UI — the audit form |
| `POST` | `/audit` | Run the audit. Form fields: `youtube_handle`, `social_urls`, `niche`, `competitor`. Returns `{markdown, html}` |
| `POST` | `/download-pdf` | Convert HTML report to PDF. Body: `{html: "..."}`. Returns PDF file |

---

## Architecture

```
src/audit-app/
├── app.py              ← FastAPI backend (3 parallel Claude calls + report generation)
├── requirements.txt    ← Python dependencies
├── templates/
│   └── index.html      ← Frontend (form, progress UI, report viewer)
├── static/             ← Static assets (empty for now)
└── README.md           ← This file
```

### How the Audit Works

```
User submits form
        │
        ▼
┌───────────────────────────────┐
│  Phase 1: Parse inputs        │
│  (YouTube handle, URLs, niche)│
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────────────────────┐
│  Phase 2: 3 Parallel Claude API Calls         │
│                                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ Agent 1:    │ │ Agent 2:    │ │ Agent 3: │ │
│  │ Platform    │ │ Competitor  │ │ Hashtag  │ │
│  │ Best        │ │ Audit       │ │ & Trend  │ │
│  │ Practices   │ │             │ │ Research │ │
│  └──────┬──────┘ └──────┬──────┘ └────┬─────┘ │
│         └───────────┬───┘──────────────┘       │
└─────────────────────┼─────────────────────────┘
                      │
                      ▼
┌───────────────────────────────┐
│  Phase 3: Generate Report     │
│  (Claude synthesizes all      │
│   research into full report)  │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  Output: Markdown + HTML      │
│  [View] [Download PDF] [Copy] │
└───────────────────────────────┘
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python) |
| AI | Claude Sonnet via Anthropic API |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| PDF | WeasyPrint (optional) |
| Markdown | Python-Markdown with tables + fenced code |

---

## Cost Per Audit

Each audit makes **4 Claude API calls** (3 research + 1 report generation):
- 3 research calls: ~2K tokens in, ~2K tokens out each
- 1 report call: ~8K tokens in, ~6K tokens out
- **Estimated total: ~20K tokens per audit**
- **Cost: ~$0.06-0.10 per audit** (Claude Sonnet pricing)

---

## Deployment

Ready to deploy to Modal.com using the `/publish-app` skill:
```
/publish-app src/audit-app
```

Or deploy manually to any platform that supports Python (Railway, Render, Fly.io, etc.).

---

## Future Roadmap

- [ ] Payment integration (Stripe) — charge per audit or subscription
- [ ] User accounts — save audit history
- [ ] Scheduled re-audits — monthly email with updated report
- [ ] White-label PDF reports — custom branding for agencies
- [ ] Batch audits — upload a CSV of clients, generate all reports
