import os

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.schemas import Status
from app.config import get_settings
from app.helpers.errors import LookupException
from app.helpers.path import secure_image_path


def register_endpoint(router: APIRouter):
    @router.get(
        "/image/{image_path}",
        description="Эндпоинт для получения картинок из отзывов",
        response_class=FileResponse,
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
