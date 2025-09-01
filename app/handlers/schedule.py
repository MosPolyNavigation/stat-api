from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.helpers.get_graph import parse_data, get_graph
from app.schemas import DataEntry
import app.globals as globals_



async def fetch_cur_data():
    try:
        data: DataEntry = await parse_data()
        for loc_name in map(lambda loc: loc.id, data.Locations):
            globals_.global_graph[loc_name] = await get_graph(data, loc_name)
    except Exception as e:
        print(e)
        print("Data parsing failed. No graphs loaded")


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})
    scheduler.add_job(fetch_cur_data, "interval", minutes=10)
    await fetch_cur_data()
    scheduler.start()
    yield
    scheduler.shutdown()
