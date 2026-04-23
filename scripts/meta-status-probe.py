"""Live probe: Meta App Review + token health. Read-only."""
import os, json, urllib.request, urllib.error, urllib.parse, time
from dotenv import load_dotenv

load_dotenv()

META_TOKEN = os.getenv("META_ACCESS_TOKEN")
IG_TOKEN = os.getenv("IG_BUSINESS_TOKEN")
META_APP_ID = os.getenv("META_APP_ID")
IG_APP_ID = os.getenv("IG_APP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")
IG_BIZ_ID = os.getenv("INSTAGRAM_BUSINESS_ID")

def get(url):
    try:
        r = urllib.request.urlopen(url, timeout=15)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return {"__http_error__": e.code, **json.loads(body)}
        except Exception:
            return {"__http_error__": e.code, "body": body}
    except Exception as e:
        return {"__exception__": str(e)}

def show(label, result):
    print(f"\n=== {label} ===")
    print(json.dumps(result, indent=2)[:900])

print(f"META_APP_ID      = {META_APP_ID}")
print(f"IG_APP_ID        = {IG_APP_ID}")
print(f"IG_BUSINESS_ID   = {IG_BIZ_ID}")
print(f"META_ACCESS_TOKEN= {'set' if META_TOKEN else 'MISSING'}")
print(f"IG_BUSINESS_TOKEN= {'set' if IG_TOKEN else 'MISSING'}")

# 1) Debug META_ACCESS_TOKEN (short/long-lived, expiry, scopes)
if META_TOKEN and META_APP_ID and META_APP_SECRET:
    app_token = f"{META_APP_ID}|{META_APP_SECRET}"
    r = get(f"https://graph.facebook.com/debug_token?input_token={META_TOKEN}&access_token={app_token}")
    show("META_ACCESS_TOKEN debug", r)
    data = r.get("data", {})
    if "expires_at" in data:
        exp = data["expires_at"]
        if exp == 0:
            print("  -> NEVER expires (Page token?)")
        else:
            remaining = exp - int(time.time())
            print(f"  -> expires in ~{remaining//3600}h ({remaining//86400}d)")
    print(f"  -> scopes: {data.get('scopes')}")
    print(f"  -> is_valid: {data.get('is_valid')}")

# 2) IG_BUSINESS_TOKEN — try /me via graph.instagram.com
if IG_TOKEN:
    r = get(f"https://graph.instagram.com/me?fields=id,username,account_type&access_token={IG_TOKEN}")
    show("IG_BUSINESS_TOKEN /me (graph.instagram.com)", r)

# 3) Read recent IG media via IG token
if IG_TOKEN and IG_BIZ_ID:
    r = get(f"https://graph.instagram.com/{IG_BIZ_ID}/media?fields=id,caption,timestamp&limit=3&access_token={IG_TOKEN}")
    show("IG recent media (read probe)", r)

# 4) App review — list the app's permissions & their review state
if META_APP_ID and META_APP_SECRET:
    app_token = f"{META_APP_ID}|{META_APP_SECRET}"
    r = get(f"https://graph.facebook.com/v21.0/{META_APP_ID}/permissions?access_token={app_token}")
    show("META app permissions review state", r)

if IG_APP_ID and META_APP_SECRET:
    # IG app usually has its own secret; try META_APP_SECRET as fallback
    ig_secret = os.getenv("IG_APP_SECRET") or META_APP_SECRET
    app_token = f"{IG_APP_ID}|{ig_secret}"
    r = get(f"https://graph.facebook.com/v21.0/{IG_APP_ID}/permissions?access_token={app_token}")
    show("IG app permissions review state", r)
