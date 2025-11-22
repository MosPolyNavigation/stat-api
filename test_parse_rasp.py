import asyncio
import json
from app.helpers.rasp.parse import parse


async def main():
    schedule = await parse()
    schedule_json_ready = {
        auditory_id: json.loads(auditory.model_dump_json())
        for auditory_id, auditory in schedule.items()
    }

    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(schedule_json_ready, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
