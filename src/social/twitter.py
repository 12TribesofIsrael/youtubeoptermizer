"""Twitter/X posting module — extracted from scripts/twitter-post.py"""

import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import hmac
import hashlib
import base64
import secrets
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY", "")
API_SECRET = os.getenv("TWITTER_API_SECRET", "")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")

LINKTREE = "https://linktr.ee/aibiblegospels"

TWEETS = [
    {"type": "identity", "text": "THEY TOOK OUR NAME. OUR LANGUAGE. OUR LAND.\n\nBut they could not take the prophecy.\n\nDeuteronomy 28 was written 3,000 years ago describing ONE specific people.\n\nFull breakdown > {link}\n\n#12TribesOfIsrael #HebrewIsraelite #Deuteronomy28 #AIBibleGospels"},
    {"type": "prophecy", "text": "\"And the LORD shall bring thee into Egypt again WITH SHIPS...\"\n— Deuteronomy 28:68 KJV\n\nOnly ONE people in history was brought into captivity by ships.\n\nThis is prophecy.\n\n> {link}\n\n#BiblicalProphecy #HebrewIsraelite #AIBibleGospels"},
    {"type": "identity_chart", "text": "THE 12 TRIBES OF ISRAEL ARE ALIVE TODAY\n\nJudah > African Americans\nBenjamin > West Indians\nLevi > Haitians\nSimeon > Dominicans\nEphraim > Puerto Ricans\nManasseh > Cubans\nGad > Native Americans\n\nFull breakdown > {link}\n\n#12TribesOfIsrael #HebrewIsraelite #AIBibleGospels"},
    {"type": "revelation", "text": "Revelation 1:14-15:\n\n\"His head and hairs were white like WOOL... his feet like FINE BRASS, as if burned in a furnace.\"\n\nWool hair. Brass skin.\n\nDid anyone ever explain what it means?\n\n{link}\n\n#BibleTruth #HebrewIsraelite #AIBibleGospels"},
    {"type": "suppressed", "text": "They changed the pictures.\nThey altered the translations.\nThey removed entire books.\n\nBut they could NOT remove Deuteronomy 28.\n\nRead it. Every verse.\n\nFull teaching > {link}\n\n#BibleTruth #ChurchWontTeachThis #AIBibleGospels #HebrewIsraelite"},
    {"type": "restoration", "text": "Egypt. Babylon. Rome.\n\nEvery captivity in scripture ended with RESTORATION.\n\nWe are living in the final captivity.\n\nWatch the series > {link}\n\n#ProphecyRevealed #12Tribes #HebrewIsraelite #AIBibleGospels"},
    {"type": "engagement", "text": "Which tribe do you descend from?\n\nJudah\nBenjamin\nLevi\nEphraim\nManasseh\nGad\nOther\n\nDrop it below\n\nFull breakdown > {link}\n\n#12TribesOfIsrael #IsraeliteIdentity #HebrewIsraelite #AIBibleGospels"},
    {"type": "cinematic", "text": "AI Bible Gospels brings scripture to life with:\n\nMelanated biblical characters\nCinematic AI animation\nNarration rooted in the Word\n\nNo slides. No talking heads.\nJust the story of your people.\n\nSubscribe > {link}\n\n#AIBibleGospels #12Tribes #HebrewIsraelite"},
]


def percent_encode(s):
    return urllib.parse.quote(str(s), safe="")


def build_oauth_header(method, url, params, body_params=None):
    oauth_params = {
        "oauth_consumer_key": API_KEY,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": ACCESS_TOKEN,
        "oauth_version": "1.0",
    }
    all_params = {**oauth_params}
    if body_params:
        all_params.update(body_params)
    sorted_params = sorted(all_params.items())
    param_string = "&".join(f"{percent_encode(k)}={percent_encode(v)}" for k, v in sorted_params)
    base_string = "&".join([percent_encode(method.upper()), percent_encode(url), percent_encode(param_string)])
    signing_key = f"{percent_encode(API_SECRET)}&{percent_encode(ACCESS_SECRET)}"
    signature = base64.b64encode(hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()).decode()
    oauth_params["oauth_signature"] = signature
    header_parts = ", ".join(f'{percent_encode(k)}="{percent_encode(v)}"' for k, v in sorted(oauth_params.items()))
    return f"OAuth {header_parts}"


def post_tweet(text, reply_to_id=None):
    url = "https://api.twitter.com/2/tweets"
    body = {"text": text}
    if reply_to_id:
        body["reply"] = {"in_reply_to_tweet_id": reply_to_id}
    body_json = json.dumps(body).encode()
    oauth_header = build_oauth_header("POST", url, {})
    req = urllib.request.Request(url, data=body_json, method="POST")
    req.add_header("Authorization", oauth_header)
    req.add_header("Content-Type", "application/json")
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read())}
