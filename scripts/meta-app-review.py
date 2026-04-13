"""
Meta App Review — Browser-assisted test call registration.

Uses Playwright to open a real browser, lets you log in manually,
captures a properly-scoped token via OAuth, then makes the required
API test calls so Meta counts them toward App Review.

Usage:
    python scripts/meta-app-review.py

You will be prompted to log in manually in the browser window.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from dotenv import load_dotenv

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed.")
    print("Run: python -m pip install playwright && python -m playwright install chromium")
    sys.exit(1)

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────
APP_ID = os.getenv("META_APP_ID", "1452257036358754")
APP_SECRET = os.getenv("META_APP_SECRET", "")
IG_ID = os.getenv("INSTAGRAM_BUSINESS_ID", "17841454335324028")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "601690023018873")
PROFILE_DIR = str(Path.home() / ".meta-playwright-profile")
REDIRECT_PORT = 9876
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"
API_VERSION = "v25.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

PERMISSIONS = ",".join([
    "pages_show_list",
    "pages_read_engagement",
    "business_management",
    "instagram_basic",
    "instagram_manage_comments",
    "instagram_content_publish",
])


# ── API helpers ─────────────────────────────────────────────────────────
def api_get(url):
    try:
        r = urllib.request.urlopen(url)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return {"error": json.loads(body)}
        except Exception:
            return {"error": body.decode()}


def api_post(url, data):
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=encoded, method="POST")
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return {"error": json.loads(body)}
        except Exception:
            return {"error": body.decode()}


# ── OAuth callback server ──────────────────────────────────────────────
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Captures the OAuth auth code from the redirect."""
    auth_code = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            OAuthCallbackHandler.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family:sans-serif;text-align:center;padding:60px;">
                <h1>&#10003; Authorization successful!</h1>
                <p>You can close this tab and go back to the terminal.</p>
                </body></html>
            """)
        else:
            error = params.get("error_description", params.get("error", ["Unknown error"]))
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Error</h1><p>{error}</p></body></html>".encode())

    def log_message(self, format, *args):
        pass  # suppress logs


def start_callback_server():
    server = HTTPServer(("localhost", REDIRECT_PORT), OAuthCallbackHandler)
    server.timeout = 300  # 5 min
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    return server, thread


# ── Token operations ───────────────────────────────────────────────────
def exchange_code_for_token(code):
    """Exchange OAuth auth code for a short-lived access token."""
    url = (
        f"{BASE_URL}/oauth/access_token?"
        f"client_id={APP_ID}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"client_secret={APP_SECRET}&"
        f"code={code}"
    )
    result = api_get(url)
    if "error" in result:
        print(f"   ERROR exchanging code: {result['error']}")
        return None
    return result.get("access_token")


def exchange_for_long_lived(short_token):
    """Exchange a short-lived token for a long-lived one (~60 days)."""
    url = (
        f"{BASE_URL}/oauth/access_token?"
        f"grant_type=fb_exchange_token&"
        f"client_id={APP_ID}&"
        f"client_secret={APP_SECRET}&"
        f"fb_exchange_token={short_token}"
    )
    result = api_get(url)
    if "error" in result:
        print(f"   WARNING: Could not get long-lived token: {result['error']}")
        return short_token
    return result.get("access_token", short_token)


def get_page_token(user_token):
    """Get a Page Access Token from the User token."""
    url = f"{BASE_URL}/me/accounts?fields=id,name,access_token&access_token={user_token}"
    result = api_get(url)
    if "error" in result:
        print(f"   ERROR getting page token: {result['error']}")
        return None
    pages = result.get("data", [])
    for page in pages:
        if page.get("id") == PAGE_ID:
            print(f"   Found page: {page.get('name')} (ID: {page['id']})")
            return page.get("access_token")
    if pages:
        page = pages[0]
        print(f"   Using first page: {page.get('name')} (ID: {page['id']})")
        return page.get("access_token")
    print("   ERROR: No pages found for this user token")
    return None


def get_ig_account(page_token):
    """Get the Instagram Business Account ID linked to the page."""
    url = f"{BASE_URL}/{PAGE_ID}?fields=instagram_business_account&access_token={page_token}"
    result = api_get(url)
    if "error" in result:
        print(f"   ERROR getting IG account: {result['error']}")
        return IG_ID
    ig = result.get("instagram_business_account", {})
    ig_id = ig.get("id", IG_ID)
    print(f"   Instagram Business Account ID: {ig_id}")
    return ig_id


def debug_token(token):
    """Verify token is tied to the correct app."""
    app_token = f"{APP_ID}|{APP_SECRET}"
    url = f"{BASE_URL}/debug_token?input_token={token}&access_token={app_token}"
    result = api_get(url)
    if "error" in result:
        print(f"   WARNING: Could not debug token: {result['error']}")
        return False
    data = result.get("data", {})
    app_id = str(data.get("app_id", ""))
    is_valid = data.get("is_valid", False)
    scopes = data.get("scopes", [])
    print(f"   Token app_id: {app_id} (expected: {APP_ID})")
    print(f"   Valid: {is_valid}")
    print(f"   Scopes: {', '.join(scopes)}")
    if app_id != APP_ID:
        print(f"   WARNING: Token is for a DIFFERENT app! Test calls won't count.")
        return False
    return is_valid


# ── Test API calls ─────────────────────────────────────────────────────
def make_test_calls(token, ig_id):
    """Make the required test API calls for App Review."""

    print()
    print("=" * 60)
    print("  TEST CALL 1: instagram_business_manage_comments")
    print("=" * 60)
    print()

    # 1a: Get media
    print("1a. Fetching Instagram media posts...")
    url = f"{BASE_URL}/{ig_id}/media?fields=id,caption,timestamp,media_type&limit=5&access_token={token}"
    result = api_get(url)
    media_id = None
    if "error" in result:
        print(f"   ERROR: {result['error']}")
    else:
        posts = result.get("data", [])
        print(f"   OK - Found {len(posts)} posts")
        for p in posts[:3]:
            caption = (p.get("caption") or "")[:60]
            print(f"   [{p['id']}] {p.get('media_type','')} | {caption}...")
        if posts:
            media_id = posts[0]["id"]

    # 1b: Get comments
    if media_id:
        print(f"\n1b. Fetching comments on post {media_id}...")
        url2 = f"{BASE_URL}/{media_id}/comments?fields=id,text,timestamp,username&limit=10&access_token={token}"
        result2 = api_get(url2)
        if "error" in result2:
            print(f"   ERROR: {result2['error']}")
        else:
            comments = result2.get("data", [])
            print(f"   OK - Found {len(comments)} comments")

    # 1c: Get tags
    print(f"\n1c. Fetching tagged media...")
    url3 = f"{BASE_URL}/{ig_id}/tags?fields=id,caption,timestamp&limit=5&access_token={token}"
    result3 = api_get(url3)
    if "error" in result3:
        print(f"   ERROR: {result3['error']}")
    else:
        print(f"   OK - Found {len(result3.get('data', []))} tagged posts")

    print()
    print("=" * 60)
    print("  TEST CALL 2: instagram_business_content_publish")
    print("=" * 60)
    print()

    # 2a: Content publishing limit
    print("2a. Checking content publishing limit...")
    url4 = f"{BASE_URL}/{ig_id}/content_publishing_limit?fields=config,quota_usage&access_token={token}"
    result4 = api_get(url4)
    if "error" in result4:
        print(f"   ERROR: {result4['error']}")
    else:
        print(f"   OK - Publishing limit data retrieved")

    # 2b: Create media container (won't publish)
    print("\n2b. Creating test media container (will NOT publish)...")
    test_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
    url5 = f"{BASE_URL}/{ig_id}/media"
    data = {
        "image_url": test_image,
        "caption": "API test - do not publish",
        "access_token": token,
    }
    result5 = api_post(url5, data)
    if "error" in result5:
        print(f"   ERROR: {result5['error']}")
        print("   (Permission error is expected — the API call itself still registers)")
    else:
        print(f"   OK - Container created: {result5.get('id', '?')}")

    # Bonus: account info
    print(f"\n3. Fetching Instagram account info...")
    url6 = f"{BASE_URL}/{ig_id}?fields=id,name,username,followers_count,media_count&access_token={token}"
    result6 = api_get(url6)
    if "error" in result6:
        print(f"   ERROR: {result6['error']}")
    else:
        print(f"   Account: @{result6.get('username', '?')}")
        print(f"   Followers: {result6.get('followers_count', '?')}")


# ── Main flow ──────────────────────────────────────────────────────────
def main():
    if not APP_SECRET:
        print("ERROR: META_APP_SECRET not set in .env")
        print("Find it at: developers.facebook.com/apps/{}/settings/basic/".format(APP_ID))
        sys.exit(1)

    print("=" * 60)
    print("  Meta App Review — Browser-Assisted Test Calls")
    print("=" * 60)
    print()
    print(f"  App ID:     {APP_ID}")
    print(f"  IG ID:      {IG_ID}")
    print(f"  Page ID:    {PAGE_ID}")
    print()

    # ── Phase A: OAuth flow ────────────────────────────────────────────
    print("PHASE A: Getting a properly-scoped token via OAuth...")
    print()

    # First, check if redirect URI is configured
    print("  IMPORTANT: Your app's Valid OAuth Redirect URIs must include:")
    print(f"  {REDIRECT_URI}")
    print()
    print("  If not set, go to:")
    print(f"  developers.facebook.com/apps/{APP_ID}/facebook-login/settings/")
    print("  and add it under 'Valid OAuth Redirect URIs', then re-run.")
    print()

    # Start local callback server
    print("  Starting local callback server on port", REDIRECT_PORT, "...")
    server, thread = start_callback_server()

    # Build OAuth URL
    oauth_url = (
        f"https://www.facebook.com/{API_VERSION}/dialog/oauth?"
        f"client_id={APP_ID}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"scope={PERMISSIONS}&"
        f"response_type=code"
    )

    # Launch browser
    print("  Launching browser for Facebook login...")
    print()
    print("  >>> LOG IN and AUTHORIZE the app in the browser window <<<")
    print("  >>> The browser will redirect back when done <<<")
    print()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        # Navigate to OAuth dialog
        page.goto(oauth_url)

        # Wait for auth — poll browser URL + callback server
        print("  Waiting for you to log in and authorize (up to 5 minutes)...")
        print("  The browser should redirect to localhost when done.")
        print()

        deadline = time.time() + 300  # 5 minutes
        while time.time() < deadline:
            # Check callback server
            if OAuthCallbackHandler.auth_code:
                print("  Authorization code received via callback!")
                break

            # Check browser URL for redirect
            try:
                current_url = page.url
                if "localhost" in current_url and "code=" in current_url:
                    parsed = urllib.parse.urlparse(current_url)
                    params = urllib.parse.parse_qs(parsed.query)
                    code = params.get("code", [None])[0]
                    if code:
                        OAuthCallbackHandler.auth_code = code
                        print("  Authorization code captured from browser redirect!")
                        break
                # Also check if we got an error in the URL
                if "localhost" in current_url and "error" in current_url:
                    parsed = urllib.parse.urlparse(current_url)
                    params = urllib.parse.parse_qs(parsed.query)
                    error = params.get("error_description", params.get("error", ["Unknown"]))
                    print(f"  ERROR from Facebook: {error}")
                    break
            except Exception:
                pass  # page might be navigating

            time.sleep(2)

        if not OAuthCallbackHandler.auth_code:
            print("\n  FATAL: No authorization code received after 5 minutes.")
            print("  Make sure you logged in and clicked 'Continue' in the browser.")
            context.close()
            sys.exit(1)
        print()

        # ── Phase B: Exchange code for tokens ──────────────────────────
        print("PHASE B: Exchanging auth code for access token...")
        print()

        short_token = exchange_code_for_token(OAuthCallbackHandler.auth_code)
        if not short_token:
            print("  FATAL: Could not get access token. Exiting.")
            context.close()
            sys.exit(1)
        print(f"  Short-lived token: {short_token[:30]}...")

        # Verify token is tied to our app
        print("\n  Verifying token...")
        debug_token(short_token)

        # Get long-lived token
        print("\n  Exchanging for long-lived token...")
        long_token = exchange_for_long_lived(short_token)
        print(f"  Long-lived token: {long_token[:30]}...")

        # Get page token
        print("\n  Getting Page Access Token...")
        page_token = get_page_token(long_token)

        if page_token:
            # Get IG account through the page
            print("\n  Getting Instagram Business Account from Page...")
            ig_id = get_ig_account(page_token)
            test_token = page_token
        else:
            print("  WARNING: No page token — using user token directly")
            ig_id = IG_ID
            test_token = long_token

        # ── Phase C: Make test API calls ───────────────────────────────
        print()
        print("PHASE C: Making test API calls...")
        make_test_calls(test_token, ig_id)

        # ── Phase D: Navigate to App Review to verify ──────────────────
        print()
        print("=" * 60)
        print("  PHASE D: Checking App Review status")
        print("=" * 60)
        print()
        print("  Navigating to App Review page...")

        page.goto(f"https://developers.facebook.com/apps/{APP_ID}/review/")
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep(3)

        # Take screenshot
        screenshot_path = os.path.join(os.path.dirname(__file__), "..", "app-review-status.png")
        screenshot_path = os.path.abspath(screenshot_path)
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"  Screenshot saved: {screenshot_path}")

        print()
        print("=" * 60)
        print("  DONE!")
        print("=" * 60)
        print()
        print("  Test calls completed with an app-scoped token.")
        print("  Meta may take up to 24 hours to register them as 1/1.")
        print()
        print(f"  Your long-lived token (save to .env as META_ACCESS_TOKEN):")
        print(f"  {long_token[:50]}...")
        print()
        print("  Next steps:")
        print("  1. Wait up to 24 hours")
        print("  2. Check App Review page for 1/1 on both permissions")
        print("  3. Once 1/1 — click Submit")
        print()

        # Keep browser open for user to check
        print("  Browser will stay open for 30 seconds so you can check...")
        print("  Press Ctrl+C to close immediately.")
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            pass

        context.close()


if __name__ == "__main__":
    main()
