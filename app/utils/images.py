import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def _get_upload_dir() -> Path:
    path = Path(settings.MEDIA_DIR) / "products"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _validate_image(file: UploadFile) -> None:
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {settings.ALLOWED_IMAGE_TYPES}",
        )


async def save_product_image(file: UploadFile) -> str:
    _validate_image(file)

    contents = await file.read()

    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_IMAGE_SIZE_MB}MB",
        )

    ext = Path(file.filename or "image.jpg").suffix.lower() or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = _get_upload_dir() / filename

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    relative_path = f"{settings.MEDIA_URL}/products/{filename}"
    return relative_path


def build_image_url(relative_path: str | None) -> str | None:
    if not relative_path:
        return None
    return f"{settings.BASE_URL}{relative_path}"
