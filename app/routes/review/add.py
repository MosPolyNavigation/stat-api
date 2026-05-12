import os
import uuid
import aiofiles

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException

from app.database import get_db
from app.config import get_settings
from app.handlers import insert_review
from app.schemas import Status, Problem
from app.guards.file_checker import image_validator
from app.guards.review_governor import review_rate_limiter


def register_endpoint(router: APIRouter):
    @router.post(
        "/add",
        description="Эндпоинт для добавления отзывов",
        response_model=Status,
        tags=["review"],
        dependencies=[Depends(review_rate_limiter)],
        responses={
            500: {
                'model': Status,
                'description': "Server side error",
                'content': {
                    "application/json": {
                        "example": {"status": "Some error"}
                    }
                }
            },
            404: {
                'model': Status,
                'description': "Item not found",
                'content': {
                    "application/json": {
                        "example": {"status": "User not found"}
                    }
                }
            },
            413: {
                'model': Status,
                'description': "File or text too large",
                'content': {
                    "application/json": {
                        "example": {"status": "Image too large"}
                    }
                }
            },
            415: {
                'model': Status,
                'description': "Unsupported Media Type",
                'content': {
                    "application/json": {
                        "example": {"status": "This endpoint accepts only images"}
                    }
                }
            },
            200: {
                'model': Status,
                "description": "Status of adding new object to db"
            },
            429: {
                "description": "Too many requests",
                'content': {
                    "application/json": {
                        "example": {
                            "detail":
                                "Too many requests for this user within one second"
                        }
                    }
                }
            }
        }
    )
    async def add_review(
            image: Optional[UploadFile] = Depends(image_validator),
            # TODO: Поменять тип, как фронты перейдут на новую схему событий
            client_id: Optional[str] = Form(
                None,
                title="client_id",
                description="Уникальный идентификатор клиента",
                min_length=36,
                max_length=36,
                pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}"
            ),
            # TODO: Удалить, как фронты перейдут на новую схему событий
            user_id: Optional[str] = Form(None, min_length=36, max_length=36),
            problem: Problem = Form(
                title="problem",
                description="User problem",
                json_schema_extra={
                    "type": "string",
                    "pattern": r"way|other|plan|work"
                }
            ),
            text: str = Form(
                title="text",
                description="User review",
                min_length=1,
                max_length=5000
            ),
            db: AsyncSession = Depends(get_db),
    ):
        # TODO: Удалить, как фронты перейдут на новую схему событий
        if client_id is None and user_id is not None:
            client_id = user_id
        # TODO: Удалить, как фронты перейдут на новую схему событий
        if client_id is None:
            raise HTTPException(
                status_code=422,
                detail=f"Validation failed"
            )

        base_path: str = os.path.join(get_settings().static_files, "images")
        image_name: str | None = None

        if (
            image is not None
            and image.content_type is not None
            and image.filename is not None
            and image.content_type.startswith("image/")
        ):
            image_ext = os.path.splitext(image.filename)[-1]
            image_id = uuid.uuid4().hex
            image_name: str = f"{image_id}{image_ext}"
            image_path = os.path.join(base_path, image_name)

            async with aiofiles.open(image_path, "wb") as file:
                contents = await image.read()
                await file.write(contents)
        return await insert_review(db, image_name, client_id, problem, text)
