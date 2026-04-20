---
name: Aspect ratios — short-form vs long-form
description: Quick reference for vertical/square/horizontal dimensions and JSON2Video keywords, and why TikTok demands 9:16
type: reference
originSessionId: 3f97120f-9e3e-4e35-89e8-cf5aa8126068
---
Quick reference for video aspect ratios and the JSON2Video keyword used to request each.

| Aspect | Dimensions | Form | Native platforms | JSON2Video keyword |
|---|---|---|---|---|
| **9:16 vertical** | 1080 × 1920 | **SHORT** | TikTok, Instagram Reels, YouTube Shorts | `instagram-story` |
| **1:1 square** | 1080 × 1080 | middle | Facebook / Instagram feed | `instagram-feed` |
| **16:9 horizontal** | 1920 × 1080 | **LONG** | YouTube desktop, TV | `full-hd` |

## Why this matters on TikTok

TikTok's feed is a 9:16 vertical canvas. A 9:16 video fills the entire phone screen with zero black bars — full immersive scroll experience, maximum thumb-stopping power. A 16:9 video uploaded to TikTok gets pillar-boxed or letter-boxed (black bars top + bottom) and occupies only ~33% of the phone screen. Viewers perceive it as low-effort, swipe within 1 second, and TikTok's algorithm throttles distribution.

This is exactly what happened to Clone #1 (2026-04-19 tiktok.com/.../7630560963900558622): 14 likes / 4 shares / 0 comments in 18h vs the seed viral's 447 / 361 / 31 at the same age. The clone was rendered at `"full-hd"` (1920×1080 = 16:9) — algorithm-death on TikTok.

## Rule for any short-form content we produce

**Always render at 9:16 vertical (1080×1920) = JSON2Video's `"instagram-story"` keyword** for TikTok, Reels, and YouTube Shorts. Only use `"full-hd"` (16:9) for long-form YouTube desktop content.

## Source of truth

- Make.com seed template uses `"resolution": "instagram-story"` — confirmed in `G:/My Drive/AI BIBLE GOSPELS/Make.com Master/Master Shorts/MasterCSV.json`
- User confirmed the aspect-ratio rule on 2026-04-20 during diagnosis of Clone #1's flop
