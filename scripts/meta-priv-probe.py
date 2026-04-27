"""
Meta privileged-scope probe (graph.instagram.com).
Reads, never writes. Returns OK / DENIED for each advanced permission so
we can tell whether the App Review submission has flipped to live.
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("IG_BUSINESS_TOKEN") or os.getenv("META_ACCESS_TOKEN")
IG_ID = os.getenv("IG_BUSINESS_ID") or os.getenv("INSTAGRAM_BUSINESS_ID")

assert TOKEN, "IG_BUSINESS_TOKEN / META_ACCESS_TOKEN missing"
assert IG_ID, "IG_BUSINESS_ID / INSTAGRAM_BUSINESS_ID missing"

BASE = "https://graph.instagram.com/v23.0"


def call(method, path, params=None, data=None):
    params = dict(params or {})
    params["access_token"] = TOKEN
    qs = urllib.parse.urlencode(params)
    url = f"{BASE}{path}?{qs}" if method == "GET" else f"{BASE}{path}"
    body = urllib.parse.urlencode(data).encode() if data else None
    if method == "POST":
        url = f"{BASE}{path}?{qs}"
        body = b""
    req = urllib.request.Request(url, data=body, method=method)
    try:
        r = urllib.request.urlopen(req, timeout=15)
        return {"ok": True, "code": r.status, "data": json.loads(r.read())}
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read())
        except Exception:
            payload = {"raw": e.read().decode(errors="replace")}
        return {"ok": False, "code": e.code, "data": payload}


def label(test, scope, result):
    head = f"[{test}] scope={scope}"
    if result["ok"]:
        print(f"  PASS {head}")
        return
    err = result["data"].get("error", result["data"])
    msg = err.get("message", "")
    code = err.get("code", "?")
    sub = err.get("error_subcode", "")
    print(f"  FAIL {head}  http={result['code']} code={code} sub={sub}")
    if msg:
        print(f"       {msg[:240]}")


print(f"IG_ID = {IG_ID}")
print(f"TOKEN = {TOKEN[:18]}...")
print()

print("=== /me  (instagram_business_basic) ===")
r = call("GET", "/me", {"fields": "id,username,account_type"})
print(json.dumps(r, indent=2)[:400])
print()

print("=== media list  (basic) ===")
media = call("GET", f"/{IG_ID}/media", {"fields": "id,timestamp,media_type", "limit": 3})
label("media list", "instagram_business_basic", media)
post_id = None
if media["ok"] and media["data"].get("data"):
    post_id = media["data"]["data"][0]["id"]
    print(f"  -> first post id: {post_id}")
print()

print("=== comments read  (instagram_business_manage_comments) ===")
if post_id:
    r = call("GET", f"/{post_id}/comments", {"fields": "id,text,username,timestamp", "limit": 5})
    label("comments read", "manage_comments", r)
    if r["ok"]:
        n = len(r["data"].get("data", []))
        print(f"       {n} comment(s)")
print()

print("=== insights  (instagram_business_manage_insights) ===")
r = call("GET", f"/{IG_ID}/insights", {"metric": "reach,follower_count,profile_views", "period": "day"})
label("account insights", "manage_insights", r)
if r["ok"]:
    print(f"       {json.dumps(r['data'], indent=2)[:400]}")
print()

print("=== conversations list  (instagram_business_manage_messages) ===")
r = call("GET", f"/{IG_ID}/conversations", {"platform": "instagram", "limit": 1})
label("conversations", "manage_messages", r)
print()

print("=== media container POST  (instagram_business_content_publish) ===")
test_image = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
r = call(
    "POST",
    f"/{IG_ID}/media",
    {"image_url": test_image, "caption": "scope-probe (will NOT publish)"},
)
label("container create", "content_publish", r)
if r["ok"]:
    cid = r["data"].get("id")
    print(f"       container_id={cid} (auto-expires in 24h, NOT published)")
print()

print("=== DONE ===")
