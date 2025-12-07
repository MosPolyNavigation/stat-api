"""Маршрут создания отзыва с текстом и изображением."""

import os
import uuid
from typing import Optional

import aiofiles
from fastapi import APIRouter, Depends, File, Form, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.handlers import insert_review
from app.schemas import Problem, Status


def register_endpoint(router: APIRouter):
    """Регистрирует ручку `/add` для отправки отзыва."""

    @router.post(
        "/add",
        description="Принимает отзыв пользователя: текст, тип проблемы и изображение.",
        response_model=Status,
        tags=["review"],
        responses={
            500: {
                "model": Status,
                "description": "Server side error",
                "content": {"application/json": {"example": {"status": "Some error"}}},
            },
            404: {
                "model": Status,
                "description": "Item not found",
                "content": {"application/json": {"example": {"status": "User not found"}}},
            },
            415: {
                "model": Status,
                "description": "Unsupported Media Type",
                "content": {"application/json": {"example": {"status": "This endpoint accepts only images"}}},
            },
            200: {
                "model": Status,
                "description": "Status of adding new object to db",
            },
        },
    )
    async def add_review(
        response: Response,
        image: Optional[UploadFile] = File(default=None, description="Изображение с проблемой"),
        user_id: str = Form(
            title="id",
            description="Unique user id",
            min_length=36,
            max_length=36,
            pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
        ),
        problem: Problem = Form(
            title="problem",
            description="Категория проблемы",
            json_schema_extra={"type": "string", "pattern": r"way|other|plan|work"},
        ),
        text: str = Form(title="text", description="Текст отзыва"),
        db: AsyncSession = Depends(get_db),
    ):
        """Сохраняет файл (если он есть) и создает запись отзыва."""
        base_path = os.path.join(get_settings().static_files, "images")
        if image is not None and image.content_type.split("/")[0] == "image":
            image_ext = os.path.splitext(image.filename)[-1]
            image_id = uuid.uuid4().hex
            image_name = image_id + image_ext
            image_path = os.path.join(base_path, image_name)
            async with aiofiles.open(image_path, "wb") as file:
                contents = await image.read()
                await file.write(contents)
        elif image is not None and image.content_type.split("/")[0] != "image":
            response.status_code = 415
            return Status(status="This endpoint accepts only images")
        else:
            image_name = None
        return await insert_review(db, image_name, user_id, problem, text)
