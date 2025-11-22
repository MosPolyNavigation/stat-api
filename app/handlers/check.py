from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from datetime import datetime, timedelta
from app.state import AppState
from app.schemas import UserIdCheck, Status
from app.models import UserId
from app.helpers.errors import LookupException


def check_user(state: AppState, user_id) -> float:
    """
    Функция для проверки пользователя.

    Эта функция проверяет пользователя
    и возвращает время, прошедшее с последней проверки.

    Args:
        state: Состояние приложения;
        user_id: Идентификатор пользователя.

    Returns:
        float: Время, прошедшее с последней проверки.
    """
    state.user_access.setdefault(
        user_id,
        datetime.now() - timedelta(seconds=1)
    )
    delta = datetime.now() - state.user_access[user_id]
    state.user_access[user_id] = datetime.now()
    return delta.total_seconds()


async def check_user_id(db: AsyncSession, data: UserIdCheck) -> Status:
    user = (await db.execute(
        Select(UserId).filter_by(user_id=data.user_id)
    )).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    return Status()
