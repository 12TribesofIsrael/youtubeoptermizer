"""
Meta Post Updater — AI Bible Gospels
Updates all Facebook Page posts and Instagram posts with viral captions + YouTube CTAs.
"""

import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("META_ACCESS_TOKEN")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
IG_ID = os.getenv("INSTAGRAM_BUSINESS_ID")

YOUTUBE_CTA = "Watch the full breakdown on YouTube → https://linktr.ee/aibiblegospels"

# ── Viral Hook Banks (from competitor research 2025-2026) ─────────────────────

IDENTITY_HOOKS = [
    "They took our name, our language, and our land — but they could not take the prophecy. 🔱",
    "The Most High said He would scatter His people to the four corners of the earth. Look where we are. 🔱",
    "Deuteronomy 28 is not a curse upon strangers. It is a mirror.",
    "Your ancestors did not come here on slave ships by accident. Scripture told you they would.",
    "Nobody in the Bible looked like what they showed you in Sunday school. Here is the truth. 👀",
    "The so-called Negro. The Black man in America. Deuteronomy 28 describes you EXACTLY. This is not coincidence. This is prophecy.",
    "Which tribe do you descend from? The answer is in the scripture — and it will change everything. Drop your tribe below 👇",
]

PROPHECY_HOOKS = [
    "This prophecy was written 3,000 years ago. It's happening RIGHT NOW. 🔥",
    "Every prophecy in Deuteronomy 28 has been fulfilled. Every single one.",
    "We are living in the time of Jacob's trouble. The signs are everywhere.",
    "The Most High is waking up His people right now. This is the moment scripture described.",
    "Everything happening right now was written. Yahuah does nothing without first revealing it to His servants the prophets. (Amos 3:7)",
    '"And the LORD shall scatter thee among all people, from the one end of the earth even unto the other." — Deuteronomy 28:64 KJV\n\nThis was written 3,000 years ago. How did Moses know?',
]

TRUTH_HOOKS = [
    "They changed the pictures. They altered the translations. They removed the books. But Yahuah preserved the truth in scripture. Nobody can hide what He ordained.",
    "The reason they don't teach this in church. The reason Sunday school never showed you THIS passage.",
    "This verse has been in your Bible your whole life. Did anyone ever explain what it actually means?",
    "They removed this from the curriculum. They could not remove it from the Word.",
    "Your pastor has never shown you this passage. Ask yourself why. 👀",
    "The history books changed everything except the prophecy. Read it for yourself.",
]

AWE_HOOKS = [
    'Revelation 1:14–15 — "His head and his hairs were white like wool... and his feet like unto fine brass, as if they burned in a furnace." 📖\n\nThis has been in your Bible your whole life.',
    "Egypt. Babylon. Rome. Every captivity in scripture ended with restoration. We are next. 🔥",
    "The Most High chose the most oppressed people on earth to be His covenant nation. That was not an accident.",
    "The 12 Tribes of Israel are alive today. Here is who they are according to scripture. 🔱",
    "Before the foundations of the earth, your name was written. The Most High remembered His people.",
    "Simon of Cyrene carried the cross of Yashua. He was African. The first to follow Christ was one of us.",
]

CTA_ROTATION = [
    "Full breakdown on YouTube — link in bio 🔗 https://linktr.ee/aibiblegospels",
    "This is the short version. The full teaching is on my channel → https://linktr.ee/aibiblegospels",
    "I could not fit everything in this clip. The full teaching is on YouTube → https://linktr.ee/aibiblegospels",
    "Save this post. Then watch the full video — this is just the beginning → https://linktr.ee/aibiblegospels",
    "Full series on YouTube: AI Bible Gospels. Every part is posted. Start from Episode 1 → https://linktr.ee/aibiblegospels",
    "Watch the complete series on YouTube → https://linktr.ee/aibiblegospels",
    "YouTube: AI Bible Gospels. Search it. Watch the full series → https://linktr.ee/aibiblegospels",
]

import hashlib

def pick_hook(post_id, hook_list):
    """Deterministically pick a hook based on post ID so it's consistent on re-runs."""
    idx = int(hashlib.md5(post_id.encode()).hexdigest(), 16) % len(hook_list)
    return hook_list[idx]

def pick_cta(post_id):
    idx = int(hashlib.md5((post_id + "cta").encode()).hexdigest(), 16) % len(CTA_ROTATION)
    return CTA_ROTATION[idx]

