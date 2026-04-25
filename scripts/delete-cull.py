"""
Phase YPP-prep cull — delete 23 Shorts flagged in docs/kill-list.md.

Approved 2026-04-24 for the 2026-07-08 YPP reapply window. Permanent.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

# (video_id, views, tier, title)
to_delete = [
    # Tier A — Dead weight (Shorts, >90d, <200v)
    ("3riiNCfzQ_g",   37, "A", "They've Been Using the Same Deception for 2000 Years"),
    ("zQaLpyUFfNA",   58, "A", "Why Governments Fear Moral Truth"),
    ("wlRi_e-zzE4",   83, "A", "The Tribe of Ephraim - A Watchman in the House of God"),
    ("p0xBHbtk7CI",   98, "A", "Powerful Biblical Knowledge That Nobody Talks About"),
    ("2e_pe-3GpBI",  100, "A", "The SHOCKING Reality of How Nations Fall From Within"),
    ("Ox_dozHLaaM",  104, "A", "The Hidden Truth About Biblical Identity That Will SHOCK You!"),
    ("CuNKO1aBdRM",  123, "A", "The Tribe of Ephraim - Scattered but Never Forgotten"),
    ("6lbjD5o_ulk",  133, "A", "This 12 Tribes Prophecy Changes Everything"),
    ("puRpiE4KtXQ",  145, "A", "Deuteronomy 7:6-7"),
    ("4-lwx45nL1A",  149, "A", "The Tribe of Ephraim - Arrows Against the Enemy"),
    ("V1X-iqGgYls",  163, "A", "Journey with us, The Most High Chosen People!"),
    ("U9Odey7BrxE",  170, "A", "The Tribe of Naphtali - Possess Thou the West and the South"),
    ("YZOq2NBT3d8",  185, "A", "The Tribe of Asher - Dipping His Foot in Oil"),
    ("w8fXqQPM26o",  192, "A", "The Tribe of Naphtali - Full of the Blessing of the Lord"),
    ("FEkLq5XApX0",  197, "A", "The Everlasting Covenant Israel's Promise"),

    # Tier B — Tribe-series tail
    ("TK82X4dOE7w",  208, "B", "The Tribe of Naphtali - Satisfied With Favor"),
    ("Mo1wDJhH3d8",  211, "B", "The Tribe of Ephraim - Fruitful in a Strange Land"),
    ("EVXPdM8tGcQ",  436, "B", "The Tribe of Judah - Sold Into Slavery, Psalms 83 Conspiracy"),
    ("hJZ3g3ThGik",  487, "B", "The Tribe of Judah - The Lion's Whelp Shall Rise Again"),

    # Tier C — Generic hype titles, no scripture anchor
    ("3ase0yJE_Xs",  219, "C", "The 12 Tribes of Israel The Most High Holy People"),
    ("ggAF28BvCqY",  222, "C", "The Most High Chosen People How special and Holy they are"),
    ("sN_UHGSkArg",  226, "C", "Why These 12 Tribes Changed The World FOREVER"),
    ("dwd69b2G-gU",  339, "C", "The Hidden Truth About Biblical Identity That Will SHOCK You!"),
]

client = YouTubeClient()

print(f"Deleting {len(to_delete)} Shorts (Tier A: 15, Tier B: 4, Tier C: 4)")
print("=" * 70)

deleted = []
errors = []

for vid, views, tier, label in to_delete:
    try:
        video = client.get_video(vid)
        if not video:
            print(f"  SKIP [{vid}] — already gone")
            continue
        actual_title = video["snippet"]["title"]
        client.delete_video(vid)
        deleted.append((vid, views, tier, actual_title))
        print(f"  DELETED [{tier}] [{vid}] {views:>4}v  {actual_title[:60]}")
        time.sleep(0.5)
    except Exception as e:
        errors.append((vid, str(e)))
        print(f"  ERROR   [{tier}] [{vid}] {e}")

print("=" * 70)
print(f"Deleted: {len(deleted)} / {len(to_delete)}")
if errors:
    print(f"Errors: {len(errors)}")
    for vid, msg in errors:
        print(f"  {vid}: {msg}")
