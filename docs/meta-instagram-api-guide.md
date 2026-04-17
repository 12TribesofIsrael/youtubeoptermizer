# Meta Instagram Business API — Setup & App Review Guide

**Last Updated:** April 17, 2026
**Author:** AI Bible Gospels engineering team
**Purpose:** Complete reference for onboarding any Instagram Business account via Meta's API. Written from 2+ weeks of hard-won debugging on the @aibiblegospels account.

---

## Table of Contents

1. [Overview: Two Different Instagram APIs](#1-overview-two-different-instagram-apis)
2. [Architecture: Apps, IDs, and Tokens](#2-architecture-apps-ids-and-tokens)
3. [Step-by-Step: New Client Onboarding](#3-step-by-step-new-client-onboarding)
4. [App Review: What Actually Registers Test Calls](#4-app-review-what-actually-registers-test-calls)
5. [Bugs We Hit and How to Avoid Them](#5-bugs-we-hit-and-how-to-avoid-them)
6. [Token Management](#6-token-management)
7. [API Reference: Correct Endpoints and Parameters](#7-api-reference-correct-endpoints-and-parameters)
8. [Checklist: Client Onboarding Runbook](#8-checklist-client-onboarding-runbook)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Overview: Two Different Instagram APIs

Meta has **two completely separate Instagram APIs**. Using the wrong one is the #1 cause of wasted time. They share similar permission names but use different endpoints, tokens, and OAuth flows.

| | Old: Instagram Graph API | New: Instagram Business Login API |
|---|---|---|
| **API base URL** | `graph.facebook.com` | `graph.instagram.com` |
| **OAuth provider** | Facebook Login (`facebook.com/dialog/oauth`) | Instagram Login (`instagram.com/oauth/authorize`) |
| **App credentials** | Facebook App ID + Secret | Instagram App ID + Secret (separate!) |
| **Permission prefix** | `instagram_basic`, `instagram_manage_comments` | `instagram_business_basic`, `instagram_business_manage_comments` |
| **Account ID** | Instagram Business Account ID (from Facebook Page) | Instagram User ID (from `/me` endpoint) |
| **Token format** | Starts with `EAA...` | Starts with `IGA...` |
| **Status** | Being deprecated | Current standard |

**Rule: If the permission starts with `instagram_business_`, you MUST use `graph.instagram.com` with Instagram Login credentials. No exceptions.**

---

## 2. Architecture: Apps, IDs, and Tokens

This is confusing because Meta nests things. Here's how it works:

```
Meta Developer Account
└── Facebook App (App ID: 1452257036358754)
    ├── Facebook Login settings
    ├── Use Cases
    │   └── "Manage messaging & content on Instagram"
    │       └── Instagram App (IG App ID: 922450807234394)  ← SEPARATE credentials
    │           ├── Instagram App Secret
    │           ├── Business Login Settings (redirect URIs)
    │           └── Permissions (instagram_business_*)
    ├── App Review (submitted through the Facebook App)
    └── Testing page
```

### Key IDs You'll Need Per Client

| ID | Where to find it | Example |
|----|-----------------|---------|
| Facebook App ID | Meta Developer Dashboard → App Settings → Basic | `1452257036358754` |
| Facebook App Secret | Same page (click Show) | `47d07f1212...` |
| Instagram App ID | Use Cases → Manage messaging & content on Instagram → API setup with Instagram login | `922450807234394` |
| Instagram App Secret | Same page (click Show) | `52a686a35d...` |
| Facebook Page ID | Graph API: `GET /me/accounts` with user token | `601690023018873` |
| Instagram Business Account ID | Graph API: `GET /{page-id}?fields=instagram_business_account` | `17841454335324028` |
| Instagram User ID | Instagram API: `GET /me` with IG token | `26231113889873297` |

**Critical: The Instagram Business Account ID and Instagram User ID are DIFFERENT numbers for the same account.** The first is used with `graph.facebook.com`, the second with `graph.instagram.com`.

---

## 3. Step-by-Step: New Client Onboarding

### 3.1 Create (or reuse) a Facebook App

1. Go to `developers.facebook.com/apps/` → Create App
2. Select "Other" → "Business" type
3. Add a use case: "Manage messaging & content on Instagram"
4. This generates an **Instagram App ID** separate from the Facebook App ID

### 3.2 Configure Instagram Business Login

1. In the app dashboard, go to: Use Cases → "Manage messaging & content on Instagram" → "API setup with Instagram login"
2. **Step 1 — Permissions:** Add all required permissions:
   - `instagram_business_basic` (required for all others)
   - `instagram_business_content_publish`
   - `instagram_business_manage_comments`
   - `instagram_business_manage_insights`
   - `instagram_business_manage_messages`
3. **Step 2 — Access tokens:** Click "Add Instagram account" → client logs in with their Instagram credentials → generates a test token
4. **Step 4 — Business Login Settings:** Add your redirect URI (must be HTTPS):
   - For local dev: `https://localhost:9876/callback`
   - For production: `https://yourdomain.com/callback`

### 3.3 OAuth Flow (Get Client Token)

```
1. Redirect client to:
   https://www.instagram.com/oauth/authorize
     ?client_id={IG_APP_ID}
     &redirect_uri={HTTPS_REDIRECT_URI}
     &response_type=code
     &scope=instagram_business_basic,instagram_business_content_publish,...
     &force_reauth=true

2. Client authorizes → redirected to your callback with ?code=AUTH_CODE

3. Exchange code for short-lived token:
   POST https://api.instagram.com/oauth/access_token
   Body: client_id, client_secret, grant_type=authorization_code, redirect_uri, code

4. Upgrade to long-lived token (~60 days):
   GET https://graph.instagram.com/access_token
     ?grant_type=ig_exchange_token
     &client_secret={IG_APP_SECRET}
     &access_token={SHORT_LIVED_TOKEN}
```

### 3.4 Submit App Review

See Section 4 below — this is where most teams get stuck.

---

## 4. App Review: What Actually Registers Test Calls

App Review requires you to make at least 1 successful API call per permission before you can submit. Meta tracks these automatically but is VERY specific about what counts.

### What Counts vs. What Doesn't

| Permission | Call that COUNTS | Call that DOES NOT count |
|---|---|---|
| `instagram_business_basic` | `GET /me?fields=id,username,account_type` | — (usually auto-completes) |
| `instagram_business_content_publish` | `POST /{ig-user-id}/media` (create container) | `GET /content_publishing_limit` (read-only, does NOT count) |
| `instagram_business_manage_comments` | `GET /{media-id}/comments` | `GET /{ig-user-id}/media` alone (that's basic, not comments) |
| `instagram_business_manage_insights` | `GET /{ig-user-id}/insights?metric=reach&period=day` | `GET /insights?metric=impressions` (invalid metric — returns error) |
| `instagram_business_manage_messages` | `GET /{ig-user-id}/conversations?platform=instagram` | — (usually works on first try) |

### The Content Publish Trap

The most common trap: `content_publishing_limit` is a read endpoint. Meta needs to see you actually attempt content creation. Create a media container — it won't publish unless you also call `/media_publish`:

```python
POST https://graph.instagram.com/v22.0/{ig_user_id}/media
Body: {
    "image_url": "https://upload.wikimedia.org/...",  # any public image
    "caption": "API test - will not be published",
    "access_token": TOKEN
}
```

The container auto-expires in 24 hours. It never goes live unless you explicitly publish it.

### The Insights Metrics Trap

The Instagram Business Login API has **different valid metrics** than the old Facebook-based API:

**Account-level (`GET /{ig-user-id}/insights`):**
| Valid Metrics | Invalid Metrics |
|---|---|
| `reach` | `impressions` (NOT supported at account level) |
| `follower_count` | `engagement` |
| `website_clicks` | `follower_demographics` |
| `profile_views` | |
| `online_followers` | |

Period must be `day` for account-level metrics.

**Media-level (`GET /{media-id}/insights`):**
| Valid Metrics | Invalid Metrics |
|---|---|
| `reach` | `impressions` (not for all media types) |
| `saved` | `engagement` |
| `likes` | |
| `comments` | |
| `shares` | |

No period parameter needed for media-level (always lifetime).

### Timeline for Test Call Registration

- Calls typically register within **1-4 hours**
- Meta says "up to 24 hours" — plan for that
- If still 0/1 after 24 hours, the call is wrong (not a timing issue)
- Once all show "Completed" (green dot), the Submit button enables
- Review takes **1-10 business days** after submission

---

## 5. Bugs We Hit and How to Avoid Them

These are real bugs that cost us 2+ weeks on the @aibiblegospels account. Each one is a trap that any developer would fall into.

### Bug 1: Using graph.facebook.com instead of graph.instagram.com

**What happened:** For 2 weeks (April 2-15, 2026), all test call scripts used `graph.facebook.com` with the Facebook App token. Calls succeeded — the API returned real data. But Meta's App Review dashboard showed 0/1 because the calls were against the wrong API for `instagram_business_*` permissions.

**Why it's confusing:** The old Instagram API literally lives on `graph.facebook.com`. If you Google "Instagram API" most results still reference the old endpoints. The new `instagram_business_*` permissions use a completely different API at `graph.instagram.com`.

**How to avoid:** Check the permission prefix. If it starts with `instagram_business_`, use `graph.instagram.com`. Always verify the token starts with `IGA...` not `EAA...`.

### Bug 2: Using the wrong App ID / Secret

**What happened:** The Facebook App and Instagram App have DIFFERENT IDs and secrets. We initially used `META_APP_ID` for the Instagram OAuth flow. The OAuth page loaded and looked correct, but the resulting token was tied to the wrong app.

**Why it's confusing:** Both are in the same developer dashboard. The Instagram App ID is buried under Use Cases → Instagram use case → API setup with Instagram login. It's easy to miss.

**How to avoid:** Store both sets of credentials in `.env` with clear names:
```
META_APP_ID=...        # Facebook app — for graph.facebook.com
META_APP_SECRET=...
IG_APP_ID=...          # Instagram app — for graph.instagram.com
IG_APP_SECRET=...
```

### Bug 3: GET vs POST for content_publish

**What happened:** The test call for `instagram_business_content_publish` used `GET /content_publishing_limit`. This is a valid endpoint that returns data — but it's a READ operation. Meta needs to see a WRITE operation (`POST /media`) to count it.

**Why it's confusing:** `content_publishing_limit` contains the word "publishing" and it requires the `content_publish` scope. It looks like the right call. But Meta tracks whether you actually attempted to create content, not just checked your quota.

**How to avoid:** For any permission related to writing/creating/publishing, make sure the test call is a write operation (POST/PUT/DELETE), not just a read (GET).

### Bug 4: Invalid insight metrics silently fail

**What happened:** The script passed `impressions` as a metric for account-level insights. The API returned an error object, but the script just logged "FAIL" without investigating why. The metric is valid on the OLD Instagram API but invalid on the NEW one.

**Why it's confusing:** `impressions` is probably the most common social media metric. It works on Facebook's API. It works on the old Instagram API. It just doesn't work on the new Instagram Business Login API at the account level.

**How to avoid:** Always check the error response body. A 400 error with a message like "metric[0] must be one of the following values" tells you exactly what's valid. Don't assume metric names transfer between APIs.

### Bug 5: Same Instagram account, two different IDs

**What happened (narrowly avoided):** The Instagram Business Account ID (`17841454335324028`, from the Facebook Page connection) is different from the Instagram User ID (`26231113889873297`, from `graph.instagram.com/me`). Using the wrong ID with the wrong API returns confusing errors.

**How to avoid:**
- `graph.facebook.com` → use Instagram Business Account ID (from Page)
- `graph.instagram.com` → use Instagram User ID (from `/me`)
- Never mix them. Store both in `.env` with clear names.

---

## 6. Token Management

### Token Types and Lifetimes

| Token | Lifetime | How to get |
|---|---|---|
| Instagram short-lived | ~1 hour | OAuth code exchange |
| Instagram long-lived | ~60 days | Upgrade from short-lived via `ig_exchange_token` |
| Dashboard-generated | ~1 hour (short) or ~60 days (long) | "Generate token" button in API setup |

### Refreshing Long-Lived Tokens

Long-lived tokens can be refreshed before they expire:

```
GET https://graph.instagram.com/refresh_access_token
  ?grant_type=ig_refresh_token
  &access_token={CURRENT_LONG_LIVED_TOKEN}
```

Returns a new long-lived token with a fresh 60-day expiry. The old token is invalidated.

**For a SaaS:** Build automated token refresh. Check token age on every API call. If older than 50 days, refresh automatically. Store the new token. Never wait for expiry — a dead token means the client's automations silently stop.

### Token Validation

Before making any API calls for a client, verify the token:

```python
# Quick health check
r = GET https://graph.instagram.com/v22.0/me
      ?fields=id,username
      &access_token={TOKEN}

# If this returns an error, the token is dead — re-auth required
```

---

## 7. API Reference: Correct Endpoints and Parameters

All endpoints below use `https://graph.instagram.com/v22.0` as the base URL.

### Read Operations

```
# Get account info (instagram_business_basic)
GET /me?fields=id,username,account_type,media_count,profile_picture_url

# Get media posts (instagram_business_basic)
GET /{ig-user-id}/media?fields=id,caption,media_type,timestamp,permalink&limit=25

# Get comments on a post (instagram_business_manage_comments)
GET /{media-id}/comments?fields=id,text,username,timestamp&limit=50

# Get replies to a comment (instagram_business_manage_comments)
GET /{comment-id}/replies?fields=id,text,username,timestamp

# Get account insights (instagram_business_manage_insights)
GET /{ig-user-id}/insights?metric=reach,follower_count,profile_views&period=day

# Get media insights (instagram_business_manage_insights)
GET /{media-id}/insights?metric=reach,saved,likes,comments,shares

# Get conversations (instagram_business_manage_messages)
GET /{ig-user-id}/conversations?platform=instagram

# Get publishing quota (instagram_business_content_publish)
GET /{ig-user-id}/content_publishing_limit?fields=config,quota_usage
```

### Write Operations

```
# Create media container — image (instagram_business_content_publish)
POST /{ig-user-id}/media
Body: image_url={PUBLIC_URL}&caption={TEXT}&access_token={TOKEN}

# Create media container — video/reel (instagram_business_content_publish)
POST /{ig-user-id}/media
Body: video_url={PUBLIC_URL}&caption={TEXT}&media_type=REELS&access_token={TOKEN}

# Publish container (instagram_business_content_publish)
POST /{ig-user-id}/media_publish
Body: creation_id={CONTAINER_ID}&access_token={TOKEN}

# Reply to a comment (instagram_business_manage_comments)
POST /{comment-id}/replies
Body: message={TEXT}&access_token={TOKEN}

# Update caption on existing post (instagram_business_manage_comments)
POST /{media-id}
Body: caption={NEW_CAPTION}&access_token={TOKEN}
```

---

## 8. Checklist: Client Onboarding Runbook

Use this for every new client. Check off each step.

### Phase 1: App Configuration (30 minutes)

```
[ ] 1. Client provides their Instagram Business account username
[ ] 2. Verify account is a Business or Creator account (not Personal)
[ ] 3. In Meta Dashboard: Use Cases → "Manage messaging & content on Instagram"
[ ] 4. Note the Instagram App ID and Secret (NOT the Facebook App ID)
[ ] 5. Under Business Login Settings, add your production redirect URI
[ ] 6. Add all required permissions in Step 1 of API setup
[ ] 7. Have client connect their IG account in Step 2 → "Add account"
```

### Phase 2: OAuth & Token (10 minutes)

```
[ ] 8. Run OAuth flow with instagram.com/oauth (NOT facebook.com)
[ ] 9. Use IG_APP_ID and IG_APP_SECRET (NOT META_APP_ID)
[ ] 10. Exchange code → short-lived token
[ ] 11. Upgrade to long-lived token (~60 days)
[ ] 12. Verify token: GET /me returns the client's username
[ ] 13. Store token securely with expiry date
```

### Phase 3: App Review Test Calls (15 minutes)

```
[ ] 14. GET /me → OK (instagram_business_basic)
[ ] 15. POST /{ig-user-id}/media with test image → OK (content_publish)
[ ] 16. GET /{media-id}/comments → OK (manage_comments)
[ ] 17. GET /{ig-user-id}/insights?metric=reach&period=day → OK (manage_insights)
[ ] 18. GET /{ig-user-id}/conversations?platform=instagram → OK (manage_messages)
[ ] 19. ALL calls return 200 with real data (not error objects)
[ ] 20. Wait up to 24 hours for Meta dashboard to show "Completed" (green dot)
```

### Phase 4: Submit & Wait (1-10 business days)

```
[ ] 21. All permissions show "Completed" in Allowed usage tab
[ ] 22. Verification — green check
[ ] 23. App settings — green check
[ ] 24. Allowed usage — green check (all permissions)
[ ] 25. Data handling — green check
[ ] 26. Reviewer instructions — green check (include test account, screencast, sample post URL)
[ ] 27. Click Submit for Review
[ ] 28. Set calendar reminder for 10 business days out
```

### Phase 5: Post-Approval (5 minutes)

```
[ ] 29. Verify approval email received
[ ] 30. Test a real API call (read a post, read insights)
[ ] 31. If building caption updater: test POST /{media-id} with caption update
[ ] 32. Set up automated token refresh (refresh at 50 days, before 60-day expiry)
[ ] 33. Document client's IDs in the system (IG User ID, token expiry date)
```

---

## 9. Troubleshooting

### "0 of 1 API call(s) required" won't change

| Check | How |
|---|---|
| Are you using `graph.instagram.com`? | Verify base URL in script — NOT `graph.facebook.com` |
| Is the token from the Instagram App? | Token should start with `IGA...`. If `EAA...`, it's a Facebook token |
| Is the API call actually succeeding? | Check the response body — a 200 with `{"error": {...}}` is still a failure |
| For content_publish: are you POSTing? | `GET /content_publishing_limit` doesn't count. Must `POST /media` |
| For insights: correct metrics? | Use `reach`, `follower_count`, `profile_views`. NOT `impressions` |
| Has it been 24 hours? | Meta says up to 24h. If still 0/1 after 24h, the call is wrong |

### "Invalid OAuth redirect URI"

- Redirect URI must exactly match what's in Business Login Settings
- Must be HTTPS (even for localhost)
- No trailing slash differences
- Fragment (#) in the URL is stripped by Instagram — don't rely on it

### Token expired or invalid

- Short-lived tokens die after ~1 hour
- Long-lived tokens die after ~60 days
- Revoked tokens return `OAuthException` with code 190
- Fix: re-run OAuth flow from scratch

### "The Media Insights API does not support the X metric"

Different media types support different metrics:
- **IMAGE/CAROUSEL_ALBUM**: reach, saved, likes, comments, shares
- **VIDEO/REEL**: reach, saved, likes, comments, shares, plays
- **STORY**: reach, replies, exits, taps_forward, taps_back

Always check the `media_type` field before requesting insights.

### Rate Limits

- 200 calls per user per hour (graph.instagram.com)
- 4800 calls per app per 24 hours
- Publishing: 100 posts per 24-hour period per account
- For bulk operations on client accounts, add 0.5s delay between calls

---

## Scripts Reference

| Script | Purpose | API Used |
|---|---|---|
| `scripts/meta-ig-business-review.py` | OAuth + test calls for App Review | graph.instagram.com (correct) |
| `scripts/meta-ig-business-review.py --reuse` | Re-run test calls with stored token | graph.instagram.com (correct) |
| `scripts/meta-ig-business-review.py --token TOKEN` | Test calls with dashboard token | graph.instagram.com (correct) |
| `scripts/meta-test-calls.py` | OLD — do not use for instagram_business_* | graph.facebook.com (wrong for new perms) |
| `scripts/meta-app-review.py` | OLD — do not use for instagram_business_* | graph.facebook.com (wrong for new perms) |
| `scripts/meta-update-posts.py` | Update captions on FB/IG posts | graph.facebook.com (uses Page token) |

---

## Version History

| Date | Change |
|---|---|
| April 17, 2026 | Initial document — written after resolving 2+ weeks of App Review failures |
