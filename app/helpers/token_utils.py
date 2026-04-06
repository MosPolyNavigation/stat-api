from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import uuid
import jwt
from fastapi import Request, Response
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from user_agents import parse

from app.config import get_settings
from app.constants import GOALS_BY_ID, RIGHTS_BY_ID
from app.models.auth.refresh_token import RefreshToken
from app.models.auth.user import User
from app.services.permission_service import PermissionService

ALGORITHM = "HS256"
REFRESH_COOKIE_NAME = "refresh_token"


# Хеширует токен перед сохранением в БД
def hash_token_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

# Преобразует permissions в JSON-сериализуемый список строк для JWT
def build_permissions_claim(permissions: set[tuple[int, int]]) -> list[str]:
    result: list[str] = []
    for right_id, goal_id in sorted(permissions, key=lambda x: (x[1], x[0])):
        right_name = RIGHTS_BY_ID.get(right_id)
        goal_name = GOALS_BY_ID.get(goal_id)
        if not right_name or not goal_name:
            continue
        result.append(f"{goal_name}:{right_name}")
    return result

# Создаёт Access JWT для пользователя
async def create_access_token(user: User, db: AsyncSession) -> str:
    settings = get_settings()
    permission_service = PermissionService(db)

    permissions = await permission_service.get_user_permissions(user.id)
    permissions_claim = build_permissions_claim(permissions)

    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(seconds=settings.access_duration)

    payload = {
        "sub": str(user.id),
        "exp": int(expires_at.timestamp()),
        "iat": int(issued_at.timestamp()),
        "type": "access",
        "permissions": permissions_claim,
    }

    return jwt.encode(payload, settings.access_secret, algorithm=ALGORITHM)


def build_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    settings = get_settings()
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(seconds=settings.refresh_duration)
    raw_jti = str(uuid.uuid4())
    payload = {
        "sub": str(user_id),
        "exp": int(expires_at.timestamp()),
        "iat": int(issued_at.timestamp()),
        "type": "refresh",
        "jti": raw_jti,
    }
    return raw_jti, jwt.encode(payload, settings.refresh_secret, algorithm=ALGORITHM), expires_at


async def create_refresh_token_session(
    user: User,
    db: AsyncSession,
    request: Request,
    client_id: str | None = None,
    user_ip: str | None = None,
) -> tuple[str, RefreshToken]:
    raw_jti, refresh_token, expires_at = build_refresh_token(user.id)

    session = RefreshToken(
        user_id=user.id,
        jti=hash_token_value(raw_jti),
        exp_date=expires_at.replace(tzinfo=None),
        browser=parse_browser(request.headers.get("User-Agent")),
        user_ip=client_id if client_id is not None else user_ip,
        revoked=False,
    )
    db.add(session)
    return refresh_token, session


async def get_refresh_session(db: AsyncSession, user_id: int, raw_jti: str) -> RefreshToken | None:
    hashed_jti = hash_token_value(raw_jti)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.jti == hashed_jti,
        )
    )
    return result.scalar_one_or_none()


def decode_access_token(token: str) -> dict[str, Any]:
    return decode_token(token, get_settings().access_secret)


def decode_refresh_token(token: str) -> dict[str, Any]:
    return decode_token(token, get_settings().refresh_secret)


def decode_token(token: str, secret: str) -> dict[str, Any]:
    return jwt.decode(token, secret, algorithms=[ALGORITHM])


class InvalidAccessTokenError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


def validate_access_payload(payload: dict[str, Any]) -> int:
    if payload.get("type") != "access":
        raise InvalidAccessTokenError("Неверный тип токена")

    subject = payload.get("sub")
    if not subject:
        raise InvalidAccessTokenError("В токене отсутствует идентификатор пользователя")

    try:
        return int(subject)
    except (TypeError, ValueError) as exc:
        raise InvalidAccessTokenError("Некорректный идентификатор пользователя в токене") from exc



def validate_refresh_payload(payload: dict[str, Any]) -> tuple[int, str]:
    if payload.get("type") != "refresh":
        raise InvalidRefreshTokenError("Неверный тип токена")

    subject = payload.get("sub")
    jti = payload.get("jti")
    if not subject or not jti:
        raise InvalidRefreshTokenError("В refresh токене отсутствуют обязательные поля")

    try:
        return int(subject), str(jti)
    except (TypeError, ValueError) as exc:
        raise InvalidRefreshTokenError("Некорректные данные в refresh токене") from exc



def normalize_token_error(exc: Exception, *, refresh: bool = False) -> str:
    if isinstance(exc, ExpiredSignatureError):
        return "Срок действия токена истёк"
    if isinstance(exc, (InvalidTokenError, InvalidAccessTokenError, InvalidRefreshTokenError)):
        if refresh:
            return "Неверный refresh токен"
        return "Неверный access токен"
    return "Ошибка проверки токена"



def parse_browser(user_agent: str | None) -> str | None:
    if not user_agent:
        return None

    ua = parse(user_agent)
    return f"{ua.browser.family} {ua.browser.version_string}".strip()



# def is_secure_request(request: Request) -> bool:
#     forwarded_proto = request.headers.get("X-Forwarded-Proto")
#     if forwarded_proto:
#         return forwarded_proto.lower() == "https"
#     return request.url.scheme.lower() == "https"



def set_refresh_cookie(response: Response, request: Request, refresh_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.refresh_duration,
        expires=settings.refresh_duration,
        path="/",
    )



def clear_refresh_cookie(response: Response, request: Request) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
