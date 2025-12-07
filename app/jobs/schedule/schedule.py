import logging
from app.jobs.schedule.get_graph import parse_data, get_graph
from app.schemas import DataEntry
import app.globals as globals_

logger = logging.getLogger(f"uvicorn.{__name__}")


async def fetch_cur_data():
    try:
        logger.info("Starting graph fetching")
        data: DataEntry = await parse_data()
        for loc_name in map(lambda loc: loc.id, data.Locations):
            globals_.global_graph[loc_name] = await get_graph(data, loc_name)
        logger.info("Graph fetching finished successful")
    except Exception as e:
        logger.warning(f"Graph fetching failed with error: {e}")
