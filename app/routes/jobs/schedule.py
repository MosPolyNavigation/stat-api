from fastapi import APIRouter, BackgroundTasks, Depends, Request
from starlette.responses import Response

from app.helpers.permissions import require_rights_with_logging
from app.jobs.rasp import fetch_cur_rasp
from app.schemas import Status
from app.state import AppState
from app.services.user_logger_service import UserLoggerService, get_user_logger_service
from app.models import User


def register_endpoint(router: APIRouter):
    @router.post(
        "/schedule",
        response_model=Status,
        responses={
            409: {
                'model': Status,
                'description': "Task is executed now",
                'content': {
                    'application/json': {
                        'example': {
                            'status': 'Сейчас идет выполнение этой задачи'
                        }
                    }
                }
            }
        }
    )
    async def start_schedule_job(
        request: Request,
        response: Response,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(
            require_rights_with_logging("tasks", "edit", error_text="Попытка управления задачей без прав",)
        ),
        logger: UserLoggerService = Depends(get_user_logger_service),
    ):
        state: AppState = request.app.state.app_state
        if state._rasp_lock.locked():
            response.status_code = 409
            return Status(status="Сейчас идет выполнение этой задачи")
        background_tasks.add_task(fetch_cur_rasp, state=state)
        logger.log(current_user, "Запуск задачи schedule")
        return Status()
