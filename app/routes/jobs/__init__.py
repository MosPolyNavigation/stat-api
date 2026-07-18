from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from app.helpers.permissions import require_rights_with_logging
from app.jobs.api.deps import get_job_manager
from app.jobs.manager import JobManager
from app.models import User
from app.services.user_logger_service import UserLoggerService, get_user_logger_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("")
async def list_jobs(
    job_manager: JobManager = Depends(get_job_manager),
    current_user: User = Depends(
        require_rights_with_logging(
            "tasks",
            "view",
            error_text="Попытка управления задачей без прав",
        )
    ),
    logger: UserLoggerService = Depends(get_user_logger_service),
):
    """Список всех зарегистрированных задач со статусами."""
    logger.log(current_user, "Просмотр списка задач")
    return {"jobs": job_manager.get_registered_tasks()}


@router.get("/{name}")
async def get_job(
    name: str,
    job_manager: JobManager = Depends(get_job_manager),
    current_user: User = Depends(
        require_rights_with_logging(
            "tasks",
            "view",
            error_text="Попытка управления задачей без прав",
        )
    ),
    logger: UserLoggerService = Depends(get_user_logger_service),
):
    """Детали задачи + последние 5 запусков."""
    detail = job_manager.get_task_detail(name)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Job '{name}' not found")
    detail["last_runs"] = await job_manager.get_history(name, limit=5)
    logger.log(current_user, f"Просмотр задачи {name}")
    return detail


@router.post("/{name}/trigger")
async def trigger_job(
    name: str,
    background_tasks: BackgroundTasks,
    job_manager: JobManager = Depends(get_job_manager),
    current_user: User = Depends(
        require_rights_with_logging(
            "tasks",
            "create",
            error_text="Попытка управления задачей без прав",
        )
    ),
    logger: UserLoggerService = Depends(get_user_logger_service),
):
    """Ручной запуск задачи. Возвращает run_id сразу, не ждёт завершения."""
    if job_manager.get_task_detail(name) is None:
        raise HTTPException(status_code=404, detail=f"Job '{name}' not found")
    if job_manager.is_running(name):
        raise HTTPException(status_code=409, detail="Task is already running")
    run_id = await job_manager.trigger_now(name, background_tasks)
    logger.log(current_user, f"Запуск задачи {name}")
    return {"run_id": run_id, "status": "accepted"}


@router.post("/{name}/pause")
async def pause_job(
    name: str,
    job_manager: JobManager = Depends(get_job_manager),
    current_user: User = Depends(
        require_rights_with_logging(
            "tasks",
            "edit",
            error_text="Попытка управления задачей без прав",
        )
    ),
    logger: UserLoggerService = Depends(get_user_logger_service),
):
    """Приостановить задачу в планировщике."""
    try:
        job_manager.pause_job(name)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    logger.log(current_user, f"Приостановка задачи {name}")
    return {"status": "paused"}


@router.post("/{name}/resume")
async def resume_job(
    name: str,
    job_manager: JobManager = Depends(get_job_manager),
    current_user: User = Depends(
        require_rights_with_logging(
            "tasks",
            "edit",
            error_text="Попытка управления задачей без прав",
        )
    ),
    logger: UserLoggerService = Depends(get_user_logger_service),
):
    """Возобновить задачу в планировщике."""
    try:
        job_manager.resume_job(name)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    logger.log(current_user, f"Продолжение задачи {name}")
    return {"status": "resumed"}


@router.post("/{name}/stop")
async def stop_job(
    name: str,
    job_manager: JobManager = Depends(get_job_manager),
    current_user: User = Depends(
        require_rights_with_logging(
            "tasks",
            "delete",
            error_text="Попытка управления задачей без прав",
        )
    ),
    logger: UserLoggerService = Depends(get_user_logger_service),
):
    """Удалить задачу из планировщика (до перезапуска сервиса)."""
    try:
        job_manager.stop_job(name)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    logger.log(current_user, f"Остановка задачи {name}")
    return {"status": "stopped"}


@router.get("/{name}/history")
async def get_job_history(
    name: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    job_manager: JobManager = Depends(get_job_manager),
    current_user: User = Depends(
        require_rights_with_logging(
            "tasks",
            "view",
            error_text="Попытка управления задачей без прав",
        )
    ),
    logger: UserLoggerService = Depends(get_user_logger_service),
):
    """История запусков задачи с пагинацией."""
    if job_manager.get_task_detail(name) is None:
        raise HTTPException(status_code=404, detail=f"Job '{name}' not found")
    history = await job_manager.get_history(name, limit=limit, offset=offset)
    logger.log(current_user, f"Просмотр истории задачи {name}")
    return {"history": history, "limit": limit, "offset": offset}
