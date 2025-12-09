"""Эндпоинт для выдачи расписания аудиторий."""

from fastapi import APIRouter
from starlette.responses import Response
from typing import Union
from app.schemas import Status
from app.schemas.rasp.schedule import Schedule, Auditory
import app.globals as globals_


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт `/schedule` (Swagger tag `get`) для получения расписания.

    Args:
        router: Экземпляр APIRouter.

    Returns:
        APIRouter: Роутер с добавленным эндпоинтом.
    """

    @router.get(
        "/schedule",
        tags=["get"],
        response_model=Union[Schedule, Auditory, Status],
        responses={
            404: {
                'model': Status,
                'description': "No schedule for auditory",
                'content': {
                    'application/json': {
                        'example': {
                            'status': 'No schedule for specified auditory'
                        }
                    }
                }
            },
            425: {
                'model': Status,
                'description': "Schedule is not loaded yet",
                'content': {
                    'application/json': {
                        'example': {
                            'status': "Schedule is not loaded yet. Try again later"
                        }
                    }
                }
            }
        }
    )
    async def get_schedule(
            response: Response,
            auditory: Union[str, None] = None,
    ):
        """
        Возвращает расписание целиком или для конкретной аудитории.

        Args:
            response: Объект Response для управления статусом.
            auditory: Идентификатор аудитории или None для полного расписания.

        Returns:
            Schedule | Auditory | Status: Расписание либо описание ошибки.
        """
        if not globals_.global_rasp:
            response.status_code = 425
            return Status(status="Schedule is not loaded yet. Try again later")
        if not auditory:
            return globals_.global_rasp
        aud_schedule = globals_.global_rasp[auditory]
        if aud_schedule:
            return aud_schedule
        response.status_code = 404
        return Status(status="No schedule for specified auditory")

    return router
