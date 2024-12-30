from fastapi import FastAPI, Depends, Body, Response
from methods import *
from schemas import UserId, SiteStat, Status, SelectedAuditory
from models import Base
from database import engine, get_db
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/api/get_uuid", response_model=UserId)
async def get_uuid(db: Session = Depends(get_db)):
    return await create_uuid(db)


@app.put("/api/site", response_model=Status)
async def add_site_stat(response: Response, data: SiteStat = Body(), db: Session = Depends(get_db)):
    answer, status = await insert_site_stat(db, data)
    response.status_code = status
    return answer


@app.put("/api/select-aud", response_model=Status)
async def add_selected_aud(response: Response, data: SelectedAuditory = Body(), db: Session = Depends(get_db)):
    answer, status = await insert_aud_selection(db, data)
    response.status_code = status
    return answer


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
