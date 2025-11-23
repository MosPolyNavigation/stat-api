from fastapi import APIRouter, Depends, BackgroundTasks
from app.helpers.permissions import require_rights
from app.jobs import fetch_cur_rasp
from app.schemas import Status


def register_endpoint(router: APIRouter):
    @router.post(
        "/schedule",
        response_model=Status,
        dependencies=[Depends(require_rights("tasks", "edit"))]
    )
    async def start_schedule_job(
        background_tasks: BackgroundTasks
    ):
        background_tasks.add_task(fetch_cur_rasp)
        return Status()
