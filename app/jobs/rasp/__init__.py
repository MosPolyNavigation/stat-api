import logging
import app.globals as globals_
from app.database import AsyncSessionLocal
from app.jobs.rasp.parse import parse

logger = logging.getLogger(f"uvicorn.{__name__}")


async def fetch_cur_rasp():
    try:
        if globals_.locker:
            return
        globals_.locker = True
        logger.info("Starting schedule fetching")
        async with AsyncSessionLocal() as db:
            globals_.global_rasp = await parse(db)
        logger.info("Schedule fetching finished successful")
        globals_.locker = False
    except Exception as e:
        globals_.locker = False
        logger.warning(f"Schedule fetching failed with error: {e}")
