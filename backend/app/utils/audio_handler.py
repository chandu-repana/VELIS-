import os
import uuid
import aiofiles
import logging
import subprocess
from fastapi import UploadFile, HTTPException, status

logger = logging.getLogger(__name__)

ALLOWED_AUDIO_TYPES = {
    "audio/wav": ".wav",
    "audio/wave": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp4": ".mp4",
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "video/webm": ".webm",
    "application/octet-stream": ".webm"
}

MAX_AUDIO_SIZE_MB = 50


def convert_to_wav(input_path: str) -> str:
    output_path = input_path.rsplit(".", 1)[0] + "_converted.wav"
    try:
        result = subprocess.run([
            "ffmpeg", "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            output_path
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0 and os.path.exists(output_path):
            logger.info(f"Converted to WAV: {output_path}")
            return output_path
        else:
            logger.warning(f"FFmpeg failed: {result.stderr[:200]}")
            return input_path
    except Exception as e:
        logger.warning(f"Conversion failed, using original: {e}")
        return input_path


async def save_audio_file(file: UploadFile, subfolder: str = "responses") -> str:
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty"
        )

    max_bytes = MAX_AUDIO_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio too large. Max {MAX_AUDIO_SIZE_MB}MB"
        )

    content_type = file.content_type or "application/octet-stream"
    ext = ALLOWED_AUDIO_TYPES.get(content_type, ".webm")

    unique_filename = f"{uuid.uuid4().hex}{ext}"
    save_dir = os.path.join("audio", subfolder)
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, unique_filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    logger.info(f"Audio saved: {file_path} ({len(content)} bytes)")
    converted_path = convert_to_wav(file_path)
    return converted_path
