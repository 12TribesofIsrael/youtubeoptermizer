"""Download Kling MP4 clips in parallel before TTS starts (signed URLs expire)."""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

MIN_SIZE_BYTES = 100 * 1024  # 100 KB sanity floor


def _download_one(scene_id: str, url: str, out_path: Path, retries: int = 3) -> Path:
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=120, stream=True)
            if r.status_code == 403:
                raise RuntimeError(f"403 Forbidden — signed URL may have expired for scene {scene_id}")
            r.raise_for_status()
            out_path.write_bytes(r.content)
            size = out_path.stat().st_size
            if size < MIN_SIZE_BYTES:
                raise RuntimeError(f"Downloaded clip too small ({size} bytes) — likely an error page")
            print(f"  [{scene_id}] downloaded {size / (1024*1024):.1f} MB -> {out_path.name}")
            return out_path
        except Exception as e:
            if attempt == retries:
                raise
            wait = 2 ** attempt
            print(f"  [{scene_id}] attempt {attempt} failed ({e}), retrying in {wait}s...")
            time.sleep(wait)


def download_all(scenes: list[dict], clips_dir: Path, max_workers: int = 4) -> dict[str, Path]:
    """Download all scene clips in parallel. Returns {scene_id: local_path}."""
    print(f"Downloading {len(scenes)} clips (up to {max_workers} parallel)...")
    results: dict[str, Path] = {}
    futures = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for scene in scenes:
            sid = scene["scene_id"]
            out_path = clips_dir / f"scene_{sid}.mp4"
            if out_path.exists() and out_path.stat().st_size >= MIN_SIZE_BYTES:
                print(f"  [{sid}] already cached, skipping download")
                results[sid] = out_path
                continue
            fut = pool.submit(_download_one, sid, scene["kling_url"], out_path)
            futures[fut] = sid

        for fut in as_completed(futures):
            sid = futures[fut]
            try:
                results[sid] = fut.result()
            except Exception as e:
                raise RuntimeError(f"Failed to download clip for scene {sid}: {e}") from e

    print(f"All {len(results)} clips downloaded.\n")
    return results
