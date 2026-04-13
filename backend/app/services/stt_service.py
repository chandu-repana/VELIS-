import os
import logging

logger = logging.getLogger(__name__)

_model = None

NOISE_PHRASES = [
    "you", "the", "a", "i", ".", ",", "thank you", "thanks",
    "um", "uh", "hmm", "ah", "oh", "okay", "ok", "yes", "no",
    "bye", "hi", "hello", "hey", "so", "well", "like", "and"
]


def get_model():
    global _model
    if _model is None:
        import whisper
        logger.info("Loading Whisper small model...")
        _model = whisper.load_model("small")
        logger.info("Whisper small model loaded")
    return _model


def is_valid_transcription(text: str, min_words: int = 4) -> bool:
    if not text or not text.strip():
        return False
    words = [w.strip('.,!?').lower() for w in text.split() if w.strip('.,!?')]
    real_words = [w for w in words if w not in NOISE_PHRASES and len(w) > 1]
    return len(real_words) >= min_words


def transcribe_audio(audio_path: str) -> dict:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    file_size = os.path.getsize(audio_path)
    if file_size < 3000:
        logger.warning(f"Audio file too small: {file_size} bytes")
        return {
            "text": "",
            "language": "en",
            "duration": None,
            "error": "recording_too_short"
        }

    try:
        model = get_model()
        result = model.transcribe(
            audio_path,
            language="en",
            task="transcribe",
            fp16=False,
            temperature=0.0,
            best_of=5,
            beam_size=5,
            condition_on_previous_text=False,
            no_speech_threshold=0.6,
            logprob_threshold=-1.0
        )

        text = result.get("text", "").strip()
        language = result.get("language", "en")

        segments = result.get("segments", [])
        if segments:
            avg_no_speech = sum(s.get("no_speech_prob", 0) for s in segments) / len(segments)
            if avg_no_speech > 0.7:
                logger.warning(f"High no-speech probability: {avg_no_speech}")
                return {"text": "", "language": "en", "duration": None, "error": "no_speech_detected"}

        if not is_valid_transcription(text):
            logger.warning(f"Invalid transcription: '{text}'")
            return {"text": "", "language": "en", "duration": None, "error": "insufficient_speech"}

        logger.info(f"Transcription OK: '{text[:100]}'")
        return {"text": text, "language": language, "duration": None}

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise


def transcribe_audio_safe(audio_path: str) -> dict:
    try:
        return transcribe_audio(audio_path)
    except Exception as e:
        logger.error(f"Safe transcription failed: {e}")
        return {"text": "", "language": "en", "duration": None, "error": str(e)}
