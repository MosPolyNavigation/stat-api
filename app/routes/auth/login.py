from datetime import datetime, timezone
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Cookie, Form, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pwdlib import PasswordHash
from pydantic import BaseModel
from app.database import get_db
from app.models.auth.user import User
from app.helpers.auth_utils import get_current_active_user
from app.helpers.permissions import group_rights_by_goals
from app.schemas import UserOut
from app.services.permission_service import PermissionService
from app.helpers.token_utils import REFRESH_COOKIE_NAME, clear_refresh_cookie, create_access_token, create_refresh_token_session, decode_refresh_token, hash_token_value, normalize_token_error, set_refresh_cookie, validate_refresh_payload, get_refresh_session
from app.schemas.auth import AuthScheme

# Будет использоваться рекомендуемый алгоритм хэширования паролей
password_hash = PasswordHash.recommended()


class Token(BaseModel):
    """Схема ответа при выдаче токена"""

    access_token: str
    token_type: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """проверка введённого пароля"""
    """метод verify проверяет, совпадает ли введённый пароль с хэшированным.
    Метод автоматически определяет алгоритм, использованный при хэшировании."""
    return password_hash.verify(plain_password, hashed_password)


# Пока что нигде не используется (создание пароля)
# def get_password_hash(password):
#     """Создание хэша пароля"""
#     return password_hash.hash(password)


async def get_user_by_login(db: AsyncSession, login: str) -> Optional[User]:
    """Получить пользователя по логину"""
    return (await db.execute(select(User).filter_by(login=login))).scalar()


async def authenticate_user(db: AsyncSession, login: str, password: str) -> Optional[User]:
    """проверка, существует ли пользователь и правильный ли пароль"""
    user = await get_user_by_login(db, login)
    if not user or not verify_password(password, user.hash):
        return None
    return user


# Создаёт refresh сессию и устанавливает refresh токен в cookie
async def issue_refresh_token(
    user: User,
    db: AsyncSession,
    request: Request,
    response: Response,
    user_ip: str | None = None,
) -> None:
    refresh_token, _ = await create_refresh_token_session(
        user=user,
        db=db,
        request=request,
        user_ip=user_ip,
    )
    set_refresh_cookie(response, request, refresh_token)




def register_endpoint(router: APIRouter):
    """Эндпоинт для аутентификации и выдачи токена пользователя"""

    @router.post(
        "/token",
        description="Эндпоинт для получения токена аутентификации",
        response_model=Token,
        tags=["auth"],
    )
    async def login(
            request: Request,
            response: Response,
            form_data: Annotated[AuthScheme, Form()],
            db: AsyncSession = Depends(get_db)
    ):
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Некорректный логин или пароль")

        access_token = await create_access_token(user, db)

        if form_data.scope == "long":
            await issue_refresh_token(
                user=user,
                db=db,
                request=request,
                response=response,
                user_ip=form_data.user_ip,
            )
            await db.commit()

        return Token(access_token=access_token, token_type="bearer")

    """Эндпоинт для получения данных пользователя по токену"""

    @router.get(
        "/me",
        description="Эндпоинт для получения данных текущего пользователя по токену",
        response_model=UserOut,
        tags=["auth"],
    )
    async def read_users_me(
            current_user: Annotated[User, Depends(get_current_active_user)],
            db: AsyncSession = Depends(get_db),
    ):
        """Возвращает актуальные данные текущего пользователя"""
        await db.refresh(current_user)
        service: PermissionService = PermissionService(db)

        result = UserOut(
            id=current_user.id,
            login=current_user.login,
            is_active=current_user.is_active
        )
        rights_goals = await service.get_user_permissions(current_user.id)
        result.rights_by_goals = group_rights_by_goals(rights_goals)
        return result

    """Эндпоинт для обновления пары токенов по refresh cookie"""

    @router.post(
        "/refresh",
        description="Эндпоинт для обновления пары токенов по refresh cookie",
        response_model=Token,
        tags=["auth"],
    )
    async def refresh(
            request: Request,
            response: Response,
            db: AsyncSession = Depends(get_db),
            user_ip: str | None = Form(default=None),
            refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
    ):
        # Refresh токен должен приходить в cookie
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh токен отсутствует")

        try:
            # Проверка подписи refresh токена и извлечение данных из payload
            payload = decode_refresh_token(refresh_token)
            user_id, raw_jti = validate_refresh_payload(payload)
        except Exception as exc:
            clear_refresh_cookie(response, request)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=normalize_token_error(exc, refresh=True),
            ) from exc

        # Ищем активную refresh сессию в БД
        session = await get_refresh_session(db, user_id, raw_jti)
        if not session or session.revoked:
            clear_refresh_cookie(response, request)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Refresh сессия не найдена или отозвана")

        # Если refresh сессия истекла, помечаем её отозванной
        if session.exp_date <= datetime.now(timezone.utc).replace(tzinfo=None):
            session.revoked = True
            await db.commit()
            clear_refresh_cookie(response, request)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Срок действия refresh токена истёк")

        # Получаем пользователя, которому принадлежит refresh токен
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
        if not user:
            session.revoked = True
            await db.commit()
            clear_refresh_cookie(response, request)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

        # Refresh токены выдаются только активным пользователям
        if not user.is_active:
            session.revoked = True
            await db.commit()
            clear_refresh_cookie(response, request)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неактивный пользователь")

        # Ротация refresh токена: старую сессию отзываем
        session.revoked = True

        # Выдаём новый access токен
        access_token = await create_access_token(user, db)

        # Создаём новую refresh сессию и обновляем cookie
        await issue_refresh_token(
            user=user,
            db=db,
            request=request,
            response=response,
            user_ip=user_ip if user_ip is not None else session.user_ip,
        )
        await db.commit()

        return Token(access_token=access_token, token_type="bearer")
