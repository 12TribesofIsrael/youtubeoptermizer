"""Build output/manifests/eden-part1.json — the full 26-scene Part 1 assembler manifest.

Narration is the human-written prose from drafts/eden-part1-scene-plan.md with the
[phonetic] helper brackets STRIPPED: subtitles come from Whisper transcribing the TTS audio
(scripts/assemble/transcribe.py), so feeding the real spelling keeps captions correct. Hard
proper nouns are QC'd by ear in the pronunciation canary; only ones ElevenLabs actually
mangles get phoneticized individually.

clip_path is repo-relative (download_clips._resolve_local joins it to repo root). Non-figure
scenes point at output/clips/eden-part1/<id>.mp4 (built by build-eden-clips.py); figure scenes
point at output/clips/eden-part1-figures/<id>.mp4 (Kling renders).

SFX moods are pre-assigned for control (sfx_map.json mood -> file). The library may be empty;
the assembler skips missing SFX gracefully, so v1 can ship narration+visuals and gain ambience
later once the Pixabay files are dropped into scripts/assemble/sfx_library/.

Usage: python scripts/build-eden-manifest.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Figure scenes come from Kling (output/clips/eden-part1-figures/); the rest are
# cards/maps/stills/artifacts built by build-eden-clips.py. Keep this in sync with
# FIGURE_CLIPS in build-eden-clips.py.
FIGURE_IDS = {"co2", "p3", "p7", "p9", "p10", "p15"}

VOICE_ID = "RKqAcMj3TkzJjyZpEbj0"   # Tommy's ElevenLabs clone (reference_thomas_israel_voice)
VOICE_SPEED = 0.92                  # measured documentary pace (smoke-validated with this voice)
OUT = ROOT / "output" / "manifests" / "eden-part1.json"

with open(ROOT / "scripts" / "assemble" / "sfx_map.json", encoding="utf-8") as f:
    SFX_MOODS = json.load(f)["moods"]

# scene_id -> (sfx_mood, narration). Narration = clean spelling (no phonetic brackets).
SCENES = [
    ("co1", "void-opening",
     "Before there was a Europe… there was a garden."),
    ("co2", "ancient-river",
     "Before there was a kingdom in the West, before a single stone of Rome was laid, before the word white or the word black had ever been spoken to divide one man from another — there was a people. A dark and shining people, walking between two rivers, in the oldest civilization this earth has ever known."),
    ("co3", "golden-ambient",
     "History gave them a hundred names. Sumerians. Cushites. Babylonians. Egyptians. Hebrews. The world remembers their pyramids and forgets their faces. It studies their laws and erases their complexion. It built its alphabet on their alphabet, its mathematics on their mathematics, its calendar on their calendar — and then it told their children they came from nothing. This is the record they did not want assembled in one place."),
    ("co4", "map-animation",
     "From the Garden of Eden to the libraries of Timbuktu. From the first civilization on earth to the last great Black empires of West Africa. This is the journey of a people the Scriptures call Israel — and the long road that scattered them to the ends of the earth. Sit with me. This is going to take a while. Because the truth always does."),
    ("in1", "study-library",
     "Peace, family, and welcome back to AI Bible Gospels. It has been a minute. And I want you to know — we never stopped. We were preparing. Because some stories you don't post in sixty seconds. Some stories you have to sit down and tell properly, from the beginning, with the receipts on the table. This is that story."),
    ("in2", "map-animation",
     "What you are about to watch is a journey across six thousand years — built on the work of historians, on the testimony of ancient writers like Herodotus and Josephus, and above all on the witness of the Scriptures themselves. We're going to lean heavily on a book that changed how a generation read its own history: From Babylon to Timbuktu, by the historian Rudolph R. Windsor. We'll follow his trail, weigh his arguments, and test them against the text — because that is what serious students of the Word are supposed to do."),
    ("in3", "map-animation",
     "Here is the claim we are going to examine, and it is a bold one. That civilization itself — the very first of it — began among dark-skinned peoples of the ancient Near East and Africa. That the patriarchs, the prophets, the kings of Israel, and the surrounding nations of the Bible were a melanated people. That after the great scatterings — by Assyria, by Babylon, by Rome, and finally by the slave ships — the descendants of Israel did not vanish. They walked into Africa. They built empires. And they were carried across an ocean."),
    ("in4", "golden-ambient",
     "Now hear me clearly, because this matters. Some of what we cover is settled history that any honest scholar will confirm. Some of it is interpretation — a thesis, an argument that not everyone accepts. I'm going to tell you which is which as we go. I'm not here to sell you certainty. I'm here to put the evidence in front of you and let the Spirit and your own mind do the rest. As the Scripture says, Prove all things; hold fast that which is good."),
    ("in5", "golden-ambient",
     "So whatever you came in believing, do me one favor: stay till the end. Because the last chapter of this — the part about what happened to these people, and what the prophets said would happen to them — is the part that changes everything. Let's begin where everything began. Let's begin in the garden."),
    ("p1", "golden-ambient",
     "Part One. Ancient Black Civilization."),
    ("p2", "ancient-river",
     "More than six thousand years ago, in a land the Greeks would later call Mesopotamia — the land between the rivers — something happened that had never happened before on this planet. People stopped wandering. They settled. They dug canals and raised cities of brick. They invented writing, and law, and the wheel, and the measurement of time. They looked up at the stars and began to map them. This was not a small step. This was the beginning of the human story as we know it."),
    ("p3", "ancient-river",
     "The two rivers were the Tigris and the Euphrates. They rise in the mountains of Armenia and run southeast toward the Persian Gulf, and the land they water is so rich with the silt they carry that the ancients struggled to describe it. The Scriptures don't struggle. The Scriptures tell us exactly what was planted there."),
    ("p4", "golden-ambient",
     "Open the book of Genesis, the second chapter. And a river went out of Eden to water the garden; and from thence it was parted, and became into four heads. Four rivers. And the writer of Genesis, thousands of years ago, names them — and in naming them, he hands us a map."),
    # NOTE: the clone voices "Hiddekel" roughly as "Hittacle" in this sentence context; a
    # phonetic respelling didn't help in-context (context-dependent), so we keep the canonical
    # spelling. The caption is restored to "Hiddekel" by the assembler's caption_glossary.
    # Audio for this one obscure river name stays slightly off — acceptable for v1.
    ("p5", "golden-ambient",
     "Listen to the third and fourth, because they're the ones we can still find on a map today. Genesis chapter two, verse fourteen: And the name of the third river is Hiddekel; that is it which goeth toward the east of Assyria. And the fourth river is Euphrates. Hiddekel is the ancient name of the Tigris. The Euphrates still runs by that name today. So already we are not in a fairy tale. We are standing in southern Iraq, in the cradle of civilization, exactly where the archaeologists dig."),
    ("p6", "golden-ambient",
     "Now go back one verse, to the second river, and watch what the text does. Genesis chapter two, verse thirteen: And the name of the second river is Gihon: the same is it that compasseth the whole land of Ethiopia. Ethiopia. The land the Hebrews called the land of Cush. And that single word is a thread — pull it, and the whole tapestry of the ancient world begins to move."),
    ("p7", "vision-divine",
     "Because in the Bible's own geography, the garden — the seedbed of humanity — is tied directly to the land of Cush, the land of the dark-skinned peoples. This is the argument Windsor presses, and he's not alone in it. The great medieval commentator Rashi, writing in the eleventh century, identified that river Gihon with the Nile, the river that runs through Ethiopia and Egypt. The association is old, and it is in the text."),
    ("p8", "study-library",
     "So who were these first people? The Bible gives us a genealogy, and it is one of the most important and most ignored chapters in all of Scripture: Genesis chapter ten. The Table of Nations. The family tree of the whole human race after the flood."),
    ("p9", "throne-royal",
     "It tells us this: And Cush begat Nimrod: he began to be a mighty one in the earth. Cush — whose very name, scholars agree, means black, or burnt-faced; it is the Hebrew word for the Ethiopian peoples. And Cush is the father of Nimrod, the first empire-builder named in the Bible. The text says Nimrod's kingdom began in the land of Shinar — and it names the cities. Babel. Erech. Accad. Babylon itself."),
    ("p10", "throne-royal",
     "Sit with the weight of that. The Bible says the first great kingdom on earth — the first cities, the first empire — was founded by the son of Cush. By the line the Hebrews themselves identified as the dark-skinned, Ethiopian peoples. The builders of Babylon, in the Bible's own reckoning, were a Black people."),
    ("p11", "study-library",
     "And this is where the historians and the archaeologists meet the text. The civilization beneath Babylon — older than Babylon — was Sumer. The Sumerians called themselves, in their own language, the black-headed people. Their oldest cities — Eridu, Lagash, Ur, Kish — were already ancient when Babylon was young. And when archaeologists opened the graves of Ur and Kish, the skeletal remains they found, and the statues those people carved of themselves, pointed again and again to a kinship with the dark-skinned peoples of the Nile and of the Indus valley in India — the people history calls the Dravidians. A belt of related dark-skinned civilization, Windsor argues, stretching from Africa across Arabia to India."),
    ("p12", "study-library",
     "And we should linger on just how much the whole world owes to that first Mesopotamian flowering, because nearly every foundation stone of civilized life was laid right there. The first true writing on earth — wedge-shaped marks pressed into wet clay, what we call cuneiform — was invented in Sumer. The first wheel turned there. The first great cities rose there. The first written codes of law, the first schools, the first works of epic literature — every one of these began among the dark-skinned people between the two rivers. So hear it in plain terms: when you write your name, when you read a story, when you check the time, when you live under written law inside a city, you are living inside an inheritance handed down from ancient Sumer. They did not merely build a civilization. They built the very idea of civilization, and every people who came after has been borrowing from it ever since."),
    ("p13", "map-animation",
     "And do not miss whose family the Bible draws out of exactly this place. When Scripture introduces Abraham — the father of Israel, the father of the faithful — it does not set him down in some distant, separate land. It says plainly that he came up out of Ur of the Chaldees. Ur — one of the greatest cities of ancient Sumer, sitting in the very heart of this valley. The father of the entire Hebrew nation was born in the cradle of the world's first civilization, among the dark-skinned founders of the human story. Tuck that away, because in a few chapters we are going to pull on that single thread, and watch the whole tapestry move."),
    ("p14", "golden-ambient",
     "Now, was every individual in ancient Mesopotamia uniformly one complexion? No serious person claims that — the ancient Near East was a crossroads. But the founding stock, the oldest layer, the people who lit the first lamp of civilization in that valley — the evidence says they were a dark and melanated people. And the Bible, in Genesis ten, says the same thing in the only language it had: it traces them to Cush. Here is something else the ancients understood that we have forgotten. They did not file people by skin color. That is a modern invention. The Egyptians, the Greeks, the Romans — they identified men by nation and by tribe. The idea of sorting all of humanity into a white column and a black column the way we do today — that did not exist in the ancient world. So when an ancient writer doesn't stop to tell you a man was Black, it is often because, in that part of the world, in that age, it did not need saying. It was the assumption."),
    ("p15", "desert-wind",
     "The name Ethiopia itself is a key, and Windsor makes a sharp observation here. There was not only the Ethiopia of Africa that we know today. The ancient writers spoke of an eastern Ethiopia as well — a Cushite presence on the Asian side, around the Persian Gulf, in the very region of the garden. Two Ethiopias. One in Africa, one in Asia. And the people of that eastern land did not go around calling themselves the Ethiopians. They named themselves after their cities and their works. After they built the tower and their language was confused at Babel — Babel, which in Hebrew means confusion — they became known as Babylonians, after the city. That is how nations have always worked. A people is so often known not by its bloodline, but by its address."),
    ("p16", "golden-ambient",
     "So before we go one step further, let's set the foundation plainly, because everything else is built on it. The first civilization on earth rose between the Tigris and the Euphrates. The Bible traces its founders to Cush — to the dark-skinned, Ethiopian line of Noah's grandson. The people called themselves the black-headed ones. And from this single valley, the light of civilization — writing, law, the calendar, the city itself — would spread to the entire world, including, one day, to a Europe that was at that moment still living in the Stone Age."),
    ("p17", "void-opening",
     "Hold onto that picture: a dark and brilliant people, standing at the headwaters of history. Because the next question is the one that breaks the whole story open. If the first people were a dark people… then where did the rest of us come from? Where, exactly, did the white race begin? That is Part Two."),
]

NONFIG_DIR = "output/clips/eden-part1"
FIG_DIR = "output/clips/eden-part1-figures"


def build():
    scenes = []
    for sid, mood, narration in SCENES:
        clip_path = f"{FIG_DIR}/{sid}.mp4" if sid in FIGURE_IDS else f"{NONFIG_DIR}/{sid}.mp4"
        sfx_file = SFX_MOODS.get(mood, {}).get("file")
        scenes.append({
            "scene_id": sid,
            "clip_path": clip_path,
            "narration_text": narration,
            "sfx": {"file": sfx_file, "volume": 0.12, "mood": mood},
            "is_figure": sid in FIGURE_IDS,
        })
    manifest = {
        "topic": "eden-part1",
        "title": "From Eden to Timbuktu: The Hidden History of the Black Hebrews — Part 1",
        "aspect": "16x9",
        "voice_id": VOICE_ID,
        "voice_speed": VOICE_SPEED,
        "scenes": scenes,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    words = sum(len(n.split()) for _, _, n in SCENES)
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"  {len(scenes)} scenes · {words} narration words (~{words/150:.1f} min @150wpm)")
    print(f"  figure scenes: {sorted(FIGURE_IDS)}")


if __name__ == "__main__":
    build()
