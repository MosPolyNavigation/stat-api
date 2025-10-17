import strawberry
from sqlalchemy import select
from sqlalchemy.orm import Session
from strawberry import Info
from typing import Optional
from app.models import Problem
from .filter_handlers import _validated_limit


@strawberry.type
class ProblemType:
    id: str


def _to_problem(problem: Optional[Problem]) -> Optional[ProblemType]:
    if problem is None:
        return None
    return ProblemType(id=problem.id)


async def resolve_problems(
        info: Info,
        problem_id: Optional[str] = None,
        limit: Optional[int] = None
) -> list[ProblemType]:
    session: Session = info.context["db"]
    statement = select(Problem).order_by(Problem.id)
    if problem_id:
        statement = statement.where(Problem.id == problem_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [ProblemType(id=record.id) for record in records]
