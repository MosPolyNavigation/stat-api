from datetime import datetime
import strawberry
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from strawberry import Info
from typing import Optional
from .filter_handlers import _validated_limit
from .problem import ProblemType, _to_problem
from .user_id import UserIdType, _to_user_id
from app.models import Review


@strawberry.type
class ReviewType:
    id: int
    user_id: str
    problem_id: str
    text: str
    image_name: Optional[str]
    creation_date: datetime
    problem: Optional[ProblemType]
    user: Optional[UserIdType]


def _to_review(model: Review) -> ReviewType:
    return ReviewType(
        id=model.id,
        user_id=model.user_id,
        problem_id=model.problem_id,
        text=model.text,
        image_name=model.image_name,
        creation_date=model.creation_date,
        problem=_to_problem(model.problem),
        user=_to_user_id(model.user)
    )


async def resolve_reviews(
        info: Info,
        user_id: Optional[str] = None,
        problem_id: Optional[str] = None,
        limit: Optional[int] = None
) -> list[ReviewType]:
    session: Session = info.context["db"]
    statement = (
        select(Review)
        .options(
            selectinload(Review.user),
            selectinload(Review.problem)
        )
        .order_by(Review.creation_date.desc())
    )
    if user_id:
        statement = statement.where(Review.user_id == user_id)
    if problem_id:
        statement = statement.where(Review.problem_id == problem_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [_to_review(record) for record in records]
