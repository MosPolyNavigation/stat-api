from app.models.event import EventType
from app.seed.base_seeder import BaseSeeder
from app.constants import (
    EVENT_TYPE_SITE_ID,
    EVENT_TYPE_AUDS_ID,
    EVENT_TYPE_WAYS_ID,
    EVENT_TYPE_PLANS_ID,
)


class EventTypeSeeder(BaseSeeder):
    model = EventType

    def gather_data(self) -> list[dict[str, int | str]]:
        return [
            {
                "id": EVENT_TYPE_SITE_ID,
                "code_name": "site",
                "description": "События сайта",
            },
            {
                "id": EVENT_TYPE_AUDS_ID,
                "code_name": "auds",
                "description": "События выбора аудиторий",
            },
            {
                "id": EVENT_TYPE_WAYS_ID,
                "code_name": "ways",
                "description": "События построения маршрутов",
            },
            {
                "id": EVENT_TYPE_PLANS_ID,
                "code_name": "plans",
                "description": "События смены планов",
            },
        ]
