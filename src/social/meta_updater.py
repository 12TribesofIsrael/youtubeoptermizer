"""Meta post updater module — extracted from scripts/meta-update-posts.py"""

import os
import json
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("META_ACCESS_TOKEN", "")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
IG_ID = os.getenv("INSTAGRAM_BUSINESS_ID", "")

IDENTITY_HOOKS = [
    "They took our name, our language, and our land — but they could not take the prophecy.",
    "The Most High said He would scatter His people to the four corners of the earth. Look where we are.",
    "Deuteronomy 28 is not a curse upon strangers. It is a mirror.",
    "Your ancestors did not come here on slave ships by accident. Scripture told you they would.",
    "Nobody in the Bible looked like what they showed you in Sunday school. Here is the truth.",
    "The so-called Negro. The Black man in America. Deuteronomy 28 describes you EXACTLY.",
    "Which tribe do you descend from? The answer is in the scripture.",
]

PROPHECY_HOOKS = [
    "This prophecy was written 3,000 years ago. It's happening RIGHT NOW.",
    "Every prophecy in Deuteronomy 28 has been fulfilled. Every single one.",
    "We are living in the time of Jacob's trouble. The signs are everywhere.",
    "The Most High is waking up His people right now. This is the moment scripture described.",
    "Everything happening right now was written.",
]

TRUTH_HOOKS = [
    "They changed the pictures. They altered the translations. They removed the books. But Yahuah preserved the truth.",
    "The reason they don't teach this in church.",
    "This verse has been in your Bible your whole life. Did anyone ever explain what it actually means?",
    "They removed this from the curriculum. They could not remove it from the Word.",
    "Your pastor has never shown you this passage. Ask yourself why.",
]

AWE_HOOKS = [
    'Revelation 1:14-15 — "His head and his hairs were white like wool... and his feet like unto fine brass."',
    "Egypt. Babylon. Rome. Every captivity in scripture ended with restoration. We are next.",
    "The Most High chose the most oppressed people on earth to be His covenant nation.",
    "The 12 Tribes of Israel are alive today. Here is who they are according to scripture.",
    "Before the foundations of the earth, your name was written.",
]

CTA_ROTATION = [
    "Full breakdown on YouTube — link in bio https://linktr.ee/aibiblegospels",
    "The full teaching is on my channel > https://linktr.ee/aibiblegospels",
    "The full teaching is on YouTube > https://linktr.ee/aibiblegospels",
    "Save this post. Then watch the full video > https://linktr.ee/aibiblegospels",
    "Full series on YouTube: AI Bible Gospels > https://linktr.ee/aibiblegospels",
]


def pick_hook(post_id, hook_list):
    idx = int(hashlib.md5(post_id.encode()).hexdigest(), 16) % len(hook_list)
    return hook_list[idx]


def pick_cta(post_id):
    idx = int(hashlib.md5((post_id + "cta").encode()).hexdigest(), 16) % len(CTA_ROTATION)
    return CTA_ROTATION[idx]


def _api_get(url):
    try:
        r = urllib.request.urlopen(url)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read())}


def get_facebook_posts(limit=100):
    url = (
        f"https://graph.facebook.com/v25.0/{PAGE_ID}/posts"
        f"?fields=id,message,story,created_time"
        f"&limit={limit}&access_token={TOKEN}"
    )
    data = _api_get(url)
    posts = data.get("data", [])
    while "paging" in data and "next" in data.get("paging", {}):
        data = _api_get(data["paging"]["next"])
        posts.extend(data.get("data", []))
    return posts


def update_facebook_post(post_id, new_message):
    url = f"https://graph.facebook.com/v25.0/{post_id}"
    data = urllib.parse.urlencode({"message": new_message, "access_token": TOKEN}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read())}


def build_viral_caption(original_text, platform="facebook", post_id=""):
    clean = original_text or ""
    for phrase in ["linktr.ee/aibiblegospels", "Watch the full breakdown", "Watch on YouTube", "Subscribe on YouTube", "Link in bio", "link in bio"]:
        clean = clean.replace(phrase, "").strip()

    text_lower = clean.lower()
    if any(w in text_lower for w in ["tribe", "judah", "benjamin", "identity"]):
        hook = pick_hook(post_id, IDENTITY_HOOKS)
        tags = "#12TribesOfIsrael #HebrewIsraelite #AIBibleGospels"
    elif any(w in text_lower for w in ["prophecy", "deut", "revelation", "fulfilled"]):
        hook = pick_hook(post_id, PROPHECY_HOOKS)
        tags = "#BiblicalProphecy #12TribesOfIsrael #AIBibleGospels"
    elif any(w in text_lower for w in ["church", "pastor", "teach", "hidden", "truth"]):
        hook = pick_hook(post_id, TRUTH_HOOKS)
        tags = "#BibleTruth #HebrewIsraelite #AIBibleGospels"
    else:
        hook = pick_hook(post_id, AWE_HOOKS)
        tags = "#12TribesOfIsrael #HebrewIsraelite #AIBibleGospels"

    cta = pick_cta(post_id)
    caption = f"{hook}\n\n{clean}\n\nShare this with someone who needs to hear the truth.\n\n{tags}"
    return caption.strip()
