# Custom Script 2.0 — Verbatim-Preserving Render Pipeline

Production tooling for paste-exact rendering through the ai-bible-gospels FLUX → Kling → JSON2Video pipeline. **Bypasses the Claude AI scene-generator step that paraphrases scripture.**

**Status:** Verified 2026-05-16 — 1-scene smoke test rendered successfully end-to-end with Daniel voice + Kling v1.6 + 16:9. Test MP4: https://json2video-cdn1.s3.amazonaws.com/clients/9DS66w8oSB/renders/2026-05-16-70921.mp4

---

## Why this exists

On 2026-05-16, we wrote a 20-min Edom long-form script with verbatim 1611 KJV pulled from `docs/1611KjvW_apocrypha - Copy.pdf`, pasted it into the Custom Script Mode web UI, and the pipeline's Claude AI scene-generator **paraphrased 22 of 39 scenes** — collapsing verbatim KJV into 1-2 sentence summaries and appending a contaminating sentence to the locked hook formula. Both violate hard rules (`docs/viral-formula-deuteronomy-28.md:29-38` + global CLAUDE.md "verses verbatim, never paraphrased").

Custom Script 2.0 solves this by skipping Claude entirely — you author scenes (narration + image prompt + motion + lighting) in [Script Format v2](script-format-v2.md), and a converter emits the exact `scenes.json` that `generate.py` accepts via its bypass path.

## When to use which mode

| Mode | When | Trade-off |
|---|---|---|
| **Custom Script Mode (web UI)** at `localhost:8000/custom` | Loose concept → fully creative video. Letting Claude interpret a topic. Iterating on small renders with retry / fix-a-scene support. | LLM paraphrases scripture. Don't use for verbatim-load-bearing scripts. |
| **Biblical Cinematic Mode (web UI)** at `localhost:8000` | Pure KJV chapter → cinematic narration of that chapter, word-for-word. | Narration IS the scripture; visuals are Claude-generated. Good for chapter readings, less control over visual specifics. |
| **Custom Script 2.0 (this repo)** | Verbatim scripture + specific visual direction required. Long-form deep dives, hook-formula content, anything where the EXACT words matter. | No retry / fix-a-scene from CLI; failed renders re-run from scratch. |

## File map

| File | Purpose |
|---|---|
| [docs/script-format-v2.md](script-format-v2.md) | Format spec for authored `.txt` scripts |
| [scripts/script-to-scenes.py](../scripts/script-to-scenes.py) | Converter: `.txt` → `scenes.json` (auto-splits >900 words, auto-injects melanated keywords on human-figure scenes, appends safety suffix) |
| [scripts/render-via-pipeline.py](../scripts/render-via-pipeline.py) | Thin wrapper around `generate.py` — pins Daniel voice + Kling model selection |
| `drafts/<topic>-longform-<date>.txt` | Authored scripts in v2 format |
| `output/scenes/<topic>-*-scenes.json` | Converter output (gitignored — regenerable) |
| `C:/Users/Claude/ai-bible-gospels/workflows/custom-script/generate.py` | Pipeline CLI — accepts our `scenes.json` via the bypass path. Carries the `--voice-id` + `--kling-model` flags we added on 2026-05-16 (~8 lines total). |

## Workflow (the only 3 commands you need)

```bash
# 1. Author the script in Script Format v2 (see docs/script-format-v2.md for format)
# Example: drafts/edom-genesis49-longform-2026-05-16.txt

# 2. Convert to scenes.json (auto-splits long scripts into Part 1 / Part 2)
python scripts/script-to-scenes.py drafts/edom-genesis49-longform-2026-05-16.txt --out-dir output/scenes/

# 3. Render. ALWAYS do the cheap 1-scene gate first, then production model.
python scripts/script-to-scenes.py drafts/edom-genesis49-longform-2026-05-16.txt --first-n 1 --out-dir output/scenes/
python scripts/render-via-pipeline.py output/scenes/edom-genesis49-first1-scenes.json --kling-model v1.6
# (watch the output MP4; verify Daniel voice, 16:9, verbatim subtitles, hook fidelity)

# Once verified perfect:
python scripts/render-via-pipeline.py output/scenes/edom-genesis49-part1-scenes.json --kling-model o3-pro
python scripts/render-via-pipeline.py output/scenes/edom-genesis49-part2-scenes.json --kling-model o3-pro
```

