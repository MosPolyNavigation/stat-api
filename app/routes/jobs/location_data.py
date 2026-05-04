from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response

from app.helpers.permissions import require_rights
from app.jobs.location_data.worker import fetch_location_data
from app.schemas import Status
from app.state import AppState


# Эндпоинт ручного запуска воркера
def register_endpoint(router: APIRouter):
    @router.post(
        "/locationData",
        response_model=Status,
        dependencies=[Depends(require_rights("tasks", "edit"))],
        responses={409: {"model": Status, "description": "Task is executed now"}},
    )
    async def start_location_data_job(
        request: Request,
        response: Response,
        background_tasks: BackgroundTasks,
    ) -> Status:
        state: AppState = request.app.state.app_state
        if state._location_lock.locked():
            response.status_code = 409
            return Status(status="Сейчас идет выполнение этой задачи")
        background_tasks.add_task(fetch_location_data, state=state)
        return Status()
