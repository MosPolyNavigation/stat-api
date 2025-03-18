from fastapi import Depends, APIRouter, Response, Body, Request
from app.database import get_db
from app.schemas import *
from app.handlers import *

router = APIRouter(
    prefix="/api/stat"
)


@router.put(
    "/site",
    description="Эндпоинт для добавления статистики посещений сайта",
    response_model=status.Status,
    tags=["stat"],
    responses={
        500: {
            'model': status.Status,
            'description': "Server side error",
            'content': {
                "application/json": {
                    "example": {"status": "Some error"}
                }
            }
        },
        404: {
            'model': status.Status,
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
async def add_site_stat(data: SiteStatIn = Body(), db: Session = Depends(get_db)):
    """
    Эндпоинт для добавления статистики посещений сайта.

    Этот эндпоинт добавляет статистику посещений сайта в базу данных.

    Args:
        data: Данные статистики сайта.
        db: Сессия базы данных.

    Returns:
        Status: Статус добавления нового объекта в базу данных.
    """
    return await insert_site_stat(db, data)


@router.put(
    "/select-aud",
    description="Эндпоинт для добавления выбора аудитории",
    response_model=Status,
    tags=["stat"],
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
        request: Request,
        response: Response,
        data: SelectedAuditoryIn = Body(),
        db: Session = Depends(get_db),
):
    """
    Эндпоинт для добавления выбора аудитории.

    Этот эндпоинт добавляет выбор аудитории в базу данных.

    Args:
        request: Запрос.
        response: Ответ.
        data: Данные выбора аудитории.
        db: Сессия базы данных.

    Returns:
        Status: Статус добавления нового объекта в базу данных.
    """
    state = request.app.state
    if check_user(state, data.user_id) < 1:
        response.status_code = 429
        return Status(status="Too many requests for this user within one second")
    return await insert_aud_selection(db, data)


@router.put(
    "/start-way",
    description="Эндпоинт для добавления начатого пути",
    response_model=status.Status,
    tags=["stat"],
    responses={
        500: {
            'model': status.Status,
            'description': "Server side error",
            'content': {
                "application/json": {
                    "example": {"status": "Some error"}
                }
            }
        },
        404: {
            'model': status.Status,
            'description': "Item not found",
            'content': {
                "application/json": {
                    "example": {"status": "End auditory not found"}
                }
            }
        },
        200: {
            'model': Status,
            "description": "Status of adding new object to db"
        }
    }
)
async def add_started_way(
        data: StartWayIn = Body(),
        db: Session = Depends(get_db)
):
    """
    Эндпоинт для добавления начатого пути.

    Этот эндпоинт добавляет начатый путь в базу данных.

    Args:
        data: Данные начатого пути.
        db: Сессия базы данных.

    Returns:
        Status: Статус добавления нового объекта в базу данных.
    """
    return await insert_start_way(db, data)


@router.put(
    "/change-plan",
    description="Эндпоинт для добавления смены плана",
    response_model=status.Status,
    tags=["stat"],
    responses={
        500: {
            'model': status.Status,
            'description': "Server side error",
            'content': {
                "application/json": {
                    "example": {"status": "Some error"}
                }
            }
        },
        404: {
            'model': status.Status,
            'description': "Item not found",
            'content': {
                "application/json": {
                    "example": {"status": "Changed plan not found"}
                }
            }
        },
        200: {
            'model': Status,
            "description": "Status of adding new object to db"
        }
    }
)
async def add_changed_plan(
        data: ChangePlanIn = Body(),
        db: Session = Depends(get_db)
):
    """
    Эндпоинт для добавления смены плана.

    Этот эндпоинт добавляет смену плана в базу данных.

    Args:
        data: Данные смены плана.
        db: Сессия базы данных.

    Returns:
        Status: Статус добавления нового объекта в базу данных.
    """
    return await insert_changed_plan(db, data)
