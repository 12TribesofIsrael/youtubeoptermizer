"""One-time authentication script. Run this first to authorize YouTube access."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.auth import get_credentials, CREDENTIALS_FILE

print("YouTube API Authentication")
print("=" * 40)

if not CREDENTIALS_FILE.exists():
    print(f"\nERROR: {CREDENTIALS_FILE} not found!")
    print("\nTo fix this:")
    print("1. Go to https://console.cloud.google.com")
    print("2. Create OAuth 2.0 credentials (Desktop app)")
    print("3. Download the JSON and save as 'credentials.json' in the project root")
    sys.exit(1)

print("\nOpening browser for Google authorization...")
print("Sign in with the Google account that owns your YouTube channel.\n")

creds = get_credentials()
print("\nAuthentication successful!")
print("Token saved — you won't need to do this again unless you revoke access.")
