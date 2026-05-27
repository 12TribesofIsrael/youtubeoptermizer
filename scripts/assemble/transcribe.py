"""Transcribe narration MP3s with per-word timestamps using faster-whisper."""
from pathlib import Path

from faster_whisper import WhisperModel

_model: WhisperModel | None = None


def _get_model(model_size: str = "base") -> WhisperModel:
    global _model
    if _model is None:
        print(f"Loading Whisper {model_size} model...")
        _model = WhisperModel(model_size, device="cpu", compute_type="int8")
        print("Whisper loaded.\n")
    return _model


def transcribe(
    audio_path: Path,
    model_size: str = "base",
) -> list[dict]:
    """
    Transcribe an MP3 and return per-word timing as list of
    {word: str, start: float, end: float}.

    VAD disabled so word offsets align with the muxed audio from t=0.
    Upgrade model_size to 'small.en' if KJV proper-noun timing is poor.
    """
    model = _get_model(model_size)
    segments_iter, _ = model.transcribe(
        str(audio_path),
        word_timestamps=True,
        vad_filter=False,
        language="en",
    )
    words = []
    for seg in segments_iter:
        if seg.words:
            for w in seg.words:
                words.append({
                    "word": w.word.strip(),
                    "start": round(w.start, 4),
                    "end": round(w.end, 4),
                })
    return words


def transcribe_all(
    scenes: list[dict],
    audio_paths: dict[str, Path],
    model_size: str = "base",
) -> dict[str, list[dict]]:
    """Transcribe all scenes. Returns {scene_id: [{word, start, end}, ...]}."""
    print(f"Transcribing {len(scenes)} narrations (Whisper {model_size})...")
    results: dict[str, list[dict]] = {}
    for scene in scenes:
        sid = scene["scene_id"]
        words = transcribe(audio_paths[sid], model_size)
        print(f"  [{sid}] {len(words)} words")
        results[sid] = words
    print(f"Transcription complete.\n")
    return results
