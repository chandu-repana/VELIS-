import os
import uuid
import aiofiles
import logging
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
    "application/octet-stream": ".wav"
}


async def save_audio_file(file: UploadFile, subfolder: str = "responses") -> str:
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty"
        )

    content_type = file.content_type or "application/octet-stream"
    ext = ALLOWED_AUDIO_TYPES.get(content_type, ".wav")

    unique_filename = f"{uuid.uuid4().hex}{ext}"
    save_dir = os.path.join("audio", subfolder)
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, unique_filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    logger.info(f"Audio saved: {file_path} ({len(content)} bytes)")
    return file_path
