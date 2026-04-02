# AI Bible Gospels — Master Status Doc
**Last Updated:** April 1, 2026
**Channel:** @AIBIBLEGOSPELS | 5,876 subs | 764K views

---

## Platform API Status

| Platform | API Keys | Script Built | Can Post New | Can Edit Existing | Status |
|----------|----------|-------------|--------------|-------------------|--------|
| Facebook | ✅ | ✅ | ✅ | ✅ | 🟢 LIVE |
| Instagram | ✅ | ✅ | ✅ | ❌ | 🟡 Blocked — Meta App Review pending |
| X/Twitter | ✅ | ✅ | ❌ | ❌ | 🔴 Free tier = no posting via API |
| TikTok | ❌ | ❌ | ❌ | ❌ | ⬜ Not started |

---

## What's Been Done

### YouTube Channel
- ✅ Deleted 30 low-performing / duplicate videos
- ✅ Cleaned @AIBIBLEGOSPELS from 154 titles
- ✅ Fixed 84 "Part X" titles (renamed to descriptive titles)
- ✅ Fixed 50 em dash formatting issues
- ✅ 20 custom thumbnails uploaded (brand guide applied)
- ✅ 14 playlists created and organized
- ✅ Channel trailer script written

### Facebook
- ✅ Meta developer app created and published
- ✅ API keys saved to .env
- ✅ `scripts/facebook-post.py` built
- ✅ **8 viral posts live on Facebook Page** (April 1, 2026)
  - identity, prophecy, identity_chart, suppressed_truth, awe, tribe_engagement, cinematic, current_events

### Instagram
- ✅ Instagram Business ID connected
- ✅ `scripts/meta-update-posts.py` built (538 posts ready to update)
- ❌ **Blocked by Meta App Review** — error #10, insufficient permissions
- 🔲 TODO: Submit App Review request in Meta dashboard
- 🔲 Once approved: run `python scripts/meta-update-posts.py instagram --live`

### X / Twitter
- ✅ Developer account created (console.x.com)
- ✅ API keys saved to .env (Consumer Key, Secret, Access Token, Access Secret)
- ✅ `scripts/twitter-post.py` built (8 viral tweets ready)
- ❌ **Blocked by Free tier** — Pay-per-use plan does not support OAuth 1.0a posting
- 🔲 Option: Use Repurpose.io to post to X instead
- 🔲 Option: Upgrade to X Basic ($100/month) for API posting

### TikTok
- ⬜ API keys not yet obtained
- ⬜ Apply at developers.tiktok.com (1-3 day approval)
- 🔲 Once approved: build `scripts/tiktok-post.py`

---

## Existing Posts — Can We Fix Them?

| Platform | Fix Existing Captions? | Method |
|----------|----------------------|--------|
| Facebook | ✅ Yes — via API | `meta-update-posts.py facebook --live` |
| Instagram | ⏳ Pending App Review | `meta-update-posts.py instagram --live` |
| X/Twitter | ❌ No — API blocked | Manual only |
| TikTok | ❌ No — TikTok API does not allow caption edits on existing posts | Manual only |

**Bottom line on existing posts for TikTok/X:** There is no API (paid or free) that lets you edit captions on posts that are already published on TikTok or X. Those platforms don't expose that endpoint. Only Instagram and Facebook allow caption edits via API.

---

## Repurpose.io — What It Can and Can't Do

| Task | Repurpose Can Do? |
|------|------------------|
| Auto-post new videos to TikTok, IG, X, FB | ✅ Yes |
| Add captions/descriptions to NEW posts | ✅ Yes — via caption templates |
| Edit captions on EXISTING posts | ❌ No |
| Fix old TikTok/X/IG posts | ❌ No |

**The fix for existing posts on TikTok and X:** Manual. You would need to go into each post and edit the caption by hand — there is no automation path.

---

## Active Scripts

