from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.handlers import insert_changed_plan
from app.schemas import ChangePlanIn, Status


def register_endpoint(router: APIRouter):
    @router.put(
        "/change-plan",
        description="Эндпоинт для добавления смены плана",
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
    async def add_changed_plan(
            data: ChangePlanIn = Body(),
            db: Session = Depends(get_db)
    ):
        """
        Эндпоинт для добавления смены плана.

        Этот эндпоинт добавляет смену плана в базу данных.

        Args:
            data: Данные смены плана;
            db: Сессия базы данных.

        Returns:
            Статус добавления нового объекта в базу данных.
        """
        return await insert_changed_plan(db, data)
