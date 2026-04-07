"""
fix-facebook-captions.py
Strips AI-generated garbage appended by Repurpose.io from Facebook posts.
Run dry first, then --live to apply.
"""

import os, json, time, urllib.request, urllib.parse, urllib.error
from dotenv import load_dotenv

load_dotenv()

USER_TOKEN = os.getenv("META_ACCESS_TOKEN")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

# Markers where the AI garbage starts — truncate everything from here onward
GARBAGE_MARKERS = [
    "Exciting News Alert",
    "[Industry/Topic]",
    "[Web Link]",
    "[Product/Service]",
    "[Describe the benefit",
    "[Benefit 1]",
    "game-changer of 202",
    "InnovationUnleashed",
    "Revolutionize202",
    "magical souls",
    "Wanderlust",
    "TikTok-optimized version",
    "Sure! Here",
    "cutting-edge [",
    "Join our vibrant community of pioneers",
    "transformative journey",
    "limitless possibilities",
    "Embrace the rhythm of wellness",
]

def api_get(url):
    try:
        r = urllib.request.urlopen(url)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read())}

def api_post(url, data):
    data_encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data_encoded, method="POST")
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read())}

def get_page_token():
    url = f"https://graph.facebook.com/v25.0/{PAGE_ID}?fields=access_token&access_token={USER_TOKEN}"
    data = api_get(url)
    if "error" in data:
        print("Could not get page token:", data["error"])
        return USER_TOKEN
    return data.get("access_token", USER_TOKEN)

def get_all_posts(page_token):
    url = (
        f"https://graph.facebook.com/v25.0/{PAGE_ID}/posts"
        f"?fields=id,message,created_time&limit=100&access_token={page_token}"
    )
    data = api_get(url)
    posts = data.get("data", [])
    while "paging" in data and "next" in data.get("paging", {}):
        data = api_get(data["paging"]["next"])
        posts.extend(data.get("data", []))
    return posts

def find_garbage_start(text):
    """Return index where garbage begins, or -1 if none found."""
    for marker in GARBAGE_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            return idx
    return -1

def clean_message(text):
    """Strip AI garbage from message, return cleaned version."""
    idx = find_garbage_start(text)
    if idx == -1:
        return None  # no garbage found
    return text[:idx].rstrip()

def run(dry_run=True):
    print(f"\n{'='*55}")
    print(f"  FACEBOOK CAPTION FIX {'(DRY RUN)' if dry_run else '(LIVE)'}")
    print(f"{'='*55}\n")

    page_token = get_page_token()
    posts = get_all_posts(page_token)
    print(f"Fetched {len(posts)} posts\n")

    fixed = 0
    clean = 0
    errors = 0

    for post in posts:
        post_id = post["id"]
        message = post.get("message", "")
        date = post.get("created_time", "")[:10]

        if not message:
            continue

        cleaned = clean_message(message)

        if cleaned is None:
            print(f"  OK     {date} | {message[:70]}")
            clean += 1
            continue

        print(f"\n  DIRTY  {date} | {message[:70]}...")
        print(f"  CLEAN  -> {cleaned[:70]}...")

        if not dry_run:
            result = api_post(
                f"https://graph.facebook.com/v25.0/{post_id}",
                {"message": cleaned, "access_token": page_token}
            )
            if "error" in result:
                print(f"  ERROR: {result['error'].get('message','unknown')}")
                errors += 1
            else:
                print(f"  UPDATED")
                fixed += 1
            time.sleep(0.5)
        else:
            fixed += 1

    print(f"\n{'='*55}")
    if dry_run:
        print(f"  Would fix: {fixed} posts | Already clean: {clean}")
        print(f"  Run with --live to apply")
    else:
        print(f"  Fixed: {fixed} | Already clean: {clean} | Errors: {errors}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    import sys
    live = "--live" in sys.argv
    if not live:
        print("\n  DRY RUN — no changes will be made")
        print("  Run with --live to apply\n")
    run(dry_run=not live)
