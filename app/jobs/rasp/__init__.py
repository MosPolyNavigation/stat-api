import logging

from app.database import get_session_maker
from app.jobs.manager import scheduled_task
from app.jobs.rasp.parse import parse
from app.state import AppState

logger = logging.getLogger(f"uvicorn.{__name__}")


@scheduled_task(name="fetch_cur_rasp")
async def fetch_cur_rasp(state: AppState):
    # Скип, если воркер уже выполняется (другой триггер планировщика или ручной вызов).
    if state._rasp_lock.locked():
        return

    async with state._rasp_lock:
        try:
            logger.info("Starting schedule fetching")
            session_maker = get_session_maker()
            async with session_maker() as db:
                state.global_rasp = await parse(db)
            logger.info("Schedule fetching finished successful")
        except Exception as e:
            logger.warning(f"Schedule fetching failed with error: {e}")
