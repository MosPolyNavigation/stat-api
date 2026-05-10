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

        stmt = select(self.model).where(self.model.id.in_(keys))  # noqa
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
        DashboardType
    )

    return {
        "value_type": SQLAlchemyLoader(session, ValueType),
        "payload_type": SQLAlchemyLoader(session, PayloadType),
        "event_type": SQLAlchemyLoader(session, EventType),
        "client_id": SQLAlchemyLoader(session, ClientId),
        "review_status": SQLAlchemyLoader(session, ReviewStatus),
        "dashboard_type": SQLAlchemyLoader(session, DashboardType),
        # Добавляй новые по мере необходимости
        "payloads_by_event_id": ForeignKeyLoader(session, Payload, "event_id"),
    }
