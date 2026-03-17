"""Rename the 26 remaining Part videos with viral standalone titles."""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()

# Titles crafted based on series theme and part sequence
renames = [
    ("hhUc8eF3fzQ", "78", 776, "The Tribe of Benjamin — Wolves in the Last Days, Genesis 49:27"),
    ("hJDgZIu3gas", "85", 757, "The 12 Tribes Gathering — Prophecy of the Final Restoration"),
    ("8aaTGPQmSXo", "81", 754, "The Tribe of Benjamin — A Light in the Darkness, Isaiah 9:2"),
    ("TmTLdel9HhM", "75", 737, "The Tribe of Manasseh — A Multitude of Nations Prophesied"),
    ("Tf390YnbgRg", "83", 727, "Israel's Return — The Dry Bones of Ezekiel 37 Live Again"),
    ("gVtjIGub94w", "74", 723, "The Tribe of Manasseh — Separated From His Brothers"),
    ("hb56WpRKlSk", "77", 717, "The Tribe of Benjamin — Devouring the Prey at Dawn"),
    ("thvQjWzAhJI", "86", 691, "The 12 Tribes Awaken — The Prophecy of the Last Days"),
    ("Tg9tXQBBEVU", "76", 690, "The Tribe of Manasseh — Half Tribe in a Foreign Land"),
    ("t898Bmt9Pzc", "53", 690, "The Tribe of Asher — Royal Dainties and Hidden Blessings"),
    ("Mgp2CgZtG64", "72", 683, "The Tribe of Naphtali — Goodly Words and a Fruitful Land"),
    ("5IHuhAx9184", "82", 681, "The Tribe of Benjamin — Sons of the Right Hand Revealed"),
    ("0hjJSaaUgpU", "73", 668, "The Tribe of Naphtali — A Hind Let Loose, Genesis 49:21"),
    ("hJZ3g3ThGik", "30", 487, "The Tribe of Judah — The Lion's Whelp Shall Rise Again"),
    ("EVXPdM8tGcQ", "27", 436, "The Tribe of Judah — Sold Into Slavery, Psalms 83 Conspiracy"),
    ("g713EId0x3U", "46", 331, "The Tribe of Dan — Judging His People as Prophesied"),
    ("2oP2-iyMf20", "7", 227, "The Curses Came True — Israel Scattered Across the Earth"),
    ("Mo1wDJhH3d8", "63", 211, "The Tribe of Ephraim — Fruitful in a Strange Land"),
    ("TK82X4dOE7w", "60", 208, "The Tribe of Naphtali — Satisfied With Favor, Deuteronomy 33"),
    ("w8fXqQPM26o", "59", 192, "The Tribe of Naphtali — Full of the Blessing of the Lord"),
    ("YZOq2NBT3d8", "51", 185, "The Tribe of Asher — Dipping His Foot in Oil, Deuteronomy 33"),
    ("U9Odey7BrxE", "54", 170, "The Tribe of Naphtali — Possess Thou the West and the South"),
    ("4-lwx45nL1A", "65", 149, "The Tribe of Ephraim — Arrows Against the Enemy, Zechariah 9"),
    ("0nM51QdNWLU", "50", 148, "The Tribe of Asher — His Bread Shall Be Fat, Genesis 49:20"),
    ("CuNKO1aBdRM", "67", 123, "The Tribe of Ephraim — Scattered but Never Forgotten"),
    ("wlRi_e-zzE4", "69", 83, "The Tribe of Ephraim — A Watchman in the House of God"),
]

print(f"Renaming {len(renames)} remaining Part videos...")
print("=" * 60)

updated = 0
errors = []

for vid, part_num, views, new_title in renames:
    try:
        video = client.get_video(vid)
        if not video:
            print(f"  SKIP [{vid}] Part {part_num} — not found")
            continue

        old_desc = video["snippet"].get("description", "")
        part_line = f"Part {part_num} of The Prophecy Revealed series"
        if f"Part {part_num}" not in old_desc:
            new_desc = f"{part_line}\n\n{old_desc}"
        else:
            new_desc = old_desc

        client.update_video(vid, title=new_title, description=new_desc)
        updated += 1
        print(f"  [{updated}] Part {part_num} → {new_title}")
        time.sleep(0.5)
    except Exception as e:
        errors.append({"id": vid, "part_num": part_num, "error": str(e)})
        print(f"  ERROR [{vid}] Part {part_num}: {e}")
        if "quotaExceeded" in str(e):
            print(f"\nQuota hit after {updated} updates.")
            break

print(f"\n{'=' * 60}")
print(f"Updated: {updated}")
print(f"Errors:  {len(errors)}")
