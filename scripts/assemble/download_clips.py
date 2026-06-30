"""Download Kling MP4 clips in parallel before TTS starts (signed URLs expire)."""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
MIN_SIZE_BYTES = 100 * 1024  # 100 KB sanity floor


def _resolve_local(scene_id: str, clip_path: str) -> Path:
    """Resolve a local archival/stock clip path (absolute, or relative to repo root)."""
    p = Path(clip_path)
    if not p.is_absolute():
        p = ROOT / clip_path
    p = p.resolve()
    if not p.exists():
        raise RuntimeError(f"clip_path for scene {scene_id} not found: {p}")
    size = p.stat().st_size
    if size < MIN_SIZE_BYTES:
        raise RuntimeError(f"Local clip for scene {scene_id} too small ({size} bytes): {p}")
    print(f"  [{scene_id}] local clip {size / (1024*1024):.1f} MB <- {p.name}")
    return p


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
            # Local archival/stock clip — use in place, no download (source of truth).
            if scene.get("clip_path"):
                results[sid] = _resolve_local(sid, scene["clip_path"])
                continue
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
