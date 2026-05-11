from fastapi import APIRouter, Depends, HTTPException, status, Query, Request

from app.schemas import Status
from app.schemas.ban import BanListOut, BanInfoOut, UnbanRequest
from app.guards.review_governor import review_rate_limiter
from app.helpers.permissions import require_rights_with_logging
from app.services.user_logger_service import UserLoggerService, get_user_logger_service
from app.models import User


def register_endpoint(router: APIRouter):
    @router.get(
        "/review-bans",
        description="Получение списка забаненных пользователей для отзывов",
        response_model=BanListOut,
        tags=["admin"],
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
        current_user: User = Depends(
            require_rights_with_logging("admin", "view",  error_text="Попытка просмотра без прав",)
        ),
        logger: UserLoggerService = Depends(get_user_logger_service),
    ):
        """
        Возвращает пагинированный список пользователей, забаненных
        за нарушения при отправке отзывов.
        """
        offset = (page - 1) * size
        result = review_rate_limiter.get_banned_users(
            state=request.app.state.app_state,
            limit=size,
            offset=offset,
        )
        logger.log(current_user, "Запрос списка забаненных клиентов")
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
    )
    async def get_user_ban_info(
        user_id: str,
        request: Request,
            current_user: User = Depends(
                require_rights_with_logging(
                    "admin",
                    "view",
                    error_text="Попытка доступа к несуществующей записи/без прав",
                )
            ),
            logger: UserLoggerService = Depends(get_user_logger_service),
    ):
        """
        Возвращает детальную информацию о бане пользователя.
        """
        info = review_rate_limiter.get_user_ban_info(
            state=request.app.state.app_state,
            user_id=user_id,
        )
        if info is None:
            logger.log(current_user, "Попытка доступа к несуществующей записи/без прав")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not banned or not found",
            )

        logger.log(current_user, f"Запрос информации по забаненному клиенту {user_id}")
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
    )
    async def unban_user(
        rq: Request,
        user_id: str,
        _request: UnbanRequest = None,
        current_user: User = Depends(
            require_rights_with_logging("admin", "edit",  error_text="Попытка снятия бана без прав",)
        ),
        logger: UserLoggerService = Depends(get_user_logger_service),
    ):
        """
        Снимает перманентный бан с пользователя.
        """
        success = review_rate_limiter.unban_user(
            state=rq.app.state.app_state,
            user_id=user_id,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or not banned",
            )

        # Опционально: логирование для аудита
        # reason = request.reason if request and request.reason else "No reason provided"
        # logger.info(f"Admin unbanned user {user_id}: {reason}")

        logger.log(current_user, f"Снятие бана с пользователя {user_id}")

        return Status(status="User unbanned successfully")
