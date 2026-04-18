# Social Media Automation Plan — AI Bible Gospels

**Goal:** Wire up APIs for Instagram, TikTok, X/Twitter, and Facebook so one command pushes every YouTube upload to all 4 platforms automatically.

---

## What We're Building

| Script | What It Does |
|--------|-------------|
| `auto-repurpose` | You upload a Short to YouTube → one command pushes it to all 4 platforms with the right caption + hashtags from the template system |
| `auto-thread` | Generate and post an X/Twitter thread from a YouTube video title/transcript |
| `bio-updater` | Update bios across all platforms in one command |
| `weekly-scheduler` | Queue all week's posts from the repurpose calendar in one session |
Update descriptions and add keywords and hash tags 

---

## Status

| Platform | API Keys | Script Built | Live |
|----------|----------|-------------|------|
| X/Twitter | ✅ | ✅ | ❌ Free tier blocks posting |
| Facebook | ✅ | ✅ | ✅ Live |
| Instagram | ✅ | ✅ | ⏳ Meta App Review submitted 2026-04-17 |
| TikTok | ✅ | ✅ | ⏳ TikTok App Review pending demo video |

---

## Step 1 — X/Twitter (Start Here — Easiest)

**Time to get working: under 1 hour**

### Get API Keys
1. Go to **developer.twitter.com**
2. Sign in with **@AIbiblegospels**
3. Click "Sign up for Free Account" — use case: *"Posting content to my own account to promote my YouTube channel"*
4. Dashboard → Projects & Apps → Create App
5. Keys and Tokens → generate all 4 keys (make sure permissions = **Read and Write**)
6. App Settings → User authentication settings → enable OAuth 1.0a → Read and Write

### Add to .env
```
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
```

### What Gets Built
- `scripts/twitter-post.py` — post a single tweet or full thread
- Auto-pulls caption from `docs/caption-templates.md` based on video type
- Attaches video/image if provided
- Posts YouTube link in first reply (avoids X's link suppression)

---

## Step 2 — Facebook + Instagram (Same API)

**Time to get working: 1-2 hours**

### Get API Keys
1. Go to **developers.facebook.com**
2. Create an app → select "Business" type
3. Add products: **Instagram Graph API** + **Pages API**
4. Generate a long-lived Page Access Token
5. Find your Facebook Page ID (Settings → Page Info) and Instagram Business Account ID

### Add to .env
```
META_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=
INSTAGRAM_BUSINESS_ID=
```

### What Gets Built
- `scripts/facebook-post.py` — post native video + caption to Facebook Page
- `scripts/instagram-post.py` — post Reel + caption to Instagram
- Both pull from `docs/caption-templates.md` automatically
- YouTube link goes in first comment (avoids Facebook's link reach penalty)

---

## Step 3 — TikTok

**Time to get working: 1-3 days (API approval required)**

### Get API Keys
1. Go to **developers.tiktok.com**
2. Create an app → apply for **Content Posting API** access
3. Wait for approval (1-3 business days)
4. Once approved, generate access token

### Add to .env
```
TIKTOK_CLIENT_KEY=
TIKTOK_CLIENT_SECRET=
TIKTOK_ACCESS_TOKEN=
```

### What Gets Built
- `scripts/tiktok-post.py` — upload video + caption + hashtags to TikTok
- Pulls from caption template system automatically
- "Link in bio" CTA appended to every caption

---

## Step 4 — Master Repurpose Script (All Platforms at Once)

Once all 4 APIs are live, one final script ties everything together:

```
python scripts/repurpose.py --video "path/to/short.mp4" --type "tribe-identity" --title "The Tribe of Judah: Who They Are Today"
```

This single command will:
1. Push the video to TikTok with correct caption + 6 hashtags
2. Push to Instagram Reels with cliffhanger caption + 30 hashtags
3. Upload natively to Facebook + drop YouTube link in first comment
4. Post to X/Twitter natively + drop YouTube link in first reply
5. Log everything to `docs/changelog.md`

---

## File Map (Once Built)

```
scripts/
├── twitter-post.py        ← post tweets and threads to X/Twitter
├── facebook-post.py       ← post native video to Facebook Page
├── instagram-post.py      ← post Reels to Instagram
├── tiktok-post.py         ← upload video to TikTok
└── repurpose.py           ← master script — all 4 platforms at once
```

---

## Dependencies to Install

```bash
pip install tweepy                        # X/Twitter
pip install facebook-sdk                  # Facebook + Instagram
pip install requests                      # TikTok (uses REST API directly)
pip install python-dotenv                 # loads .env variables
```

---

## Notes
- All scripts read API keys from `.env` — never hardcode credentials
- Caption templates live in `docs/caption-templates.md` — edit there to update all scripts
- Watermark stripping for cross-posts: use Repurpose.io for now; can be automated later with ffmpeg
- TikTok API approval is the only blocker — apply now so it's ready when needed
