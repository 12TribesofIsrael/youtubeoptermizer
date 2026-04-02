# YouTube & Social Media Optimizer — AI Bible Gospels

Automation toolkit for the **AI Bible Gospels** (@AIBIBLEGOSPELS) YouTube channel and social media platforms. Uses YouTube Data API v3, Meta Graph API, and X API to manage content, metadata, captions, and cross-platform publishing.

---

## Channel Stats (March 30, 2026)

| Metric | Value |
|--------|-------|
| Subscribers | 5,910 |
| Total Views | 769,000+ |
| Videos | 238 |
| CTR | 4.06% (target: 6%+) |
| Niche | 12 Tribes of Israel, Hebrew Israelite identity, biblical prophecy |

---

## What This System Can Do

### YouTube
| Feature | Script | Command |
|---------|--------|---------|
| Full channel audit | `scripts/full-audit.py` | `python scripts/full-audit.py` |
| Check live metrics (subs, views, CTR) | `scripts/channel-status.py` | `python scripts/channel-status.py` |
| Bulk rename Part titles | `scripts/rename-parts.py` | `python scripts/rename-parts.py` |
| Fix broken em dash encoding | `scripts/fix-dashes.py` | `python scripts/fix-dashes.py` |
| Fix handle in titles | `scripts/fix-handle-titles.py` | `python scripts/fix-handle-titles.py` |
| Delete duplicate videos | `scripts/delete-duplicates.py` | `python scripts/delete-duplicates.py` |
| Delete Matthew 6 flood videos | `scripts/delete-matthew6.py` | `python scripts/delete-matthew6.py` |
| Delete short/low-performing videos | `scripts/delete-short-and-low.py` | `python scripts/delete-short-and-low.py` |
| Extract video transcripts | `scripts/extract-transcripts.py` | `python scripts/extract-transcripts.py` |
| AI-generate optimized titles | `scripts/generate-titles.py` | `python scripts/generate-titles.py` |
| Export current channel data | `scripts/export-current-data.py` | `python scripts/export-current-data.py` |
| Thumbnail priority list | `scripts/thumbnail-priorities.py` | `python scripts/thumbnail-priorities.py` |
| Check API quota remaining | `scripts/check-quota.py` | `python scripts/check-quota.py` |
| Upload custom thumbnails | `scripts/upload-thumbnails.py` | `python scripts/upload-thumbnails.py` |
| Create tribe-based playlists | `scripts/create-playlists.py` | `python scripts/create-playlists.py` |
| Reorganize existing playlists | `scripts/reorganize-playlists.py` | `python scripts/reorganize-playlists.py` |
| Generate scripture card images | `scripts/generate-scripture-cards.py` | `python scripts/generate-scripture-cards.py` |
| First-time OAuth setup | `scripts/connect.py` | `python scripts/connect.py` |
| Test YouTube API connection | `scripts/test-connection.py` | `python scripts/test-connection.py` |

---

### Facebook
| Feature | Script | Command |
|---------|--------|---------|
| Post 8 viral posts to Facebook Page | `scripts/facebook-post.py` | `python scripts/facebook-post.py --live` |
| Post 1 test post | `scripts/facebook-post.py` | `python scripts/facebook-post.py --live 1` |
| Dry run preview | `scripts/facebook-post.py` | `python scripts/facebook-post.py` |
| Update existing post captions | `scripts/meta-update-posts.py` | `python scripts/meta-update-posts.py facebook --live` |

---

### Instagram
| Feature | Script | Command |
|---------|--------|---------|
| Update all 538 post captions | `scripts/meta-update-posts.py` | `python scripts/meta-update-posts.py instagram --live` |
| Dry run preview | `scripts/meta-update-posts.py` | `python scripts/meta-update-posts.py instagram` |
| Update both FB + IG | `scripts/meta-update-posts.py` | `python scripts/meta-update-posts.py --live` |

> ⚠️ Instagram caption editing requires Meta App Review approval (pending). Run dry run until approved.

---

### X / Twitter
| Feature | Script | Command |
|---------|--------|---------|
| Post 8 viral tweets | `scripts/twitter-post.py` | `python scripts/twitter-post.py --live` |
| Post 1 test tweet | `scripts/twitter-post.py` | `python scripts/twitter-post.py --live 1` |
| Dry run preview | `scripts/twitter-post.py` | `python scripts/twitter-post.py` |

> ⚠️ X Free tier (Pay-per-use) does not support OAuth 1.0a posting. Use Repurpose.io for X until upgraded.

---

## Repurpose.io Integration

Repurpose auto-posts videos from Google Drive to X, Instagram, TikTok, and Facebook at 9am and 6pm daily.

- **Caption templates**: See `docs/repurpose-templates.md` — paste into each Repurpose workflow
- **Platform bios**: See `docs/repurpose-templates.md` — paste into each platform profile
- **Limitation**: Repurpose cannot edit existing posts or generate AI captions

---

## Platform API Status

