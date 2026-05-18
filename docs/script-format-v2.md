# Script Format v2 — Custom Script 2.0

Authored script format for the FLUX → Kling → JSON2Video pipeline at `C:/Users/Claude/ai-bible-gospels/workflows/custom-script/`. Bypasses the Claude AI scene-generator (which paraphrases scripture) and feeds scenes directly via `generate.py scenes.json`.

Converter: [scripts/script-to-scenes.py](../scripts/script-to-scenes.py)

## File anatomy

```
<HEADER — free text, ignored by parser. Use for production notes>

================================================================
[SECTION NAME — TIMESTAMP]
================================================================

[Visual: <description — character / setting / composition only>]
[Motion: <one of: zoom-in | zoom-out | ken-burns | pan-right | pan-left>]
[Lighting: <specific lighting description>]

Narrator:
"<verbatim narration text — what gets spoken, exact words>"
```

One scene = one `[Visual:]` block + one `Narrator:` quote. Pair them in order. `[Motion:]` and `[Lighting:]` are optional (defaults apply if omitted).

Section divider lines (`====...`) split the script into parts for long-script auto-splitting; they don't otherwise change parsing.

## Field rules

### `[Visual: ...]` → `imagePrompt`
- Character/setting/composition description for FLUX. Photorealistic scene description.
- **Do not include text-rendering instructions** (no "text saying X", no logos, no captions). FLUX misspells text. Subtitles handle all on-screen text downstream.
- Melanated character keywords auto-injected if missing (see Auto-injection below).
- Safety suffix `, no text, no letters, no symbols, photorealistic, cinematic, 8K detail` always appended.

### `[Motion: ...]` → `motion`
- One of exactly: `zoom-in | zoom-out | ken-burns | pan-right | pan-left`
- Default: `ken-burns` if omitted
- Converter fails loudly on unknown values (don't write `slow zoom in` — write `zoom-in`)

### `[Lighting: ...]` → `lighting`
- Free-text lighting description appended to FLUX prompt inside the pipeline
- Default: `Deep navy chiaroscuro with golden divine amber light` if omitted

### `Narrator: "..."` → `narration`
- Verbatim text spoken in the rendered video by Daniel Steady Broadcaster voice (`onwK4e9ZLuTAKqWW03F9`)
- Used twice in JSON2Video: once as the TTS source (`text`) and once as the subtitle transcript (`transcript`)
- **Scripture must come from `docs/1611KjvW_apocrypha - Copy.pdf`** — never paraphrased from training memory
- Use straight ASCII double-quotes (`"..."`) — curly quotes confuse the parser

## Auto-injection rules

The converter modifies `imagePrompt` automatically:

1. **Melanated keywords** — if the visual description doesn't already contain any of `dark-brown`, `melanated`, or `wool-textured`, the converter appends:
   ```
   , dark-brown to deep-brown skinned, melanated African American complexion, wool-textured / tightly curled hair, NOT white, NOT pale, NOT Caucasian
   ```
   Log line emitted for each auto-injection so you can review.

2. **Safety suffix** — always appended:
   ```
   , no text, no letters, no symbols, photorealistic, cinematic, 8K detail
   ```

These exist because FLUX defaults to Caucasian biblical figures and renders garbled text in image prompts. Both rules are non-negotiable per [CLAUDE.md](../CLAUDE.md) MANDATORY blocks.

## Long-script split

Scripts >900 narration words auto-split into `<name>-part1-scenes.json` + `<name>-part2-scenes.json`. Split happens at the last section divider before the midpoint, so sections never break mid-thought. Two-part series matches the Bible in Black binge pattern (see `docs/competitors.md`).

## Example scene

```
================================================================
[HOOK — 0:00-1:30]
================================================================

[Visual: Golden light breaking through a wall of black storm clouds over the mountains of Edom. Ancient stone tablets glowing faintly. An old leather scroll rolling open across a wooden table.]
[Motion: zoom-in]
[Lighting: Dark cinematic chiaroscuro with deep amber rim light]

Narrator:
"They don't teach this in church. Read Genesis 49 slowly."
```

## CLI

```bash
# Convert authored script → scenes.json (one or more parts)
python scripts/script-to-scenes.py drafts/edom-genesis49-longform-2026-05-16.txt --out-dir output/scenes/

# Render a single scene end-to-end for verification (slice first scene from output JSON)
# Then render full parts via:
python scripts/render-via-pipeline.py output/scenes/edom-genesis49-part1-scenes.json
```

## Schema emitted

```json
{
  "scenes": [
    {
      "narration": "...",
      "imagePrompt": "...",
      "motion": "ken-burns",
      "lighting": "..."
    }
  ]
}
```

Matches the shape consumed by `C:/Users/Claude/ai-bible-gospels/workflows/custom-script/generate.py` at line 320 (`if args.script_file.endswith(".json"): scenes = json.loads(raw)["scenes"]`).
