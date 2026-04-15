"""
Meta App Review — Instagram Business Login test calls.

Runs the NEW Instagram API with Instagram Login OAuth flow
(instagram.com/oauth), captures an IG User token with the five
instagram_business_* scopes, and fires one test call per permission
against graph.instagram.com so they register toward App Review.

IMPORTANT: This script uses the Instagram app credentials (IG_APP_ID
/ IG_APP_SECRET), NOT the Facebook app credentials (META_APP_ID).
These are different apps — see Meta Dashboard -> Use cases ->
"Manage messaging & content on Instagram" -> API setup with
Instagram login -> Instagram app ID / Instagram app secret.

Redirect URI MUST be:
    https://localhost:9876/callback
and must be registered under "Business login settings" in that same
section. Meta requires HTTPS, so this script runs a local HTTPS
server with a self-signed cert. The browser will warn "connection
not private" once — click Advanced -> Proceed.

Run:
    python scripts/meta-ig-business-review.py
    python scripts/meta-ig-business-review.py --reuse   # skip OAuth, retry test calls
"""

from __future__ import annotations

import datetime
import json
import os
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────
IG_APP_ID = os.getenv("IG_APP_ID", "922450807234394")
IG_APP_SECRET = os.getenv("IG_APP_SECRET", "")

REDIRECT_HOST = "localhost"
REDIRECT_PORT = 9876
REDIRECT_URI = f"https://{REDIRECT_HOST}:{REDIRECT_PORT}/callback"

SCOPES = [
    "instagram_business_basic",
    "instagram_business_manage_messages",
    "instagram_business_manage_comments",
    "instagram_business_content_publish",
    "instagram_business_manage_insights",
]

AUTHORIZE_URL = (
    "https://www.instagram.com/oauth/authorize"
    f"?force_reauth=true"
    f"&client_id={IG_APP_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
    f"&response_type=code"
    f"&scope={urllib.parse.quote(','.join(SCOPES))}"
)

IG_TOKEN_URL = "https://api.instagram.com/oauth/access_token"
IG_LONG_LIVED_URL = "https://graph.instagram.com/access_token"
IG_API = "https://graph.instagram.com/v21.0"

CERT_DIR = Path.home() / ".meta-ig-review-cert"
CERT_FILE = CERT_DIR / "localhost.pem"
KEY_FILE = CERT_DIR / "localhost-key.pem"


# ── Self-signed cert for https://localhost ─────────────────────────────
def ensure_self_signed_cert() -> tuple[Path, Path]:
    if CERT_FILE.exists() and KEY_FILE.exists():
        return CERT_FILE, KEY_FILE

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    CERT_DIR.mkdir(parents=True, exist_ok=True)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "localhost")]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow() - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=825))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    KEY_FILE.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    CERT_FILE.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    print(f"  Generated self-signed cert: {CERT_FILE}")
    return CERT_FILE, KEY_FILE


# ── HTTP helpers ────────────────────────────────────────────────────────
def _read_err(e: urllib.error.HTTPError) -> dict:
    body = e.read()
    try:
        return {"error": json.loads(body)}
    except Exception:
        return {"error": body.decode(errors="replace")}


def http_get(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return _read_err(e)
    except Exception as e:
        return {"error": str(e)}


def http_post(url: str, data: dict) -> dict:
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=encoded, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return _read_err(e)
    except Exception as e:
        return {"error": str(e)}


# ── OAuth callback (HTTPS) ─────────────────────────────────────────────
class CallbackHandler(BaseHTTPRequestHandler):
    auth_code: str | None = None
    error: str | None = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # Ignore everything that isn't the OAuth callback path (favicon,
        # preflight probes, etc.). Chrome auto-fetches /favicon.ico after
        # rendering the success page, which used to clobber auth_code
        # with a bogus "unknown" error.
        if parsed.path != "/callback":
            self.send_response(204)
            self.end_headers()
            return

        if "code" in params:
            CallbackHandler.auth_code = params["code"][0]
            msg = (
                "<html><body style='font-family:sans-serif;text-align:center;"
                "padding:60px;background:#0a0a0a;color:#e8c46b;'>"
                "<h1>Authorization successful</h1>"
                "<p>Return to the terminal window.</p></body></html>"
            )
            self.send_response(200)
        elif "error" in params or "error_description" in params:
            err = params.get("error_description", params.get("error", ["unknown"]))[0]
            CallbackHandler.error = err
            msg = f"<html><body><h1>OAuth error</h1><pre>{err}</pre></body></html>"
            self.send_response(400)
        else:
            # /callback hit with no params at all (manual reload, etc.) —
            # don't treat as an error, just show a neutral message.
            msg = "<html><body><p>Waiting for Instagram redirect...</p></body></html>"
            self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(msg.encode())

    def log_message(self, *_):
        pass


def run_https_callback_server(timeout_sec: int = 300) -> None:
    """Run an HTTPS server that accepts requests until we capture an auth
    code or error. Uses serve_forever() in a thread — we shut it down
    when the callback lands. handle_request() (one-shot) caused races
    because Chrome fires preflight probes that consumed the single
    accept, leaving the real callback with nothing listening."""
    cert, key = ensure_self_signed_cert()
    srv = HTTPServer((REDIRECT_HOST, REDIRECT_PORT), CallbackHandler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=str(cert), keyfile=str(key))
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)

    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    time.sleep(0.3)
    webbrowser.open(AUTHORIZE_URL)

    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if CallbackHandler.auth_code or CallbackHandler.error:
            break
        time.sleep(0.5)
    try:
        srv.shutdown()
        srv.server_close()
    except Exception:
        pass


