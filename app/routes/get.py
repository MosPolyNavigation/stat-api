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
    "/user-id",
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
async def get_uuid(db: Session = Depends(get_db)):
    return await create_user_id(db)


@router.get(
    "/site",
    response_model=Page[SiteStatOut],
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
            'model': Page[SiteStatOut],
            "description": "List of found data"
        }
    }
)
async def get_sites(
        query: Filter = Depends(),
        db: Session = Depends(get_db)
) -> Page[SiteStatOut]:
    return paginate(db, await item_pagination(models.SiteStat, query))


@router.get(
    "/auds",
    response_model=Page[SelectedAuditoryOut],
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
            'model': Page[SelectedAuditoryOut],
            "description": "List of found data"
        }
    }
)
async def get_auds(
        query: Filter = Depends(),
        db: Session = Depends(get_db)
) -> Page[SelectedAuditoryOut]:
    return paginate(db, await item_pagination(models.SelectAuditory, query))


@router.get(
    "/ways",
    response_model=Page[StartWayOut],
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
            'model': Page[StartWayOut],
            "description": "List of found data"
        }
    }
)
async def get_ways(
        query: Filter = Depends(),
        db: Session = Depends(get_db)
) -> Page[StartWayOut]:
    return paginate(db, await item_pagination(models.StartWay, query))


@router.get(
    "/plans",
    response_model=Page[ChangePlanOut],
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
            'model': Page[ChangePlanOut],
            "description": "List of found data"
        }
    }
)
async def get_plans(
        query: Filter = Depends(),
        db: Session = Depends(get_db)
) -> Page[ChangePlanOut]:
    return paginate(db, await item_pagination(models.ChangePlan, query))
