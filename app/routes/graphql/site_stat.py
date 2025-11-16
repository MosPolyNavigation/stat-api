from datetime import datetime
import strawberry
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from strawberry import Info
from typing import Optional
from .filter_handlers import _validated_limit
from .permissions import ensure_stats_view_permission
from .user_id import UserIdType, _to_user_id
from app.models import SiteStat


@strawberry.type
class SiteStatType:
    id: int
    user_id: str
    visit_date: datetime
    endpoint: Optional[str]
    user: Optional[UserIdType]


def _to_site_stat(model: SiteStat) -> SiteStatType:
    return SiteStatType(
        id=model.id,
        user_id=model.user_id,
        visit_date=model.visit_date,
        endpoint=model.endpoint,
        user=_to_user_id(model.user)
    )


async def resolve_site_stats(
    info: Info,
    user_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    limit: Optional[int] = None
) -> list[SiteStatType]:
    session: Session = ensure_stats_view_permission(info)
    statement = (
        select(SiteStat)
        .options(selectinload(SiteStat.user))
        .order_by(SiteStat.visit_date.desc())
    )
    if user_id:
        statement = statement.where(SiteStat.user_id == user_id)
    if endpoint:
        statement = statement.where(SiteStat.endpoint == endpoint)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [_to_site_stat(record) for record in records]
