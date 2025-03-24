from sqlalchemy.orm import Session
from sqlalchemy import Select
from app import schemas, models
from app.helpers.errors import LookupException

async def insert_review(
        db: Session,
        image_name: str,
        user_id: str,
        problem: schemas.Problem,
        text: str
) -> schemas.Status:
    user = db.execute(Select(models.UserId).filter_by(user_id=user_id)).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    item = models.Review(
        image_name=image_name,
        user=user,
        problem_id=problem.__str__(),
        text=text
    )
    db.add(item)
    db.commit()
    return schemas.Status()
