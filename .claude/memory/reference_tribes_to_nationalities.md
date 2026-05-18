---
name: tribes-to-nationalities
description: "12 tribes → modern nationality mapping (Hebrew Israelite canon, source theology doc); used for converter auto-injection of tribe-specific visual markers"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9a9379a4-a54f-4582-892e-f286cf99730c
---

The channel's canonical 12-tribes-to-nationality mapping, sourced from `G:/My Drive/AI BIBLE GOSPELS/Book Folders/12 Tribes Movie/The Prophecy Revealed/The Prophecy Revealed.txt`. Used by `scripts/script-to-scenes.py` (`TRIBE_MARKERS` dict) to auto-inject nationality features when a tribe name appears in a `[Visual:]` cue.

## The Mapping

| Tribe | Nationality |
|---|---|
| Judah | African American |
| Benjamin | West Indian / Jamaican |
| Levi | Scattered priestly line (Africa + U.S.) |
| Reuben | Seminole / Eastern Native American |
| Simeon | Dominican (Hispaniola) |
| Issachar | Aztec / Mexican |
| Zebulun | Mayan |
| Gad | North American Indian (300+ tribes) |
| Naphtali | Chilean / Polynesian |
| Asher | Americas diaspora (less specific in source) |
| Manasseh | Cuban |
| Ephraim | Puerto Rican |
| Dan | NOT in 12 — considered Gentile per channel canon |

## Full mapping with visual markers + example prompts

Lives at `c:/Users/Claude/youtubeoptermizer/docs/tribes-to-nationalities.md`.

## How the converter uses it

Source `[Visual:]` cue mentions a tribe name → converter detects via regex → appends the tribe's nationality markers to imagePrompt AFTER the base Israelite identity stack. So:

```
Source: [Visual: A close-up on Judah — strong, melanated, ...]
                                      ↓
Result: ...Judah... Black Hebrew Israelite with rich African American complexion, 
        ..., from the tribe of Judah — African American features, deeply melanated 
        dark brown skin, locs or braids, royal Lion-of-Judah sigil and gold 
        accents when biblical...
```

## What this is NOT

The channel's theological position used for visual production. Not making claims about modern political identity outside the BHI framework.

Related: [[custom-script-2-pipeline]], [[canonical-identity-framework]].
