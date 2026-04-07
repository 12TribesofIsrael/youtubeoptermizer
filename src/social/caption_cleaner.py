"""Caption cleaner module — extracted from scripts/fix-facebook-captions.py"""

GARBAGE_MARKERS = [
    "Exciting News Alert",
    "[Industry/Topic]",
    "[Web Link]",
    "[Product/Service]",
    "[Describe the benefit",
    "[Benefit 1]",
    "game-changer of 202",
    "InnovationUnleashed",
    "Revolutionize202",
    "magical souls",
    "Wanderlust",
    "TikTok-optimized version",
    "Sure! Here",
    "cutting-edge [",
    "Join our vibrant community of pioneers",
    "transformative journey",
    "limitless possibilities",
    "Embrace the rhythm of wellness",
]


def find_garbage_start(text):
    """Return index where garbage begins, or -1 if none found."""
    for marker in GARBAGE_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            return idx
    return -1


def clean_message(text):
    """Strip AI garbage from message. Returns cleaned version or None if no garbage found."""
    idx = find_garbage_start(text)
    if idx == -1:
        return None
    return text[:idx].rstrip()
