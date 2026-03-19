# /movie-director — AI Bible Gospels Script & Direction Engine

A Claude Code skill that turns Claude into your personal screenwriter and movie director for biblical video productions.

## How to Use

```bash
/movie-director [topic] [duration] [style] [source]
```

| Argument | Options | Default | Example |
|----------|---------|---------|---------|
| **topic** | Any title, tribe, or subject | *(required)* | `"Tribe of Judah"` |
| **duration** | `short` (30-60s), `medium` (5-10min), `long` (15-25min) | `medium` | `long` |
| **style** | `cinematic`, `documentary`, `sermon` | `cinematic` | `cinematic` |
| **source** | Scripture ref OR file path | `docs/12tribesunlocked.md` | See below |

## Source Options

### Option A: Book/Chapter/Verse (reads from 1611 KJV + Apocrypha)

```bash
/movie-director "Tribe of Judah" long cinematic Genesis:49:8-12,Hebrews:7:14
/movie-director "Slave Ships Prophecy" medium documentary Deuteronomy:28:15-68
/movie-director "Valley of Dry Bones" short cinematic Ezekiel:37
/movie-director "Lost Tribes Migration" long cinematic 2Esdras:13:39-45
```

**Format:** `Book:Chapter:StartVerse-EndVerse`
- Whole chapter: `Genesis:49`
- Specific verses: `Genesis:49:8-12`
- Multiple references: `Genesis:49:8-12,Deuteronomy:33:7,Hebrews:7:14`
- Apocrypha works: `2Esdras:13:39-45`, `1Maccabees:13:28`

### Option B: File Path (any reference document)

```bash
/movie-director "12 Tribes Complete" long cinematic docs/12tribesunlocked.md
/movie-director "Book of Enoch" long documentary docs/enoch-research.md
```

### Option C: No Source (writes from Scripture knowledge)

```bash
/movie-director "The Awakening" short sermon
```

## Duration Guide

| Duration | Length | Word Count | Best For |
|----------|--------|------------|----------|
| `short` | 30-60 sec | ~100-150 words | YouTube Shorts, teasers, hooks |
| `medium` | 5-10 min | ~750-1,500 words | Single tribe deep-dive, topic explainer |
| `long` | 15-25 min | ~2,500-3,500 words | Pillar videos, full breakdowns, movies |

## Style Guide

| Style | Tone | Best For |
|-------|------|----------|
| `cinematic` | Movie trailer, dramatic, epic | Tribe reveals, prophecy breakdowns, flagship content |
| `documentary` | Evidence-based, historical, sources cited | Historical proofs, Deuteronomy 28, Montezinos account |
| `sermon` | Passionate, prophetic, call-to-action | Awakening content, community posts, emotional pieces |

## What It Produces

Every script includes:

1. **Full narration script** with `[VISUAL:]` tags for video conversion
2. **Timestamps** per section with word counts
3. **YouTube metadata:**
   - Viral title (under 70 chars, curiosity gap)
   - Description (500+ chars with Scripture refs and playlist links)
   - Tags (30-40 search terms)
   - Thumbnail prompt (DALL-E, matching brand guide)

## Writing Style

Combines six legendary storytellers:

| Director/Writer | What We Take | How It Shows Up |
|----------------|-------------|-----------------|
| **Benioff & Weiss** (Game of Thrones) | Cold opens, cliffhangers | Every script opens mid-action, no slow builds |
| **George R.R. Martin** | Epic world-building | Tribes as Great Houses, each with prophecy and destiny |
| **Michael Hirst** (Vikings) | Raw historical authenticity | Slavery, exile, genocide — never sanitized |
| **Markus & McFeely** (Avengers) | Ensemble hero moments | Each tribe gets their moment, Ezekiel 37 = assembling |
| **Christopher Nolan** | Nonlinear timelines | "Nolan cuts" — prophecy jumps to modern proof |

## Brand Guide (Non-Negotiable)

All visual directions follow this locked style:
- **Colors:** Deep navy/black backgrounds, golden/amber light, warm bronze skin tones
- **Lighting:** Dramatic chiaroscuro — divine golden light breaking through darkness
- **Font:** Bold gold serif with subtle glow
- **Figures:** Dark/brown-skinned biblical characters, Hebrew Israelite representation
- **Mood:** Cinematic, revelatory, powerful

## Examples

### Quick Short for daily posting
```bash
/movie-director "Deuteronomy 28:68 Slave Ships" short cinematic Deuteronomy:28:68
```

### Medium tribe video
```bash
/movie-director "Tribe of Benjamin" medium cinematic Genesis:49:27,Deuteronomy:33:12
```

### Full-length pillar video from research doc
```bash
/movie-director "Complete 12 Tribes Breakdown" long cinematic docs/12tribesunlocked.md
```

### Documentary with multiple Scripture sources
```bash
/movie-director "Apocrypha: What They Removed" long documentary 2Esdras:13:39-45,1Maccabees:13:28
```

## Source Files

| File | What It Contains |
|------|-----------------|
| `docs/1611KjvW_apocrypha - Copy.pdf` | Full 1611 KJV Bible + Apocrypha (primary Scripture source) |
| `docs/12tribesunlocked.md` | Master reference — all 12 tribes with Genesis 49, Deut 33, historical evidence |
| `docs/pillar-video-script.md` | First pillar video script (reference for format and tone) |
