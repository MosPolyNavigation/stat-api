from datetime import datetime, date
from typing import Optional
import strawberry
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from strawberry.extensions import QueryDepthLimiter
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
from app import models, schemas
from app.handlers import get_endpoint_stats
from app.database import get_db
from app.schemas.filter import TargetEnum


@strawberry.type
class UserIdType:
    user_id: str
    creation_date: Optional[datetime]


@strawberry.type
class ProblemType:
    id: str


@strawberry.type
class ChangePlanType:
    id: int
    user_id: str
    plan_id: str
    visit_date: datetime
    user: Optional[UserIdType]


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


@strawberry.type
class StartWayType:
    id: int
    user_id: str
    start_id: str
    end_id: str
    success: bool
    visit_date: datetime
    user: Optional[UserIdType]


@strawberry.type
class SelectAuditoryType:
    id: int
    user_id: str
    auditory_id: str
    success: bool
    visit_date: datetime
    user: Optional[UserIdType]


@strawberry.type
class SiteStatType:
    id: int
    user_id: str
    visit_date: datetime
    endpoint: Optional[str]
    user: Optional[UserIdType]


@strawberry.type
class EndpointStatisticsType:
    unique_visitors: int
    all_visits: int
    visitor_count: int
    period: date


def _validated_limit(limit: Optional[int]) -> Optional[int]:
    if limit is None:
        return None
    if limit <= 0:
        return 0
    return limit


def _to_user(user: Optional[models.UserId]) -> Optional[UserIdType]:
    if user is None:
        return None
    return UserIdType(
        user_id=user.user_id,
        creation_date=user.creation_date
    )


def _to_problem(problem: Optional[models.Problem]) -> Optional[ProblemType]:
    if problem is None:
        return None
    return ProblemType(id=problem.id)


def _to_change_plan(model: models.ChangePlan) -> ChangePlanType:
    return ChangePlanType(
        id=model.id,
        user_id=model.user_id,
        plan_id=model.plan_id,
        visit_date=model.visit_date,
        user=_to_user(model.user)
    )


def _to_review(model: models.Review) -> ReviewType:
    return ReviewType(
        id=model.id,
        user_id=model.user_id,
        problem_id=model.problem_id,
        text=model.text,
        image_name=model.image_name,
        creation_date=model.creation_date,
        problem=_to_problem(model.problem),
        user=_to_user(model.user)
    )


def _to_start_way(model: models.StartWay) -> StartWayType:
    return StartWayType(
        id=model.id,
        user_id=model.user_id,
        start_id=model.start_id,
        end_id=model.end_id,
        success=model.success,
        visit_date=model.visit_date,
        user=_to_user(model.user)
    )


def _to_select_auditory(model: models.SelectAuditory) -> SelectAuditoryType:
    return SelectAuditoryType(
        id=model.id,
        user_id=model.user_id,
        auditory_id=model.auditory_id,
        success=model.success,
        visit_date=model.visit_date,
        user=_to_user(model.user)
    )


def _to_site_stat(model: models.SiteStat) -> SiteStatType:
    return SiteStatType(
        id=model.id,
        user_id=model.user_id,
        visit_date=model.visit_date,
        endpoint=model.endpoint,
        user=_to_user(model.user)
    )


def _to_endpoint_statistics(model: schemas.Statistics) -> EndpointStatisticsType:
    return EndpointStatisticsType(
        unique_visitors=model.unique_visitors,
        visitor_count=model.visitor_count,
        all_visits=model.all_visits,
        period=model.period,
    )

