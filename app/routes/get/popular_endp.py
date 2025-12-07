"""Маршрут получения популярных аудиторий."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers import get_popular_auds
from app.schemas import Status


def register_endpoint(router: APIRouter):
    """Регистрирует ручку `/popular`."""

    @router.get(
        "/popular",
        tags=["get"],
        response_model=list[str],
        responses={
            500: {
                "model": Status,
                "description": "Server side error",
                "content": {"application/json": {"example": {"status": "Some error"}}},
            },
            200: {
                "description": "Популярные аудитории в порядке убывания",
                "content": {"application/json": {"example": ["a-100", "a-101", "a-103", "a-102"]}},
            },
        },
    )
    async def get_popular(db: AsyncSession = Depends(get_db)) -> JSONResponse:
        """Возвращает отсортированный список id аудиторий."""
        data = await get_popular_auds(db)
        return JSONResponse(data, status_code=200)
