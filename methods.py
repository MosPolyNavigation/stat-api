from sqlalchemy.orm import Session
import models, schemas

def create_uuid(db: Session) -> schemas.UUID:
    item = models.UUID()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
