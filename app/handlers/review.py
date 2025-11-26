from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from app import schemas, models
from app.helpers.errors import LookupException


async def insert_review(
        db: AsyncSession,
        image_name: str,
        user_id: str,
        problem: schemas.Problem,
        text: str
) -> schemas.Status:
    user = (await db.execute(
        Select(models.UserId).filter_by(user_id=user_id)
    )).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    item = models.Review(
        image_name=image_name,
        user=user,
        problem_id=problem.__str__(),
        text=text
    )
    db.add(item)
    await db.commit()
    return schemas.Status()
