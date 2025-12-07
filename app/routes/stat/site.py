"""Маршрут сохранения статистики по страницам сайта."""

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers import insert_site_stat
from app.schemas import SiteStatIn, Status


def register_endpoint(router: APIRouter):
    """Регистрирует PUT `/site`."""

    @router.put(
        "/site",
        description="Сохраняет обращение пользователя к разделу сайта.",
        response_model=Status,
        tags=["stat"],
        responses={
            500: {
                "model": Status,
                "description": "Server side error",
                "content": {"application/json": {"example": {"status": "Some error"}}},
            },
            404: {
                "model": Status,
                "description": "Item not found",
                "content": {"application/json": {"example": {"status": "User not found"}}},
            },
            200: {
                "model": Status,
                "description": "Status of adding new object to db",
            },
        },
    )
    async def add_site_stat(
        data: SiteStatIn = Body(),
        db: AsyncSession = Depends(get_db),
    ):
        """Добавляет запись о посещении сайта в статистику."""
        return await insert_site_stat(db, data)
