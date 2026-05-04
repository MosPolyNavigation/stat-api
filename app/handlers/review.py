from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from app import schemas, models
from app.helpers.errors import LookupException


async def insert_review(
        db: AsyncSession,
        image_name: str,
        client_id: str,
        problem: schemas.Problem,
        text: str
) -> schemas.Status:
    client = (await db.execute(
        Select(models.ClientId).filter_by(ident=client_id)
    )).scalar_one_or_none()
    if client is None:
        raise LookupException("Client")
    item = models.Review(
        image_name=image_name,
        client=client,
        problem_id=problem.__str__(),
        text=text
    )
    db.add(item)
    await db.commit()
    return schemas.Status()
