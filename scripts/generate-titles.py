"""Generate standalone searchable titles from Part video transcripts."""

import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

topics_file = Path(__file__).resolve().parent.parent / "analytics" / "part-topics.json"
data = json.loads(topics_file.read_text())

print(f"Analyzing {len(data)} transcripts to identify topics...")
print("=" * 70)

# Keywords/phrases to look for in transcripts to identify the tribe or topic
tribe_keywords = {
    "reuben": "Tribe of Reuben",
    "simeon": "Tribe of Simeon",
    "levi": "Tribe of Levi",
    "judah": "Tribe of Judah",
    "dan": "Tribe of Dan",
    "naphtali": "Tribe of Naphtali",
    "gad": "Tribe of Gad",
    "asher": "Tribe of Asher",
    "issachar": "Tribe of Issachar",
    "zebulun": "Tribe of Zebulun",
    "joseph": "Tribe of Joseph",
    "ephraim": "Tribe of Ephraim",
    "manasseh": "Tribe of Manasseh",
    "benjamin": "Tribe of Benjamin",
}

topic_keywords = {
    "scattered": "Scattered",
    "captivity": "Captivity",
    "slavery": "Slavery",
    "curse": "Curses",
    "blessing": "Blessings",
    "covenant": "Covenant",
    "prophecy": "Prophecy",
    "deuteronomy": "Deuteronomy",
    "exodus": "Exodus",
    "revelation": "Revelation",
    "identity": "Identity",
    "chosen": "Chosen People",
    "promised land": "Promised Land",
    "babylo": "Babylon",
    "egypt": "Egypt",
    "assyria": "Assyria",
    "exile": "Exile",
    "return": "Return",
    "restoration": "Restoration",
    "judgment": "Judgment",
    "obedience": "Obedience",
    "disobedience": "Disobedience",
    "commandment": "Commandments",
    "law": "The Law",
    "temple": "The Temple",
    "king": "Kingdom",
    "david": "David",
    "solomon": "Solomon",
    "moses": "Moses",
    "jacob": "Jacob",
    "israel": "Israel",
    "america": "Americas",
    "caribbean": "Caribbean",
    "africa": "Africa",
    "native": "Native",
    "aboriginal": "Aboriginal",
    "trans-atlantic": "Trans-Atlantic",
    "slave trade": "Slave Trade",
    "middle passage": "Middle Passage",
    "negro": "Negro",
    "indian": "Indian",
    "latin": "Latin America",
    "mexico": "Mexico",
    "cuba": "Cuba",
    "haiti": "Haiti",
    "jamaica": "Jamaica",
    "brazil": "Brazil",
    "semitic": "Semitic",
    "hebrew": "Hebrew",
    "gentile": "Gentiles",
    "heathen": "Nations",
    "end times": "End Times",
    "last days": "Last Days",
    "tribulation": "Tribulation",
    "rapture": "Rapture",
    "remnant": "Remnant",
    "awakening": "Awakening",
}

proposals = []