| Platform | API Connected | Can Post New | Can Edit Existing |
|----------|--------------|--------------|-------------------|
| YouTube | ✅ | ✅ | ✅ |
| Facebook | ✅ | ✅ | ✅ |
| Instagram | ✅ | ✅ (via Repurpose) | ⏳ Pending App Review |
| X/Twitter | ✅ (keys saved) | ⚠️ Free tier limited | ❌ |
| TikTok | ❌ Not set up | ❌ | ❌ |

---

## Setup

### Prerequisites
- Python 3.8+
- Google Cloud project with YouTube Data API v3 enabled
- Meta developer app (AI Bible Gospels — App ID: 1452257036358754)
- X Developer account (console.x.com)

### Install
```bash
pip install -r requirements.txt
```

### Authenticate YouTube
```bash
python scripts/connect.py
```
Opens browser for Google OAuth. Token saved to `token.json`.

### Environment Variables
Copy `.env.example` to `.env` and fill in all keys:
```
META_ACCESS_TOKEN=         # Meta Graph API (expires ~60 days — refresh at developers.facebook.com/tools/explorer)
FACEBOOK_PAGE_ID=          # 601690023018873
INSTAGRAM_BUSINESS_ID=     # 17841454335324028
TWITTER_API_KEY=           # X Developer Console
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
TIKTOK_CLIENT_KEY=         # Not yet set up
TIKTOK_CLIENT_SECRET=
TIKTOK_ACCESS_TOKEN=
```

> ⚠️ Never commit `.env` — it contains live API keys. Only `.env.example` is committed.

---

## Project Structure

```
youtubeoptimization/
├── src/youtube/                  # YouTube API client and auth
│   ├── auth.py                   # OAuth 2.0 authentication
│   └── client.py                 # YouTubeClient — list, update, delete, thumbnails
├── scripts/                      # All automation scripts
│   ├── connect.py                # First-time YouTube OAuth setup
│   ├── channel-status.py         # Live metrics: subs, views, CTR
│   ├── full-audit.py             # Scan all videos for issues
│   ├── facebook-post.py          # Post 8 viral posts to Facebook Page
│   ├── meta-update-posts.py      # Bulk update FB + IG post captions
│   ├── twitter-post.py           # Post 8 viral tweets to X
│   ├── rename-parts.py           # Bulk rename Part titles
│   ├── fix-dashes.py             # Fix broken em dash encoding
│   ├── upload-thumbnails.py      # Batch thumbnail upload
│   ├── create-playlists.py       # Create tribe-based playlists
│   ├── generate-scripture-cards.py # Generate scripture card images
│   └── ...                       # See full list above
├── analytics/                    # CSV snapshots for before/after tracking
├── docs/
│   ├── changelog.md              # Every change with dates and impact
│   ├── status.md                 # Living status doc — all platforms
│   ├── repurpose-templates.md    # Repurpose.io caption templates + bios
│   ├── social-media-audit.md     # Full 4-platform audit with competitor benchmark
│   ├── caption-templates.md      # Master caption system by video type
│   ├── competitors.md            # Competitor profiles and tactics
│   └── project-plan.md           # Full roadmap (Phases 1-5)
├── thumbnails/                   # Custom thumbnails
├── output/                       # Generated assets (scripture cards, etc.)
├── CLAUDE.md                     # AI assistant context and brand rules
├── .env                          # API keys (never commit)
├── .env.example                  # Key template (safe to commit)
└── README.md                     # This file
```

---

## Optimization Progress

| Phase | Status | Impact |
|-------|--------|--------|
| Phase 1: Channel Cleanup | ✅ Done | 30 videos deleted, 154 titles cleaned |
| Phase 2: Title Optimization | ✅ Done | 84 Part titles renamed, 50 em dash fixes |
| Phase 3: Thumbnails | ✅ Done | 20 custom thumbnails, brand guide locked |
| Phase 4A: Playlists + Trailer | ✅ Done | 14/14 playlists, trailer script ready |
| Phase 4B: Long-form Content | 🔄 In Progress | First pillar video script written |
| Phase 5: Social Media Automation | 🔄 In Progress | FB live, IG pending App Review |

---

## Key Docs

| Doc | Purpose |
|-----|---------|
| `docs/status.md` | Current status of every platform and pending tasks |
| `docs/repurpose-templates.md` | Caption templates and bios — paste into Repurpose.io |
| `docs/social-media-audit.md` | Full competitor benchmark and platform strategy |
| `docs/caption-templates.md` | Master repurpose system by video type |
| `docs/changelog.md` | Every change made with dates and measurement plan |

---

## API Quota Notes (YouTube)

- Daily limit: 10,000 units (resets midnight Pacific)
- `videos.update` = 50 units
- `thumbnails.set` = 50 units
- `videos.list` = 1 unit per page
- `playlistItems.insert` = 50 units

## GitHub

https://github.com/12TribesofIsrael/youtubeoptermizer