## Kling model cost / quality matrix

(Costs are rough per-scene — the actual fal.ai price card is authoritative.)

| Model | When to use | Per-scene cost (rough) | Per-scene duration |
|---|---|---|---|
| `v1.6` | **Cheap pipeline gate.** 1-scene test renders. Validates structure, not aesthetics. | ~$0.30 | 10 s |
| `v2.1` | Mid-tier production for less-critical content (Shorts B-rolls). | ~$0.50 | 10 s |
| `v3.0` | Pipeline default. Decent quality without the premium tier. | ~$0.69 | 15 s |
| `v3.0-pro` | Premium quality. Use for hero content. | ~$1.20 | 15 s |
| `o3` | Newest model, standard tier. | ~$1.00 | 15 s |
| `o3-pro` | **Best quality available.** Use for production long-form (Bible in Black archetype renders). | ~$1.80 | 15 s |

Wrapper default is `v3.0` for safety; pass `--kling-model o3-pro` explicitly for production runs.

## Locked rules the converter enforces

1. **Verbatim narration.** Whatever you put inside `Narrator: "..."` goes into the video word-for-word. No LLM rewrite.
2. **Melanated character auto-injection.** Visual cues that mention humans without melanated keywords get the rule appended:
   `dark-brown to deep-brown skinned, melanated African American complexion, wool-textured / tightly curled hair, NOT white, NOT pale, NOT Caucasian`
   Person-detection heuristic — landscape/object scenes don't get spurious injections. Each injection is logged at convert time.
3. **No-text safety suffix.** Always appended to imagePrompt:
   `no text, no letters, no symbols, photorealistic, cinematic, 8K detail`
   FLUX can't render text reliably; subtitles handle on-screen text downstream.
4. **Daniel voice locked.** Wrapper passes `onwK4e9ZLuTAKqWW03F9` by default. Override with `--voice-id <other>` only when intentional.
5. **16:9 aspect locked.** For Shorts (9:16) we'd need to add `--aspect-ratio` (same pattern as `--voice-id` — future work).

## The small ai-bible-gospels edits (one-time, 2026-05-16)

To make the CLI usable for production we added:
- `--voice-id` flag (4 lines, `generate.py` lines ~180, 215, 304, 357)
- `--kling-model` flag with `KLING_MODELS` URL map (12 lines, copied verbatim from `router.py:33-39`)

Both default to the prior hard-coded values — the web UI's voice picker and Kling model dropdown still work identically. The edits are isolated to `generate.py`; `router.py`, `server.py`, and the `recover*.py` scripts are untouched.

If you need to roll either flag back: `git revert` the two commits in the ai-bible-gospels repo. Or pass the flags with their old hard-coded values to restore the previous behavior at runtime.

## What we lose vs. the web UI

| Feature | Web UI | Custom Script 2.0 |
|---|---|---|
| Verbatim narration | ❌ Claude paraphrases | ✅ |
| Verbatim image prompts | ❌ Claude rewrites | ✅ |
| Daniel voice | ✅ pickable | ✅ (--voice-id default) |
| Kling model select | ✅ radio buttons | ✅ (--kling-model) |
| Aspect ratio select | ✅ 16:9 / 1:1 / 9:16 | ❌ hard-coded 16:9 |
| Retry from failed scene | ✅ | ❌ re-run whole pipeline |
| Fix a Scene panel | ✅ | ❌ |
| Render history persistence | ✅ | ❌ (output URLs print to stdout only) |
| Auto-split >900 words | ✅ pipeline-side | ✅ converter-side |

For long-form production where exact narration matters, the trade-offs are worth it. For exploratory creative work, the web UI's retry/fix loop is more efficient.

## Related docs

- [script-format-v2.md](script-format-v2.md) — authoring format
- [viral-formula-deuteronomy-28.md](viral-formula-deuteronomy-28.md) — hook formula rules (locked)
- [competitors.md](competitors.md) — archetypes (Bible in Black, AI Bible Sagas)
- [remotion-video-framework.md](remotion-video-framework.md) — alternative framework for motion-graphics videos (not cinematic)
- [project-plan.md](project-plan.md) — overall channel strategy + Phase 4B long-form plan
