import os
import uuid
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def text_to_speech(text: str, filename: str = None) -> str:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if filename is None:
        filename = f"{uuid.uuid4().hex}.mp3"

    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    audio_path = os.path.join(settings.AUDIO_DIR, filename)

    try:
        from gtts import gTTS
        tts = gTTS(text=text.strip(), lang=settings.TTS_LANGUAGE, slow=False)
        tts.save(audio_path)
        logger.info(f"TTS audio saved: {audio_path}")
        return audio_path
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        raise


def generate_question_audio(question_text: str, question_id: int) -> str:
    filename = f"question_{question_id}_{uuid.uuid4().hex[:8]}.mp3"
    return text_to_speech(question_text, filename)
