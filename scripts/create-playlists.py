"""Create tribe-based playlists and populate them with videos."""

import sys
import time
sys.path.insert(0, ".")
from src.youtube.client import YouTubeClient

client = YouTubeClient()

# ── Existing playlists to update ──────────────────────────────────

BENJAMIN_PLAYLIST_ID = "PLFyw-nH_HYIs0L1563zcfGSqY7SbVqEvr"
BENJAMIN_MISSING = ["hhUc8eF3fzQ"]  # Wolves in the Last Days, Genesis 49:27

# ── New playlists to create ───────────────────────────────────────

PLAYLISTS = [
    {
        "title": "The Tribe of Ephraim — Fruitful in a Strange Land",
        "description": "The Tribe of Ephraim, Joseph, and Manasseh — scattered across the Caribbean, Puerto Rico, and the Americas. From Genesis 49 to Hosea 9, discover the prophecies fulfilled.",
        "videos": [
            "xMqnO931dic", "gK7bK1ktRR4", "kPO91HQ5nU0", "Mo1wDJhH3d8",
            "4-lwx45nL1A", "CuNKO1aBdRM", "wlRi_e-zzE4",
            "dHw41Z7hmVM",  # Joseph
            "gVtjIGub94w", "Tg9tXQBBEVU", "TmTLdel9HhM",  # Manasseh
        ],
    },
    {
        "title": "The Tribe of Naphtali — A Hind Let Loose",
        "description": "The Tribe of Naphtali — from the Southern Hemisphere to Chile and the South Sea Islands. Genesis 49:21, Deuteronomy 33, and the prophecies revealed.",
        "videos": [
            "V-dUWFIYZQE", "A7cH3cIkFUg", "Mgp2CgZtG64", "0hjJSaaUgpU",
            "w8fXqQPM26o", "TK82X4dOE7w", "U9Odey7BrxE",
        ],
    },
    {
        "title": "The Tribes of Zebulun & Issachar — Mayans and Aztecs",
        "description": "Zebulun and Issachar — the Mayans, Aztecs, Mexicans, Guatemalans, and Panamanians. Deuteronomy 33, Genesis 49, and the Assyrian Captivity.",
        "videos": [
            "EWksyIbaImo", "nVOXmuAJPuY", "UrZyd9pzI70", "SWZId0P96f8",
            "ry_PjMpdi8Q", "jzhLtWD4Qtw", "9YpL3hEPQuY",
        ],
    },
    {
        "title": "The Tribe of Gad — Native Nations of Israel",
        "description": "The Tribe of Gad — over 300 Native nations descending from Israel. North American Indians in Genesis 49:19.",
        "videos": ["isBUYL7jvdY", "wlF2yDtDdfo", "TZV8LKt-t5E"],
    },
    {
        "title": "The Tribe of Reuben — Nomadic Warriors",
        "description": "The Tribe of Reuben — Seminole Indians and the nomadic warriors the Europeans feared. Genesis 49 prophecy revealed.",
        "videos": ["0XrtYFN9Kr0", "NAYa0kXwSwQ"],
    },
    {
        "title": "The Tribe of Asher — Mighty Warriors",
        "description": "The Tribe of Asher — mighty warriors with buckler and sword, royal dainties, and hidden blessings. Genesis 49:20, Deuteronomy 33.",
        "videos": ["StUObmgtTqw", "t898Bmt9Pzc", "YZOq2NBT3d8", "0nM51QdNWLU"],
    },
    {
        "title": "The Tribes of Simeon & Levi — Divided in Israel",
        "description": "Simeon and Levi — fierce anger prophesied in Genesis 49. Haiti, Dominican Republic, Hispaniola, and the adoption of Voodoo. Malachi 2:9 fulfilled.",
        "videos": ["mMkUmDuniVQ", "vEB569AEDwg", "9jiykCkltok", "0bcCriDBO7w"],
    },
    {
        "title": "The Tribe of Dan — Judging His People",
        "description": "The Tribe of Dan — judging his people as prophesied in Genesis 49:16.",
        "videos": ["g713EId0x3U"],
    },
    {
        "title": "The Lost Tribes of Israel — Where Did They Go?",
        "description": "Where did the Lost Tribes of Israel go? From 2 Esdras 13:39 to the Americas, the Bering Strait myth debunked, and the awakening happening now.",
        "videos": [
            "H9jblXXVHxY", "m51Aex5Y6Aw", "9H4yPDLobmw", "8sw0hlTmmaw",
            "h7pYxWAEci0", "yo48yhFzwaM", "LwPZQ-wPjnc", "4vj5cDipimw",
            "WBTvL8yDu70", "Zydb5yxsPZo", "PCxBqyvr8NA", "ocXSvMnJaLE",
            "onnUvy4ryAA", "2oP2-iyMf20",
        ],
    },
    {
        "title": "Deuteronomy 28 — Curses & Prophecy Fulfilled",
        "description": "Every curse of Deuteronomy 28 has been fulfilled. Slave ships, scattered among nations, smitten before enemies. Biblical prophecy is history written in advance.",
        "videos": [
            "WpEsJWK1Awo", "dKw6UGVQF98", "svPYMDJB6f4", "XJYSaQ1fpxU",
            "crLefjKVnVk", "bjjjgJR1wKY", "MkoJO402Rmc", "OHfVqkni9g0",
            "dpERIR0YZZ8", "bhXtvLHRkrU", "_RxAAxLNQNU", "KGVZHGopiQ0",
            "EVXPdM8tGcQ", "qyh745BNjw0",
        ],
    },
    {
        "title": "12 Tribes of Israel — The Big Picture",
        "description": "The complete overview of the 12 Tribes of Israel — who they are, where they went, and why the prophecy is being revealed now. Start here.",
        "videos": [
            "UObM30FGdSs", "mAJS97kNC5E", "Ad3mUsbLL3w", "L84JUXnMoR8",
            "Zs2ctQoZmhU", "rq27Uvxudwg", "8qjE34r7ISM", "GrqhQqq8hCQ",
            "wKtfQLOH9ww", "KK4BaRSCneI", "7f9Pk1Wwn5o", "ooFdPFS_qvs",
            "hJDgZIu3gas", "MFTYh87UX00", "thvQjWzAhJI", "Jb9l1tT95ok",
            "DCBxC0F0fBY", "xL8v7eZ9mwc", "ggAF28BvCqY", "V1X-iqGgYls",
            "sN_UHGSkArg", "3ase0yJE_Xs", "FxBcgMI3Rcc", "ZnCssbJ2ndw",
            "zyS-Q2F_Hps", "5clbXshp6Ic", "6lbjD5o_ulk", "2jY6JD1f3Ak",
            "TMSy1bkK2tQ", "5PkQelhrXaM", "mYbLS7to7iM", "NbxKHpWaJwY",
            "o55RyJe0Lu4", "q9W387FmpGE", "iMNr2Xilz8c", "DEYNUT9uoxM",
        ],
    },
]


