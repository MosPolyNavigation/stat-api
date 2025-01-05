from sqlalchemy.orm import Session
from app import schemas, models


async def create_user_id(db: Session) -> schemas.UserId:
    item = models.UserId()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
