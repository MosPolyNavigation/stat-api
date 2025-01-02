from fastapi import Depends, APIRouter, Response
from app.database import get_db
from app.schemas import *
from app.methods import *
from app import models

router = APIRouter(
    prefix="/api/get"
)


@router.get(
    "/user_id",
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


@router.get(
    "/site",
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
        query: PaginationBase = Depends(),
        db: Session = Depends(get_db)
):
    answer, status_code = await item_pagination(db, models.SiteStat, query)
    response.status_code = status_code
    return answer


@router.get(
    "/auds",
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
        query: PaginationBase = Depends(),
        db: Session = Depends(get_db)
):
    answer, status_code = await item_pagination(db, models.SelectAuditory, query)
    response.status_code = status_code
    return answer
