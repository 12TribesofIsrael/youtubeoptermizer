"""Upload the Faith Walk Live anchor documentary to YouTube as Unlisted.

Single-shot script: uploads the v3 MP4, sets metadata + thumbnail + caption track,
creates the Faith Walk Live playlist if missing and adds the video, then posts the
pinned-comment text. Pinning itself is Studio-only — Tommy clicks it manually.

Outputs the live (unlisted) YT URL on success. Tommy reviews + flips to Public.

Resumable upload via googleapiclient — large file (~1 GB) is fine over slow links.
"""
import sys
import time
from pathlib import Path

from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.youtube.client import YouTubeClient

VIDEO_PATH    = ROOT / "src" / "anchor-doc" / "out" / "anchor-doc-v3.mp4"
THUMBNAIL     = ROOT / "faith-walk-live" / "anchor-doc" / "thumbnail.png"
CAPTIONS_SRT  = ROOT / "src" / "anchor-doc" / "out" / "anchor-doc.srt"

TITLE = "3000 Miles for the Kids — Why One Philly Man Is Walking to California"

DESCRIPTION = """He's walking 3,000 miles from Philadelphia to California to build a school for at-risk kids. He livestreams every step. This is Faith Walk Live.

Isaiah "Humble Zay" Thomas left Philadelphia on March 26, 2026 with a backpack and a plan most people would call impossible. Six weeks in, he's still walking — past Pennsylvania, through Ohio, into Indiana — broadcasting every mile live on Twitch. The mission: raise enough to build a school for Philly kids who, in his words, "end up in the system or end up dead." A community of strangers — Hebrew Israelite aunties, brothers, drivers slowing down on the shoulder — has shown up at every stop.

This is the documentary of his walk so far. Real footage. Real testimony. No reenactments.

— TIMESTAMPS —
0:00 Cold open
0:15 Title
0:30 Who is Humble Zay
2:00 The why — in his own words
4:30 The road
7:00 The community shows up
10:00 Why we built faithwalklive.com
12:00 Closing scripture
12:30 How to support

— HOW TO SUPPORT —
🥾 Track the walk live: https://faithwalklive.com
💰 Donate to the school (GoFundMe): https://gofund.me/19cf823bc
🎥 Watch live on Twitch: https://www.twitch.tv/hmblzayy
📺 Subscribe for more: https://www.youtube.com/@AIBIBLEGOSPELS
🐦 Follow on X: https://x.com/aibiblegospels
📰 Press kit (for journalists): https://faithwalklive.com/press

— Q&A —
Q: Who is the man walking?
A: Isaiah "Humble Zay" Thomas, a minister out of Philadelphia, walking 3,000 miles from Philadelphia to California to fund a school for at-risk Philly kids.

Q: Why is he walking?
A: To raise money to build a school — and eventually a university — that helps kids in Philadelphia (and later Baltimore, DC) develop their gifts before they "end up in the system or end up dead." The walk is the fundraiser; the livestream is the witness.

Q: How can I support the school?
A: Donate via the GoFundMe link in this description. Every dollar goes to the school in Philly.

Q: Where is he right now?
A: Track him live at https://faithwalklive.com — real-time mile counter, current location, and stream embed.

Q: What is Faith Walk Live?
A: It's both the walk itself and the live-tracking app at https://faithwalklive.com — built by AI Bible Gospels so supporters can follow the mission in real time without scrolling Twitch.

Q: Who made this video?
A: AI Bible Gospels, a faith-tech project by Tommy Lee using AI to bring Scripture to life and to build software in service of ministers like Humble Zay.

— ABOUT AI BIBLE GOSPELS —
AI Bible Gospels (@AIBIBLEGOSPELS) is a faith-tech brand founded by Tommy Lee that uses AI to narrate Scripture word-for-word from a cultural perspective underrepresented in biblical media. Flagship project: Faith Walk Live, the live tracker for Minister Zay's 3,000-mile walk from Philadelphia to California.

Website: https://aibiblegospels.com
Faith Walk Live: https://faithwalklive.com
YouTube: https://www.youtube.com/@AIBIBLEGOSPELS
X: https://x.com/aibiblegospels
LinkedIn: https://www.linkedin.com/in/ai-bible-gospels-049005353/
Press: https://faithwalklive.com/press
Contact: aibiblegospels444@gmail.com

#AIBibleGospels #FaithWalkLive #HumbleZay #3000MilesForTheKids"""

TAGS = [
    "Humble Zay", "Isaiah Thomas", "Faith Walk Live", "faithwalklive.com",
    "3000 mile walk", "Philadelphia to California walk", "walk for kids",
    "Philly school fundraiser", "GoFundMe walk", "walking documentary",
    "livestream walk", "Black men walking", "Hebrew Israelite walk",
    "AI Bible Gospels", "faith-tech", "ministry tools",
    "Black community investment", "Philly kids", "school in Philadelphia",
]

