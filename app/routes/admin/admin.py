# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import Status
from app.schemas.ban import BanListOut, BanInfoOut, UnbanRequest
from app.guards.review_governor import review_rate_limiter
from app.state import AppState
from app.helpers.auth_utils import get_current_active_user


def register_endpoint(router: APIRouter):
    @router.get(
        "/review-bans",
        description="Получение списка забаненных пользователей для отзывов",
        response_model=BanListOut,
        tags=["admin"],
        dependencies=[Depends(get_current_active_user)],
        responses={
            200: {"model": BanListOut, "description": "Список забаненных пользователей"},
            401: {"description": "Требуется аутентификация"},
            403: {"description": "Недостаточно прав"},
        },
    )
    async def get_banned_users(
        request: Request,
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(100, ge=1, le=500, description="Размер страницы"),
    ):
        """
        Возвращает пагинированный список пользователей, забаненных
        за нарушения при отправке отзывов.
        """
        offset = (page - 1) * size
        result = review_rate_limiter.get_banned_users(
            state=request.app.state,
            limit=size,
            offset=offset,
        )
        return result
    
    @router.get(
        "/review-bans/{user_id}",
        description="Получение информации о бане конкретного пользователя",
        response_model=BanInfoOut,
        tags=["admin"],
        responses={
            200: {"model": BanInfoOut, "description": "Информация о бане"},
            404: {
                "model": Status,
                "description": "Пользователь не найден или не забанен",
                "content": {"application/json": {"example": {"status": "User not banned or not found"}}}
            },
            401: {"description": "Требуется аутентификация"},
            403: {"description": "Недостаточно прав"},
        },
        dependencies=[Depends(get_current_active_user)],
    )
    async def get_user_ban_info(
        user_id: str,
        request: Request,
    ):
        """
        Возвращает детальную информацию о бане пользователя.
        """
        info = review_rate_limiter.get_user_ban_info(
            state=request.app.state,
            user_id=user_id,
        )
        if info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not banned or not found",
            )
        return info
    
    @router.post(
        "/review-bans/{user_id}/unban",
        description="Снятие бана с пользователя",
        response_model=Status,
        tags=["admin"],
        responses={
            200: {
                "model": Status,
                "content": {"application/json": {"example": {"status": "User unbanned successfully"}}}
            },
            404: {
                "model": Status,
                "content": {"application/json": {"example": {"status": "User not found or not banned"}}}
            },
            401: {"description": "Требуется аутентификация"},
            403: {"description": "Недостаточно прав"},
        },
        dependencies=[Depends(get_current_active_user)],
    )
    async def unban_user(
        rq: Request,
        user_id: str,
        request: UnbanRequest = None,
    ):
        """
        Снимает перманентный бан с пользователя.
        """
        success = review_rate_limiter.unban_user(
            state=rq.app.state,
            user_id=user_id,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or not banned",
            )
        
        # Опционально: логирование для аудита
        reason = request.reason if request and request.reason else "No reason provided"
        # logger.info(f"Admin unbanned user {user_id}: {reason}")
        
        return Status(status="User unbanned successfully")