def main():
    quota_used = 0

    # Step 1: Add missing Benjamin video
    print("=" * 60)
    print("STEP 1: Add missing Benjamin video")
    print("=" * 60)
    for vid in BENJAMIN_MISSING:
        try:
            client.add_to_playlist(BENJAMIN_PLAYLIST_ID, vid)
            quota_used += 50
            print(f"  Added {vid} to Benjamin playlist")
        except Exception as e:
            print(f"  ERROR adding {vid}: {e}")
    time.sleep(0.5)

    # Step 2: Create new playlists
    print(f"\n{'=' * 60}")
    print("STEP 2: Create new playlists")
    print("=" * 60)

    for i, pl in enumerate(PLAYLISTS, 1):
        print(f"\n[{i}/{len(PLAYLISTS)}] Creating: {pl['title']}")
        try:
            result = client.create_playlist(pl["title"], pl["description"])
            playlist_id = result["id"]
            quota_used += 50
            print(f"  Created playlist: {playlist_id}")
        except Exception as e:
            print(f"  ERROR creating playlist: {e}")
            if "quotaExceeded" in str(e):
                print(f"\nQuota hit after ~{quota_used} units. Resume tomorrow.")
                return
            continue

        # Add videos
        for j, vid in enumerate(pl["videos"], 1):
            try:
                client.add_to_playlist(playlist_id, vid)
                quota_used += 50
                print(f"    [{j}/{len(pl['videos'])}] Added {vid}")
                time.sleep(0.3)
            except Exception as e:
                print(f"    ERROR adding {vid}: {e}")
                if "quotaExceeded" in str(e):
                    print(f"\nQuota hit after ~{quota_used} units. Resume tomorrow.")
                    return

        print(f"  Done — {len(pl['videos'])} videos added")

    print(f"\n{'=' * 60}")
    print(f"ALL PLAYLISTS CREATED — ~{quota_used} quota units used")
    print("=" * 60)


if __name__ == "__main__":
    main()
