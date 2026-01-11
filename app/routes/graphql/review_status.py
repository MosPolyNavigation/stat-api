import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import Info
from typing import Optional
from .filter_handlers import _validated_limit
from .permissions import ensure_stats_view_permission
from app.models import ReviewStatus


@strawberry.type
class ReviewStatusType:
    id: int
    name: str


def _to_review_status(review_status: Optional[ReviewStatus]) -> Optional[ReviewStatusType]:
    if review_status is None:
        return None
    return ReviewStatusType(id=review_status.id, name=review_status.name)


async def resolve_review_status(
        info: Info,
        review_status_id: Optional[int] = None,
        limit: Optional[int] = None
) -> list[ReviewStatusType]:
    session: AsyncSession = await ensure_stats_view_permission(info)
    statement = select(ReviewStatus).order_by(ReviewStatus.id)
    if review_status_id:
        statement = statement.where(ReviewStatus.id == review_status_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = (await session.execute(statement)).scalars().all()
    return [_to_review_status(record) for record in records]
