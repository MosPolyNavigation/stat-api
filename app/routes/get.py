from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi.responses import JSONResponse
from fastapi import Depends, APIRouter
from fastapi_pagination import Page
from app.database import get_db
from app.schemas import *
from app.handlers import *
from app import models

router = APIRouter(
    prefix="/api/get"
)


@router.get(
    "/user-id",
    description="Эндпоинт для получения уникального идентификатора пользователя",
    response_model=UserId,
    tags=["get"],
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
    """
    Эндпоинт для получения уникального идентификатора пользователя.

    Этот эндпоинт возвращает новый уникальный идентификатор пользователя.

    Args:
        db: Сессия базы данных.

    Returns:
        UserId: Новый уникальный идентификатор пользователя.
    """
    return await create_user_id(db)


@router.get(
    "/site",
    description="Эндпоинт для получения посещений сайта",
    response_model=Page[SiteStatOut],
    tags=["get"],
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
    """
    Эндпоинт для получения посещений сайта.

    Этот эндпоинт возвращает список найденных данных.

    Args:
        query: Параметры фильтрации.
        db: Сессия базы данных.

    Returns:
        Page[SiteStatOut]: Страница с найденными данными.
    """
    return paginate(db, filter_by_user(models.SiteStat, query))


@router.get(
    "/auds",
    description="Эндпоинт для получения выбранных аудиторий",
    response_model=Page[SelectedAuditoryOut],
    tags=["get"],
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
    """
    Эндпоинт для получения выбранных аудиторий.

    Этот эндпоинт возвращает список найденных данных.

    Args:
        query: Параметры фильтрации.
        db: Сессия базы данных.

    Returns:
        Page[SelectedAuditoryOut]: Страница с найденными данными.
    """
    return paginate(db, filter_by_user(models.SelectAuditory, query))


@router.get(
    "/ways",
    description="Эндпоинт для получения начатых путей",
    response_model=Page[StartWayOut],
    tags=["get"],
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
    """
    Эндпоинт для получения начатых путей.

    Этот эндпоинт возвращает список найденных данных.

    Args:
        query: Параметры фильтрации.
        db: Сессия базы данных.

    Returns:
        Page[StartWayOut]: Страница с найденными данными.
    """
    return paginate(db, filter_by_user(models.StartWay, query))


@router.get(
    "/plans",
    description="Эндпоинт для получения смененных планов",
    response_model=Page[ChangePlanOut],
    tags=["get"],
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
    """
    Эндпоинт для получения смененных планов.

    Этот эндпоинт возвращает список найденных данных.

    Args:
        query: Параметры фильтрации.
        db: Сессия базы данных.

    Returns:
        Page[ChangePlanOut]: Страница с найденными данными.
    """
    return paginate(db, filter_by_user(models.ChangePlan, query))


@router.get(
    "/stat",
    description="Эндпоинт для получения статистики по выбранному эндпоинту",
    response_model=Statistics,
    tags=["get"],
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
        }
    }
)
async def get_stat(
    query: FilterQuery = Depends(),
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения статистики по выбранному эндпоинту.

    Этот эндпоинт возвращает статистику.

    Args:
        query: Параметры фильтрации.
        db: Сессия базы данных.

    Returns:
        Statistics: Статистика.
    """
    return await get_endpoint_stats(db, query)

@router.get(
    "/popular",
    tags=["get"],
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
            'description': 'Popular auditories in descending order',
            'content': {
                'application/json': {
                    "example": ["a-100","a-101","a-103","a-102"]
                }
            }
        }
    }
)
async def get_popular(
        db: Session = Depends(get_db)
) -> JSONResponse:
    data = await get_popular_auds(db)
    return JSONResponse(data, status_code=200)
