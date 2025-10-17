from datetime import datetime
import strawberry
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from strawberry import Info
from typing import Optional
from .filter_handlers import _validated_limit
from .user_id import UserIdType, _to_user_id
from app.models import StartWay


@strawberry.type
class StartWayType:
    id: int
    user_id: str
    start_id: str
    end_id: str
    success: bool
    visit_date: datetime
    user: Optional[UserIdType]


def _to_start_way(model: StartWay) -> StartWayType:
    return StartWayType(
        id=model.id,
        user_id=model.user_id,
        start_id=model.start_id,
        end_id=model.end_id,
        success=model.success,
        visit_date=model.visit_date,
        user=_to_user_id(model.user)
    )


async def resolve_start_ways(
    info: Info,
    user_id: Optional[str] = None,
    success: Optional[bool] = None,
    limit: Optional[int] = None
) -> list[StartWayType]:
    session: Session = info.context["db"]
    statement = (
        select(StartWay)
        .options(selectinload(StartWay.user))
        .order_by(StartWay.visit_date.desc())
    )
    if user_id:
        statement = statement.where(StartWay.user_id == user_id)
    if success is not None:
        statement = statement.where(StartWay.success.is_(success))
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [_to_start_way(record) for record in records]
