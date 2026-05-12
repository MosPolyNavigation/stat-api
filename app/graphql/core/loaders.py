from typing import Type, TypeVar, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from strawberry.dataloader import DataLoader

M = TypeVar("M", bound=DeclarativeBase)


class SQLAlchemyLoader(DataLoader[int, M]):
    """
    Универсальный лоадер для загрузки моделей по первичному ключу.
    Батчит запросы: load(1), load(2), load(3) → один SELECT WHERE id IN (1,2,3)
    """

    def __init__(self, session: AsyncSession, model: Type[M]):
        super().__init__(load_fn=self._batch_load)
        self.session = session
        self.model = model

    async def _batch_load(self, keys: List[int]) -> List[Optional[M]]:
        if not keys:
            return []

        stmt = select(self.model).where(self.model.id.in_(keys))
        result = await self.session.execute(stmt)
        items = {item.id: item for item in result.scalars().all()}

        # Возвращаем в том же порядке, что и ключи (требование DataLoader)
        return [items.get(key) for key in keys]


class ForeignKeyLoader(DataLoader[int, List[M]]):
    """
    Лоадер для загрузки списка моделей по внешнему ключу.

    Пример:
        - Ключ: event_id = 5
        - Возврат: [Payload(event_id=5), Payload(event_id=5), ...]
    """

    def __init__(self, session: AsyncSession, model: Type[M], foreign_key: str):
        super().__init__(load_fn=self._batch_load)
        self.session = session
        self.model = model
        self.fk_column = getattr(model, foreign_key)

    async def _batch_load(self, keys: List[int]) -> List[List[M]]:
        if not keys:
            return []

        # Один запрос: WHERE event_id IN (1, 2, 3, ...)
        stmt = select(self.model).where(self.fk_column.in_(keys))
        result = await self.session.execute(stmt)

        # Группируем результаты по foreign_key
        grouped: Dict[int, List[M]] = {}
        for item in result.scalars().all():
            fk_value = getattr(item, self.fk_column.key)
            grouped.setdefault(fk_value, []).append(item)

        # Возвращаем в том же порядке, что и ключи
        return [grouped.get(key, []) for key in keys]


def create_loaders(session: AsyncSession) -> Dict[str, DataLoader]:
    """Фабрика лоадеров для контекста запроса."""
    from app.models import (
        ValueType, PayloadType, EventType,
        ClientId, ReviewStatus, Payload,
        DashboardType, Review, Location,
        Corpus, Floor, Type as NavTypeModel,
        Plan, Auditory, AudPhoto, Static,
        Goal, Role, Right, RoleRightGoal,
        User, UserRole, RefreshToken, UserLog
    )

    return {
        # === event_system ===
        "value_type": SQLAlchemyLoader(session, ValueType),
        "payload_type": SQLAlchemyLoader(session, PayloadType),
        "event_type": SQLAlchemyLoader(session, EventType),
        "client_id": SQLAlchemyLoader(session, ClientId),
        "review_status": SQLAlchemyLoader(session, ReviewStatus),
        "dashboard_type": SQLAlchemyLoader(session, DashboardType),
        "payloads_by_event_id": ForeignKeyLoader(session, Payload, "event_id"),
        "reviews_by_status_id": ForeignKeyLoader(session, Review, "review_status_id"),

        # === navigation ===
        "nav_location": SQLAlchemyLoader(session, Location),
        "nav_campus": SQLAlchemyLoader(session, Corpus),
        "nav_floor": SQLAlchemyLoader(session, Floor),
        "nav_type": SQLAlchemyLoader(session, NavTypeModel),
        "nav_plan": SQLAlchemyLoader(session, Plan),
        "nav_auditory": SQLAlchemyLoader(session, Auditory),
        "nav_auditory_photo": SQLAlchemyLoader(session, AudPhoto),
        "nav_static": SQLAlchemyLoader(session, Static),

        "nav_campus_by_loc_id": ForeignKeyLoader(session, Corpus, "loc_id"),
        "nav_plan_by_cor_id": ForeignKeyLoader(session, Plan, "cor_id"),
        "nav_auditory_by_plan_id": ForeignKeyLoader(session, Auditory, "plan_id"),
        "nav_photos_by_aud_id": ForeignKeyLoader(session, AudPhoto, "aud_id"),

        # === auth ===
        "goal": SQLAlchemyLoader(session, Goal),
        "right": SQLAlchemyLoader(session, Right),
        "role": SQLAlchemyLoader(session, Role),
        "user": SQLAlchemyLoader(session, User),

        "role_right_goal_by_goal_id": ForeignKeyLoader(session, RoleRightGoal, "goal_id"),
        "role_right_goal_by_right_id": ForeignKeyLoader(session, RoleRightGoal, "right_id"),
        "role_right_goal_by_role_id": ForeignKeyLoader(session, RoleRightGoal, "role_id"),
        "user_role_by_role_id": ForeignKeyLoader(session, UserRole, "role_id"),
        "user_role_by_user_id": ForeignKeyLoader(session, UserRole, "user_id"),
        "refresh_token_by_user_id": ForeignKeyLoader(session, RefreshToken, "user_id"),
        "user_log_by_user_id": ForeignKeyLoader(session, UserLog, "user_id"),
    }
