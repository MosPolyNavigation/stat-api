from sqlalchemy.orm import Session
from fastapi_pagination import Page
from fastapi import APIRouter, Depends
from fastapi_pagination.ext.sqlalchemy import paginate

from app.models import Review
from app.database import get_db
from app.handlers import filter_by_user
from app.schemas import ReviewOut, Status, Filter


def register_endpoint(router: APIRouter):
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
        return paginate(db, filter_by_user(Review, query))
