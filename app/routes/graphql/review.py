from datetime import datetime
import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info
from typing import Annotated, Optional
from .filter_handlers import _validated_limit
from .permissions import ensure_reviews_view_permission
from .problem import ProblemType, _to_problem
from .review_status import ReviewStatusType, _to_review_status
from .event_dict import ClientIdType, _to_client_id
from app.models import Review


@strawberry.type
class ReviewType:
    id: int
    client_id: int
    problem_id: str
    status_id: int
    text: str
    image_name: Optional[str]
    creation_date: datetime
    problem: Optional[ProblemType]
    client: Optional[ClientIdType]
    status: Optional[ReviewStatusType]


def _to_review(model: Review) -> ReviewType:
    return ReviewType(
        id=model.id,
        client_id=model.client_id,
        problem_id=model.problem_id,
        status_id=model.review_status_id,
        text=model.text,
        image_name=model.image_name,
        creation_date=model.creation_date,
        problem=_to_problem(model.problem),
        client=_to_client_id(model.client),
        status=_to_review_status(model.review_status)
    )


async def resolve_reviews(
        info: Info,
        client_id: Optional[int] = None,
        review_id: Optional[int] = None,
        problem_id: Optional[str] = None,
        status_id: Annotated[Optional[int], strawberry.argument(name="status_id")] = None,
        limit: Optional[int] = None
) -> list[ReviewType]:
    session: AsyncSession = await ensure_reviews_view_permission(info)
    statement = (
        select(Review)
        .options(
            selectinload(Review.client),
            selectinload(Review.problem),
            selectinload(Review.review_status)
        )
        .order_by(Review.creation_date.desc())
    )
    if client_id is not None:
        statement = statement.where(Review.client_id == client_id)
    if review_id:
        statement = statement.where(Review.id == review_id)
    if problem_id:
        statement = statement.where(Review.problem_id == problem_id)
    if status_id is not None:
        statement = statement.where(Review.review_status_id == status_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = (await session.execute(statement)).scalars().all()
    return [_to_review(record) for record in records]