# ── OAuth: exchange code → short-lived → long-lived ────────────────────
def exchange_code(code: str) -> dict:
    return http_post(
        IG_TOKEN_URL,
        {
            "client_id": IG_APP_ID,
            "client_secret": IG_APP_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code": code,
        },
    )


def upgrade_to_long_lived(short_token: str) -> dict:
    qs = urllib.parse.urlencode(
        {
            "grant_type": "ig_exchange_token",
            "client_secret": IG_APP_SECRET,
            "access_token": short_token,
        }
    )
    return http_get(f"{IG_LONG_LIVED_URL}?{qs}")


# ── Test calls ─────────────────────────────────────────────────────────
def section(title: str) -> None:
    print()
    print("=" * 64)
    print(f"  {title}")
    print("=" * 64)


def _ok(label: str, success: bool, detail: str = "") -> None:
    mark = "OK  " if success else "FAIL"
    tail = f"  |  {detail}" if detail else ""
    print(f"  [{mark}] {label}{tail}")


def run_test_calls(token: str) -> None:
    # 1 — instagram_business_basic
    section("1/5  instagram_business_basic")
    r = http_get(
        f"{IG_API}/me?fields=id,username,account_type,media_count"
        f"&access_token={token}"
    )
    ig_id = r.get("id")
    _ok(
        "GET /me",
        "error" not in r,
        f"@{r.get('username')} ({r.get('account_type')}) id={ig_id}"
        if ig_id else str(r.get("error"))[:160],
    )
    if not ig_id:
        print("  Cannot continue without ig_user_id.")
        return

    # 2 — instagram_business_content_publish
    section("2/5  instagram_business_content_publish")
    r = http_get(
        f"{IG_API}/{ig_id}/content_publishing_limit"
        f"?fields=config,quota_usage&access_token={token}"
    )
    _ok(
        "GET /{ig-user-id}/content_publishing_limit",
        "error" not in r,
        json.dumps(r.get("data", r))[:140],
    )

    # 3 — instagram_business_manage_comments
    section("3/5  instagram_business_manage_comments")
    r = http_get(
        f"{IG_API}/{ig_id}/media?fields=id,caption,media_type"
        f"&limit=5&access_token={token}"
    )
    posts = r.get("data", []) if "error" not in r else []
    _ok("GET /me/media", "error" not in r, f"{len(posts)} posts")
    if posts:
        media_id = posts[0]["id"]
        r2 = http_get(
            f"{IG_API}/{media_id}/comments"
            f"?fields=id,text,username,timestamp&limit=10&access_token={token}"
        )
        _ok(
            f"GET /{media_id}/comments",
            "error" not in r2,
            f"{len(r2.get('data', []))} comments"
            if "error" not in r2 else str(r2.get("error"))[:140],
        )
    else:
        print("  (no media — skipping comments sub-call)")

    # 4 — instagram_business_manage_insights
    section("4/5  instagram_business_manage_insights")
    r = http_get(
        f"{IG_API}/{ig_id}/insights"
        f"?metric=reach&period=day&access_token={token}"
    )
    _ok(
        "GET /{ig-user-id}/insights?metric=reach",
        "error" not in r,
        json.dumps(r.get("data", r))[:140],
    )

    # 5 — instagram_business_manage_messages
    section("5/5  instagram_business_manage_messages")
    r = http_get(
        f"{IG_API}/{ig_id}/conversations"
        f"?platform=instagram&access_token={token}"
    )
    _ok(
        "GET /{ig-user-id}/conversations?platform=instagram",
        "error" not in r,
        f"{len(r.get('data', []))} threads"
        if "error" not in r else str(r.get("error"))[:140],
    )


