import asyncio
import json
from app.config import load_settings
from app.database import get_session_maker, init_database
from app.jobs.rasp import parse


async def main():
    init_database(load_settings())
    session_maker = get_session_maker()
    async with session_maker() as db:
        schedule = await parse(db)
    schedule_json_ready = {
        auditory_id: json.loads(auditory.model_dump_json())
        for auditory_id, auditory in schedule.items()
    }

    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(schedule_json_ready, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
