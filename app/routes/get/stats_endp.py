from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.handlers import get_endpoint_stats
from app.schemas import Statistics, Status, FilterQuery


def register_endpoint(router: APIRouter):
    @router.get(
        "/stat",
        description="Эндпоинт для получения статистики по выбранному эндпоинту",
        response_model=Statistics,
        tags=["get"],
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
            }
        }
    )
    async def get_stat(
            query: FilterQuery = Depends(),
            db: Session = Depends(get_db)
    ):
        """
        Эндпоинт для получения статистики по выбранному эндпоинту.

        Этот эндпоинт возвращает статистику.

        Args:
            query: Параметры фильтрации.
            db: Сессия базы данных.

        Returns:
            Statistics: Статистика.
        """
        return await get_endpoint_stats(db, query)
