from typing import TypedDict

from app.jobs.manager import JobManager

# Импорт воркеров, чтобы @scheduled_task отработал при импорте модуля
# и заполнил приватный реестр. Без этих импортов JobManager.setup_from_config
# не найдёт задачу по имени и пропустит её с warning'ом.
from app.jobs.location_data.worker import fetch_location_data  # noqa: F401
from app.jobs.rasp import fetch_cur_rasp  # noqa: F401


class AppLifespanState(TypedDict):
    """Состояние, возвращаемое из lifespan и прокидываемое FastAPI в request.state."""

    job_manager: JobManager
