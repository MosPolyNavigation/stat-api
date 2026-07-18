from abc import ABC, abstractmethod
from typing import Any, Sequence, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase


class BaseSeeder(ABC):
    """Базовый класс для сидеров. Поддерживает простые и составные PK."""

    model: Type[DeclarativeBase]
    pk_fields: tuple[str, ...] = ("id",)

    @abstractmethod
    def gather_data(self) -> Sequence[dict[str, Any]]:
        """Собирает эталонные данные. Должен вернуть список словарей."""
        ...

    async def add_missing(self, session: AsyncSession) -> None:
        """Добавляет только те записи, которых ещё нет в БД."""
        items = self.gather_data()
        if not items:
            return

        stmt = select(*[getattr(self.model, f) for f in self.pk_fields])
        result = await session.execute(stmt)
        existing_pks = {tuple(row) for row in result.all()}

        new_objs = [
            self.model(**item)
            for item in items
            if tuple(item[k] for k in self.pk_fields) not in existing_pks
        ]

        if new_objs:
            session.add_all(new_objs)
            await session.flush()

    async def remove_present(self, session: AsyncSession) -> None:
        """Удаляет из БД записи, которые соответствуют переданным данным."""
        items = self.gather_data()
        for item in items:
            pk = tuple(item[k] for k in self.pk_fields)
            obj = await session.get(self.model, pk)
            if obj:
                await session.delete(obj)
        await session.commit()
