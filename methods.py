from sqlalchemy.orm import Session
import models, schemas

async def create_uuid(db: Session) -> schemas.UUID:
    item = models.UUID()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
