"""Overwrite the channel About-page description with the AEO-spec text."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

ABOUT_TEXT = """AI Bible Gospels is a faith-tech brand founded by Tommy Lee that uses AI to narrate Scripture word-for-word from a cultural perspective underrepresented in biblical media. Flagship project: Faith Walk Live (faithwalklive.com), the live tracker for Minister Zay's 3,000-mile walk from Philadelphia to California.

Website: https://aibiblegospels.com
Faith Walk Live: https://faithwalklive.com
LinkedIn: https://www.linkedin.com/in/ai-bible-gospels-049005353/
Contact: aibiblegospels444@gmail.com"""

client = YouTubeClient()
print("Fetching current brandingSettings...")
current = client.get_branding_settings()
old_desc = current["brandingSettings"].get("channel", {}).get("description", "")
print(f"Old description ({len(old_desc)} chars):")
print("-" * 60)
print(old_desc[:500] + ("..." if len(old_desc) > 500 else ""))
print("-" * 60)

print(f"\nNew description ({len(ABOUT_TEXT)} chars):")
print("-" * 60)
print(ABOUT_TEXT)
print("-" * 60)

print("\nUpdating channel About page...")
client.update_channel_description(ABOUT_TEXT)
print("Done.")
