---
name: Probe asset durations BEFORE building any video timeline
description: Two distinct bugs (clip freezes + narration gaps) on anchor doc v1 both caused by trusting shot-list timestamps without measuring actual asset durations
type: feedback
originSessionId: 0734df78-6a4b-4eea-9432-c912278f58f1
---
For any Remotion (or other timeline-based) video build: probe the actual duration of every input asset BEFORE writing the timeline code. Use `mutagen` for MP3/MP4 durations:

```python
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
print(MP3(path).info.length)   # narration MP3
print(MP4(path).info.length)   # video clip
```

**Why:** anchor doc v1 (2026-05-07) had two distinct bugs that only showed up at minute 10 of a 30-minute render — both rooted in skipped duration probes:

1. **Clip-duration mismatch → frozen frames.** Shot list said "use 15s of 675_miles clip at 0:45-1:00". Actual clip was 10.5s. Remotion silently froze on last frame for 4.5s. Five other clips had the same bug; biggest was W_Day_39 (30s source) asked for 70s in Beat 4 → 40s frozen.

2. **Narration-duration mismatch → silent gaps.** Shot list assumed continuous narration. Real TTS MP3s were 71.8/19.7/37.6/82.4/53.9/68.1/38.5 sec — sum = 6:12 of audio in a 13:30 doc. Beat 2→3 had a 70s silent gap; Beat 4→CTA had an 80s gap. Both audible immediately on playback.

**How to apply:**
- BEFORE writing `timeline.ts` (or equivalent timeline code), probe every audio + video asset and write the durations into a comment block at the top of the file.
- Size every clip slot's `duration` ≤ source duration. Use `Math.round(actualSeconds * FPS)` literals where the source is short, not "approximate" round numbers from the shot list.
- Tile narration tracks contiguously by their actual durations. Don't trust shot-list narration timestamps — they assume continuous audio that real TTS doesn't produce.
- Smoke-render the first 45-60 seconds before kicking off a 30-50 min full render. Catches duration bugs in 2 min instead of 35.

`docs/remotion-video-framework.md` §Pre-flight Checklist has the runnable commands.
