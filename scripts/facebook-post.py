"""
Facebook Page Poster — AI Bible Gospels
Creates new posts on the Facebook Page linking to top YouTube videos.
Fetches latest YouTube videos and posts them with viral captions.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import hashlib
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("META_ACCESS_TOKEN")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
YT_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
CHANNEL_ID = "UCxxxxxxx"  # Will be fetched automatically

YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@AIBIBLEGOSPELS"
LINKTREE = "https://linktr.ee/aibiblegospels"

# ── Viral Post Templates (research-backed) ─────────────────────────────────────

POSTS = [
    {
        "type": "identity",
        "hook": "THEY TOOK OUR NAME. THEY TOOK OUR LANGUAGE. THEY TOOK OUR LAND.\n\nBut they could not take the prophecy.",
        "body": "Deuteronomy 28 is not a curse upon strangers. It is a mirror held up to one specific people — the people who were scattered by ships, stripped of their identity, and told to forget who they are.\n\nThe Most High preserved the truth in scripture. Nobody can hide what He ordained.",
        "cta": "Watch the full breakdown on our YouTube channel",
        "engagement": "Share this if you know who you are. The awakening is real. 🔱",
        "tags": "#12TribesOfIsrael #HebrewIsraelite #Deuteronomy28 #AIBibleGospels #BlackHistory"
    },
    {
        "type": "prophecy",
        "hook": "EVERY PROPHECY IN DEUTERONOMY 28 HAS BEEN FULFILLED.\n\nEvery single one.",
        "body": '"And the LORD shall bring thee into Egypt again with ships, by the way whereof I spake unto thee, Thou shalt see it no more again: and there ye shall be sold unto your enemies for bondmen and bondwomen, and no man shall buy you." — Deuteronomy 28:68 KJV\n\nThis was written 3,000 years ago. There is only one people on earth whose history matches this verse word for word.',
        "cta": "See the full prophecy series on YouTube",
        "engagement": "Tag a brother or sister who needs to see this. 🔥",
        "tags": "#Deuteronomy28 #BiblicalProphecy #HebrewIsraelite #12Tribes #AIBibleGospels"
    },
    {
        "type": "identity_chart",
        "hook": "THE 12 TRIBES OF ISRAEL ARE ALIVE TODAY.\n\nHere is who they are according to scripture:",
        "body": "• Judah → African Americans\n• Benjamin → West Indians / Caribbean\n• Levi → Haitians\n• Simeon → Dominicans\n• Ephraim → Puerto Ricans\n• Manasseh → Cubans\n• Gad → Native Americans\n• Reuben → Seminole Indians\n• Naphtali → Argentinians / Chileans\n• Zebulun → Guatemalans / Panamanians\n• Issachar → Mexicans\n• Asher → Colombians / Venezuelans\n\nThis is not opinion. This is scripture, history, and bloodline. Study it. Test it against the Word.",
        "cta": "Full tribe-by-tribe breakdown on YouTube",
        "engagement": "Drop your tribe in the comments below 👇 Which one are you?",
        "tags": "#12TribesOfIsrael #HebrewIsraelite #TribeOfJudah #IsraeliteIdentity #AIBibleGospels #BlackHistory"
    },
    {
        "type": "suppressed_truth",
        "hook": "THE REASON THEY CHANGED THE PICTURES IN YOUR BIBLE.",
        "body": "They changed the images. They altered the translations. They removed entire books.\n\nBut Revelation 1:14–15 is still in your Bible right now:\n\n\"His head and his hairs were white like wool... and his feet like unto fine brass, as if they burned in a furnace.\"\n\nWool hair. Brass-colored skin. This description has been in your Bible your entire life. Did anyone ever explain what it means?",
        "cta": "Watch the full teaching on YouTube — link below",
        "engagement": "Share this with someone who has never questioned what they were shown in church.",
        "tags": "#BibleTruth #Revelation #HebrewIsraelite #TrueIsraelites #AIBibleGospels #ChurchWontTeachThis"
    },
    {
        "type": "awe",
        "hook": "EGYPT. BABYLON. ROME.\n\nEvery captivity in scripture ended with restoration.",
        "body": "The children of Israel have been in captivity before. Every single time, the Most High brought them out.\n\nWe are living in the final captivity. The prophecies of restoration are being fulfilled in our generation.\n\nThis is not wishful thinking. This is documented in Deuteronomy, Isaiah, Jeremiah, Ezekiel, and Revelation — written thousands of years before any of us were born.",
        "cta": "Watch the Prophecy Revealed series on YouTube",
        "engagement": "Comment AMEN if you believe the restoration is coming. 🔱",
        "tags": "#ProphecyRevealed #BiblicalProphecy #12Tribes #HebrewIsraelite #AIBibleGospels #Restoration"
    },
    {
        "type": "tribe_engagement",
        "hook": "WHICH TRIBE DO YOU DESCEND FROM?\n\nDrop it in the comments. Let's see how many of the 12 are represented here.",
        "body": "Every tribe has a prophesied territory and a prophesied restoration. The Most High is waking up His people tribe by tribe.\n\nWe are a people being restored. Piece by piece. Tribe by tribe.\n\nIf you are just beginning to research your identity — start with Deuteronomy 28 and work your way through the prophets. The evidence is overwhelming.",
        "cta": "Full tribe breakdown series on YouTube — link below",
        "engagement": "Share this post in your community. Someone in your circle is searching for this answer right now.",
        "tags": "#12TribesOfIsrael #TribeIdentity #HebrewIsraelite #IsraeliteNation #AIBibleGospels #WakeUpIsrael"
    },
    {
        "type": "cinematic",
        "hook": "BEFORE THE FOUNDATIONS OF THE EARTH, YOUR NAME WAS WRITTEN.",
        "body": "AI Bible Gospels uses cutting-edge AI cinematics to bring the scriptures to life — with melanated biblical characters, cinematic lighting, and narration rooted in the Word.\n\nNo talking heads. No slides. Just the story of your people, told the way it deserves to be told.\n\nThe 12 Tribes of Israel. The Prophecy Revealed. The truth they tried to bury.",
        "cta": "Subscribe on YouTube and watch the full series",
        "engagement": "Share this with someone who has never seen the Bible told this way. 🎬",
        "tags": "#AIBibleGospels #BiblicalHistory #12Tribes #HebrewIsraelite #CinematicBible #ProphecyRevealed"
    },
    {
        "type": "current_events",
        "hook": "EVERYTHING HAPPENING RIGHT NOW WAS WRITTEN.\n\nThe Most High does nothing without first revealing it to His servants the prophets. (Amos 3:7)",
        "body": "The signs are everywhere. The prophecies are accelerating. The people who were scattered are waking up.\n\nDeuteronomy 28 is not ancient history — it is a living document describing the exact condition of one specific people in the earth today.\n\nOpen your Bible. Read it slowly. Ask the Most High to open your eyes.",
        "cta": "Watch our prophecy series on YouTube — link below",
        "engagement": "Tag someone who is paying attention to what is happening in the world right now.",
        "tags": "#BiblicalProphecy #EndTimes #HebrewIsraelite #12Tribes #AIBibleGospels #Awakening"
    },
]

# ── Helpers ────────────────────────────────────────────────────────────────────

def api_post_fb(endpoint, data):
    url = f"https://graph.facebook.com/v25.0/{endpoint}"
    data_encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data_encoded, method="POST")
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read())}

def api_get(url):
    try:
        r = urllib.request.urlopen(url)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read())}

def get_page_token():
    """Get Page-specific access token for posting AS the Page."""
    url = f"https://graph.facebook.com/v25.0/{PAGE_ID}?fields=access_token&access_token={TOKEN}"
    data = api_get(url)
    return data.get("access_token", TOKEN)

def build_post_message(post_template, youtube_url=None):
    """Build the full Facebook post message from a template."""
    link = youtube_url or LINKTREE
    msg = f"""{post_template['hook']}