# ── Helpers ────────────────────────────────────────────────────────────────────

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

# ── Facebook ───────────────────────────────────────────────────────────────────

def get_facebook_posts(limit=100):
    """Fetch all Facebook Page posts."""
    url = (
        f"https://graph.facebook.com/v25.0/{PAGE_ID}/posts"
        f"?fields=id,message,story,created_time"
        f"&limit={limit}&access_token={TOKEN}"
    )
    data = api_get(url)
    posts = data.get("data", [])
    # paginate
    while "paging" in data and "next" in data["paging"]:
        data = api_get(data["paging"]["next"])
        posts.extend(data.get("data", []))
    return posts

def update_facebook_post(post_id, new_message):
    """Update a Facebook post message."""
    url = f"https://graph.facebook.com/v25.0/{post_id}"
    result = api_post(url, {"message": new_message, "access_token": TOKEN})
    return result

def get_page_access_token():
    """Get the Page-specific access token (needed for posting as the Page)."""
    url = f"https://graph.facebook.com/v25.0/{PAGE_ID}?fields=access_token&access_token={TOKEN}"
    data = api_get(url)
    return data.get("access_token", TOKEN)

# ── Instagram ──────────────────────────────────────────────────────────────────

def get_instagram_posts(limit=100):
    """Fetch all Instagram media posts."""
    url = (
        f"https://graph.facebook.com/v25.0/{IG_ID}/media"
        f"?fields=id,caption,timestamp,permalink,media_type"
        f"&limit={limit}&access_token={TOKEN}"
    )
    data = api_get(url)
    posts = data.get("data", [])
    while "paging" in data and "next" in data["paging"]:
        data = api_get(data["paging"]["next"])
        posts.extend(data.get("data", []))
    return posts

def update_instagram_post(media_id, new_caption):
    """Update an Instagram post caption."""
    url = f"https://graph.facebook.com/v25.0/{media_id}"
    result = api_post(url, {
        "caption": new_caption,
        "comment_enabled": "true",
        "access_token": TOKEN
    })
    return result

# ── Caption Builder ────────────────────────────────────────────────────────────

def build_viral_caption(original_text, platform="facebook", post_id=""):
    """
    Enhance an existing caption with viral hooks and YouTube CTA.
    Uses research-backed hook formulas from top performers in this niche.
    """
    clean = original_text or ""
    for phrase in [
        "linktr.ee/aibiblegospels",
        "Watch the full breakdown",
        "Watch on YouTube",
        "Subscribe on YouTube",
        "Link in bio",
        "link in bio",
    ]:
        clean = clean.replace(phrase, "").strip()

    # Detect content type and pick matching hook bank
    text_lower = clean.lower()
    if any(w in text_lower for w in ["tribe", "tribes", "judah", "benjamin", "levi", "ephraim", "identity", "who are"]):
        hook = pick_hook(post_id, IDENTITY_HOOKS)
        if platform == "instagram":
            tags = "#12TribesOfIsrael #HebrewIsraelite #IsraeliteIdentity #TribeOfJudah #AIBibleGospels"
        else:
            tags = "#12TribesOfIsrael #HebrewIsraelite #AIBibleGospels"

    elif any(w in text_lower for w in ["prophecy", "prophec", "deut", "revelation", "daniel", "fulfilled", "end time"]):
        hook = pick_hook(post_id, PROPHECY_HOOKS)
        if platform == "instagram":
            tags = "#BiblicalProphecy #ProphecyRevealed #12TribesOfIsrael #HebrewIsraelite #AIBibleGospels"
        else:
            tags = "#BiblicalProphecy #12TribesOfIsrael #AIBibleGospels"

    elif any(w in text_lower for w in ["church", "pastor", "teach", "hidden", "truth", "lie", "they don"]):
        hook = pick_hook(post_id, TRUTH_HOOKS)
        if platform == "instagram":
            tags = "#BibleTruth #HebrewIsraelite #ChurchWontTeachThis #12TribesOfIsrael #AIBibleGospels"
        else:
            tags = "#BibleTruth #HebrewIsraelite #AIBibleGospels"

    else:
        hook = pick_hook(post_id, AWE_HOOKS)
        if platform == "instagram":
            tags = "#12TribesOfIsrael #HebrewIsraelite #BibleTruth #ProphecyRevealed #AIBibleGospels"
        else:
            tags = "#12TribesOfIsrael #HebrewIsraelite #AIBibleGospels"

    cta = pick_cta(post_id)

    if platform == "facebook":
        # Facebook: no link in body — CTA drives to comments
        # Algorithm rewards comments + shares over link clicks
        caption = f"""{hook}

{clean}

Share this with someone who needs to hear the truth. The awakening is real.

Comment 'SEND IT' and I'll drop the full YouTube link below. 👇

{tags}"""

    else:  # instagram
        # Instagram: link in bio CTA + save prompt + 5 targeted hashtags
        caption = f"""{hook}

{clean}

Save this post. Then watch the full teaching on YouTube → link in bio

Which tribe do you descend from? Drop it in the comments 👇

.
.
.
{tags} #BlackHistory #BibleStudy #WakeUpIsrael #ProphecyFulfilled #TrueIsraelites"""

    return caption.strip()

