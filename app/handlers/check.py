from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from app.schemas import ClientIdCheck, Status
from app.models import ClientId
from app.helpers.errors import LookupException
from app.schemas.old_events import UserIdCheck


# TODO: Удалить, как фронты перейдут на новую схему событий
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
