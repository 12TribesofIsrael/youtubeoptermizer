"""Facebook posting module — extracted from scripts/facebook-post.py"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("META_ACCESS_TOKEN", "")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
LINKTREE = "https://linktr.ee/aibiblegospels"

POSTS = [
    {
        "type": "identity",
        "hook": "THEY TOOK OUR NAME. THEY TOOK OUR LANGUAGE. THEY TOOK OUR LAND.\n\nBut they could not take the prophecy.",
        "body": "Deuteronomy 28 is not a curse upon strangers. It is a mirror held up to one specific people — the people who were scattered by ships, stripped of their identity, and told to forget who they are.\n\nThe Most High preserved the truth in scripture. Nobody can hide what He ordained.",
        "cta": "Watch the full breakdown on our YouTube channel",
        "engagement": "Share this if you know who you are. The awakening is real.",
        "tags": "#12TribesOfIsrael #HebrewIsraelite #Deuteronomy28 #AIBibleGospels #BlackHistory"
    },
    {
        "type": "prophecy",
        "hook": "EVERY PROPHECY IN DEUTERONOMY 28 HAS BEEN FULFILLED.\n\nEvery single one.",
        "body": '"And the LORD shall bring thee into Egypt again with ships..." — Deuteronomy 28:68 KJV\n\nThis was written 3,000 years ago. There is only one people on earth whose history matches this verse word for word.',
        "cta": "See the full prophecy series on YouTube",
        "engagement": "Tag a brother or sister who needs to see this.",
        "tags": "#Deuteronomy28 #BiblicalProphecy #HebrewIsraelite #12Tribes #AIBibleGospels"
    },
    {
        "type": "identity_chart",
        "hook": "THE 12 TRIBES OF ISRAEL ARE ALIVE TODAY.\n\nHere is who they are according to scripture:",
        "body": "Judah > African Americans\nBenjamin > West Indians / Caribbean\nLevi > Haitians\nSimeon > Dominicans\nEphraim > Puerto Ricans\nManasseh > Cubans\nGad > Native Americans\nReuben > Seminole Indians\nNaphtali > Argentinians / Chileans\nZebulun > Guatemalans / Panamanians\nIssachar > Mexicans\nAsher > Colombians / Venezuelans",
        "cta": "Full tribe-by-tribe breakdown on YouTube",
        "engagement": "Drop your tribe in the comments below. Which one are you?",
        "tags": "#12TribesOfIsrael #HebrewIsraelite #TribeOfJudah #IsraeliteIdentity #AIBibleGospels"
    },
    {
        "type": "suppressed_truth",
        "hook": "THE REASON THEY CHANGED THE PICTURES IN YOUR BIBLE.",
        "body": 'Revelation 1:14-15: "His head and his hairs were white like wool... and his feet like unto fine brass, as if they burned in a furnace."\n\nWool hair. Brass-colored skin. This description has been in your Bible your entire life.',
        "cta": "Watch the full teaching on YouTube",
        "engagement": "Share this with someone who has never questioned what they were shown in church.",
        "tags": "#BibleTruth #Revelation #HebrewIsraelite #TrueIsraelites #AIBibleGospels"
    },
    {
        "type": "awe",
        "hook": "EGYPT. BABYLON. ROME.\n\nEvery captivity in scripture ended with restoration.",
        "body": "The children of Israel have been in captivity before. Every single time, the Most High brought them out.\n\nWe are living in the final captivity. The prophecies of restoration are being fulfilled in our generation.",
        "cta": "Watch the Prophecy Revealed series on YouTube",
        "engagement": "Comment AMEN if you believe the restoration is coming.",
        "tags": "#ProphecyRevealed #BiblicalProphecy #12Tribes #HebrewIsraelite #AIBibleGospels"
    },
    {
        "type": "tribe_engagement",
        "hook": "WHICH TRIBE DO YOU DESCEND FROM?\n\nDrop it in the comments.",
        "body": "Every tribe has a prophesied territory and a prophesied restoration. The Most High is waking up His people tribe by tribe.",
        "cta": "Full tribe breakdown series on YouTube",
        "engagement": "Share this post in your community. Someone in your circle is searching for this answer right now.",
        "tags": "#12TribesOfIsrael #TribeIdentity #HebrewIsraelite #IsraeliteNation #AIBibleGospels"
    },
    {
        "type": "cinematic",
        "hook": "BEFORE THE FOUNDATIONS OF THE EARTH, YOUR NAME WAS WRITTEN.",
        "body": "AI Bible Gospels uses cutting-edge AI cinematics to bring the scriptures to life — with melanated biblical characters, cinematic lighting, and narration rooted in the Word.",
        "cta": "Subscribe on YouTube and watch the full series",
        "engagement": "Share this with someone who has never seen the Bible told this way.",
        "tags": "#AIBibleGospels #BiblicalHistory #12Tribes #HebrewIsraelite #CinematicBible"
    },
    {
        "type": "current_events",
        "hook": "EVERYTHING HAPPENING RIGHT NOW WAS WRITTEN.\n\nThe Most High does nothing without first revealing it to His servants the prophets. (Amos 3:7)",
        "body": "The signs are everywhere. The prophecies are accelerating. The people who were scattered are waking up.\n\nDeuteronomy 28 is not ancient history — it is a living document.",
        "cta": "Watch our prophecy series on YouTube",
        "engagement": "Tag someone who is paying attention to what is happening in the world right now.",
        "tags": "#BiblicalProphecy #EndTimes #HebrewIsraelite #12Tribes #AIBibleGospels"
    },
]


def api_post_fb(endpoint, data):
    url = f"https://graph.facebook.com/v25.0/{endpoint}"
    data_encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data_encoded, method="POST")
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read())}


def get_page_token():
    url = f"https://graph.facebook.com/v25.0/{PAGE_ID}?fields=access_token&access_token={TOKEN}"
    try:
        r = urllib.request.urlopen(url)
        data = json.loads(r.read())
        return data.get("access_token", TOKEN)
    except Exception:
        return TOKEN


def build_post_message(post_template, youtube_url=None):
    link = youtube_url or LINKTREE
    msg = f"""{post_template['hook']}

{post_template['body']}

{post_template['cta']} > {link}

{post_template['engagement']}

{post_template['tags']} #BlackHistory #BibleStudy #TrueIsraelites"""
    return msg.strip()


def post_to_facebook(message, link=None, dry_run=True):
    page_token = get_page_token()
    data = {"message": message, "access_token": page_token}
    if link:
        data["link"] = link
    if dry_run:
        return {"id": "dry_run_id"}
    return api_post_fb(f"{PAGE_ID}/feed", data)
