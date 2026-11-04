"""Overwrite the channel About-page description with the AEO-spec text.

Tommy hand-wrote the live About text after 2026-10-31. This script refuses to replace a
live About that differs from ABOUT_TEXT unless --force is passed, so a re-run cannot
silently wipe his own words.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

ABOUT_TEXT = """AI Bible Gospels (@AIBIBLEGOSPELS) is a faith-tech brand founded by Tommy Lee.

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

if old_desc.strip() != ABOUT_TEXT.strip() and "--force" not in sys.argv:
    print("\nLive About text differs and may be Tommy's own wording. Not overwriting.")
    print("Re-run with --force only if he asked for this replacement.")
    sys.exit(1)

print("\nUpdating channel About page...")
client.update_channel_description(ABOUT_TEXT)
print("Done.")
