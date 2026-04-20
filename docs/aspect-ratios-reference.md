# Aspect Ratios — Short-form vs Long-form Reference

Canonical reference for video aspect ratios, JSON2Video keywords, and why TikTok demands 9:16. Feed this into any pipeline work (Modal, Make.com, Remotion, CapCut, etc.) that produces video for the @aibiblegospels_ channel.

## Quick table

| Aspect | Dimensions | Form | Native platforms | JSON2Video keyword |
|---|---|---|---|---|
| **9:16 vertical** | 1080 × 1920 | **SHORT** | TikTok, Instagram Reels, YouTube Shorts | `instagram-story` |
| **1:1 square** | 1080 × 1080 | middle | Facebook / Instagram feed | `instagram-feed` |
| **16:9 horizontal** | 1920 × 1080 | **LONG** | YouTube desktop, TV | `full-hd` |

## The rule

**All TikTok / Reels / Shorts content must render at 9:16 vertical (1080 × 1920)** — JSON2Video keyword `"instagram-story"`.

**Only use `"full-hd"` (16:9) for long-form YouTube desktop content** — never for short-form.

## Why this matters on TikTok

TikTok's feed is a 9:16 vertical canvas. A 9:16 video fills the entire phone screen — full immersive scroll, maximum thumb-stopping power. A 16:9 video uploaded to TikTok gets pillar-boxed or letter-boxed (black bars top + bottom) and occupies only ~33% of the phone screen. Viewers:

1. See a tiny picture surrounded by black void → instant perception of "low-effort / amateur"
2. Can't read any text overlay at that size
3. Swipe in < 1 second

TikTok's algorithm reads that sub-1-second swipe-away rate and **throttles distribution.**

## Evidence from our own channel (2026-04-19)

This rule was discovered diagnosing why [Clone #1](https://www.tiktok.com/@aibiblegospels_/video/7630560963900558622) flopped:

| Post | Aspect ratio | Day-1 result |
|---|---|---|
| Seed viral (Make.com Feb 2025) | 9:16 (`instagram-story`) | 2,700 views / 349 likes / 270 shares — **10% share rate** |
| Clone #1 (Modal Apr 2026) | 16:9 (`full-hd`) | ~300 views / 14 likes / 4 shares — **~1% share rate** |

Same hook formula, same channel, same time window. The ONLY difference (besides voice) was aspect ratio. 10x performance gap.

## For anyone wiring this into a pipeline

### In JSON2Video payloads

Top-level `resolution` field:

```json
{
  "resolution": "instagram-story",
  "quality": "high",
  "scenes": [...]
}
```

### In Modal / Python code

Wherever `VOICE_ID` / resolution constants are hardcoded:

```python
RESOLUTION = "instagram-story"  # 1080x1920 vertical — TikTok/Reels/Shorts
```

### In Remotion

```tsx
// Composition component
<Composition
  id="Reel1"
  component={Reel1}
  width={1080}
  height={1920}
  fps={30}
  durationInFrames={1800}
/>
```

### In CapCut / manual edit

Export preset: **1080 × 1920 (9:16)** — labeled as "TikTok/Reels/Shorts" in most editors.

## Cross-references

- Channel brand identity rules: [CLAUDE.md](../CLAUDE.md) in this repo
- Viral formula playbook that produced this finding: [docs/viral-formula-deuteronomy-28.md](viral-formula-deuteronomy-28.md)
- Seed viral template (authoritative source): `G:/My Drive/AI BIBLE GOSPELS/Make.com Master/Master Shorts/MasterCSV.json` line 1116 (`"resolution": "instagram-story"`)

## Last verified

2026-04-20 — user-confirmed after Clone #1 flop diagnosis.
