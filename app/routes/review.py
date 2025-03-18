from fastapi import Depends, APIRouter, UploadFile, File, Form
from app.database import get_db
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
        200: {
            'model': Status,
            "description": "Status of adding new object to db"
        }
    }
)
async def add_review(
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
        db: Session = Depends(get_db)
):
    base_path = "static"
    image_ext = path.splitext(image.filename)[-1]
    image_name = uuid.uuid4().hex
    image_path = path.join(base_path, image_name + image_ext)
    async with aiofiles.open(image_path, "wb") as file:
        contents = await image.read()
        await file.write(contents)
    return await insert_review(db, image_name, user_id, problem, text)
