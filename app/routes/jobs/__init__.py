from fastapi import APIRouter

from app.jobs.api.endpoints import router as jobs_api_router
from .schedule import register_endpoint as register_schedule
from .location_data import register_endpoint as register_locationData

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# Старые эндпоинты ручного запуска (обратная совместимость)
register_schedule(router)
register_locationData(router)

# Новый API управления задачами (GET /api/jobs, POST /api/jobs/{name}/trigger, и т.д.)
router.include_router(jobs_api_router)
