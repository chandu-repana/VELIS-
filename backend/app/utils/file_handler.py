import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

EXTENSION_TO_TYPE = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".txt": "text/plain",
    ".rtf": "application/rtf",
    ".odt": "application/vnd.oasis.opendocument.text",
}

ALLOWED_TYPES = set(EXTENSION_TO_TYPE.values())


async def save_upload_file(file: UploadFile, subfolder: str = "resumes"):
    content = await file.read()
    file_size = len(content)

    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    filename_lower = (file.filename or "").lower()
    detected_type = None
    detected_ext = None

    for ext, mime in EXTENSION_TO_TYPE.items():
        if filename_lower.endswith(ext):
            detected_type = mime
            detected_ext = ext
            break

    if not detected_type:
        content_type = file.content_type or ""
        if content_type in ALLOWED_TYPES:
            detected_type = content_type
            for ext, mime in EXTENSION_TO_TYPE.items():
                if mime == content_type:
                    detected_ext = ext
                    break
        else:
            detected_ext = ".pdf"
            detected_type = "application/pdf"

    unique_filename = f"{uuid.uuid4().hex}{detected_ext}"
    save_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, unique_filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    logger.info(f"Saved: {file_path} ({file_size} bytes) type={detected_type}")
    return file_path, detected_type
