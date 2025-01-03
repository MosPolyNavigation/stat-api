from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi import Depends, APIRouter, Response
from fastapi_pagination import Page
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
    return await create_user_id(db)


@router.get(
    "/site",
    response_model=Page[SiteStatDB],
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
        403: {
            'model': Status,
            'description': "Api_key validation error",
            'content': {
                "application/json": {
                    "example": {"status": "no api_key"}
                }
            }
        },
        200: {
            'model': Page[SiteStatDB],
            "description": "List of found data"
        }
    }
)
async def get_sites(
        response: Response,
        query: Filter = Depends(),
        db: Session = Depends(get_db)
) -> Page[SiteStatDB]:
    try:
        return paginate(db, await item_pagination(models.SiteStat, query))
    except SQLAlchemyError as e:
        response.status_code = 500
        return Status(status=str(e))


@router.get(
    "/auds",
    response_model=Page[SelectedAuditoryDB],
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
        403: {
            'model': Status,
            'description': "Api_key validation error",
            'content': {
                "application/json": {
                    "example": {"status": "no api_key"}
                }
            }
        },
        200: {
            'model': Page[SelectedAuditoryDB],
            "description": "List of found data"
        }
    }
)
async def get_auds(
        response: Response,
        query: Filter = Depends(),
        db: Session = Depends(get_db)
) -> Page[SelectedAuditoryDB]:
    try:
        return paginate(db, await item_pagination(models.SelectAuditory, query))
    except SQLAlchemyError as e:
        response.status_code = 500
        return Status(status=str(e))
