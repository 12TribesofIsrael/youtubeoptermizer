"""
Meta App Review — Required Test API Calls
Makes the test calls needed for instagram_business_manage_comments
and instagram_business_content_publish permissions to register as 1/1.

Run this, then wait up to 24hrs for Meta to register the calls.
"""

import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("META_ACCESS_TOKEN")
IG_ID = os.getenv("INSTAGRAM_BUSINESS_ID")  # 17841454335324028

if not TOKEN:
    print("ERROR: META_ACCESS_TOKEN not set in .env")
    exit(1)
if not IG_ID:
    print("ERROR: INSTAGRAM_BUSINESS_ID not set in .env")
    exit(1)

print(f"Instagram Business ID: {IG_ID}")
print(f"Token: {TOKEN[:20]}...")
print()


def api_get(url):
    try:
        r = urllib.request.urlopen(url)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return {"error": json.loads(body)}
        except:
            return {"error": body.decode()}


def api_post(url, data):
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=encoded, method="POST")
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return {"error": json.loads(body)}
        except:
            return {"error": body.decode()}


import urllib.parse

print("=" * 60)
print("  TEST CALL 1: instagram_business_manage_comments")
print("=" * 60)
print()

# Call 1a: Get media posts (triggers manage_comments)
print("1a. Fetching Instagram media posts...")
url = f"https://graph.facebook.com/v25.0/{IG_ID}/media?fields=id,caption,timestamp,media_type&limit=5&access_token={TOKEN}"
result = api_get(url)

if "error" in result:
    print(f"   ERROR: {result['error']}")
else:
    posts = result.get("data", [])
    print(f"   OK — Found {len(posts)} posts")
    for p in posts[:3]:
        caption = (p.get("caption") or "")[:60]
        print(f"   [{p['id']}] {p.get('media_type','')} | {caption}...")

# Call 1b: Get comments on first post (directly triggers manage_comments)
if "error" not in result and posts:
    post_id = posts[0]["id"]
    print(f"\n1b. Fetching comments on post {post_id}...")
    url2 = f"https://graph.facebook.com/v25.0/{post_id}/comments?fields=id,text,timestamp,username&limit=10&access_token={TOKEN}"
    result2 = api_get(url2)
    if "error" in result2:
        print(f"   ERROR: {result2['error']}")
    else:
        comments = result2.get("data", [])
        print(f"   OK — Found {len(comments)} comments")
        for c in comments[:3]:
            print(f"   [{c.get('username','?')}] {c.get('text','').encode('ascii','replace').decode()[:50]}")

# Call 1c: Get mentioned media (also triggers manage_comments)
print(f"\n1c. Fetching mentioned media...")
url3 = f"https://graph.facebook.com/v25.0/{IG_ID}/tags?fields=id,caption,timestamp&limit=5&access_token={TOKEN}"
result3 = api_get(url3)
if "error" in result3:
    print(f"   ERROR: {result3['error']}")
else:
    print(f"   OK — Found {len(result3.get('data', []))} tagged posts")

print()
print("=" * 60)
print("  TEST CALL 2: instagram_business_content_publish")
print("=" * 60)
print()

# Call 2a: Check content publishing limit (triggers content_publish)
print("2a. Checking content publishing limit...")
url4 = f"https://graph.facebook.com/v25.0/{IG_ID}/content_publishing_limit?fields=config,quota_usage&access_token={TOKEN}"
result4 = api_get(url4)
if "error" in result4:
    print(f"   ERROR: {result4['error']}")
else:
    print(f"   OK — Publishing limit data: {json.dumps(result4, indent=2)}")

# Call 2b: Create a media container (triggers content_publish without actually posting)
print("\n2b. Creating test media container (will NOT publish)...")
# Use a public placeholder image
test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
url5 = f"https://graph.facebook.com/v25.0/{IG_ID}/media"
container_data = {
    "image_url": test_image_url,
    "caption": "API test - do not publish",
    "access_token": TOKEN,
}
result5 = api_post(url5, container_data)
if "error" in result5:
    print(f"   ERROR: {result5['error']}")
    print("   (This is OK if you get a permissions error — the API call itself still registers)")
else:
    container_id = result5.get("id", "")
    print(f"   OK — Container created: {container_id}")
    print(f"   NOTE: Container was NOT published. It will expire in 24hrs automatically.")

print()
print("=" * 60)
print("  ADDITIONAL CALLS (belt and suspenders)")
print("=" * 60)
print()

# Call 3: Get Instagram account info (basic)
print("3. Fetching Instagram account info...")
url6 = f"https://graph.facebook.com/v25.0/{IG_ID}?fields=id,name,username,followers_count,media_count,profile_picture_url&access_token={TOKEN}"
result6 = api_get(url6)
if "error" in result6:
    print(f"   ERROR: {result6['error']}")
else:
    print(f"   Account: @{result6.get('username', '?')}")
    print(f"   Followers: {result6.get('followers_count', '?')}")
    print(f"   Media count: {result6.get('media_count', '?')}")

# Call 4: Get Instagram stories (if any)
print("\n4. Fetching Instagram stories...")
url7 = f"https://graph.facebook.com/v25.0/{IG_ID}/stories?fields=id,timestamp,media_type&access_token={TOKEN}"
result7 = api_get(url7)
if "error" in result7:
    print(f"   ERROR: {result7['error']}")
else:
    print(f"   OK — Found {len(result7.get('data', []))} stories")

print()
print("=" * 60)
print("  SUMMARY")
print("=" * 60)
print()
print("  Test calls made:")
print("    - GET /{ig_id}/media (manage_comments)")
print("    - GET /{post_id}/comments (manage_comments)")
print("    - GET /{ig_id}/tags (manage_comments)")
print("    - GET /{ig_id}/content_publishing_limit (content_publish)")
print("    - POST /{ig_id}/media (content_publish — container only)")
print("    - GET /{ig_id} (basic)")
print("    - GET /{ig_id}/stories (basic)")
print()
print("  NEXT STEPS:")
print("  1. Wait up to 24 hours for Meta to register these calls")
print("  2. Go to App Review page and check if both show 1/1")
print("  3. Once 1/1 — click Submit")
print()
print("  If calls still show 0/1 after 24hrs, try again from")
print("  Graph API Explorer (developers.facebook.com/tools/explorer)")
print("=" * 60)
