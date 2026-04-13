"""
Opens the Meta App Review Testing page in a browser so you can
interact with it manually. Browser stays open until you press Ctrl+C.
"""

import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed.")
    sys.exit(1)

APP_ID = "1452257036358754"
PROFILE_DIR = str(Path.home() / ".meta-playwright-profile")

PAGES = [
    ("Testing Page", f"https://developers.facebook.com/apps/{APP_ID}/review/testing/"),
    ("App Review", f"https://developers.facebook.com/apps/{APP_ID}/review/"),
    ("Use Cases", f"https://developers.facebook.com/apps/{APP_ID}/use_cases/"),
]

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False,
        viewport={"width": 1400, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = context.pages[0] if context.pages else context.new_page()

    # Open Testing page first
    print("Opening Meta Testing page...")
    print("If you need to log in, do that first in the browser.")
    print()

    page.goto(PAGES[0][1])
    page.wait_for_load_state("networkidle", timeout=30000)
    time.sleep(2)

    # Take screenshot
    page.screenshot(path="meta-testing-page.png", full_page=True)
    print("Screenshot saved: meta-testing-page.png")

    # Open the other pages in new tabs
    for name, url in PAGES[1:]:
        tab = context.new_page()
        tab.goto(url)
        print(f"Opened tab: {name}")

    print()
    print("Browser is open with 3 tabs:")
    print("  1. Testing page")
    print("  2. App Review page")
    print("  3. Use Cases page")
    print()
    print("Look for any 'Run Test' or 'Make Test Call' buttons.")
    print("Press Ctrl+C in terminal when done.")
    print()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nClosing browser...")

    context.close()
