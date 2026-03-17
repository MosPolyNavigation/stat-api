from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers import insert_site_stat
from app.schemas import SiteStatIn, Status
from app.guards.governor import stat_rate_limiter


def register_endpoint(router: APIRouter):
    @router.put(
        "/site",
        description="Эндпоинт для добавления статистики посещений сайта",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(stat_rate_limiter)],
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
                            "detail":
                                "Too many requests for this user within one second"
                        }
                    }
                }
            }
        }
    )
    async def add_site_stat(
            data: SiteStatIn = Body(),
            db: AsyncSession = Depends(get_db)
    ):
        """
        Эндпоинт для добавления статистики посещений сайта.

        Этот эндпоинт добавляет статистику посещений сайта в базу данных.

        Args:
            data: Данные статистики сайта;
            db: Сессия базы данных.

        Returns:
            Status: Статус добавления нового объекта в базу данных.
        """
        return await insert_site_stat(db, data)
