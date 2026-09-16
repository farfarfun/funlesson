"""语音转写，复用 funtalk 的 Whisper 封装。"""

from typing import Callable, Optional

from .models import Transcript, TranscriptSegment

_model = None


def _get_model(name: str = "turbo"):
    global _model
    if _model is None:
        from funtalk.asr import WhisperASR

        _model = WhisperASR(name=name)
    return _model


def transcribe(
    audio_path: str,
    *,
    language: str = "ZH",
    model_name: str = "turbo",
    on_progress: Optional[Callable[[float], None]] = None,
) -> Transcript:
    model = _get_model(model_name)
    result = model.transcribe(audio_path, language=language, on_progress=on_progress)
    segments = [
        TranscriptSegment(start=seg["start"], end=seg["end"], text=seg["text"].strip())
        for seg in result.get("segments", [])
    ]
    return Transcript(full_text=result.get("text", "").strip(), segments=segments)
