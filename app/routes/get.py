from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi import Depends, APIRouter, Response
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Route
from app.schemas import Status
from app.schemas import UserId
from app.schemas import Filter
from app.schemas import WayOut
from app.schemas import StepOut
from app.schemas import RouteOut
from app.schemas import Statistics
from app.schemas import FilterRoute
from app.schemas import SiteStatOut
from app.schemas import StartWayOut
from app.schemas import FilterQuery
from app.schemas import ChangePlanOut
from app.schemas import SelectedAuditoryOut
from app.handlers import filter_by_user
from app.handlers import create_user_id
from app.handlers import get_popular_auds
from app.handlers import get_endpoint_stats
from app import models
import app.globals as globals

router = APIRouter(
    prefix="/api/get"
)


@router.get(
    "/user-id",
    description="Эндпоинт для получения уникального id пользователя",
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
                    "example": ["a-100", "a-101", "a-103", "a-102"]
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


@router.get(
    "/route",
    tags=["get"],
    responses={
        200: {
            'model': RouteOut,
            'description': "Route from one auditory to another",
            'content': {
                'application/json': {
                    'example': {
                        "to": "a-101",
                        "from": "a-100",
                        "steps": [
                            {
                                "plan": "A-1",
                                "way": [
                                    {
                                        "id": "a-100",
                                        "x": 1567,
                                        "y": 1857,
                                        "type": "entrancesToAu"
                                    },
                                    {
                                        "id": "a-1_16",
                                        "x": 1460,
                                        "y": 1857,
                                        "type": "hallway"
                                    },
                                    {
                                        "id": "a-1-stair-2",
                                        "x": 1460,
                                        "y": 1703,
                                        "type": "stair"
                                    },
                                    {
                                        "id": "a-1_41",
                                        "x": 1451,
                                        "y": 1531,
                                        "type": "hallway"
                                    },
                                    {
                                        "id": "a-1_10",
                                        "x": 1441,
                                        "y": 1530,
                                        "type": "hallway"
                                    },
                                    {
                                        "id": "a-1_15",
                                        "x": 1374,
                                        "y": 1530,
                                        "type": "hallway"
                                    },
                                    {
                                        "id": "a-1_18",
                                        "x": 1267,
                                        "y": 1530,
                                        "type": "hallway"
                                    },
                                    {
                                        "id": "a-1_19",
                                        "x": 1189,
                                        "y": 1530,
                                        "type": "hallway"
                                    },
                                    {
                                        "id": "a-1_20",
                                        "x": 1080,
                                        "y": 1530,
                                        "type": "hallway"
                                    },
                                    {
                                        "id": "a-101",
                                        "x": 1080,
                                        "y": 1581,
                                        "type": "entrancesToAu"
                                    }
                                ],
                                "distance": 855.29
                            }
                        ],
                        "fullDistance": 855
                    }
                }
            }
        },
        400: {
            'model': Status,
            'description': "Route from one auditory to another",
            'content': {
                'application/json': {
                    'example': {
                        'status': 'The requested route is impossible'
                    }
                }
            }
        },
        404: {
            'model': Status,
            'description': "Route from one auditory to another",
            'content': {
                'application/json': {
                    'example': {
                        'status': 'You are trying to get a route along non-existent vertex'
                    }
                }
            }
        }
    }
)
async def get_route(
    response: Response,
    query: FilterRoute = Depends()
):
    try:
        graph_bs = globals.global_graph["BS"]
    except KeyError:
        response.status_code = 500
        return Status(
            status="No graphs loaded"
        )
    from_v = graph_bs.vertexes.get(query.from_, None)
    to_v = graph_bs.vertexes.get(query.to, None)
    if from_v is None or to_v is None:
        response.status_code = 404
        return Status(
            status="You are trying to get a route along non-existent vertex"
        )
    try:
        route = Route(from_=query.from_, to=query.to, graph=graph_bs)
        data = RouteOut(
            from_=route.from_,
            to=route.to,
            steps=[StepOut(
                plan=x.plan.id,
                distance=x.distance,
                way=[WayOut(
                    id=v.id,
                    x=v.x,
                    y=v.y,
                    type=v.type
                ) for v in x.way]
            ) for x in route.steps],
            fullDistance=route.fullDistance
        )
        return data
    except Exception as e:
        print(e)
        response.status_code = 400
        return Status(
            status="The requested route is impossible"
        )
