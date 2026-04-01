"""
Twitter/X Poster — AI Bible Gospels
Posts viral tweets and threads to @aibiblegospels to drive traffic to YouTube.
"""

import os
import sys
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

API_KEY        = os.getenv("TWITTER_API_KEY")
API_SECRET     = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN   = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET  = os.getenv("TWITTER_ACCESS_SECRET")

YOUTUBE_URL  = "https://www.youtube.com/@AIBIBLEGOSPELS"
LINKTREE     = "https://linktr.ee/aibiblegospels"

# ── Viral Tweet Templates ──────────────────────────────────────────────────────

TWEETS = [
    {
        "type": "identity",
        "text": "THEY TOOK OUR NAME. OUR LANGUAGE. OUR LAND.\n\nBut they could not take the prophecy.\n\nDeuteronomy 28 was written 3,000 years ago describing ONE specific people.\n\nRead it slowly. Ask yourself who it describes.\n\n🔱 Full breakdown → {link}\n\n#12TribesOfIsrael #HebrewIsraelite #Deuteronomy28 #AIBibleGospels"
    },
    {
        "type": "prophecy",
        "text": "\"And the LORD shall bring thee into Egypt again WITH SHIPS...\"\n— Deuteronomy 28:68 KJV\n\nWritten 3,000 years ago.\n\nOnly ONE people in history was brought into captivity by ships and sold as slaves.\n\nThis is not coincidence. This is prophecy.\n\n▶️ {link}\n\n#BiblicalProphecy #HebrewIsraelite #AIBibleGospels"
    },
    {
        "type": "identity_chart",
        "text": "THE 12 TRIBES OF ISRAEL ARE ALIVE TODAY 🔱\n\n• Judah → African Americans\n• Benjamin → West Indians\n• Levi → Haitians\n• Simeon → Dominicans\n• Ephraim → Puerto Ricans\n• Manasseh → Cubans\n• Gad → Native Americans\n\nThis is scripture. Study it.\n\nFull tribe breakdown → {link}\n\n#12TribesOfIsrael #HebrewIsraelite #AIBibleGospels"
    },
    {
        "type": "revelation",
        "text": "Revelation 1:14–15 is still in your Bible right now:\n\n\"His head and hairs were white like WOOL... his feet like FINE BRASS, as if burned in a furnace.\"\n\nWool hair. Brass skin.\n\nThis has been in your Bible your whole life.\n\nDid anyone ever explain what it means? 👀\n\n{link}\n\n#BibleTruth #HebrewIsraelite #AIBibleGospels"
    },
    {
        "type": "suppressed",
        "text": "They changed the pictures.\nThey altered the translations.\nThey removed entire books.\n\nBut they could NOT remove Deuteronomy 28 from your Bible.\n\nRead it. Every verse. Ask the Most High to open your eyes.\n\n▶️ Full teaching → {link}\n\n#BibleTruth #ChurchWontTeachThis #AIBibleGospels #HebrewIsraelite"
    },
    {
        "type": "restoration",
        "text": "Egypt. Babylon. Rome.\n\nEvery captivity in scripture ended with RESTORATION.\n\nWe are living in the final captivity. The prophecies are accelerating.\n\nThe Most High remembered His people every single time.\n\nHe will again. 🔥\n\nWatch the series → {link}\n\n#ProphecyRevealed #12Tribes #HebrewIsraelite #AIBibleGospels"
    },
    {
        "type": "engagement",
        "text": "Which tribe do you descend from?\n\n• Judah 🔱\n• Benjamin\n• Levi\n• Ephraim\n• Manasseh\n• Gad\n• Other tribe\n\nDrop it below 👇\n\nFull tribe identity breakdown → {link}\n\n#12TribesOfIsrael #IsraeliteIdentity #HebrewIsraelite #AIBibleGospels"
    },
    {
        "type": "cinematic",
        "text": "AI Bible Gospels brings scripture to life with:\n\n✅ Melanated biblical characters\n✅ Cinematic AI animation\n✅ Narration rooted in the Word\n✅ The truth they tried to bury\n\nNo slides. No talking heads.\n\nJust the story of your people, told the way it deserves. 🎬\n\nSubscribe → {link}\n\n#AIBibleGospels #12Tribes #HebrewIsraelite #BiblicalHistory"
    },
]

# ── OAuth 1.0a Signing ─────────────────────────────────────────────────────────

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
    base_string = "&".join([
        percent_encode(method.upper()),
        percent_encode(url),
        percent_encode(param_string),
    ])

    signing_key = f"{percent_encode(API_SECRET)}&{percent_encode(ACCESS_SECRET)}"
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()

    oauth_params["oauth_signature"] = signature
    header_parts = ", ".join(
        f'{percent_encode(k)}="{percent_encode(v)}"'
        for k, v in sorted(oauth_params.items())
    )
    return f"OAuth {header_parts}"


def post_tweet(text, reply_to_id=None):
    """Post a tweet using Twitter API v2."""
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


# ── Main ───────────────────────────────────────────────────────────────────────

def run(dry_run=True, count=None):
    print(f"\n{'='*55}")
    print(f"  TWITTER POSTER {'(DRY RUN)' if dry_run else '(LIVE)'}")
    print(f"  Account: @aibiblegospels")
    print(f"{'='*55}\n")

    tweets_to_run = TWEETS[:count] if count else TWEETS
    posted = 0

    for i, template in enumerate(tweets_to_run):
        text = template["text"].replace("{link}", LINKTREE)

        print(f"Tweet {i+1}/{len(tweets_to_run)}: [{template['type']}]")

        if dry_run:
            print(f"{'─'*50}")
            print(text[:280] + "..." if len(text) > 280 else text)
            print(f"  Chars: {len(text)}")
            print(f"{'─'*50}\n")
            posted += 1
        else:
            result = post_tweet(text)
            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                tweet_id = result.get("data", {}).get("id", "")
                print(f"  ✅ Posted — ID: {tweet_id}")
                posted += 1
            time.sleep(3)  # rate limiting

    print(f"\n{'='*55}")
    print(f"  {'Would post' if dry_run else 'Posted'}: {posted}/{len(tweets_to_run)} tweets")
    if dry_run:
        print(f"  Run with --live to actually post")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    live = "--live" in sys.argv
    count_arg = next((int(a) for a in sys.argv[1:] if a.isdigit()), None)

    if not live:
        print("\n⚠️  DRY RUN — no tweets will be posted")
        print("   Run with --live to post for real")
        print("   Run with --live 1 to post just 1 as a test\n")

    run(dry_run=not live, count=count_arg)
