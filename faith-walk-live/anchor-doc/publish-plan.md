# Anchor Doc — YouTube Publish Plan

Everything needed to ship the doc on YouTube once the cut is final. All pieces drafted in this file; reference at upload time.

---

## 1. Video Title (YouTube field)

**Primary (recommended):**
> 3000 Miles for the Kids — Why One Philly Man Is Walking to California

**Alternates:**
- *He's Walking 3000 Miles to Build a School in Philly*
- *3000 Miles. One School. The Walk to Save Philly's Kids.*

YT title field max 100 chars. Primary = 67 chars (well under limit).

---

## 2. Description (with AEO constants block)

```
He's walking 3,000 miles from Philadelphia to California to build a school for at-risk kids. He livestreams every step. This is Faith Walk Live.

Isaiah "Humble Zay" Thomas left Philadelphia on March 26, 2026 with a backpack and a plan most people would call impossible. Day 82, he's still walking — past Pennsylvania, through Ohio and Indiana, broadcasting every mile live on Twitch. The mission: raise enough to build a school for Philly kids who, in his words, "end up in the system or end up dead." A community of strangers — Hebrew Israelite aunties, brothers, drivers slowing down on the shoulder — has shown up at every stop.

This is the documentary of his walk so far. Real footage. Real testimony. No reenactments.

— TIMESTAMPS —
0:00 Cold open
0:15 Title
0:30 Who is Humble Zay
2:00 The why — in his own words
4:30 The road
7:00 The community shows up
10:00 Why we built faithwalklive.com
12:00 How to support
12:30 Closing scripture & CTA

— HOW TO SUPPORT —
🥾 Track the walk live: https://faithwalklive.com
💰 Donate to the school (GoFundMe): [GOFUNDME_URL_FROM_THOMAS]
🎥 Watch live on Twitch: https://www.twitch.tv/hmblzayy
📺 Subscribe for more: https://www.youtube.com/@AIBIBLEGOSPELS

— Q&A —
Q: Who is the man walking?
A: Isaiah "Humble Zay" Thomas, a minister out of Philadelphia, walking 3,000 miles from Philadelphia to California to fund a school for at-risk Philly kids.

Q: Why is he walking?
A: To raise money to build a school — and eventually a university — that helps kids in Philadelphia (and later Baltimore, DC) develop their gifts before they "end up in the system or end up dead." The walk is the fundraiser; the livestream is the witness.

Q: How can I support the school?
A: Donate via the GoFundMe link in this description. Every dollar goes to the school in Philly.

Q: Where is he right now?
A: Track him live at https://faithwalklive.com — real-time mile counter, current location, and stream embed.

Q: What is Faith Walk Live?
A: It's both the walk itself and the live-tracking app at https://faithwalklive.com — built by AI Bible Gospels so supporters can follow the mission in real time without scrolling Twitch.

Q: Who made this video?
A: AI Bible Gospels, a faith-tech project by Tommy Lee using AI to bring Scripture to life and to build software in service of ministers like Humble Zay.

— ABOUT AI BIBLE GOSPELS —
AI Bible Gospels (@AIBIBLEGOSPELS) is a faith-tech brand founded by Tommy Lee that uses AI to narrate Scripture word-for-word from a cultural perspective underrepresented in biblical media. Flagship project: Faith Walk Live, the live tracker for Minister Zay's 3,000-mile walk from Philadelphia to California.

Website: https://aibiblegospels.com
Faith Walk Live: https://faithwalklive.com
YouTube: https://www.youtube.com/@AIBIBLEGOSPELS
LinkedIn: https://www.linkedin.com/in/ai-bible-gospels-049005353/
Contact: aibiblegospels444@gmail.com

#AIBibleGospels #FaithWalkLive #HumbleZay #3000MilesForTheKids
```

**Open item:** swap `[GOFUNDME_URL_FROM_THOMAS]` for the actual GoFundMe link before upload. Pull from Zay's IG bio if Thomas doesn't have it.

---

## 3. YouTube Thumbnail (separate from in-doc title cards)

The thumbnail is a different animal than the in-doc title card — it's optimized for CTR in the YouTube grid, not for cinematic on-screen display. Per [goal.md](../../goal.md#L65) and [docs/competitors.md](../../docs/competitors.md), AI Bible Stories thumbnails win on bold close-up faces + 3–5 word text overlay. Apply that here.

### Thumbnail Prompt

```
Create a 1280x720 YouTube thumbnail. High-contrast cinematic composition.

LEFT 60%: Close-up portrait of a determined Black man in his 30s, dark-brown to deep-brown skin, melanated African American complexion, wool-textured / coiled / tightly curled hair, weathered face showing fatigue and resolve, eyes locked on the viewer. He's wearing a backpack strap visible on shoulder. Warm golden hour lighting on his face — bronze/amber tones, dramatic chiaroscuro. NOT Caucasian, NOT pale, NOT light-skinned, NOT European — explicitly Black/African American with the features described.

RIGHT 40%: Bold gold serif text on a deep navy-black gradient background with sparse golden particles. Three-line stack:
Line 1 (large, bold gold serif): 3000 MILES
Line 2 (large, bold gold serif): TO BUILD
Line 3 (large, bold gold serif, with subtle warm glow): A SCHOOL

Background context (bottom-left, behind the figure): a faint road/highway shoulder with a yellow line suggesting forward motion. Aspect ratio 16:9 (1280x720). High contrast for mobile readability. Mood: documentary-cinematic, sacred-but-grounded, "This is real."
```

