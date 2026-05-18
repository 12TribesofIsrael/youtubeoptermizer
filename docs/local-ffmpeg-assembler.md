# Local FFmpeg Assembler — Planned (Not Built Yet)

**Status:** PLANNED — design complete, implementation deferred. Picked up next time we sit down to kick this off. ~1 full day of focused work when we start.

A local-only video assembler that replaces JSON2Video as the last-mile step in the Custom Script 2.0 pipeline. Ingests 16 Kling MP4 URLs + narration text → produces the same branded MP4 that JSON2Video currently produces, but assembled on this machine with FFmpeg.

---

## Why this exists

Custom Script 2.0 currently pays JSON2Video ~$1.50 per render to do the last-mile assembly: pull 16 Kling URLs, call ElevenLabs internally for Daniel-voice TTS, generate yellow-current-word karaoke subtitles in Oswald Bold, stitch into one MP4. We already control every input and every output. JSON2Video is a hosted dependency we don't need.

**Wins:**

- Net savings ~$1-2/video (see honest cost math below — not the $3-4 first claimed).
- Removes a third-party render service from the critical path. No outage at json2video.com can stall production.
- Full control over subtitle styling, encoder params, output codec. JSON2Video's `classic` style is great but we can't tune it.

**Why not just keep JSON2Video:** the dependency-removal is the bigger lever than the dollar savings. Bigger reason: if/when we want to expose this rendering capability inside `aibiblegospels.com` (faith-tech tools brand) as a hosted product, we need the full pipeline locally first.

## Repo location decision

**Lives in youtubeoptermizer.** Not in ai-bible-gospels, not in its own repo. Three reasons:

1. **All the building blocks are already in youtubeoptermizer** — [`scripts/generate-narration.py`](../scripts/generate-narration.py), [`scripts/transcribe-narrations.py`](../scripts/transcribe-narrations.py), [`scripts/probe-clips.py`](../scripts/probe-clips.py), [`scripts/subtitles-json-to-srt.py`](../scripts/subtitles-json-to-srt.py), [`scripts/render-via-pipeline.py`](../scripts/render-via-pipeline.py). Six of the eight new modules are 60-80% copy-paste from these. New repo = re-importing all of them or submoduling.
2. **Repo-scope rule already settled it.** ai-bible-gospels is READ-ONLY from this Claude instance (owned by a different Claude session). Custom Script 2.0 already lives here and treats `ai-bible-gospels/.../generate.py` as a CLI dependency via subprocess. The local assembler is the same pattern.
3. **Conceptual fit.** youtubeoptermizer is "YouTube channel ops + finishing". ai-bible-gospels is the pipeline engine (FLUX + Kling). Clean separation: engine over there, finishing here.

Spin into its own repo *later* only if we want to reuse for Faith Walk Live recaps or other non-AI-Bible-Gospels work. Premature extraction would slow shipping.

## Architecture

```
ai-bible-gospels/generate.py --skip-json2video
        ↓ writes clips_manifest.json
youtubeoptermizer/scripts/assemble-video.py
        ↓ download Kling MP4s in parallel
        ↓ synthesize Daniel TTS per scene (ElevenLabs)
        ↓ Whisper transcribe with word_timestamps=True
        ↓ emit per-scene ASS with karaoke color overrides
        ↓ FFmpeg Pass A: loop clip to narration length, mux audio (×16)
        ↓ FFmpeg Pass B: concat demuxer + subtitles burn-in
        → output/renders/<topic>.mp4
```

### Upstream contract (handled by a separate Claude session in ai-bible-gospels)

Add a `--skip-json2video` flag to `c:\Users\Claude\ai-bible-gospels\workflows\custom-script\generate.py` that stops after Kling and writes `clips_manifest.json`:

```json
{
  "topic": "edom-genesis49-part1",
  "aspect": "16:9",
  "voice_id": "onwK4e9ZLuTAKqWW03F9",
  "voice_speed": 0.9,
  "scenes": [
    {"scene_id": "01", "kling_url": "https://...", "narration_text": "...", "duration_hint": 15.0, "prompt": "...", "motion": "zoom-in"},
    ...16 entries
  ]
}
```

Same precedent as the `--voice-id` and `--kling-model` flags added 2026-05-16 ([custom-script-2.0.md:80-88](custom-script-2.0.md)). Scoped, ~10-line edit. Defaults to current behavior — passing the flag is opt-in.

## Task zero (before any feature code)

