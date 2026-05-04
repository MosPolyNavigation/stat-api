from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from datetime import datetime, timedelta
from app.state import AppState
from app.schemas import ClientIdCheck, UserIdCheck, Status
from app.models import ClientId
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
    return await check_client_id(
        db,
        ClientIdCheck(client_id=data.user_id),
    )


async def check_client_id(db: AsyncSession, data: ClientIdCheck) -> Status:
    client = (await db.execute(
        Select(ClientId).filter_by(ident=data.client_id)
    )).scalar_one_or_none()
    if client is None:
        raise LookupException("Client")
    return Status()
