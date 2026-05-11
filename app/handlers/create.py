from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, models


async def create_client_id(db: AsyncSession) -> schemas.ClientIdentResponse:
    item = models.ClientId()
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return schemas.ClientIdentResponse(
        ident=item.ident,
        creation_date=item.creation_date,
    )
