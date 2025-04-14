from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pytz import utc
from helpers.get_graph import parse_data, get_graph
from schemas import Graph
from typing import Dict

graph: Dict[str, Graph] = dict()

scheduler = AsyncIOScheduler(timezone=utc)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()

@scheduler.scheduled_job('cron', minute="*/10")
async def fetch_current_time():
    data = await parse_data()
    graph["BS"] = get_graph(data, "BS")