# ── Env persistence ────────────────────────────────────────────────────
def save_token(token: str) -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    text = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    lines = [ln for ln in text.splitlines() if not ln.startswith("IG_BUSINESS_TOKEN=")]
    lines.append(f"IG_BUSINESS_TOKEN={token}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Saved IG_BUSINESS_TOKEN to {env_path}")


# ── Main ──────────────────────────────────────────────────────────────
def preflight() -> bool:
    problems = []
    if not IG_APP_ID:
        problems.append("IG_APP_ID missing in .env")
    if not IG_APP_SECRET:
        problems.append("IG_APP_SECRET missing in .env")
    if problems:
        for p in problems:
            print(f"  [preflight fail] {p}")
        return False
    return True


def main() -> int:
    section("Meta App Review — Instagram Business Login")
    print(f"  Instagram App ID:  {IG_APP_ID}")
    print(f"  Redirect URI:      {REDIRECT_URI}")
    print(f"  Scopes:            {', '.join(SCOPES)}")
    print()

    if not preflight():
        return 1

    existing = os.getenv("IG_BUSINESS_TOKEN")
    if existing and "--reuse" in sys.argv:
        print("  --reuse: skipping OAuth, reusing stored IG_BUSINESS_TOKEN\n")
        run_test_calls(existing)
        return 0

    # --code shortcut: user copied an auth code from the browser URL bar
    # (because the local server died before the callback landed). The code
    # is single-use and expires in ~10 min, so redeem it immediately.
    code_from_cli = None
    for i, a in enumerate(sys.argv):
        if a == "--code" and i + 1 < len(sys.argv):
            code_from_cli = sys.argv[i + 1]
            break
        if a.startswith("--code="):
            code_from_cli = a.split("=", 1)[1]
            break

    if code_from_cli:
        # Instagram appends "#_" to the code in the URL fragment — strip it
        code_from_cli = code_from_cli.split("#")[0].strip()
        section("Step 1 — skipping OAuth (using --code)")
        print(f"  Using supplied auth code: {code_from_cli[:12]}...")
        CallbackHandler.auth_code = code_from_cli
    else:
        section("Step 1 — authorize with Instagram")
        print("  Opening Instagram authorize URL in your browser.")
        print("  Browser will warn 'connection not private' once the redirect fires —")
        print("  click Advanced -> Proceed to localhost. That's the self-signed cert.")
        print()
        run_https_callback_server(timeout_sec=300)
        if CallbackHandler.error:
            print(f"\n  OAuth failed: {CallbackHandler.error}")
            return 2
        if not CallbackHandler.auth_code:
            print("\n  Timed out waiting for authorization (5 min).")
            return 2

    code = CallbackHandler.auth_code
    print(f"  Using auth code: {code[:12]}...")

    # Step 2 — exchange for short-lived
    section("Step 2 — exchange code for short-lived IG token")
    r = exchange_code(code)
    if "error" in r or "access_token" not in r:
        print(f"  ERROR: {r}")
        return 3
    short = r["access_token"]
    print(f"  Short-lived token: {short[:20]}...  user_id={r.get('user_id')}")

    # Step 3 — upgrade
    section("Step 3 — upgrade to long-lived IG token (~60 days)")
    r2 = upgrade_to_long_lived(short)
    long_token = r2.get("access_token", short)
    if "error" in r2:
        print(f"  WARNING: long-lived upgrade failed ({r2['error']}); using short-lived")
    else:
        print(f"  Long-lived token: {long_token[:20]}...  expires_in={r2.get('expires_in')}s")
    save_token(long_token)

    # Step 4 — fire test calls
    run_test_calls(long_token)

    section("Done")
    print("  Wait up to 24h for Meta to register the calls.")
    print("  Then refresh App Review — each instagram_business_* row should show 1/1.")
    print()
    print("  Re-run test calls only (skip OAuth):")
    print("      python scripts/meta-ig-business-review.py --reuse")
    return 0


if __name__ == "__main__":
    sys.exit(main())
