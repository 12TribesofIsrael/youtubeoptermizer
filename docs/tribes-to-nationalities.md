# 12 Tribes → Modern Nationality Mapping

The canonical Hebrew Israelite identification of each tribe with a modern nationality, extracted verbatim from `G:/My Drive/AI BIBLE GOSPELS/Book Folders/12 Tribes Movie/The Prophecy Revealed/The Prophecy Revealed.txt`. This is the channel's foundational theology document.

**Use this mapping when writing FLUX/Kling prompts for any tribe-specific scene.** The figure should combine:
- Melanated Black Hebrew Israelite identity (the locked `aibgospels` LoRA style)
- The specific tribe's modern-nationality features (skin tone variation, garment patterns, regional markers below)

## The Mapping

| Tribe | Modern Nationality | Visual Markers (for prompts) |
|---|---|---|
| **Judah** | American Blacks (African American) | Deeply melanated dark brown skin, locs / braids / afro, modern AA features when contemporary, royal/lion sigil when biblical (Lion of Judah). |
| **Benjamin** | West Indians (Jamaican, Caribbean) | Caribbean / West Indian features, dreadlocks common, vibrant traditional fabrics, reggae/dancehall aesthetic for modern context. |
| **Levi** | Scattered — Africa + U.S. priestly line | Tall, lean African features, ceremonial priestly vestments (ephod, tzitzit) when biblical, scattered/diaspora in modern context. |
| **Reuben** | Seminoles + Eastern Native Americans | Native American features with melanated skin (per BHI), traditional Seminole patchwork in modern context, ancient Hebrew robes when biblical. |
| **Simeon** | Dominicans (Hispaniola) | Dominican features, mixed Afro-Caribbean phenotype, melanated. Hispaniola = Dominican Republic + Haiti context. |
| **Issachar** | Aztecs / Mexicans | Mexican / Aztec features with deeply melanated skin (per BHI), ancient Aztec headdress and feathered regalia when historical, modern Mexican features when contemporary. |
| **Zebulun** | Mayans | Mayan features with melanated skin, jade jewelry, traditional Mayan textiles, pyramid/temple settings, Central American context (Guatemala/Yucatan). |
| **Gad** | North American Indians (300+ tribes) | Native American features with deeply melanated skin (per BHI), war bonnet / feathered crown ("teareth the arm with the crown of the head"), lion-like stance, Plains/Eastern Woodlands aesthetic. |
| **Naphtali** | Chileans + Polynesians | South Pacific Polynesian features with melanated skin OR Chilean features, coconuts/taro imagery, South Pacific island settings, "satisfied with favour, full with blessing." |
| **Asher** | (Americas — specific group less explicit in source) | Default to generic melanated Black Hebrew Israelite Americas-diaspora features. |
| **Manasseh** | Cubans | Cuban features with deeply melanated skin (per BHI), Afro-Cuban phenotype, modern Cuban context. |
| **Ephraim** | Puerto Ricans | Puerto Rican / Boricua features with melanated skin (per BHI), Caribbean aesthetic, sometimes altar/idol imagery in critique context. |
| **Dan** | NOT a tribe in BHI canon — considered Gentiles | Per the source: "The tribe of Dan is now considered Gentiles because of the Unrighteousness of their forefathers." Excluded from the 12. |

**Total active tribes:** 12 (Joseph splits into Ephraim + Manasseh, Dan is replaced).

## How to use this in prompts

For any scene depicting a specific tribe, build the prompt as:

```
aibgospels [generic-archetype] from the tribe of [Tribe], [biblical-era OR modern-era] 
context, [tribe-specific visual markers from table above], 
[scene-specific composition], 
photorealistic, cinematic, 8K detail, shot on RED V-Raptor, hyper-detailed skin texture
```

### Example: Biblical-era scene of Tribe of Issachar

```
aibgospels israelite from the tribe of Issachar, ancient Aztec-influenced ceremonial 
robes with feathered crown, deeply melanated dark brown skin, locs and ritual face paint, 
standing atop a stepped temple at dawn, scrolls and astronomical instruments at his feet, 
photorealistic, cinematic, 8K detail, shot on RED V-Raptor, hyper-detailed skin texture 
and fabric weave, natural film grain
```

### Example: Modern-context scene of Tribe of Benjamin

```
aibgospels israelite from the tribe of Benjamin, contemporary West Indian / Jamaican 
features, deeply melanated dark brown skin, dreadlocks, traditional Caribbean-inflected 
modern clothing, standing in a sun-drenched Kingston street, photorealistic, cinematic, 
8K detail, shot on RED V-Raptor
```

## What this is NOT

- This mapping is the channel's theological perspective, used for visual production. It is not making claims about modern political identity outside the BHI framework.
- The trained LoRA does NOT learn the tribe-specific looks (we lack 20-30 photoreal refs per tribe). Tribe specificity comes from prompt engineering using this mapping until we have per-tribe photoreal training data.
- Dan is excluded per the source. Use 12: Judah, Benjamin, Levi, Reuben, Simeon, Issachar, Zebulun, Gad, Naphtali, Asher, Manasseh, Ephraim.

## Related

- Source theology: `G:/My Drive/AI BIBLE GOSPELS/Book Folders/12 Tribes Movie/The Prophecy Revealed/The Prophecy Revealed.txt`
- Channel character rule: [CLAUDE.md](../CLAUDE.md) Character Depiction Rule (MANDATORY)
- LoRA training: [scripts/train-flux-lora.py](../scripts/train-flux-lora.py) — trains `aibgospels` trigger word on photoreal Israelite refs
- Esau/Edom inverse rule: [feedback_esau_edom_caucasian_rule.md](~/.claude/projects/c--Users-Claude-youtubeoptermizer/memory/feedback_esau_edom_caucasian_rule.md) memory
