# -*- coding: utf-8 -*-
"""Estimate daily quota usage based on API calls made today."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# YouTube Data API v3 quota costs:
# - videos.list = 1 unit per call
# - videos.update = 50 units per call
# - videos.delete = 50 units per call
# - thumbnails.set = 50 units per call
# - channels.list = 1 unit per call
# - search.list = 100 units per call

print("=" * 60)
print("DAILY QUOTA ESTIMATE — March 17, 2026")
print("=" * 60)
print()

operations = [
    ("export-current-data.py (list_videos)", 3, 1, "videos.list pages"),
    ("thumbnail-priorities.py", 0, 0, "no API calls, reads CSV"),
]

# Today's known API calls
api_used = 3  # ~3 list calls for the export script

print(f"API calls today:")
for desc, calls, cost_each, note in operations:
    total = calls * cost_each
    print(f"  {desc}: {calls} calls × {cost_each} units = {total} units ({note})")

print(f"\nEstimated units used today: ~{api_used}")
print(f"Daily limit: 10,000")
print(f"Remaining: ~{10000 - api_used}")
print()
print("Cost reference:")
print("  videos.list    = 1 unit/call")
print("  videos.update  = 50 units/call")
print("  videos.delete  = 50 units/call")
print("  thumbnails.set = 50 units/call")
print("  search.list    = 100 units/call")
print("  channels.list  = 1 unit/call")
