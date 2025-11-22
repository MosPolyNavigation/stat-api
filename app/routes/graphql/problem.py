import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import Info
from typing import Optional
from .filter_handlers import _validated_limit
from .permissions import ensure_stats_view_permission
from app.models import Problem


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
    session: AsyncSession = ensure_stats_view_permission(info)
    statement = select(Problem).order_by(Problem.id)
    if problem_id:
        statement = statement.where(Problem.id == problem_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = (await session.execute(statement)).scalars().all()
    return [ProblemType(id=record.id) for record in records]
