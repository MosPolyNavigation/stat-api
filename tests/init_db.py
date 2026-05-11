from pathlib import Path
from pydantic import RootModel

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine
from fastapi import FastAPI

from app.helpers.seeder import apply_seeding
from app.models import Base
from app.schemas.rasp.schedule import Auditory
from app.jobs.location_data.worker import fetch_location_data
from app.seed.base_seeder import BaseSeeder
from tests.seed import TEST_ONLY_SEEDERS
from app.seed import (
    AllowedPayloadSeeder, DashboardTypeSeeder, EventTypeSeeder,
    GoalSeeder, PayloadTypeSeeder, ProblemSeeder,
    ReviewStatusSeeder, RightSeeder, RoleRightGoalSeeder,
    RoleSeeder, ValueTypeSeeder,
)


class Schedule(RootModel[dict[str, Auditory]]):
    pass


async def init_test_database(test_engine: AsyncEngine, test_session_maker: async_sessionmaker, app: FastAPI) -> None:
    """Инициализирует тестовую БД: создаёт таблицы + применяет сидеры + загружает state."""
    # 1️⃣ Создаём таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2️⃣ Применяем сидеры (и апп, и тест-специфичные)
    seeders: list[BaseSeeder] = [
        ProblemSeeder(), ReviewStatusSeeder(), GoalSeeder(), RightSeeder(),
        RoleSeeder(), RoleRightGoalSeeder(), ValueTypeSeeder(),
        EventTypeSeeder(), PayloadTypeSeeder(), AllowedPayloadSeeder(),
        DashboardTypeSeeder(),
        *TEST_ONLY_SEEDERS,
    ]
    
    await apply_seeding(seeders, session_maker=test_session_maker)

    # 3️⃣ Загружаем расписание в app.state
    schedule_path = Path(__file__).parent / "schedule_test.json"
    json_text = schedule_path.read_text(encoding="utf-8")
    app.state.app_state.global_rasp = Schedule.model_validate_json(json_text).root

    # 4️⃣ Инициализируем locationData
    await fetch_location_data(state=app.state.app_state)
