from fastapi import APIRouter, Depends, BackgroundTasks
from starlette.responses import Response

from app.helpers.permissions import require_rights
from app.jobs import fetch_cur_rasp
from app.schemas import Status
import app.globals as globals_


def register_endpoint(router: APIRouter):
    @router.post(
        "/schedule",
        response_model=Status,
        dependencies=[Depends(require_rights("tasks", "edit"))],
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
        response: Response,
        background_tasks: BackgroundTasks
    ):
        if globals_.locker:
            response.status_code = 409
            return Status(status="Сейчас идет выполнение этой задачи")
        background_tasks.add_task(fetch_cur_rasp)
        return Status()
