---
name: Default video clips to UNMUTED — silence reads as broken
description: When building Remotion video compositions, never default clips to mute=true; only mute when narration is actively replacing the clip's audio for that segment
type: feedback
originSessionId: 0734df78-6a4b-4eea-9432-c912278f58f1
---
For any Remotion-based video work (Shorts, recaps, anchor doc, future projects): **default clips to play their natural audio**. Only set `mute: true` when a narration MP3 or another audio track is actively replacing the clip's audio during that segment.

**Why:** silence in a mobile-vertical 30s Short reads as broken, not stylistic. Viewers think the audio is missing and swipe away. Even fast-cut montages need ambient (rain, road noise, voices) to feel real.

**How to apply:**
- In `shorts.ts` / `timeline.ts` `ClipEntry` configs, leave `mute` undefined (defaults to false in `Short.tsx` / `DocumentaryTimeline.tsx`).
- Only set `mute: true` when there's an explicit narration track playing for that exact frame range.
- The publish-plan / shot list saying "text-overlay-driven" or "punch line + footage" does NOT mean mute the audio — text overlays sit ON TOP of the natural ambient.
- For anchor-doc-style long-form, narration sections (Beat 1 setup, Beat 2 road) DO mute clips because Daniel's voice is the spine — that's correct usage. Beat 3 community montage has no narration over it for parts → those clips stay unmuted.

**Pattern that worked (anchor doc):** `mute: true` on Beat 1/2/4 b-roll under Daniel narration; `mute` undefined on Beat 3 community montage where no narration plays. Same logic should apply to all future video work.

**Pattern that bit us:** Shorts s2 (The Hit), s5 (The Milestone), s6 (The Test) all had `mute: true` because publish-plan called them "text-driven." All three rendered as 30s of silence. Re-rendered unmuted, all three felt right.

`docs/remotion-video-framework.md` §Pre-flight Checklist now has this as rule #3.
