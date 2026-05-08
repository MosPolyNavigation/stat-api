from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response

from app.helpers.permissions import require_rights_with_logging
from app.jobs.location_data.worker import fetch_location_data
from app.schemas import Status
from app.state import AppState
from app.services.user_logger_service import UserLoggerService, get_user_logger_service
from app.models import User


# Эндпоинт ручного запуска воркера
def register_endpoint(router: APIRouter):
    @router.post(
        "/locationData",
        response_model=Status,
        responses={409: {"model": Status, "description": "Task is executed now"}},
    )
    async def start_location_data_job(
        request: Request,
        response: Response,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(
            require_rights_with_logging("tasks", "edit", error_text="Попытка управления задачей без прав",)
        ),
        logger: UserLoggerService = Depends(get_user_logger_service),
    ) -> Status:
        state: AppState = request.app.state.app_state
        if state._location_lock.locked():
            response.status_code = 409
            return Status(status="Сейчас идет выполнение этой задачи")
        background_tasks.add_task(fetch_location_data, state=state)
        logger.log(current_user, "Запуск задачи locationData")
        return Status()
