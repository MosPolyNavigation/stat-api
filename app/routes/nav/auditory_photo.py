import os
import uuid
import base64
import aiofiles

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.helpers.errors import LookupException
from app.helpers.path import ALLOWED_EXTENSIONS, secure_image_path
from app.helpers.permissions import require_rights
from app.helpers.thumbnail import create_thumbnail_async
from app.models.nav.aud_photo import AudPhoto
from app.models.nav.auditory import Auditory
from app.schemas import Status
from app.guards.file_checker import photo_validator


def register_endpoint(router: APIRouter):
    @router.post(
        "/auditory/photos/upload",
        tags=["nav"],
        response_model=Status,
        dependencies=[Depends(require_rights("resources", "create"))],
        responses={
            404: {"model": Status, "description": "Auditory not found"},
            415: {"model": Status, "description": "Unsupported Media Type"},
        },
    )
    async def upload_auditory_photos(
        aud_id: str = Form(..., description="Auditory id"),
        photos: list[UploadFile] = Depends(photo_validator),
        db: AsyncSession = Depends(get_db),
    ) -> Status:
        auditory = (
            await db.execute(
                Select(Auditory).filter(Auditory.id_sys == aud_id)
            )
        ).scalar_one_or_none()
        if auditory is None:
            raise HTTPException(status_code=404, detail="Auditory not found")

        base_path = os.path.join(get_settings().static_files, "auditories")
        thumbnail_path = os.path.join(get_settings().static_files, "thumbnails")
        os.makedirs(base_path, exist_ok=True)
        os.makedirs(thumbnail_path, exist_ok=True)

        photos_to_create: list[AudPhoto] = []
        for photo in photos:
            if not photo.content_type or photo.content_type.split("/")[0] != "image":
                raise HTTPException(status_code=415, detail="This endpoint accepts only images")

            ext = os.path.splitext(photo.filename or "")[-1].lower().lstrip(".")
            if not ext or ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=415, detail="Unsupported image extension")

            image_name = f"{uuid.uuid4().hex}.{ext}"
            image_path = os.path.join(base_path, image_name)
            image_link = f"/api/nav/auditory/photos/{image_name}"

            async with aiofiles.open(image_path, "wb") as file:
                contents = await photo.read()
                await file.write(contents)

            # Создаем thumbnail для загруженного изображения
            await create_thumbnail_async(image_path, thumbnail_path)

            photos_to_create.append(
                AudPhoto(
                    aud_id=auditory.id,
                    ext=ext,
                    name=image_name,
                    path=image_path,
                    link=image_link,
                )
            )

        db.add_all(photos_to_create)
        await db.commit()
        return Status(status=f"Uploaded {len(photos_to_create)} image(s)")

    @router.get(
        "/auditory/photos/{image_path}",
        tags=["nav"],
        response_class=FileResponse,
        responses={
            404: {"model": Status, "description": "Image not found"},
        },
    )
    async def get_auditory_photo(image_path: str) -> FileResponse:
        base_path = os.path.join(get_settings().static_files, "auditories")
        sanitized_path = secure_image_path(base_path, image_path)
        if sanitized_path is None:
            raise LookupException("Image")
        return FileResponse(sanitized_path)

    @router.get(
        "/auditory/{aud_id}/photos/links",
        tags=["nav"],
        response_model=list[str],
        responses={
            404: {"model": Status, "description": "Auditory not found"},
        },
    )
    async def get_auditory_photo_links(
        aud_id: str,
        db: AsyncSession = Depends(get_db),
    ) -> list[str]:
        auditory = (
            await db.execute(
                Select(Auditory).filter(Auditory.id_sys == aud_id)
            )
        ).scalar_one_or_none()
        if auditory is None:
            raise HTTPException(status_code=404, detail="Auditory not found")

        photos = await db.execute(
            Select(AudPhoto.link)
            .filter(AudPhoto.aud_id == auditory.id)
            .order_by(AudPhoto.id)
        )
        return list(photos.scalars().all())

    @router.get(
        "/auditory/{aud_id}/thumbnails",
        tags=["nav"],
        response_model=dict[str, str],
        responses={
            404: {"model": Status, "description": "Auditory not found"},
        },
    )
    async def get_auditory_thumbnails(
        aud_id: str,
        db: AsyncSession = Depends(get_db),
    ) -> dict[str, str]:
        """
        Получить все thumbnails для аудитории в виде словаря с base64-кодированными изображениями.

        Args:
            aud_id: ID аудитории
            db: Сессия базы данных

        Returns:
            Словарь вида {"image_name": "base64_encoded_data", ...}

        Example response:
            {
                "abc123.jpg": "iVBORw0KGgoAAAANS...",
                "def456.jpg": "iVBORw0KGgoAAAANS..."
            }
        """
        auditory = (
            await db.execute(
                Select(Auditory).filter(Auditory.id_sys == aud_id)
            )
        ).scalar_one_or_none()
        if auditory is None:
            raise HTTPException(status_code=404, detail="Auditory not found")

        photos = await db.execute(
            Select(AudPhoto.name)
            .filter(AudPhoto.aud_id == auditory.id)
            .order_by(AudPhoto.id)
        )
        photo_names = list(photos.scalars().all())

        thumbnails_dir = os.path.join(get_settings().static_files, "thumbnails")
        result = {}

        for photo_name in photo_names:
            # Заменяем расширение на .jpg для thumbnails
            base_name = os.path.splitext(photo_name)[0]
            thumbnail_name = f"{base_name}.jpg"
            thumbnail_path = os.path.join(thumbnails_dir, thumbnail_name)

            if os.path.exists(thumbnail_path):
                try:
                    async with aiofiles.open(thumbnail_path, "rb") as file:
                        thumbnail_data = await file.read()
                        # Кодируем в base64
                        encoded_data = base64.b64encode(thumbnail_data).decode("utf-8")
                        result[thumbnail_name] = encoded_data
                except Exception as e:
                    # Если не удалось прочитать файл, пропускаем его
                    print(f"Error reading thumbnail {thumbnail_name}: {e}")
                    continue

        return result
