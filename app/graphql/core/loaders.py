from typing import Type, TypeVar, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from strawberry.dataloader import DataLoader

from app.models import (
    ValueType, PayloadType, EventType,
    ClientId, ReviewStatus, DashboardType,
    Payload, Review, Location, Corpus, Floor,
    Type as NavTypeModel, Plan, Auditory,
    AudPhoto, Static, Goal, Role, Right,
    RoleRightGoal, User, UserRole, RefreshToken,
    UserLog,
)

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
        self.id_column = getattr(model, "id")

    async def _batch_load(self, keys: List[int]) -> List[Optional[M]]:
        if not keys:
            return []

        stmt = select(self.model).where(self.id_column.in_(keys))
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

        stmt = select(self.model).where(self.fk_column.in_(keys))
        result = await self.session.execute(stmt)

        grouped: Dict[int, List[M]] = {}
        for item in result.scalars().all():
            fk_value = getattr(item, self.fk_column.key)
            grouped.setdefault(fk_value, []).append(item)

        return [grouped.get(key, []) for key in keys]


# =============================================================================
# Типизированный контейнер лоадеров
# =============================================================================
class Loaders:
    """
    Контейнер лоадеров с полной типизацией.

    Использование:
        - Через атрибуты: ctx.loaders.user.load(1)
    """

    def __init__(self, session: AsyncSession):
        # === event_system ===
        self.value_type: DataLoader[int, ValueType] = SQLAlchemyLoader(session, ValueType)
        self.payload_type: DataLoader[int, PayloadType] = SQLAlchemyLoader(session, PayloadType)
        self.event_type: DataLoader[int, EventType] = SQLAlchemyLoader(session, EventType)
        self.client_id: DataLoader[int, ClientId] = SQLAlchemyLoader(session, ClientId)
        self.review_status: DataLoader[int, ReviewStatus] = SQLAlchemyLoader(session, ReviewStatus)
        self.dashboard_type: DataLoader[int, DashboardType] = SQLAlchemyLoader(session, DashboardType)

        self.payloads_by_event_id: DataLoader[int, List[Payload]] = ForeignKeyLoader(
            session,
            Payload,
            "event_id"
        )
        self.reviews_by_status_id: DataLoader[int, List[Review]] = ForeignKeyLoader(
            session,
            Review,
            "review_status_id"
        )

        # === navigation ===
        self.nav_location: DataLoader[int, Location] = SQLAlchemyLoader(session, Location)
        self.nav_campus: DataLoader[int, Corpus] = SQLAlchemyLoader(session, Corpus)
        self.nav_floor: DataLoader[int, Floor] = SQLAlchemyLoader(session, Floor)
        self.nav_type: DataLoader[int, NavTypeModel] = SQLAlchemyLoader(session, NavTypeModel)
        self.nav_plan: DataLoader[int, Plan] = SQLAlchemyLoader(session, Plan)
        self.nav_auditory: DataLoader[int, Auditory] = SQLAlchemyLoader(session, Auditory)
        self.nav_auditory_photo: DataLoader[int, AudPhoto] = SQLAlchemyLoader(session, AudPhoto)
        self.nav_static: DataLoader[int, Static] = SQLAlchemyLoader(session, Static)

        self.nav_campus_by_loc_id: DataLoader[int, List[Corpus]] = ForeignKeyLoader(
            session,
            Corpus,
            "loc_id"
        )
        self.nav_plan_by_cor_id: DataLoader[int, List[Plan]] = ForeignKeyLoader(
            session,
            Plan,
            "cor_id"
        )
        self.nav_auditory_by_plan_id: DataLoader[int, List[Auditory]] = ForeignKeyLoader(
            session,
            Auditory,
            "plan_id"
        )
        self.nav_photos_by_aud_id: DataLoader[int, List[AudPhoto]] = ForeignKeyLoader(
            session,
            AudPhoto,
            "aud_id"
        )

        # === auth ===
        self.goal: DataLoader[int, Goal] = SQLAlchemyLoader(session, Goal)
        self.right: DataLoader[int, Right] = SQLAlchemyLoader(session, Right)
        self.role: DataLoader[int, Role] = SQLAlchemyLoader(session, Role)
        self.user: DataLoader[int, User] = SQLAlchemyLoader(session, User)

        self.role_right_goal_by_goal_id: DataLoader[int, List[RoleRightGoal]] = ForeignKeyLoader(
            session,
            RoleRightGoal,
            "goal_id"
        )
        self.role_right_goal_by_right_id: DataLoader[int, List[RoleRightGoal]] = ForeignKeyLoader(
            session,
            RoleRightGoal,
            "right_id"
        )
        self.role_right_goal_by_role_id: DataLoader[int, List[RoleRightGoal]] = ForeignKeyLoader(
            session,
            RoleRightGoal,
            "role_id"
        )
        self.user_role_by_role_id: DataLoader[int, List[UserRole]] = ForeignKeyLoader(
            session,
            UserRole,
            "role_id"
        )
        self.user_role_by_user_id: DataLoader[int, List[UserRole]] = ForeignKeyLoader(
            session,
            UserRole,
            "user_id"
        )
        self.refresh_token_by_user_id: DataLoader[int, List[RefreshToken]] = ForeignKeyLoader(
            session,
            RefreshToken,
            "user_id"
        )
        self.user_log_by_user_id: DataLoader[int, List[UserLog]] = ForeignKeyLoader(
            session,
            UserLog,
            "user_id"
        )