CATEGORY_ID = "27"  # Education — channel default per all-videos.csv

PINNED_COMMENT = """3 ways to support this mission:

🥾 Track the walk live → https://faithwalklive.com
💰 Donate to the school → https://gofund.me/19cf823bc
🎥 Watch the broadcast live → https://www.twitch.tv/hmblzayy

Follow on X → https://x.com/aibiblegospels
Press kit (journalists) → https://faithwalklive.com/press

Every dollar goes to the school in Philly. Every step is a brick."""

PLAYLIST_TITLE = "Faith Walk Live — The 3000-Mile Walk"
PLAYLIST_DESCRIPTION = (
    "Documentary, recap, and Shorts cuts following Minister Humble Zay's "
    "3,000-mile walk from Philadelphia to California. Track live at faithwalklive.com."
)


def main():
    # Pre-flight
    for p in (VIDEO_PATH, THUMBNAIL, CAPTIONS_SRT):
        if not p.exists():
            sys.exit(f"MISSING: {p}")

    print(f"Video: {VIDEO_PATH.relative_to(ROOT)} ({VIDEO_PATH.stat().st_size / 1e9:.2f} GB)")
    print(f"Thumb: {THUMBNAIL.relative_to(ROOT)}")
    print(f"SRT:   {CAPTIONS_SRT.relative_to(ROOT)}")
    print()

    yt = YouTubeClient()
    youtube = yt.youtube

    # ── 1. Upload video ────────────────────────────────────────────────────
    print("[1/6] Uploading video as UNLISTED (resumable, may take 5-15 min)...")
    body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": TAGS,
            "categoryId": CATEGORY_ID,
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False,
            "madeForKids": False,
        },
    }
    media = MediaFileUpload(str(VIDEO_PATH), chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"     Upload progress: {int(status.progress() * 100)}%")
    video_id = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"     Done. video_id = {video_id}")
    print(f"     URL: {video_url}")

    # ── 2. Set thumbnail ───────────────────────────────────────────────────
    print(f"\n[2/6] Setting thumbnail...")
    yt.set_thumbnail(video_id, str(THUMBNAIL))
    print(f"     Done.")

    # ── 3. Upload caption track (SRT) ──────────────────────────────────────
    print(f"\n[3/6] Uploading caption track (.srt)...")
    cap_media = MediaFileUpload(str(CAPTIONS_SRT), mimetype="text/plain", resumable=False)
    cap_body = {
        "snippet": {
            "videoId": video_id,
            "language": "en",
            "name": "English (auto-generated from narration)",
            "isDraft": False,
        }
    }
    cap_resp = youtube.captions().insert(part="snippet", body=cap_body, media_body=cap_media).execute()
    print(f"     Done. caption_id = {cap_resp['id']}")

    # ── 4. Find or create playlist ─────────────────────────────────────────
    print(f"\n[4/6] Finding or creating playlist '{PLAYLIST_TITLE}'...")
    playlists = yt.list_playlists()
    target = next((p for p in playlists if p["snippet"]["title"] == PLAYLIST_TITLE), None)
    if target:
        playlist_id = target["id"]
        print(f"     Found existing. id = {playlist_id}")
    else:
        new_pl = yt.create_playlist(PLAYLIST_TITLE, PLAYLIST_DESCRIPTION, "public")
        playlist_id = new_pl["id"]
        print(f"     Created. id = {playlist_id}")

    print(f"\n[5/6] Adding video to playlist...")
    yt.add_to_playlist(playlist_id, video_id)
    print(f"     Done.")

    # ── 6. Post pinned-comment text ────────────────────────────────────────
    print(f"\n[6/6] Posting pinned-comment text (you'll click 'Pin' in Studio manually)...")
    comment_body = {
        "snippet": {
            "videoId": video_id,
            "topLevelComment": {
                "snippet": {"textOriginal": PINNED_COMMENT}
            },
        }
    }
    comment_resp = youtube.commentThreads().insert(part="snippet", body=comment_body).execute()
    print(f"     Done. comment_id = {comment_resp['id']}")

    print("\n" + "=" * 78)
    print("UPLOAD COMPLETE -- video is UNLISTED. Final 3 manual steps:\n")
    print(f"  1. Watch the live YT player: {video_url}")
    print(f"     (Confirm subtitles, audio mix, thumbnail render in YT's encoder)")
    print(f"  2. Studio -> Content -> the video -> Comments -> 3-dot on your comment -> Pin.")
    print(f"  3. Studio -> Content -> the video -> Visibility -> Public, then Save.")
    print("\nOptional after publishing:")
    print(f"  - Add 3-element End Screen (Subscribe + Best-for-viewer + top 12 Tribes Short).")
    print(f"  - Set 'Faith Walk Live' as Featured Playlist on the channel home page.")
    print("=" * 78)


if __name__ == "__main__":
    main()
