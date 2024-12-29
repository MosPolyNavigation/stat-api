from fastapi import FastAPI, Depends, Body, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from methods import create_uuid, insert_site_stat
from schemas import UUID, SiteStat, Status
from models import Base
from database import SessionLocal, engine, get_db
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/get_uuid", response_model=UUID)
async def get_uuid(db: Session = Depends(get_db)):
    return await create_uuid(db)


@app.post("/api/site", response_model=Status)
async def add_site_stat(response: Response, data: SiteStat = Body(), db: Session = Depends(get_db)):
    answer, status = await insert_site_stat(db, data)
    response.status_code = status
    return answer

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