# ── Main ───────────────────────────────────────────────────────────────────────

def run_facebook_update(dry_run=True):
    print(f"\n{'='*55}")
    print(f"  FACEBOOK POST UPDATER {'(DRY RUN)' if dry_run else '(LIVE)'}")
    print(f"{'='*55}\n")

    posts = get_facebook_posts()
    print(f"Found {len(posts)} Facebook posts\n")

    updated = 0
    skipped = 0

    for post in posts:
        post_id = post["id"]
        original = post.get("message") or post.get("story") or ""
        created = post.get("created_time", "")[:10]

        if not original or len(original) < 10:
            skipped += 1
            continue

        # Skip if already has our CTA
        if "linktr.ee/aibiblegospels" in original:
            print(f"  SKIP (already updated): {original[:60]}...")
            skipped += 1
            continue

        new_caption = build_viral_caption(original, platform="facebook", post_id=post_id)

        print(f"  POST: {created} — {original[:60]}...")
        print(f"  NEW:  {new_caption[:80]}...")

        if not dry_run:
            result = update_facebook_post(post_id, new_caption)
            if "error" in result:
                print(f"  ERROR: {result['error']}")
            else:
                print(f"  ✅ Updated")
                updated += 1
            time.sleep(0.5)  # rate limit
        else:
            updated += 1

        print()

    print(f"\n{'='*55}")
    print(f"  Facebook: {updated} would be updated, {skipped} skipped")
    if dry_run:
        print(f"  Run with dry_run=False to apply changes")
    print(f"{'='*55}\n")


def run_instagram_update(dry_run=True):
    print(f"\n{'='*55}")
    print(f"  INSTAGRAM POST UPDATER {'(DRY RUN)' if dry_run else '(LIVE)'}")
    print(f"{'='*55}\n")

    posts = get_instagram_posts()
    print(f"Found {len(posts)} Instagram posts\n")

    updated = 0
    skipped = 0

    for post in posts:
        media_id = post["id"]
        original = post.get("caption") or ""
        created = post.get("timestamp", "")[:10]
        media_type = post.get("media_type", "")
        permalink = post.get("permalink", "")

        if not original or len(original) < 10:
            skipped += 1
            continue

        if "linktr.ee/aibiblegospels" in original:
            print(f"  SKIP (already updated): {original[:60]}...")
            skipped += 1
            continue

        new_caption = build_viral_caption(original, platform="instagram", post_id=media_id)

        print(f"  POST: {created} [{media_type}] — {original[:60]}...")
        print(f"  NEW:  {new_caption[:80]}...")
        if permalink:
            print(f"  URL:  {permalink}")

        if not dry_run:
            result = update_instagram_post(media_id, new_caption)
            if "error" in result:
                print(f"  ERROR: {result['error']}")
            else:
                print(f"  ✅ Updated")
                updated += 1
            time.sleep(0.5)
        else:
            updated += 1

        print()

    print(f"\n{'='*55}")
    print(f"  Instagram: {updated} would be updated, {skipped} skipped")
    if dry_run:
        print(f"  Run with dry_run=False to apply changes")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    import sys
    live = "--live" in sys.argv
    platform = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "all"

    if dry_run := not live:
        print("\n⚠️  DRY RUN MODE — no changes will be made")
        print("   Run with --live to apply updates\n")

    if platform in ("all", "facebook"):
        run_facebook_update(dry_run=dry_run)

    if platform in ("all", "instagram"):
        run_instagram_update(dry_run=dry_run)
