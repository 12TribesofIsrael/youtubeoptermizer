---
name: feedback_brand_line_no_ai_disclosure_text
description: "Since 2026-10-31 no YT description/playlist/template mentions AI voice cloning, AI artwork, \"uses AI to…\", or Faith Walk Live/Minister Zay as flagship; disclosure moves to containsSyntheticMedia flag"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 194842f3-9913-4d5e-8d1d-9fdbada921aa
  modified: 2026-11-04T13:43:26.787Z
---

Tommy's call 2026-10-31 (biblerevamp commit 5d914c7): channel copy says only "This narration is Tommy Lee's voice." Brand line is now just "AI Bible Gospels (@AIBIBLEGOSPELS) is a faith-tech brand founded by Tommy Lee." Stripped: AI voice cloning, "artwork is AI-generated", "uses AI to narrate/bring Scripture…", "Flagship project: Faith Walk Live… Minister Zay's walk". The AI disclosure lives in `status.containsSyntheticMedia=true` instead. biblerevamp `src/scrub_descriptions.py` applied it to all 272 live videos (scrub_state.json = 272 done, verified 2026-11-04).

**Why:** Tommy's decision; the text disclosure is replaced by YouTube's own synthetic-media flag.

**How to apply:** YouTube scripts in this repo were fixed 2026-11-04 (aeo-bulk-update, aeo-yt-phase-b prompt, upload-eden-*, upload-anchor-doc footer, update-about-page now needs --force because Tommy hand-wrote the live About). Faith Walk *subject* content (anchor doc, FWL Shorts, narration) and the "Faith Walk Live: faithwalklive.com" link line were left alone, matching what the scrub kept. Still carrying old text: the IG/FB scripts (aeo-fb-bulk-update, aeo-ig-bulk-update, aeo-ig-pin-comment), which were out of scope since the decision was about the YouTube channel. Ask before re-running them. Live leftover: the Eden doc jnfMCN4cuv4 description reads "…Tommy Lee that bring Scripture to life…" (broken) and still has a CONTENT TRANSPARENCY block mentioning AI imagery. Supersedes the AEO constants block in [[project_aeo_description_rollout_2026]].
