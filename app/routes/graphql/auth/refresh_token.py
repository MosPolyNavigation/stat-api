from typing import List, Optional
from datetime import datetime

import strawberry
from graphql import GraphQLError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info

from app.models import RefreshToken, User
from app.routes.graphql.filter_handlers import (
    _create_pagination_info,
    _validated_limit_2,
    _validated_offset,
)
from app.routes.graphql.pagination import PageInfo, PaginationInfo, PaginationInput
from app.routes.graphql.permissions import ensure_permissions_by_ids
from app.constants import VIEW_RIGHT_ID, REFRESH_TOKEN_GOAL_ID
from app.routes.graphql.user_role.types import UserType
from app.routes.graphql.user_role.user import _to_user_safe
from app.services.refresh_token_service import RefreshTokenService


@strawberry.type
class RefreshTokenType:
    id: int
    user_id: int
    jti: str
    exp_date: datetime
    browser: Optional[str]
    user_ip: Optional[str]
    revoked: bool
    created_at: datetime
    user: Optional[UserType] = None


@strawberry.type
class RefreshTokenConnection:
    nodes: List[RefreshTokenType]
    page_info: PageInfo
    pagination_info: PaginationInfo


@strawberry.input
class RefreshTokenFilterInput:
    user_id: Optional[int] = None
    jti: Optional[str] = None


def _to_refresh_token(model: RefreshToken) -> RefreshTokenType:
    return RefreshTokenType(
        id=model.id,
        user_id=model.user_id,
        jti=model.jti,
        exp_date=model.exp_date,
        browser=model.browser,
        user_ip=model.user_ip,
        revoked=model.revoked,
        created_at=model.created_at,
        user=_to_user_safe(model.user) if model.user else None,
    )


async def resolve_refresh_tokens(
    info: Info,
    pagination: Optional[PaginationInput] = None,
    filter: Optional[RefreshTokenFilterInput] = None,
) -> RefreshTokenConnection:
    """
    Получает refresh-токены с пагинацией и фильтрацией, предварительно проверяя право на просмотр.
    """

    session: AsyncSession = await ensure_permissions_by_ids(
        info,
        [(VIEW_RIGHT_ID, REFRESH_TOKEN_GOAL_ID)],
        "Недостаточно прав для просмотра refresh токенов",
    )

    limit = _validated_limit_2(pagination.limit if pagination else 10)
    offset = _validated_offset(pagination.offset if pagination else 0)

    statement = (
        select(RefreshToken)
        .options(selectinload(RefreshToken.user))
        .order_by(RefreshToken.created_at.desc(), RefreshToken.id.desc())
    )

    count_statement = select(func.count()).select_from(RefreshToken)

    if filter:
        if filter.user_id is not None:
            statement = statement.where(RefreshToken.user_id == filter.user_id)
            count_statement = count_statement.where(RefreshToken.user_id == filter.user_id)

        if filter.jti is not None:
            statement = statement.where(RefreshToken.jti == filter.jti)
            count_statement = count_statement.where(RefreshToken.jti == filter.jti)

    total_count_result = await session.execute(count_statement)
    total_count = total_count_result.scalar() or 0

    if offset > 0:
        statement = statement.offset(offset)
    if limit > 0:
        statement = statement.limit(limit)

    records = (await session.execute(statement)).scalars().all()
    records_count = len(records)

    page_info, pagination_info = _create_pagination_info(
        total_count=total_count,
        offset=offset,
        limit=limit,
        records_count=records_count,
    )

    return RefreshTokenConnection(
        nodes=[_to_refresh_token(record) for record in records],
        page_info=page_info,
        pagination_info=pagination_info,
    )

