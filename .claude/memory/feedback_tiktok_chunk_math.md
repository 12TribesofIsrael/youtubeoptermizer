---
name: TikTok video upload chunk math — last chunk must be ≥ chunk_size
description: TikTok rejects multi-chunk uploads when the last chunk is smaller than chunk_size; use single-chunk for files ≤64 MB, otherwise total_chunks = video_size // chunk_size
type: feedback
---
TikTok's `/v2/post/publish/inbox/video/init/` (and `/v2/post/publish/video/init/`) reject `total_chunk_count` values that produce a last chunk smaller than `chunk_size`. Error returned: `invalid_params: "The total chunk count is invalid"`.

**Why:** TikTok's chunk rule is *not* the standard ceiling-divide pattern. They require **last chunk size ∈ [chunk_size, 2 × chunk_size)**. A 64 MB file with `chunk_size=10MB` and `total_chunks=ceil(64/10)=7` produces a 4 MB last chunk → rejected. Hit on 2026-05-01 during the App Review demo upload; original `scripts/tiktok-post.py` used the wrong formula.

**How to apply** — when computing the chunk plan:
```python
MAX_SINGLE_CHUNK = 64_000_000  # decimal 64 MB stays under TikTok's 64 MiB hard ceiling

def compute_chunk_plan(video_size: int) -> tuple[int, int]:
    if video_size <= MAX_SINGLE_CHUNK:
        return video_size, 1                 # single chunk
    chunk_size = 10_000_000
    total_chunks = video_size // chunk_size  # last chunk absorbs remainder
    return chunk_size, total_chunks
```

Both `init_*_upload()` and the actual byte-streaming function MUST use the same chunk plan — the pre-signed URL is bound to whatever was sent at init time.

`scripts/tiktok-post.py` already carries the fix as of `compute_chunk_plan()` (2026-05-01).
