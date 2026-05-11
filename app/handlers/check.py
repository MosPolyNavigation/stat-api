from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from app.schemas import ClientIdCheck, Status
from app.models import ClientId
from app.helpers.errors import LookupException


async def check_client_id(db: AsyncSession, data: ClientIdCheck) -> Status:
    client = (await db.execute(
        Select(ClientId).filter_by(ident=data.client_id)
    )).scalar_one_or_none()
    if client is None:
        raise LookupException("Client")
    return Status()
