from datetime import datetime
import strawberry
from sqlalchemy import select
from sqlalchemy.orm import Session
from strawberry import Info
from typing import Optional
from app.models import UserId
from app.routes.graphql.filter_handlers import _validated_limit


@strawberry.type
class UserIdType:
    user_id: str
    creation_date: Optional[datetime]


def _to_user_id(user: Optional[UserId]) -> Optional[UserIdType]:
    if user is None:
        return None
    return UserIdType(
        user_id=user.user_id,
        creation_date=user.creation_date
    )


async def resolve_user_ids(
        info: Info,
        user_id: Optional[str] = None,
        limit: Optional[int] = None
) -> list[UserIdType]:
    session: Session = info.context["db"]
    statement = select(UserId).order_by(
        UserId.creation_date.desc()
    )
    if user_id:
        statement = statement.where(UserId.user_id == user_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [_to_user_id(record) for record in records if record is not None]
