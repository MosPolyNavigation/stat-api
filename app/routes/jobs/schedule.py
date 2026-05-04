from fastapi import APIRouter, BackgroundTasks, Depends, Request
from starlette.responses import Response

from app.helpers.permissions import require_rights
from app.jobs.rasp import fetch_cur_rasp
from app.schemas import Status
from app.state import AppState


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
        request: Request,
        response: Response,
        background_tasks: BackgroundTasks
    ):
        state: AppState = request.app.state.app_state
        if state._rasp_lock.locked():
            response.status_code = 409
            return Status(status="Сейчас идет выполнение этой задачи")
        background_tasks.add_task(fetch_cur_rasp, state=state)
        return Status()
