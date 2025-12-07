"""Проверки пользовательских данных и ограничения по частоте запросов."""

from datetime import datetime, timedelta

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserId
from app.schemas import Status, UserIdCheck
from app.helpers.errors import LookupException
from app.state import AppState


def check_user(state: AppState, user_id) -> float:
    """
    Ставит ограничение в один запрос в секунду для конкретного пользователя.

    Запоминает время последнего обращения и возвращает прошедшие секунды.
    """
    state.user_access.setdefault(user_id, datetime.now() - timedelta(seconds=1))
    delta = datetime.now() - state.user_access[user_id]
    state.user_access[user_id] = datetime.now()
    return delta.total_seconds()


async def check_user_id(db: AsyncSession, data: UserIdCheck) -> Status:
    """Проверяет наличие пользователя в БД по user_id."""
    user = (await db.execute(Select(UserId).filter_by(user_id=data.user_id))).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    return Status()
