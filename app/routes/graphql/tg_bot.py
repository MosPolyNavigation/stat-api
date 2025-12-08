from datetime import date, datetime, time, timedelta
from typing import Optional
import strawberry
from sqlalchemy import String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from strawberry import Info
from app.models import TgEvent, TgEventType, TgUser
from .filter_handlers import _validated_limit
from .permissions import ensure_stats_view_permission


@strawberry.type
class TgBotUserType:
    id: int
    tg_id: int


@strawberry.type
class TgBotEventKindType:
    id: int
    name: str


@strawberry.type
class TgBotEventType:
    id: int
    tg_user_id: int
    event_type_id: int
    is_dod: bool
    time: datetime
    tg_user: Optional[TgBotUserType]
    event_type: Optional[TgBotEventKindType]


@strawberry.type
class TgBotEventStatisticType:
    event_type: str
    is_dod: bool
    period: date
    count: int


def _to_tg_bot_user(model: TgUser | None) -> Optional[TgBotUserType]:
    if model is None:
        return None
    return TgBotUserType(
        id=model.id,
        tg_id=model.tg_id
    )


def _to_tg_bot_event_kind(model: TgEventType | None) -> Optional[TgBotEventKindType]:
    if model is None:
        return None
    return TgBotEventKindType(
        id=model.id,
        name=model.name
    )


def _to_tg_bot_event(model: TgEvent) -> TgBotEventType:
    return TgBotEventType(
        id=model.id,
        tg_user_id=model.tg_user_id,
        event_type_id=model.event_type_id,
        is_dod=model.is_dod,
        time=model.time,
        tg_user=_to_tg_bot_user(model.tg_user),
        event_type=_to_tg_bot_event_kind(model.event_type)
    )


async def resolve_tg_bot_users(
    info: Info,
    tg_id: Optional[int] = None,
    limit: Optional[int] = None
) -> list[TgBotUserType]:
    session: AsyncSession = await ensure_stats_view_permission(info)
    statement = select(TgUser).order_by(TgUser.id)
    if tg_id is not None:
        statement = statement.where(TgUser.tg_id == tg_id)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = (await session.execute(statement)).scalars().all()
    return [_to_tg_bot_user(record) for record in records if record is not None]


async def resolve_tg_bot_event_types(
    info: Info,
    name: Optional[str] = None,
    limit: Optional[int] = None
) -> list[TgBotEventKindType]:
    session: AsyncSession = await ensure_stats_view_permission(info)
    statement = select(TgEventType).order_by(TgEventType.name)
    if name:
        statement = statement.where(TgEventType.name == name)
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = (await session.execute(statement)).scalars().all()
    return [_to_tg_bot_event_kind(record) for record in records if record is not None]


async def resolve_tg_bot_events(
    info: Info,
    tg_id: Optional[int] = None,
    event_type: Optional[str] = None,
    is_dod: Optional[bool] = None,
    limit: Optional[int] = None
) -> list[TgBotEventType]:
    session: AsyncSession = await ensure_stats_view_permission(info)
    statement = (
        select(TgEvent)
        .options(
            selectinload(TgEvent.tg_user),
            selectinload(TgEvent.event_type)
        )
        .order_by(TgEvent.time.desc())
    )
    if tg_id is not None:
        statement = (
            statement.join(TgEvent.tg_user)
            .where(TgUser.tg_id == tg_id)
        )
    if event_type:
        statement = (
            statement.join(TgEvent.event_type)
            .where(TgEventType.name == event_type)
        )
    if is_dod is not None:
        statement = statement.where(TgEvent.is_dod.is_(is_dod))
    validated_limit = _validated_limit(limit)
    if validated_limit == 0:
        return []
    if validated_limit is not None:
        statement = statement.limit(validated_limit)
    records = (await session.execute(statement)).scalars().unique().all()
    return [_to_tg_bot_event(record) for record in records]


def _fill_missing_tg_event_stats(
    stats_map: dict[tuple[str, bool], dict[date, int]],
    event_type_names: list[str],
    is_dod_values: list[bool],
    start_date: date,
    end_date: date
) -> list[TgBotEventStatisticType]:
    end_date_inclusive = end_date + timedelta(days=1)
    filled: list[TgBotEventStatisticType] = []
    current_date = start_date
    while current_date < end_date_inclusive:
        for event_type in event_type_names:
            for dod_flag in is_dod_values:
                count = stats_map.get((event_type, dod_flag), {}).get(current_date, 0)
                filled.append(
                    TgBotEventStatisticType(
                        event_type=event_type,
                        is_dod=dod_flag,
                        period=current_date,
                        count=count
                    )
                )
        current_date += timedelta(days=1)
    return filled


async def _event_type_names(
    session: AsyncSession,
    filter_name: Optional[str]
) -> list[str]:
    if filter_name:
        return [filter_name]
    names = (await session.execute(select(TgEventType.name))).scalars().all()
    return sorted(set(names))


async def resolve_tg_bot_event_statistics(
    info: Info,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    is_dod: Optional[bool] = None,
    event_type: Optional[str] = None,
    tg_id: Optional[int] = None
) -> list[TgBotEventStatisticType]:
    session: AsyncSession = await ensure_stats_view_permission(info)
    event_type_names = await _event_type_names(session, event_type)
    if not event_type_names:
        return []

    today = date.today()
    effective_end_date = None
    effective_start_date = start_date
    if end_date is not None:
        effective_end_date = min(end_date, today)

    date_expr = func.date(TgEvent.time)
    period_str_expr = func.cast(date_expr, String)
    statement = (
        select(
            TgEventType.name.label("event_type"),
            TgEvent.is_dod.label("is_dod"),
            period_str_expr.label("period"),
            func.count(TgEvent.id).label("count")
        )
        .join(TgEventType, TgEvent.event_type_id == TgEventType.id)
        .group_by(TgEventType.name, TgEvent.is_dod, period_str_expr)
        .order_by(period_str_expr, TgEventType.name)
    )
    if tg_id is not None:
        statement = statement.join(TgEvent.tg_user).where(TgUser.tg_id == tg_id)
    if event_type:
        statement = statement.where(TgEventType.name == event_type)
    if is_dod is not None:
        statement = statement.where(TgEvent.is_dod.is_(is_dod))
    if effective_start_date is not None:
        statement = statement.where(
            TgEvent.time >= datetime.combine(effective_start_date, time.min)
        )
    if effective_end_date is not None:
        statement = statement.where(
            TgEvent.time <= datetime.combine(effective_end_date, time.max)
        )

    rows = (await session.execute(statement)).fetchall()
    stats_map: dict[tuple[str, bool], dict[date, int]] = {}
    for row in rows:
        period_date = date.fromisoformat(row.period)
        key = (row.event_type, row.is_dod)
        stats_map.setdefault(key, {})[period_date] = row.count

    dod_values = [is_dod] if is_dod is not None else [True, False]
    if effective_start_date is not None and effective_end_date is not None:
        return _fill_missing_tg_event_stats(
            stats_map,
            event_type_names,
            dod_values,
            effective_start_date,
            effective_end_date
        )

    result: list[TgBotEventStatisticType] = []
    for (event_kind, dod_flag), date_map in stats_map.items():
        for period_date, count in sorted(date_map.items()):
            result.append(
                TgBotEventStatisticType(
                    event_type=event_kind,
                    is_dod=dod_flag,
                    period=period_date,
                    count=count
                )
            )
    return result