1. **Install FFmpeg.** Verified NOT on PATH as of 2026-05-18. Either bundle a static gyan.dev essentials build under `tools/ffmpeg/` (~80MB, gitignored) OR install system-wide and add to PATH. Wrapper code resolves `ffmpeg.exe` via env var `FFMPEG_BIN` → `tools/ffmpeg/bin/ffmpeg.exe` → system PATH, in that order.
2. **Add deps to [`requirements.txt`](../requirements.txt):** `faster-whisper>=1.0.0`, `av>=12.0.0` (PyAV — used by existing `probe-clips.py`), `requests>=2.31.0` (explicit). `faster-whisper` and `av` are imported by existing scripts but missing from requirements — clean that up when adding.
3. **Ship Oswald-Bold.ttf in-repo** at `scripts/assemble/fonts/Oswald-Bold.ttf` and pass via FFmpeg `subtitles=...:fontsdir='...'`. Do NOT depend on Windows font install.

## Module layout

| File | Role |
|---|---|
| `scripts/assemble-video.py` | **CLI entrypoint.** argparse, dotenv load with ai-bible-gospels fallback (same pattern as [`generate-narration.py:18-21`](../scripts/generate-narration.py)), orchestrates phases. Flags: `--manifest`, `--aspect {16x9,9x16}`, `--vertical-strategy {crop,blur-pad}`, `--topic`, `--scenes N` (canary), `--keep-intermediates`, `--post-produce`. |
| `scripts/assemble/manifest.py` | Load + validate `clips_manifest.json`. Build per-topic dirs: `output/clips/<topic>/`, `output/audio/<topic>/`, `output/subs/<topic>/`, `output/scenes_tmp/<topic>/`, `output/renders/`. |
| `scripts/assemble/download_clips.py` | `ThreadPoolExecutor(max_workers=4)` Kling MP4 download with retry/backoff. Distinguish 403/expired-URL from network error in messages. Assert size > 100KB. Run BEFORE TTS so signed URLs don't expire during the render. |
| `scripts/assemble/tts.py` | `synthesize(text, voice_id, model_id, voice_settings) -> Path`. Copy the request shape from [`generate-narration.py:155-178`](../scripts/generate-narration.py) (don't import — its module level executes the BEATS dict). Daniel voice + `eleven_multilingual_v2` + tuned voice_settings as default. |
| `scripts/assemble/transcribe.py` | Load `WhisperModel("base", device="cpu", compute_type="int8")` once at module level (same as [`transcribe-narrations.py:30`](../scripts/transcribe-narrations.py)). Per-scene `model.transcribe(path, word_timestamps=True, vad_filter=False, language="en")`. **VAD disabled** — VAD trims leading silence and breaks per-word offsets against the muxed audio. Returns `list[{word, start, end}]`. Upgrade to `small.en` if KJV proper-noun timing is poor on canary. |
| `scripts/assemble/ass_writer.py` | **Highest-risk module.** Hand-rolled ASS generator with per-word color overrides. See "ASS karaoke" below. |
| `scripts/assemble/ffmpeg_build.py` | Pass A (per-scene loop+mux) + Pass B (concat+burn). Includes `_escape_subtitle_path()` for the Windows colon-escape rabbit hole. |
| `scripts/assemble/durations.py` | `probe(path) -> {duration_s, width, height}` for both video and audio. Use the PyAV pattern from [`probe-clips.py:27-31`](../scripts/probe-clips.py). |

## FFmpeg filter graph — two-pass

A single 16-input `filter_complex` graph blows Windows cmdline limits and is undebuggable. **Two-pass is correct.**

### Pass A (per scene, parallelizable with a thread pool of 2)

```
ffmpeg -y -stream_loop -1 -i scene_03.mp4 -i scene_03.mp3 \
  -map 0:v:0 -map 1:a:0 \
  -vf "scale=1920:1080:force_original_aspect_ratio=cover,crop=1920:1080,setsar=1,fps=30" \
  -af "apad=pad_dur=0.2" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -shortest -fflags +genpts \
  output/scenes_tmp/<topic>/scene_03.mp4
```

- `-stream_loop -1` loops video; `-shortest` ends when narration ends. `apad=pad_dur=0.2` prevents AAC stutter on the tail.
- **All scenes MUST exit with identical codec params** (libx264 / yuv420p / 30fps / AAC / 48000 / stereo). Probe outputs, assert uniform, fail loud if any scene differs — mismatched params at the concat step is the #1 cause of cumulative A/V drift.

### Pass B (concat + subtitle burn)

```
ffmpeg -y -f concat -safe 0 -i concat_list.txt \
  -vf "subtitles='C\:/Users/Claude/youtubeoptermizer/output/subs/<topic>/merged.ass':fontsdir='C\:/Users/Claude/youtubeoptermizer/scripts/assemble/fonts'" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a copy \
  output/renders/<topic>.mp4
```

- concat **demuxer** (not filter) keeps streams as-is — no remux risk to A/V sync.
- Audio `-c:a copy` since Pass A already normalized.
- Windows subtitle path: forward slashes everywhere, single-quoted, colon escaped with backslash. Build via the dedicated `_escape_subtitle_path()` helper and unit-test it. This is the single biggest time-sink if you wing it.

## ASS karaoke — Approach B (per-word color override)

`\k` alone advances the karaoke clock but does NOT recolor without per-word inline overrides. To get JSON2Video's snap-color effect (yellow current word, gray others, no sweep):

- One `Style: Default` with gray `PrimaryColour=&H00CCCCCC&`, Oswald font, size 80 (16:9) or 64 (9:16), Outline=8, Shadow=6, Alignment=2 (bottom-center), MarginV=80.
- Each subtitle chunk is one `Dialogue:` event spanning `chunk_start → chunk_end`. Inside, emit words as:

```
{\1c&H00FFFF&\k<centiseconds>}word1{\1c&HCCCCCC&} {\1c&H00FFFF&\k<cs>}word2{\1c&HCCCCCC&} ...
```

Each `{\1c&H00FFFF&}` flips the current word to yellow; the trailing `{\1c&HCCCCCC&}` flips it back to gray AFTER its `\k` duration elapses. Result: word becomes yellow when reached, back to gray when the next word starts. Matches JSON2Video's `classic` style.

- **ASS color is BGR hex.** Yellow `#FFFF00` → `&H00FFFF&`. Gray `#CCCCCC` → `&HCCCCCC&`. Black outline → `&H00000000&`.
- **Chunking:** 4 words per line (16:9) or 3 (9:16). Break early on `.?!` and on `,` with > 200ms following gap. Apply cumulative per-scene offset so chunk timestamps are absolute in the merged ASS (one file covers all 16 scenes back-to-back).

## Aspect ratio (both 16:9 and 9:16 day one)

Kling clips are 16:9 source (Custom Script 2.0 hard-codes 16:9). For 9:16 output:

- `--vertical-strategy crop` → center-crop 1080×1920 from 1920×1080 source (loses left/right detail but cleanest).
- `--vertical-strategy blur-pad` → scale to fit width, fill top/bottom with blurred copy of the frame.
- Pass A `-vf` swaps to `scale=1080:1920:force_original_aspect_ratio=cover,crop=1080:1920` (crop) or a stacked blur-pad chain (blur-pad).
- `ass_writer` emits a 9:16 variant with `PlayResX=1080, PlayResY=1920, Fontsize=64`, max-words-per-line=3.

## Known risks

1. **Codec uniformity at concat.** Probe every Pass A output. Assert identical width/height/codec/fps/sample_rate/channels. Mismatch = sample drift across the 16-scene concat.
2. **Kling signed URL expiry.** fal.ai signed URLs live 1-24 hours. Download all 16 in parallel BEFORE TTS/Whisper starts.
3. **Whisper word-timing on KJV English.** "shalt", "hast", proper-noun Hebrew names will mistime on `base`. Upgrade to `small.en` after canary if needed.
4. **`vad_filter` eats narration starts.** Keep `vad_filter=False` so word offsets align with the muxed audio from t=0.
5. **Windows subtitle path escaping.** Colon must be backslash-escaped *inside* the filter string. Unit-test `_escape_subtitle_path()`.
6. **Disk:** ~2.4GB intermediates per topic. Default delete after success unless `--keep-intermediates`.
7. **libass + Windows + fontsdir:** keep font path space-free. The path under `scripts/assemble/fonts/` is fine.

## Verification — 1-scene canary first

Must pass before scaling to 16:

1. Hand-craft `tests/fixtures/canary_manifest.json` with one already-downloaded Kling clip + 12-word narration.
2. `python scripts/assemble-video.py --manifest tests/fixtures/canary_manifest.json --topic canary --scenes 1 --aspect 16x9`
3. Inspect in order:
   - `output/audio/canary/scene_01.mp3` plays Daniel voice.
   - `output/subs/canary/scene_01.ass` opens as text; `\k` values sum ≈ MP3 duration.
   - `output/scenes_tmp/canary/scene_01.mp4` plays in VLC: looped video matches narration length, audio is narration (not original Kling track).
   - `output/renders/canary.mp4`: subtitles burned, yellow word advances with speech.
4. **The objective karaoke test:** pause at 5s and 10s. Exactly one word is yellow at each pause. Proves `\k` timing + `\1c` color override work together.
5. **3-scene subset** (`--scenes 3`) validates concat A/V sync. Listen at scene boundaries for clicks/gaps.
6. **Side-by-side parity test:** pick an already-rendered JSON2Video output (e.g. the 2026-05-16 Edom 1-scene smoke at `https://json2video-cdn1.s3.amazonaws.com/clients/9DS66w8oSB/renders/2026-05-16-70921.mp4`), feed the same Kling URL + narration through the new assembler, watch both. They should be visually indistinguishable on subtitles + audio levels.

## Effort breakdown

| Phase | Time |
|---|---|
| FFmpeg install + Windows path-escape spike | 30 min |
| `manifest.py` + parallel `download_clips.py` | 45 min |
| `tts.py` (copy from `generate-narration.py`) | 20 min |
| `transcribe.py` (flip `word_timestamps`, singleton load) | 20 min |
| `ass_writer.py` (header + per-word overrides + chunking + BGR hex) | 90 min |
| `ffmpeg_build.py` (Pass A + B + path escaping) | 75 min |
| 9:16 aspect variant (crop strategy first, blur-pad in follow-up) | 60 min |
| `assemble-video.py` orchestrator + argparse | 30 min |
| 1-scene canary debug loop | 60 min |
| 3-scene + 16-scene validation | 60 min |
| **Total** | **~8 hours / 1 full day** |

The Python plumbing is trivial. The ASS karaoke timing + first-render FFmpeg debugging will eat most of the day.

## Honest cost math

20-min long-form ≈ 16,500 chars Daniel narration:

- `eleven_multilingual_v2` Creator tier (100K chars/mo, $22/mo): **~$3.63 / render**
- `eleven_multilingual_v2` Pro tier (500K chars/mo, $99/mo): **~$3.27 / render**
- `eleven_multilingual_v2` PAYG overage: **~$5.00 / render**
- `eleven_turbo_v2` (~50% cheaper, quality A/B needed): **~$1.50-2.50 / render**

| Today | With local assembler (`_multilingual_v2`) | With local assembler (`_turbo_v2`, if A/B passes) |
|---|---|---|
| $7-12/video total | $6-10/video total | $4.50-7/video total |

**Net savings: ~$1-2/video on the JSON2Video swap alone.** The bigger lever is the Turbo A/B (could double the savings if Daniel quality holds on Turbo). The biggest non-dollar lever is the dependency removal.

## Open questions to resolve at kickoff

1. Does the upstream `--skip-json2video` patch apply `voice_speed=0.9` client-side, or expect the assembler to apply it via ElevenLabs `voice_settings.speed`? Confirm with the ai-bible-gospels Claude before locking the TTS call shape.
2. Should `clips_manifest.json` include `prompt` + `motion` per scene for failure forensics? Recommended yes — cheap to add, valuable when debugging.
3. Turbo vs Multilingual A/B: run as a canary detour on day one if budget matters; defer if shipping speed matters more.

## Critical files at kickoff time

**New:**

- `scripts/assemble-video.py` (orchestrator)
- `scripts/assemble/manifest.py`
- `scripts/assemble/download_clips.py`
- `scripts/assemble/tts.py`
- `scripts/assemble/transcribe.py`
- `scripts/assemble/ass_writer.py` (highest risk)
- `scripts/assemble/ffmpeg_build.py`
- `scripts/assemble/durations.py`
- `scripts/assemble/fonts/Oswald-Bold.ttf` (shipped)
- `tools/ffmpeg/` (bundled FFmpeg, gitignored) OR system install
- `tests/fixtures/canary_manifest.json`

**Modify:**

- [`requirements.txt`](../requirements.txt) — add `faster-whisper`, `av`, `requests`
- [`.gitignore`](../.gitignore) — add `tools/ffmpeg/`, `output/scenes_tmp/`, `output/clips/`, `output/audio/`, `output/subs/`

**Reference (reuse pattern, don't import):**

- [`scripts/generate-narration.py`](../scripts/generate-narration.py) — TTS request shape
- [`scripts/transcribe-narrations.py`](../scripts/transcribe-narrations.py) — Whisper load pattern (flip `word_timestamps` to True)
- [`scripts/probe-clips.py`](../scripts/probe-clips.py) — PyAV duration probe
- [`scripts/render-via-pipeline.py`](../scripts/render-via-pipeline.py) — argparse / subprocess / env-injection pattern

**Read-only dependency (separate Claude session owns):**

- `c:\Users\Claude\ai-bible-gospels\workflows\custom-script\generate.py` — needs `--skip-json2video` flag added to dump the manifest

## Out of scope (explicitly)

- Modifying ai-bible-gospels (separate Claude session handles the upstream `--skip-json2video` flag).
- Replacing the existing `add-covers` post-production skill — `--post-produce` chains into it unchanged.
- Replacing Remotion `src/anchor-doc/` or `src/cta-overlay/` — different shape of work (motion graphics, not clip-stitching).
- Melanated-character / no-text rules — already enforced upstream by [`script-to-scenes.py`](../scripts/script-to-scenes.py).

## Related docs

- [custom-script-2.0.md](custom-script-2.0.md) — the verbatim-preserving render pipeline this assembler plugs into
- [script-format-v2.md](script-format-v2.md) — authoring format upstream of the manifest
- [remotion-video-framework.md](remotion-video-framework.md) — alternative framework for motion-graphics videos (not cinematic Kling stitching)
