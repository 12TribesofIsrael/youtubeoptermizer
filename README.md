# YouTube Optimizer — AI Bible Gospels

Automation toolkit for optimizing the **AI Bible Gospels** (@AIBIBLEGOSPELS) YouTube channel. Uses the YouTube Data API v3 to programmatically manage titles, thumbnails, playlists, and analytics.

## Channel Stats (March 17, 2026)

| Metric | Value |
|--------|-------|
| Subscribers | 5,877 |
| Total Views | 764,712 |
| Videos | 238 |
| CTR | 4.06% (target: 6%+) |
| Niche | 12 Tribes of Israel, Hebrew Israelite identity, biblical prophecy |

## What This Project Does

- **Channel audit** — scans all videos for issues (duplicates, spam signals, bad titles)
- **Bulk title optimization** — renamed 84 "Part X" titles to standalone searchable titles
- **Thumbnail management** — compress and upload custom thumbnails via API
- **Playlist automation** — create tribe-based playlists and organize videos
- **Analytics tracking** — before/after CSV snapshots to measure growth
- **Competitor analysis** — profiles of 5 competitor channels with tactics to steal

## Setup

### Prerequisites
- Python 3.8+
- Google Cloud project with YouTube Data API v3 enabled
- OAuth 2.0 Desktop App credentials

### Install
```bash
pip install -r requirements.txt
```

### Authenticate
```bash
python scripts/connect.py
```
This opens a browser for Google OAuth. Token is saved to `token.json` for future use.

### Test Connection
```bash
python scripts/test-connection.py
```

## Project Structure

```
youtubeoptimization/
├── src/youtube/           # API client and auth
│   ├── auth.py            # OAuth 2.0 authentication
│   └── client.py          # YouTubeClient — list, update, delete, thumbnails, playlists
├── scripts/               # Automation scripts
│   ├── connect.py         # First-time OAuth setup
│   ├── full-audit.py      # Scan all videos for issues
│   ├── rename-parts.py    # Bulk rename Part titles
│   ├── fix-dashes.py      # Fix broken em dash encoding
│   ├── upload-thumbnails.py  # Batch thumbnail upload
│   └── reorganize-playlists.py  # Create tribe-based playlists
├── analytics/
│   ├── pre-optimization/  # Baseline CSVs (March 16, 2026)
│   └── post-optimization/ # Current CSVs after optimization
├── docs/
│   ├── changelog.md       # Every change with dates and impact tracking
│   ├── project-plan.md    # Full roadmap (Phases 1-5)
│   └── competitors.md     # Competitor profiles and strategy
├── CLAUDE.md              # AI assistant context for this project
└── goal.md                # Original channel strategy report
```

## Optimization Completed

| Phase | Status | Impact |
|-------|--------|--------|
| Phase 1: Channel Cleanup | Done | 30 videos deleted, 154 titles cleaned |
| Phase 2: Title Optimization | Done | 84 Part titles renamed to searchable standalone titles |
| Phase 3: Thumbnails | Done | 20 custom thumbnails with bold text overlays |
| Phase 4: Content Strategy | In Progress | Playlists, channel trailer, long-form content |

## API Quota Notes

- Daily limit: 10,000 units (resets midnight Pacific)
- `videos.update` = 50 units
- `thumbnails.set` = 50 units
- `videos.list` = 1 unit per page
- `playlistItems.insert` = 50 units
- Plan operations across days to stay within quota

## License

Private project for AI Bible Gospels channel optimization.