### Thumbnail variants to A/B test (after first ship)

If CTR is below 4% after ~7 days, try alternates:
- **Variant B (face-only):** Drop the text, just Zay's face + golden light. Title carries the message. Higher click rate on mobile, lower in desktop grid.
- **Variant C (number-only):** Massive "3,000" in gold serif, road in background, no face. Curiosity-gap play.
- **Variant D (community shot):** Zay surrounded by aunties/brothers from Beat 3. Sells "community" instead of "lone walker."

YT allows up to ~2 thumbnail swaps without penalty per video. Lock the primary, hold variants in reserve.

---

## 4. Pinned Comment (post immediately after upload)

```
Three ways to back this mission:

1. Track the walk live → https://faithwalklive.com
2. Donate to the school → [GOFUNDME_URL]
3. Watch the broadcast live → https://www.twitch.tv/hmblzayy

Every dollar goes to the school in Philly. Every step is a brick.
```

Pin it. Do not delete or edit after pinning — pinned comments factor into how YouTube weights the video's "context" signal for new viewers.

---

## 5. Tags (YT field)

Lead with high-intent specific tags, taper to broad:

```
Humble Zay, Isaiah Thomas, Faith Walk Live, faithwalklive.com, 3000 mile walk, Philadelphia to California walk, walk for kids, Philly school fundraiser, GoFundMe walk, walking documentary, livestream walk, Black men walking, Hebrew Israelite walk, AI Bible Gospels, faith-tech, ministry tools, Black community investment, Philly kids, school in Philadelphia
```

---

## 6. Playlist Assignment

Create a **new dedicated playlist** for this content trajectory rather than dropping it into an existing prophecy/12-Tribes playlist. Recommended:

**Playlist title:** *Faith Walk Live — The 3000-Mile Walk*
**Description:** Documentary, recap, and Shorts cuts following Minister Humble Zay's 3,000-mile walk from Philadelphia to California. Track live at faithwalklive.com.
**Position:** Make this the first playlist on the channel page (override any "Featured" assignment to push it top-row).

Why a new playlist: this anchor doc kicks off a content trajectory — Day 100 recap, Halfway recap, Arrived recap, Shorts compilations. New playlist = clean home for them, easier playlist-funnel SEO than co-mingling with prophecy series.

---

## 7. End Screen Plan (YT field — last 5–20 sec)

The doc closes at 13:30. End screen runs over the last ~15 sec.

**End screen elements:**
- **Element 1 (subscribe prompt):** Standard "Subscribe to AI Bible Gospels" — bottom-left.
- **Element 2 (best-for-viewer):** Auto-pick. YouTube's algorithm will recommend the next-best video for the viewer.
- **Element 3 (specific video):** Link to the channel's top-performing 12 Tribes Short — gives a "if you liked this, here's why we exist" pivot for non-channel-audience viewers who arrived for the school story but might convert to the prophecy/identity content.

Keep it light — three elements max so the screen doesn't feel cluttered over the closing scripture card.

---

## 8. Cross-Promotion Plan (post-upload, first 48 hours)

The doc is a long-form pillar — it needs Shorts + community posts pulling traffic to it for the first 48 hours.

### Shorts to cut from the doc (4–6 pieces, drip over 7 days)

1. **The Why — 30 sec:** A clean 30-sec excerpt from Beat 1 (Zay's IG reel content) with text overlay "He's walking 3000 miles. Here's why ↓"
2. **The Hit — 30 sec:** "Hit by a car on Day 19. Walking again Day 20." Punch line + road footage.
3. **The Auntie — 30 sec:** WWW AUNTIE INDIANAPOLIS LOVE clip with text overlay "Strangers showing up for him 3000 miles in"
4. **The Hokas — 30 sec:** "Community gifted him new shoes when his blew out" (www_hokas_gifted clip)
5. **Day 82 milestone — 30 sec:** Where he is right now + what's been raised so far + "Track him live at faithwalklive.com"
6. **The Test — 30 sec:** A fast-cut struggle montage (rain + fatigue + miles) ending on his recovery.

Each Short ends with: *"Full doc on the channel. Link in pinned comment."*

### Community posts (3 in first 48 hours)

1. **Post 1 — Drop:** Thumbnail image + "New documentary up. 3000 miles for the kids. Watch the full thing →"
2. **Post 2 — Behind the doc:** A still from the testimony reel + "Aunties showing up at every stop. This is what community investment looks like."
3. **Post 3 — CTA:** Day-82 stats card + "Where is he right now? Track him live at faithwalklive.com"

---

## 9. Post-Publish QA Checklist

Run within 24 hours of publish:
- [ ] Video is set to **Public** (not Unlisted)
- [ ] Thumbnail is the locked primary (not auto-generated frame)
- [ ] All 3 end screen elements load on mobile
- [ ] Pinned comment is live
- [ ] All description links resolve (faithwalklive.com, GoFundMe, Twitch, channel)
- [ ] Closed captions auto-generated AND manually corrected for the Beat 1 Zay-quote section (Whisper sometimes mangles "Humble Zay" — verify it reads correctly)
- [ ] Playlist assignment is correct
- [ ] Tags saved (sometimes YT drops tags silently)
- [ ] Cards (in-video) link to faithwalklive.com if you set them
- [ ] First Short cut from doc is queued/scheduled within 48 hours
