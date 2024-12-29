from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import models, schemas

async def create_uuid(db: Session) -> schemas.UUID:
    item = models.UUID()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

async def insert_site_stat(db: Session, data: schemas.SiteStat) -> JSONResponse:
    item = models.SiteStat(uuid=data.uuid, endpoint=data.endpoint)
    try:
        db.add(item)
        db.commit()
    except:
        return JSONResponse(content={"status": "OK"}, status_code=500)
    return {"status": "OK"}
