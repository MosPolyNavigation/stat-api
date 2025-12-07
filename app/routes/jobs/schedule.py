"""Маршрут запуска фоновой задачи обновления расписания."""

from fastapi import APIRouter, BackgroundTasks, Depends
from starlette.responses import Response

import app.globals as globals_
from app.helpers.permissions import require_rights
from app.jobs import fetch_cur_rasp
from app.schemas import Status


def register_endpoint(router: APIRouter):
    """Регистрирует POST `/schedule`."""

    @router.post(
        "/schedule",
        response_model=Status,
        dependencies=[Depends(require_rights("tasks", "edit"))],
        responses={
            409: {
                "model": Status,
                "description": "Задача уже выполняется",
                "content": {
                    "application/json": {
                        "example": {"status": "Запрос на обновление уже выполняется"}
                    }
                },
            }
        },
    )
    async def start_schedule_job(
        response: Response,
        background_tasks: BackgroundTasks,
    ):
        """Стартует фоновое обновление расписания, если оно еще не идет."""
        if globals_.locker:
            response.status_code = 409
            return Status(status="Запрос на обновление уже выполняется")
        background_tasks.add_task(fetch_cur_rasp)
        return Status()