{post_template['body']}

{post_template['cta']} 👉 {link}

{post_template['engagement']}

{post_template['tags']} #BlackHistory #BibleStudy #TrueIsraelites"""
    return msg.strip()

def post_to_facebook(message, link=None, dry_run=True):
    """Post a message to the Facebook Page."""
    page_token = get_page_token()
    data = {
        "message": message,
        "access_token": page_token,
    }
    if link:
        data["link"] = link

    if dry_run:
        print(f"\n{'─'*55}")
        print("DRY RUN — Would post to Facebook Page:")
        print(f"{'─'*55}")
        print(message[:300] + "..." if len(message) > 300 else message)
        print(f"{'─'*55}")
        return {"id": "dry_run_id"}

    result = api_post_fb(f"{PAGE_ID}/feed", data)
    return result

def post_comment_with_link(post_id, youtube_url, page_token):
    """Post YouTube link as first comment (avoids FB reach penalty for links in post body)."""
    data = {
        "message": f"▶️ Watch the full series on YouTube: {youtube_url}\n\nSubscribe for new videos every week → {LINKTREE}",
        "access_token": page_token,
    }
    result = api_post_fb(f"{post_id}/comments", data)
    return result

# ── Main ───────────────────────────────────────────────────────────────────────

def run(dry_run=True, count=None):
    print(f"\n{'='*55}")
    print(f"  FACEBOOK PAGE POSTER {'(DRY RUN)' if dry_run else '(LIVE)'}")
    print(f"  Page ID: {PAGE_ID}")
    print(f"{'='*55}\n")

    page_token = get_page_token()
    posts_to_run = POSTS[:count] if count else POSTS

    posted = 0
    for i, template in enumerate(posts_to_run):
        print(f"Post {i+1}/{len(posts_to_run)}: [{template['type']}]")
        message = build_post_message(template, YOUTUBE_CHANNEL_URL)

        result = post_to_facebook(message, dry_run=dry_run)

        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            post_id = result.get("id", "")
            print(f"  ✅ Posted — ID: {post_id}")
            posted += 1

            # Drop YouTube link as first comment (avoids reach penalty)
            if not dry_run and post_id and post_id != "dry_run_id":
                time.sleep(2)
                comment = post_comment_with_link(post_id, YOUTUBE_CHANNEL_URL, page_token)
                if "error" not in comment:
                    print(f"  ✅ YouTube link added as first comment")
                time.sleep(3)  # Rate limiting between posts

    print(f"\n{'='*55}")
    print(f"  {'Would post' if dry_run else 'Posted'}: {posted}/{len(posts_to_run)} posts")
    if dry_run:
        print(f"  Run with --live to actually post")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    live = "--live" in sys.argv
    count_arg = next((int(a) for a in sys.argv[1:] if a.isdigit()), None)

    if not live:
        print("\n⚠️  DRY RUN — no posts will be created")
        print("   Run with --live to post for real")
        print("   Run with --live 1 to post just 1 as a test\n")

    run(dry_run=not live, count=count_arg)
