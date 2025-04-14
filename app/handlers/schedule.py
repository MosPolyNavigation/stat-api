from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.helpers.get_graph import parse_data, get_graph
import app.globals as globals

async def fetch_cur_data():
    data = await parse_data()
    globals.global_graph["BS"] = await get_graph(data, "BS")

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_cur_data, "interval", minutes=10)
    await fetch_cur_data()
    scheduler.start()
    yield
    scheduler.shutdown()
