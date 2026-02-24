from fastapi import APIRouter, BackgroundTasks, Depends, Response

import app.globals as globals_
from app.helpers.permissions import require_rights
from app.jobs.location_data import fetch_location_data
from app.schemas import Status

# Эндпоинт ручного запуска воркера
def register_endpoint(router: APIRouter):
    @router.post(
        "/locationData",
        response_model=Status,
        dependencies=[Depends(require_rights("tasks", "edit"))],
        responses={409: {"model": Status, "description": "Task is executed now"}},
    )
    async def start_location_data_job(response: Response, background_tasks: BackgroundTasks) -> Status:
        if globals_.location_data_locker:
            response.status_code = 409
            return Status(status="Сейчас идет выполнение этой задачи")
        background_tasks.add_task(fetch_location_data)
        return Status()