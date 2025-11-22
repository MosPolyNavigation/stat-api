import strawberry
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info
from typing import Optional
from .filter_handlers import _validated_limit
from .permissions import ensure_stats_view_permission
from .user_id import UserIdType, _to_user_id
from app.models import ChangePlan


@strawberry.type
class ChangePlanType:
    id: int
    user_id: str
    plan_id: str
    visit_date: datetime
    user: Optional[UserIdType]


def _to_change_plan(model: ChangePlan) -> ChangePlanType:
    return ChangePlanType(
        id=model.id,
        user_id=model.user_id,
        plan_id=model.plan_id,
        visit_date=model.visit_date,
        user=_to_user_id(model.user)
    )


async def resolve_change_plans(
    info: Info,
    user_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    limit: Optional[int] = None
) -> list[ChangePlanType]:
    session: AsyncSession = ensure_stats_view_permission(info)
    statement = (
        select(ChangePlan)
        .options(selectinload(ChangePlan.user))
        .order_by(ChangePlan.visit_date.desc())
    )
    if user_id:
        statement = statement.where(ChangePlan.user_id == user_id)
    if plan_id:
        statement = statement.where(ChangePlan.plan_id == plan_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = (await session.execute(statement)).scalars().all()
    return [_to_change_plan(record) for record in records]