| Script | What It Does | Command |
|--------|-------------|---------|
| `scripts/facebook-post.py` | Post 8 viral posts to Facebook Page | `python scripts/facebook-post.py --live` |
| `scripts/meta-update-posts.py` | Update all FB/IG post captions | `python scripts/meta-update-posts.py --live` |
| `scripts/twitter-post.py` | Post 8 viral tweets (blocked — see X status) | `python scripts/twitter-post.py --live` |
| `scripts/channel-status.py` | Pull live YouTube metrics | `python scripts/channel-status.py` |

---

## Repurpose.io — Capabilities Reference

| Task | Repurpose Can Do? |
|------|------------------|
| Auto-post new videos to TikTok, IG, X, FB, YouTube Shorts | ✅ Yes |
| Add caption templates to NEW posts | ✅ Yes |
| Create audiograms from audio clips | ✅ Yes |
| Edit captions on EXISTING posts | ❌ No |
| Generate AI captions | ❌ No |
| Write blog posts from video | ❌ No |
| Create quote graphics | ❌ No |
| Summarize video into text posts | ❌ No |
| Fix old TikTok/X/IG posts | ❌ No |

**Bottom line:** Repurpose handles distribution only — it moves the video file to each platform. It does not generate or edit any content. Caption templates must be written manually and pasted into Repurpose settings.

**Future plan:** Build a separate `repurpose-engine` project that uses Claude API + Whisper to auto-generate all 33 pieces of content from 1 YouTube video. Keep it separate from this repo.

---

## What Was Done (April 1-2, 2026)

- ✅ Facebook — 8 viral posts live via API (`scripts/facebook-post.py`)
- ✅ Repurpose.io — all 4 platform workflows configured (IG, TikTok, X, Facebook)
- ✅ Caption templates added to all 4 workflows (see `docs/repurpose-templates.md`)
- ✅ First comment (YouTube link) enabled on all 4 workflows
- ✅ AI auto-generate captions enabled on all 4 workflows
- ✅ TikTok bumped to 3 posts/day
- ✅ All 4 platform bios updated (Facebook, TikTok, Instagram, X)
- ✅ 15 YouTube video titles rewritten with viral hooks
- ✅ Meta App Review submitted (instagram_business_basic + instagram_business_manage_comments)
- ✅ YouTube OAuth token refreshed
- ✅ X/Twitter API keys saved + `scripts/twitter-post.py` built (8 tweets ready)
- ✅ Google Drive content workflow planned — son to create `New-Shorts\` subfolder + 4 new Repurpose workflows

## Immediate Next Steps (Priority Order)

1. 🔲 **Meta App Review approval** — 1-5 business days — then run `python scripts/meta-update-posts.py instagram --live` to fix all 538 IG captions
2. 🔲 **Son: Create New-Shorts\ subfolder** in `G:\My Drive\AI BIBLE GOSPELS\Videos\` and set up 4 new Repurpose workflows pointing to it (one per platform — IG, TikTok, X, FB)
3. ✅ **Fix X profile name** — changed to "AI Bible Gospels" (April 2, 2026)
4. 🔲 **Hit 1,000 TikTok followers** — then add YouTube link to bio (currently at 470)
5. ~~**Apply for TikTok API**~~ — **DEPRIORITIZED**: Repurpose already handles posting. API only adds analytics/comment replies — not worth the effort until 10K+ followers.
6. 🔲 **Refresh Meta token** every 60 days — use developers.facebook.com/tools/debug/accesstoken → Extend Token
7. 🔲 **Long-form content** — need 4-6 animated explainer videos (10-20 min) for ad revenue

---

## Token Expiry Tracker

| Token | Expires | How to Refresh |
|-------|---------|---------------|
| META_ACCESS_TOKEN | ~60 days (short-lived) | Graph API Explorer → Generate Access Token |
| TWITTER keys | Never (until regenerated) | X Developer Console → Apps → Keys |
| TIKTOK_ACCESS_TOKEN | Not set up yet | — |

**Note:** Meta tokens from Graph API Explorer are short-lived (1-2 hours). To get a 60-day token: use the Token Debugger at developers.facebook.com/tools/debug/accesstoken → Extend Token.
