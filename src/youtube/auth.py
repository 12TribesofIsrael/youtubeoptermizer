"""OAuth 2.0 authentication for YouTube Data API v3."""

import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CREDENTIALS_FILE = PROJECT_ROOT / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def get_credentials():
    """Load or create OAuth credentials. Opens browser on first run."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"Missing {CREDENTIALS_FILE}\n"
                    "Download your OAuth 2.0 Client ID JSON from Google Cloud Console "
                    "and save it as 'credentials.json' in the project root."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=8080)

        TOKEN_FILE.write_text(creds.to_json())
        print(f"Token saved to {TOKEN_FILE}")

    return creds


def get_authenticated_service(api="youtube", version="v3"):
    """Return an authenticated YouTube API service object."""
    creds = get_credentials()
    if api == "youtubeAnalytics":
        return build("youtubeAnalytics", "v2", credentials=creds)
    return build("youtube", version, credentials=creds)