async def resolve_change_plans(
    info: Info,
    user_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    limit: Optional[int] = None
) -> list[ChangePlanType]:
    session: Session = info.context["db"]
    statement = (
        select(models.ChangePlan)
        .options(selectinload(models.ChangePlan.user))
        .order_by(models.ChangePlan.visit_date.desc())
    )
    if user_id:
        statement = statement.where(models.ChangePlan.user_id == user_id)
    if plan_id:
        statement = statement.where(models.ChangePlan.plan_id == plan_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [_to_change_plan(record) for record in records]


async def resolve_reviews(
    info: Info,
    user_id: Optional[str] = None,
    problem_id: Optional[str] = None,
    limit: Optional[int] = None
) -> list[ReviewType]:
    session: Session = info.context["db"]
    statement = (
        select(models.Review)
        .options(
            selectinload(models.Review.user),
            selectinload(models.Review.problem)
        )
        .order_by(models.Review.creation_date.desc())
    )
    if user_id:
        statement = statement.where(models.Review.user_id == user_id)
    if problem_id:
        statement = statement.where(models.Review.problem_id == problem_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [_to_review(record) for record in records]


async def resolve_start_ways(
    info: Info,
    user_id: Optional[str] = None,
    success: Optional[bool] = None,
    limit: Optional[int] = None
) -> list[StartWayType]:
    session: Session = info.context["db"]
    statement = (
        select(models.StartWay)
        .options(selectinload(models.StartWay.user))
        .order_by(models.StartWay.visit_date.desc())
    )
    if user_id:
        statement = statement.where(models.StartWay.user_id == user_id)
    if success is not None:
        statement = statement.where(models.StartWay.success.is_(success))
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [_to_start_way(record) for record in records]


async def resolve_select_auditories(
    info: Info,
    user_id: Optional[str] = None,
    success: Optional[bool] = None,
    limit: Optional[int] = None
) -> list[SelectAuditoryType]:
    session: Session = info.context["db"]
    statement = (
        select(models.SelectAuditory)
        .options(selectinload(models.SelectAuditory.user))
        .order_by(models.SelectAuditory.visit_date.desc())
    )
    if user_id:
        statement = statement.where(models.SelectAuditory.user_id == user_id)
    if success is not None:
        statement = statement.where(models.SelectAuditory.success.is_(success))
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [_to_select_auditory(record) for record in records]


async def resolve_site_stats(
    info: Info,
    user_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    limit: Optional[int] = None
) -> list[SiteStatType]:
    session: Session = info.context["db"]
    statement = (
        select(models.SiteStat)
        .options(selectinload(models.SiteStat.user))
        .order_by(models.SiteStat.visit_date.desc())
    )
    if user_id:
        statement = statement.where(models.SiteStat.user_id == user_id)
    if endpoint:
        statement = statement.where(models.SiteStat.endpoint == endpoint)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [_to_site_stat(record) for record in records]


async def resolve_user_ids(
    info: Info,
    user_id: Optional[str] = None,
    limit: Optional[int] = None
) -> list[UserIdType]:
    session: Session = info.context["db"]
    statement = select(models.UserId).order_by(
        models.UserId.creation_date.desc()
    )
    if user_id:
        statement = statement.where(models.UserId.user_id == user_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [_to_user(record) for record in records if record is not None]


async def resolve_problems(
    info: Info,
    problem_id: Optional[str] = None,
    limit: Optional[int] = None
) -> list[ProblemType]:
    session: Session = info.context["db"]
    statement = select(models.Problem).order_by(models.Problem.id)
    if problem_id:
        statement = statement.where(models.Problem.id == problem_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = session.execute(statement).scalars().all()
    return [ProblemType(id=record.id) for record in records]


async def resolve_endpoint_statistics(
    info: Info,
    endpoint: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> list[EndpointStatisticsType]:
    session: Session = info.context["db"]
    params = schemas.FilterQuery(
        target=TargetEnum[endpoint],
        start_date=start_date.date() if start_date else None,
        end_date=end_date.date() if end_date else None
    )
    stats = await get_endpoint_stats(session, params)
    return [_to_endpoint_statistics(stat) for stat in stats]


@strawberry.type
class Query:
    change_plans: list[ChangePlanType] = strawberry.field(
        resolver=resolve_change_plans,
        description="Получить список изменений планов."
    )
    reviews: list[ReviewType] = strawberry.field(
        resolver=resolve_reviews,
        description="Получить отзывы пользователей."
    )
    start_ways: list[StartWayType] = strawberry.field(
        resolver=resolve_start_ways,
        description="Получить данные о построенных маршрутах."
    )
    select_auditories: list[SelectAuditoryType] = strawberry.field(
        resolver=resolve_select_auditories,
        description="Получить статистику выбора аудиторий."
    )
    site_stats: list[SiteStatType] = strawberry.field(
        resolver=resolve_site_stats,
        description="Получить статистику посещения эндпоинтов."
    )
    user_ids: list[UserIdType] = strawberry.field(
        resolver=resolve_user_ids,
        description="Получить зарегистрированные идентификаторы пользователей."
    )
    problems: list[ProblemType] = strawberry.field(
        resolver=resolve_problems,
        description="Получить список проблем."
    )
    endpoint_statistics: list[EndpointStatisticsType] = strawberry.field(
        resolver=resolve_endpoint_statistics,
        description="Endpoint statistics for the requested target."
    )



async def get_context(
    db: Session = Depends(get_db)
) -> dict[str, Session]:
    return {"db": db}


schema = strawberry.Schema(
    query=Query,
    extensions=[QueryDepthLimiter(max_depth=4)]
)


def register_endpoint(router: APIRouter) -> None:
    graphql_router = GraphQLRouter(
        schema,
        context_getter=get_context
    )
    router.include_router(graphql_router, prefix="/stat")

