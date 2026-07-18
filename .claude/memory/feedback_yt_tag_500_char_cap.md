---
name: feedback_yt_tag_500_char_cap
description: YouTube videos.insert rejects tags with invalidTags when the COMBINED tag length exceeds ~500 chars (incl. quotes+commas); keep tag lists lean
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e880ab15-018e-4a34-98c6-9e572112c856
---

YouTube's `videos().insert` returns HTTP 400 `invalidTags` ("The request metadata
specifies invalid video keywords.") when the **combined** length of all tags exceeds
~500 characters. The count includes the double-quotes YouTube adds around any multi-word
tag (+2 each) and the commas between tags — so a raw sum near 490 can still fail.

**Why:** bit us 2026-07-17 uploading the Eden→Timbuktu full doc — a 30-tag list (raw ~489)
was rejected. Trimmed to 18 tags (raw ~302, effective ~349 with quotes+commas) and it went
through. The insert fails BEFORE the video resource is created, so it's a clean retry — no
orphan/duplicate video.

**How to apply:** before any `videos().insert`/`update_video`, keep the tag list to
~15-18 high-value tags and sanity-check length: `raw + 2·(multiword tags) + (n-1 commas) < 500`.
Prefer the few searches that actually convert over stuffing. Relates to [[feedback_canary_before_bulk]].
