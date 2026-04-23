"""
Meta token refresh — one-shot permanent fix.

Takes the short-lived META_ACCESS_TOKEN in .env, exchanges to a 60-day
long-lived USER token, derives a NEVER-EXPIRING Page access token from it,
and writes both back to .env.

Run once after regenerating a user token in Graph API Explorer. You should
almost never need to run this again — the Page token doesn't expire unless
the user changes their password or Meta invalidates the session.
"""
import os, json, time, urllib.request, urllib.error, urllib.parse
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)

APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")
SHORT_TOKEN = os.getenv("META_ACCESS_TOKEN")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

assert APP_ID and APP_SECRET and SHORT_TOKEN and PAGE_ID, "missing env vars"


def http_get(url):
    try:
        r = urllib.request.urlopen(url, timeout=20)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}")


# 1. Exchange short-lived → long-lived user token (60-day)
print("[1/3] Exchanging short-lived -> long-lived user token...")
params = urllib.parse.urlencode({
    "grant_type": "fb_exchange_token",
    "client_id": APP_ID,
    "client_secret": APP_SECRET,
    "fb_exchange_token": SHORT_TOKEN,
})
resp = http_get(f"https://graph.facebook.com/v21.0/oauth/access_token?{params}")
long_user_token = resp["access_token"]
expires_in = resp.get("expires_in", 0)
print(f"    long-lived user token acquired, expires in {expires_in // 86400}d")

# 2. Derive Page access token (non-expiring for Pages)
print("[2/3] Deriving Page access token...")
resp = http_get(
    f"https://graph.facebook.com/v21.0/{PAGE_ID}?fields=access_token&access_token={long_user_token}"
)
page_token = resp["access_token"]
print(f"    Page token acquired ({page_token[:20]}...)")

# 3. Verify the Page token never expires
print("[3/3] Verifying Page token...")
debug_url = (
    f"https://graph.facebook.com/debug_token?input_token={page_token}"
    f"&access_token={APP_ID}|{APP_SECRET}"
)
debug = http_get(debug_url)["data"]
exp = debug.get("expires_at", -1)
if exp == 0:
    print("    Page token NEVER expires (as expected)")
else:
    remaining = exp - int(time.time())
    print(f"    Page token expires in {remaining // 86400}d (unexpected — investigate)")

# Write both tokens back to .env
print("\nWriting tokens back to .env...")
lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
out = []
wrote_user = wrote_page = False
for line in lines:
    if line.startswith("META_ACCESS_TOKEN="):
        out.append(f"META_ACCESS_TOKEN={long_user_token}")
        wrote_user = True
    elif line.startswith("META_PAGE_TOKEN="):
        out.append(f"META_PAGE_TOKEN={page_token}")
        wrote_page = True
    else:
        out.append(line)
if not wrote_page:
    out.append(f"META_PAGE_TOKEN={page_token}")
if not wrote_user:
    out.append(f"META_ACCESS_TOKEN={long_user_token}")

ENV_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
print("Done.")
print(f"  META_ACCESS_TOKEN (long-lived user, expires ~{expires_in // 86400}d)")
print(f"  META_PAGE_TOKEN   (non-expiring Page token — use this for automation)")
