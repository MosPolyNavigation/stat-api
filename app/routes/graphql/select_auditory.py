from datetime import datetime
import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info
from typing import Optional
from .filter_handlers import _validated_limit
from .permissions import ensure_stats_view_permission
from .user_id import UserIdType, _to_user_id
from app.models import SelectAuditory


@strawberry.type
class SelectAuditoryType:
    id: int
    user_id: str
    auditory_id: str
    success: bool
    visit_date: datetime
    user: Optional[UserIdType]


def _to_select_auditory(model: SelectAuditory) -> SelectAuditoryType:
    return SelectAuditoryType(
        id=model.id,
        user_id=model.user_id,
        auditory_id=model.auditory_id,
        success=model.success,
        visit_date=model.visit_date,
        user=_to_user_id(model.user)
    )


async def resolve_select_auditories(
    info: Info,
    user_id: Optional[str] = None,
    success: Optional[bool] = None,
    limit: Optional[int] = None
) -> list[SelectAuditoryType]:
    session: AsyncSession = await ensure_stats_view_permission(info)
    statement = (
        select(SelectAuditory)
        .options(selectinload(SelectAuditory.user))
        .order_by(SelectAuditory.visit_date.desc())
    )
    if user_id:
        statement = statement.where(SelectAuditory.user_id == user_id)
    if success is not None:
        statement = statement.where(SelectAuditory.success.is_(success))
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = (await session.execute(statement)).scalars().all()
    return [_to_select_auditory(record) for record in records]
