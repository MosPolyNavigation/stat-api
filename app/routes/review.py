import os
from fastapi import Depends, APIRouter, UploadFile, File, Form, Response
from fastapi.responses import FileResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page
from app.config import get_settings
from app.database import get_db
from app.helpers.path import secure_image_path
from app.schemas import *
from app.handlers import *
from os import path
import aiofiles
import uuid

router = APIRouter(
    prefix="/api/review"
)

@router.post(
    "/add",
    description="Эндпоинт для добавления отзывов",
    response_model=status.Status,
    tags=["review"],
    responses={
        500: {
            'model': status.Status,
            'description': "Server side error",
            'content': {
                "application/json": {
                    "example": {"status": "Some error"}
                }
            }
        },
        404: {
            'model': status.Status,
            'description': "Item not found",
            'content': {
                "application/json": {
                    "example": {"status": "User not found"}
                }
            }
        },
        415: {
            'model': status.Status,
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
        image: Optional[UploadFile] = File(default=None,
                                           description="User image with problem"),
        user_id: str = Form(title="id",
                            description="Unique user id",
                            min_length=36,
                            max_length=36,
                            pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}"),
        problem: Problem = Form(title="problem",
                                description="User problem",
                                json_schema_extra={"type": "string", "pattern": r"way|other|plan|work"}),
        text: str = Form(title="text",
                         description="User review"),
        db: Session = Depends(get_db),
):
    base_path = path.join(get_settings().static_files, "images")
    if image is not None and image.content_type.split("/")[0] == "image":
        image_ext = path.splitext(image.filename)[-1]
        image_id = uuid.uuid4().hex
        image_name = image_id + image_ext
        image_path = path.join(base_path, image_name)
        async with aiofiles.open(image_path, "wb") as file:
            contents = await image.read()
            await file.write(contents)
    elif image is not None and image.content_type.split("/")[0] != "image":
        response.status_code = 415
        return Status(status="This endpoint accepts only images")
    else:
        image_name = None
    return await insert_review(db, image_name, user_id, problem, text)

@router.get(
    "/get",
    description="Эндпоинт для получения отзывов",
    response_model=Page[ReviewOut],
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
        403: {
            'model': Status,
            'description': "Api_key validation error",
            'content': {
                "application/json": {
                    "example": {"status": "no api_key"}
                }
            }
        },
        200: {
            'model': Page[ReviewOut],
            "description": "List of found data"
        }
    }
)
async def get_reviews(
    query: Filter = Depends(),
    db: Session = Depends(get_db)
) -> Page[ReviewOut]:
    """
    Эндпоинт для получения отзывов.

    Этот эндпоинт возвращает список найденных данных.

    Args:
        query: Параметры фильтрации.
        db: Сессия базы данных.

    Returns:
        Page[ReviewOut]: Страница с найденными данными.
    """
    return paginate(db, filter_by_user(models.Review, query))


@router.get(
    "/image/{image_path}",
    description="Эндпоинт для получения картинок из отзывов",
    response_class=FileResponse,
    tags=["review"],
    responses={
        500: {
            'model': status.Status,
            'description': "Server side error",
            'content': {
                "application/json": {
                    "example": {"status": "Some error"}
                }
            }
        },
        404: {
            'model': status.Status,
            'description': "Item not found",
            'content': {
                "application/json": {
                    "example": {"status": "Image not found"}
                }
            }
        },
        200: {
            'content': {
                "image/png": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                },
                "image/jpeg": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                },
            },
            "description": "Review image",

        }
    }
)
async def get_image(
        image_path: str
) -> FileResponse:
    base_path = os.path.join(get_settings().static_files, "images")
    sanitized_path = secure_image_path(base_path, image_path)
    if sanitized_path is None:
        raise LookupException("Image")
    return FileResponse(image_path)
