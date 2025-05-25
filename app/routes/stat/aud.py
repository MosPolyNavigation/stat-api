from fastapi import APIRouter, Depends, Body, Request, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import Status, SelectedAuditoryIn
from app.handlers import check_user, insert_aud_selection


def register_endpoint(router: APIRouter):
    @router.put(
        "/select-aud",
        description="Эндпоинт для добавления выбора аудитории",
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
            },
            429: {
                'model': Status,
                "description": "Too many requests",
                'content': {
                    "application/json": {
                        "example": {
                            "status":
                                "Too many requests for this user within one second"
                        }
                    }
                }
            }
        }
    )
    async def add_selected_aud(
            request: Request,
            response: Response,
            data: SelectedAuditoryIn = Body(),
            db: Session = Depends(get_db),
    ):
        """
        Эндпоинт для добавления выбора аудитории.

        Этот эндпоинт добавляет выбор аудитории в базу данных.

        Args:
            request: Запрос;
            response: Ответ;
            data: Данные выбора аудитории;
            db: Сессия базы данных.

        Returns:
            Status: Статус добавления нового объекта в базу данных.
        """
        state = request.app.state
        if check_user(state, data.user_id) < 1:
            response.status_code = 429
            return Status(
                status="Too many requests for this user within one second"
            )
        return await insert_aud_selection(db, data)
