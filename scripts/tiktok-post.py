"""
TikTok Content Posting API — OAuth + video upload.

End-to-end integration for the TikTok Content Posting API:
1. OAuth flow via https://www.tiktok.com/v2/auth/authorize/
2. Code → access token exchange at open.tiktokapis.com
3. Video upload via /v2/post/publish/inbox/video/init/ (drafts — safer)
   or /v2/post/publish/video/init/ (direct publish)
4. Status polling until upload completes

Built for the @aibiblegospels account (Born Made Bosses LLC).

Redirect URI MUST be registered in your TikTok app's "Login Kit" settings:
    https://localhost:9876/callback

TikTok requires HTTPS for redirects, so this script spins up a local HTTPS
server with a self-signed cert. The browser will warn "connection not
private" once — click Advanced -> Proceed.

Run:
    # Full OAuth + upload test (recommended for the demo recording)
    python scripts/tiktok-post.py --video path/to/short.mp4

    # OAuth only — capture and save token
    python scripts/tiktok-post.py --auth-only

    # Reuse stored token and upload a video
    python scripts/tiktok-post.py --video path/to/short.mp4 --reuse

    # Use direct publish instead of inbox (drafts)
    python scripts/tiktok-post.py --video path/to/short.mp4 --direct

    # Check creator info (what modes/privacy levels the account supports)
    python scripts/tiktok-post.py --creator-info --reuse
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
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")

REDIRECT_HOST = "localhost"
REDIRECT_PORT = 9876
REDIRECT_URI = f"https://{REDIRECT_HOST}:{REDIRECT_PORT}/callback"

# Scopes requested at authorization time. Must match what's configured in
# the TikTok Developer Portal for the app.
SCOPES = [
    "user.info.basic",
    "video.upload",
    "video.publish",
]

AUTHORIZE_URL = (
    "https://www.tiktok.com/v2/auth/authorize/"
    f"?client_key={CLIENT_KEY}"
    f"&response_type=code"
    f"&scope={urllib.parse.quote(','.join(SCOPES))}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
    f"&state=bornmadebosses"
)

TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
API_BASE = "https://open.tiktokapis.com/v2"

CERT_DIR = Path.home() / ".tiktok-oauth-cert"
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


def http_get(url: str, headers: dict | None = None) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return _read_err(e)
    except Exception as e:
        return {"error": str(e)}


def http_post_json(url: str, body: dict, headers: dict | None = None) -> dict:
    data = json.dumps(body).encode()
    h = {"Content-Type": "application/json; charset=UTF-8"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return _read_err(e)
    except Exception as e:
        return {"error": str(e)}


def http_post_form(url: str, data: dict, headers: dict | None = None) -> dict:
    encoded = urllib.parse.urlencode(data).encode()
    h = {"Content-Type": "application/x-www-form-urlencoded"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=encoded, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return _read_err(e)
    except Exception as e:
        return {"error": str(e)}


def http_put_bytes(url: str, data: bytes, content_type: str,
                   content_range: str) -> tuple[int, bytes]:
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": content_type,
            "Content-Length": str(len(data)),
            "Content-Range": content_range,
        },
        method="PUT",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# ── OAuth callback (HTTPS) ─────────────────────────────────────────────
class CallbackHandler(BaseHTTPRequestHandler):
    auth_code: str | None = None
    error: str | None = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

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
            msg = "<html><body><p>Waiting for TikTok redirect...</p></body></html>"
            self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(msg.encode())

    def log_message(self, *_):
        pass


def run_https_callback_server(timeout_sec: int = 300) -> None:
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


# ── OAuth: exchange code → access token ───────────────────────────────
def exchange_code(code: str) -> dict:
    return http_post_form(
        TOKEN_URL,
        {
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        },
    )


def refresh_access_token(refresh_token: str) -> dict:
    return http_post_form(
        TOKEN_URL,
        {
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )


# ── User info (user.info.basic scope) ──────────────────────────────────
def get_user_info(access_token: str) -> dict:
    return http_get(
        f"{API_BASE}/user/info/?fields=open_id,union_id,avatar_url,display_name",
        headers={"Authorization": f"Bearer {access_token}"},
    )


# ── Creator info: supported modes, privacy levels, max duration ───────
def get_creator_info(access_token: str) -> dict:
    return http_post_json(
        f"{API_BASE}/post/publish/creator_info/query/",
        {},
        headers={"Authorization": f"Bearer {access_token}"},
    )


# ── Video upload — inbox (drafts) ──────────────────────────────────────
# Inbox means the video lands in the creator's TikTok drafts for them
# to finalize and publish manually. Safest mode — no risk of publishing
# anything unintended. Requires only video.upload scope.
def init_inbox_upload(access_token: str, video_size: int) -> dict:
    chunk_size = min(video_size, 10_000_000)  # 10 MB chunks (TikTok max)
    total_chunks = (video_size + chunk_size - 1) // chunk_size
    return http_post_json(
        f"{API_BASE}/post/publish/inbox/video/init/",
        {
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunks,
            }
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )


# ── Video upload — direct post ─────────────────────────────────────────
# Direct post publishes the video straight to the feed. Requires
# video.publish scope AND creator_info query to determine valid
# privacy_level values.
def init_direct_post(access_token: str, video_size: int,
                     title: str, privacy_level: str) -> dict:
    chunk_size = min(video_size, 10_000_000)
    total_chunks = (video_size + chunk_size - 1) // chunk_size
    return http_post_json(
        f"{API_BASE}/post/publish/video/init/",
        {
            "post_info": {
                "title": title,
                "privacy_level": privacy_level,
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunks,
            },
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )


# ── Upload video bytes to pre-signed URL ──────────────────────────────
def upload_video_file(upload_url: str, file_path: Path) -> bool:
    total = file_path.stat().st_size
    chunk_size = min(total, 10_000_000)

    with file_path.open("rb") as f:
        offset = 0
        chunk_index = 0
        while offset < total:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            end = offset + len(chunk) - 1
            content_range = f"bytes {offset}-{end}/{total}"
            print(f"  Uploading chunk {chunk_index + 1}: {content_range}")
            status, body = http_put_bytes(
                upload_url,
                chunk,
                "video/mp4",
                content_range,
            )
            if status not in (200, 201, 206):
                print(f"  Upload failed: status={status} body={body[:200]}")
                return False
            offset = end + 1
            chunk_index += 1
    return True


# ── Status polling ─────────────────────────────────────────────────────
def fetch_status(access_token: str, publish_id: str) -> dict:
    return http_post_json(
        f"{API_BASE}/post/publish/status/fetch/",
        {"publish_id": publish_id},
        headers={"Authorization": f"Bearer {access_token}"},
    )


def poll_until_done(access_token: str, publish_id: str,
                    max_wait: int = 300) -> dict:
    deadline = time.time() + max_wait
    last = {}
    while time.time() < deadline:
        r = fetch_status(access_token, publish_id)
        last = r
        status = r.get("data", {}).get("status", "")
        print(f"  Status: {status}")
        if status in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"):
            return r
        if status in ("FAILED",):
            return r
        time.sleep(5)
    return last


# ── Env persistence ────────────────────────────────────────────────────
def save_tokens(token: str, refresh_token: str, open_id: str,
                expires_in: int) -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    text = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    lines = text.splitlines()
    kept = [
        ln for ln in lines
        if not ln.startswith("TIKTOK_ACCESS_TOKEN=")
        and not ln.startswith("TIKTOK_REFRESH_TOKEN=")
        and not ln.startswith("TIKTOK_OPEN_ID=")
        and not ln.startswith("TIKTOK_TOKEN_EXPIRES_AT=")
    ]
    expires_at = int(time.time()) + expires_in
    kept.append(f"TIKTOK_ACCESS_TOKEN={token}")
    kept.append(f"TIKTOK_REFRESH_TOKEN={refresh_token}")
    kept.append(f"TIKTOK_OPEN_ID={open_id}")
    kept.append(f"TIKTOK_TOKEN_EXPIRES_AT={expires_at}")
    env_path.write_text("\n".join(kept) + "\n", encoding="utf-8")
    print(f"  Saved TikTok tokens to {env_path}")


def load_valid_token() -> str | None:
    token = os.getenv("TIKTOK_ACCESS_TOKEN", "")
    expires_at = int(os.getenv("TIKTOK_TOKEN_EXPIRES_AT", "0") or "0")
    if not token:
        return None
    if expires_at and time.time() > expires_at - 60:
        print("  Stored TikTok token is expired or near expiry.")
        refresh = os.getenv("TIKTOK_REFRESH_TOKEN", "")
        if refresh:
            print("  Refreshing automatically...")
            r = refresh_access_token(refresh)
            if "access_token" in r:
                save_tokens(
                    r["access_token"],
                    r.get("refresh_token", refresh),
                    r.get("open_id", os.getenv("TIKTOK_OPEN_ID", "")),
                    int(r.get("expires_in", 86400)),
                )
                return r["access_token"]
        return None
    return token


# ── Section printing ──────────────────────────────────────────────────
def section(title: str) -> None:
    print()
    print("=" * 64)
    print(f"  {title}")
    print("=" * 64)


# ── Main ──────────────────────────────────────────────────────────────
def preflight() -> bool:
    problems = []
    if not CLIENT_KEY:
        problems.append("TIKTOK_CLIENT_KEY missing in .env")
    if not CLIENT_SECRET:
        problems.append("TIKTOK_CLIENT_SECRET missing in .env")
    if problems:
        for p in problems:
            print(f"  [preflight fail] {p}")
        return False
    return True


def run_oauth() -> str | None:
    section("Step 1 — authorize with TikTok")
    print("  Opening TikTok authorize URL in your browser.")
    print("  Browser will warn 'connection not private' once the redirect fires —")
    print("  click Advanced -> Proceed to localhost. That's the self-signed cert.")
    print()
    run_https_callback_server(timeout_sec=300)
    if CallbackHandler.error:
        print(f"\n  OAuth failed: {CallbackHandler.error}")
        return None
    if not CallbackHandler.auth_code:
        print("\n  Timed out waiting for authorization (5 min).")
        return None

    code = CallbackHandler.auth_code
    print(f"  Using auth code: {code[:20]}...")

    section("Step 2 — exchange code for access token")
    r = exchange_code(code)
    if "access_token" not in r:
        print(f"  ERROR: {r}")
        return None
    token = r["access_token"]
    refresh = r.get("refresh_token", "")
    open_id = r.get("open_id", "")
    expires_in = int(r.get("expires_in", 86400))
    print(f"  Access token:  {token[:20]}...  expires_in={expires_in}s")
    print(f"  Refresh token: {refresh[:20]}...")
    print(f"  Open ID:       {open_id}")
    save_tokens(token, refresh, open_id, expires_in)
    return token


def run_user_info_check(token: str) -> bool:
    section("Verifying token via /user/info/")
    r = get_user_info(token)
    if "error" in r or r.get("error", {}).get("code", "ok") != "ok":
        # TikTok wraps errors in a data-level error object
        err = r.get("error") or r.get("data", {}).get("error")
        if err and err.get("code") not in ("ok", None):
            print(f"  FAIL: {err}")
            return False
    data = r.get("data", {}).get("user", {})
    print(f"  OK — @{data.get('display_name', '?')}")
    print(f"     open_id={data.get('open_id', '?')}")
    return True


def upload_video(token: str, video_path: Path, direct: bool,
                 title: str, privacy_level: str) -> None:
    section("Uploading video")
    size = video_path.stat().st_size
    print(f"  File:   {video_path} ({size:,} bytes)")
    print(f"  Mode:   {'DIRECT POST' if direct else 'INBOX (drafts)'}")

    if direct:
        init = init_direct_post(token, size, title, privacy_level)
    else:
        init = init_inbox_upload(token, size)

    data = init.get("data", {})
    publish_id = data.get("publish_id")
    upload_url = data.get("upload_url")

    if not publish_id or not upload_url:
        print(f"  ERROR during init: {init}")
        return

    print(f"  publish_id: {publish_id}")
    print(f"  upload_url: {upload_url[:60]}...")

    section("Step: upload bytes")
    if not upload_video_file(upload_url, video_path):
        print("  Upload failed.")
        return
    print("  Upload complete.")

    section("Step: poll status")
    r = poll_until_done(token, publish_id)
    status = r.get("data", {}).get("status", "UNKNOWN")
    print(f"\n  Final status: {status}")

    if status == "SEND_TO_USER_INBOX":
        print("  Video sent to your TikTok Drafts. Open the TikTok app to finalize & post.")
    elif status == "PUBLISH_COMPLETE":
        print("  Video published directly to the feed.")
    else:
        print(f"  Full response: {json.dumps(r, indent=2)[:500]}")


def main() -> int:
    section("TikTok Content Posting API")
    print(f"  Client key:  {CLIENT_KEY}")
    print(f"  Redirect URI: {REDIRECT_URI}")
    print(f"  Scopes:       {', '.join(SCOPES)}")

    if not preflight():
        return 1

    args = sys.argv[1:]
    reuse = "--reuse" in args
    auth_only = "--auth-only" in args
    direct = "--direct" in args
    creator_info = "--creator-info" in args

    video_path: Path | None = None
    if "--video" in args:
        i = args.index("--video")
        if i + 1 < len(args):
            video_path = Path(args[i + 1]).resolve()

    title = "Uploaded via the AI Bible Gospels content pipeline"
    if "--title" in args:
        i = args.index("--title")
        if i + 1 < len(args):
            title = args[i + 1]

    privacy = "SELF_ONLY"  # sandbox default — safest
    if "--privacy" in args:
        i = args.index("--privacy")
        if i + 1 < len(args):
            privacy = args[i + 1]

    # Acquire token
    token = load_valid_token() if reuse else None
    if not token:
        token = run_oauth()
        if not token:
            return 2

    # Always verify the token works
    run_user_info_check(token)

    if creator_info:
        section("Creator info")
        r = get_creator_info(token)
        print(json.dumps(r, indent=2))
        return 0

    if auth_only:
        print("\n  --auth-only: skipping upload. Token saved.")
        return 0

    if not video_path:
        print("\n  No --video supplied. Pass --video PATH/TO/short.mp4 to upload.")
        print("  Or pass --auth-only to just capture a token.")
        return 0

    if not video_path.exists():
        print(f"\n  ERROR: video file not found: {video_path}")
        return 3

    upload_video(token, video_path, direct, title, privacy)
    return 0


if __name__ == "__main__":
    sys.exit(main())
