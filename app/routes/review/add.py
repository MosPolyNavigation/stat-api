import os
import uuid
import aiofiles

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Response, UploadFile, File, Form, Depends

from app.database import get_db
from app.config import get_settings
from app.handlers import insert_review
from app.schemas import Status, Problem


def register_endpoint(router: APIRouter):
    @router.post(
        "/add",
        description="Эндпоинт для добавления отзывов",
        response_model=Status,
        tags=["review"],
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
            }
        }
    )
    async def add_review(
            response: Response,
            image: Optional[UploadFile] = File(
                default=None,
                description="User image with problem"
            ),
            user_id: str = Form(
                title="id",
                description="Unique user id",
                min_length=36,
                max_length=36,
                pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}"
            ),
            problem: Problem = Form(
                title="problem",
                description="User problem",
                json_schema_extra={
                    "type": "string",
                    "pattern": r"way|other|plan|work"
                }
            ),
            text: str = Form(title="text",
                             description="User review"),
            db: AsyncSession = Depends(get_db),
    ):
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
