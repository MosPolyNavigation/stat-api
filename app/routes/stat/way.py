from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.handlers import insert_start_way
from app.schemas import StartWayIn, Status


def register_endpoint(router: APIRouter):
    @router.put(
        "/start-way",
        description="Эндпоинт для добавления начатого пути",
        response_model=Status,
        tags=["stat"],
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
                        "example": {"status": "End auditory not found"}
                    }
                }
            },
            200: {
                'model': Status,
                "description": "Status of adding new object to db"
            }
        }
    )
    async def add_started_way(
            data: StartWayIn = Body(),
            db: Session = Depends(get_db)
    ):
        """
        Эндпоинт для добавления начатого пути.

        Этот эндпоинт добавляет начатый путь в базу данных.

        Args:
            data: Данные начатого пути;
            db: Сессия базы данных.

        Returns:
            Status: Статус добавления нового объекта в базу данных.
        """
        return await insert_start_way(db, data)
