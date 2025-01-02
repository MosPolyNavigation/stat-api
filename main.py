from fastapi import FastAPI, Depends, Body, Response
from methods import *
from schemas import *
from models import Base
from database import engine, get_db
from state import AppState, check_user
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.state = AppState()


@app.get(
    "/api/get/user_id",
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
        },
        429: {
            'model': Status,
            "description": "Too many requests",
            'content': {
                "application/json": {
                    "example": {"status": "Too many requests for this user within one second"}
                }
            }
        }
    }
)
async def add_selected_aud(
        response: Response,
        data: SelectedAuditory = Body(),
        db: Session = Depends(get_db),
        state: AppState = Depends(lambda: app.state)
):
    if check_user(state, data.user_id) < 1:
        response.status_code = 429
        return Status(status="Too many requests for this user within one second")
    answer, status = await insert_aud_selection(db, data)
    response.status_code = status
    return answer


@app.get(
    "/api/get/site",
    response_model=list[SiteStatDB],
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
            'model': SiteStatDB,
            "description": "List of found data"
        }
    }
)
async def get_sites(
        response: Response,
        query: StatisticsBase = Depends(),
        db: Session = Depends(get_db)
):
    answer, status = await item_pagination(db, models.SiteStat, query)
    response.status_code = status
    return answer


@app.get(
    "/api/get/auds",
    response_model=list[SelectedAuditoryDB],
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
            'model': SelectedAuditoryDB,
            "description": "List of found data"
        }
    }
)
async def get_auds(
        response: Response,
        query: StatisticsBase = Depends(),
        db: Session = Depends(get_db)
):
    answer, status = await item_pagination(db, models.SelectAuditory, query)
    response.status_code = status
    return answer


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
