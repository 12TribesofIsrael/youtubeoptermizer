"""Fetch TikTok publish status for a given publish_id."""
import json
import os
import sys
import urllib.request

from dotenv import load_dotenv

load_dotenv()

publish_id = sys.argv[1] if len(sys.argv) > 1 else "v_inbox_file~v2.7630180157080602638"
token = os.getenv("TIKTOK_ACCESS_TOKEN", "")

req = urllib.request.Request(
    "https://open.tiktokapis.com/v2/post/publish/status/fetch/",
    data=json.dumps({"publish_id": publish_id}).encode(),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    },
    method="POST",
)
print(json.dumps(json.loads(urllib.request.urlopen(req).read()), indent=2))