for entry in data:
    vid = entry["id"]
    part_num = entry["part_num"]
    old_title = entry["old_title"]
    views = entry["views"]
    transcript = entry.get("full_transcript", entry.get("transcript_preview", "")).lower()

    # Find tribes mentioned
    found_tribes = []
    for kw, label in tribe_keywords.items():
        if kw in transcript:
            # Count occurrences to find primary tribe
            count = transcript.count(kw)
            found_tribes.append((label, count))
    found_tribes.sort(key=lambda x: x[1], reverse=True)

    # Find topics mentioned
    found_topics = []
    for kw, label in topic_keywords.items():
        if kw in transcript:
            count = transcript.count(kw)
            found_topics.append((label, count))
    found_topics.sort(key=lambda x: x[1], reverse=True)

    primary_tribe = found_tribes[0][0] if found_tribes else None
    secondary_tribe = found_tribes[1][0] if len(found_tribes) > 1 else None
    top_topics = [t[0] for t in found_topics[:3]]

    # Generate title based on content
    # Priority: specific tribe > specific topic > general
    new_title = None

    if primary_tribe and primary_tribe != "Tribe of Joseph":
        tribe_name = primary_tribe.replace("Tribe of ", "")
        if "scatter" in transcript or "lost" in transcript:
            new_title = f"Where Is the {primary_tribe} Today? The Lost Israelites"
        elif "curse" in transcript or "punish" in transcript:
            new_title = f"The {primary_tribe}: Biblical Curses That Changed History"
        elif "blessing" in transcript:
            new_title = f"The {primary_tribe}: God's Blessings and Promises Revealed"
        elif "prophecy" in transcript or "prophes" in transcript:
            new_title = f"The {primary_tribe}: Prophecy You Were Never Told"
        elif "identity" in transcript or "who are" in transcript:
            new_title = f"Who Are the {primary_tribe}? Their True Biblical Identity"
        elif "slave" in transcript or "captiv" in transcript:
            new_title = f"The {primary_tribe}: From Captivity to Awakening"
        else:
            new_title = f"The {primary_tribe}: What the Bible Really Says"
    elif "scatter" in transcript and "nation" in transcript:
        new_title = "How Israel Was Scattered Among the Nations"
    elif "slave" in transcript and ("trade" in transcript or "ship" in transcript):
        new_title = "The Slave Trade and Biblical Prophecy Connected"
    elif "deuteronomy" in transcript and "curse" in transcript:
        new_title = "Deuteronomy's Curses: Prophecy Fulfilled Before Our Eyes"
    elif "covenant" in transcript:
        new_title = "God's Covenant With Israel: The Promise That Still Stands"
    elif "law" in transcript and "command" in transcript:
        new_title = "The Laws Israel Was Commanded to Keep Forever"
    elif "end time" in transcript or "last day" in transcript:
        new_title = "The 12 Tribes in the End Times: What's Coming Next"
    elif "awaken" in transcript or "wake" in transcript:
        new_title = "The Great Awakening of the 12 Tribes of Israel"
    elif "remnant" in transcript:
        new_title = "The Remnant of Israel: Who Will Be Saved?"
    else:
        # Generic but still better than "Part X"
        new_title = f"12 Tribes of Israel: Hidden Truth From the Scriptures"

    # Ensure uniqueness — append tribe or topic hint if title might be duplicate
    proposals.append({
        "id": vid,
        "part_num": part_num,
        "old_title": old_title,
        "new_title": new_title,
        "views": views,
        "primary_tribe": primary_tribe,
        "top_topics": top_topics,
        "transcript_preview": entry.get("transcript_preview", "")[:200],
    })

# Deduplicate titles — if same title appears multiple times, make unique
title_counts = {}
for p in proposals:
    t = p["new_title"]
    title_counts[t] = title_counts.get(t, 0) + 1

# For duplicates, add distinguishing info
seen_titles = {}
for p in proposals:
    t = p["new_title"]
    if title_counts[t] > 1:
        seen_titles[t] = seen_titles.get(t, 0) + 1
        count = seen_titles[t]
        # Try to differentiate using topics or part number
        if p["top_topics"] and len(p["top_topics"]) > 1:
            topic = p["top_topics"][1] if p["top_topics"][0] in t else p["top_topics"][0]
            p["new_title"] = f"{t.rstrip('?!.')} — {topic}"
        else:
            p["new_title"] = f"{t.rstrip('?!.')} #{count}"

# Ensure all titles are under 70 chars
for p in proposals:
    if len(p["new_title"]) > 70:
        p["new_title"] = p["new_title"][:67] + "..."

# Save proposals
output = Path(__file__).resolve().parent.parent / "analytics" / "proposed-titles.json"
output.write_text(json.dumps(proposals, indent=2, ensure_ascii=False))

# Print for review
print(f"\n{'=' * 70}")
print("PROPOSED TITLE CHANGES")
print(f"{'=' * 70}\n")

for p in proposals:
    print(f"Part {p['part_num']:>4} ({p['views']:>6} views) [{p['id']}]")
    print(f"  OLD: {p['old_title']}")
    print(f"  NEW: {p['new_title']}")
    if p['primary_tribe']:
        print(f"  Topics: {p['primary_tribe']}, {', '.join(p['top_topics'][:3])}")
    print()

print(f"Total: {len(proposals)} titles proposed")
print(f"Saved to {output}")
