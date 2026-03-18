import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def transcribe_audio(audio_path: str) -> dict:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        import whisper
        logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL}")
        model = whisper.load_model(settings.WHISPER_MODEL)
        result = model.transcribe(audio_path)
        text = result.get("text", "").strip()
        language = result.get("language", "en")
        logger.info(f"Transcription complete: {len(text)} chars")
        return {
            "text": text,
            "language": language,
            "duration": None
        }
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise


def transcribe_audio_safe(audio_path: str) -> dict:
    try:
        return transcribe_audio(audio_path)
    except Exception as e:
        logger.error(f"Safe transcription failed: {e}")
        return {
            "text": "",
            "language": "en",
            "duration": None,
            "error": str(e)
        }
