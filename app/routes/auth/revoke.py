from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.helpers.auth_utils import get_current_active_user
from app.models import User
from app.schemas import Status
from app.services.permission_service import PermissionService
from app.services.refresh_token_service import RefreshTokenService




def register_endpoint(router: APIRouter):
    @router.post(
        "/revoke",
        description="Отзывает refresh-токен по JTI",
        response_model=Status,
        tags=["auth"],
        responses={
            400: {"model": Status, "description": "Передан некорректный jti"},
            401: {"model": Status, "description": "Пользователь не авторизован"},
            403: {"model": Status, "description": "Недостаточно прав для отзыва токена"},
            404: {"model": Status, "description": "Refresh-токен не найден"},
        },
    )
    async def revoke_refresh_token(
        jti: str = Body(..., embed=True),
        current_user: Annotated[User, Depends(get_current_active_user)] = None,
        db: AsyncSession = Depends(get_db),
    ) -> Status:
        """
            Отзывает refresh-токен по его jti.
            Если токен принадлежит текущему пользователю, достаточно валидного access token.
            Если токен принадлежит другому пользователю, требуется право refresh_token - edit.
        """
        refresh_token_service = RefreshTokenService(db)

        if not jti.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Передан некорректный jti",
            )

        refresh_token = await refresh_token_service.get_by_jti(jti)
        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refresh-токен не найден",
            )

        if refresh_token.user_id != current_user.id:
            permission_service = PermissionService(db)
            has_permission = await permission_service.check_permission(
                current_user.id,
                "refresh_token",
                "edit",
            )
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав для отзыва токена другого пользователя",
                )

        await refresh_token_service.revoke_token(refresh_token)
        await db.commit()
        return Status()



