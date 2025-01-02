from fastapi import FastAPI, Depends, Body, Response

import schemas
from methods import *
from schemas import UserId, SiteStat, Status, SelectedAuditory
from models import Base
from database import engine, get_db
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get(
    "/api/get_uuid",
    response_model=UserId,
    responses={
        500: {
            'model': Status,
            'description': "Server side error",
            'content': {
                "application/json": {
                    "example": {"status": "Some error"}
                }
            }
        },
        200: {
            'model': UserId,
            "description": "Newly generated user_id"
        }
    }
)
async def get_uuid(response: Response, db: Session = Depends(get_db)):
    answer, status = await create_uuid(db)
    response.status_code = status
    return answer


@app.put(
    "/api/site",
    response_model=Status,
    responses={
        500: {
            'model': Status,
            'description': "Server side error",
            'content': {
                "application/json": {
                    "example": {"status": "Some error"}
                }
            }
        },
        404: {
            'model': Status,
            'description': "Item not found",
            'content': {
                "application/json": {
                    "example": {"status": "User not found"}
                }
            }
        },
        200: {
            'model': Status,
            "description": "Status of adding new object to db"
        }
    }
)
async def add_site_stat(response: Response, data: SiteStat = Body(), db: Session = Depends(get_db)):
    answer, status = await insert_site_stat(db, data)
    response.status_code = status
    return answer


@app.put(
    "/api/select-aud",
    response_model=Status,
    responses={
        500: {
            'model': Status,
            'description': "Server side error",
            'content': {
                "application/json": {
                    "example": {"status": "Some error"}
                }
            }
        },
        404: {
            'model': Status,
            'description': "Item not found",
            'content': {
                "application/json": {
                    "example": {"status": "Auditory not found"}
                }
            }
        },
        200: {
            'model': Status,
            "description": "Status of adding new object to db"
        }
    }
)
async def add_selected_aud(response: Response, data: SelectedAuditory = Body(), db: Session = Depends(get_db)):
    answer, status = await insert_aud_selection(db, data)
    response.status_code = status
    return answer


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
