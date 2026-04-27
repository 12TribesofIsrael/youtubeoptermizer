"""Print one full video description from YouTube so Thomas can see the update."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

VIDEO_ID = "TBNEIWRpnzI"  # "The Tribe of Judah Will Rise" — long-form


def main():
    yt = YouTubeClient()
    resp = yt.youtube.videos().list(part="snippet", id=VIDEO_ID).execute()
    item = resp["items"][0]
    title = item["snippet"]["title"]
    desc = item["snippet"]["description"]
    url = f"https://youtu.be/{VIDEO_ID}"
    print(f"Title : {title}")
    print(f"URL   : {url}")
    print("-" * 70)
    print(desc)
    print("-" * 70)
    print(f"Description length: {len(desc)} chars")


if __name__ == "__main__":
    main()
