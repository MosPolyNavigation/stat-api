from datetime import datetime
from app.constants import (
    EVENT_TYPE_AUDS_ID,
    EVENT_TYPE_PLANS_ID,
    EVENT_TYPE_SITE_ID,
    EVENT_TYPE_WAYS_ID,
)
from app.models.event import Event
from app.seed.base_seeder import BaseSeeder


class EventSeeder(BaseSeeder):
    model = Event

    def gather_data(self) -> list[dict]:
        return [
            {
                "id": 1,
                "client_id": 1,
                "event_type_id": EVENT_TYPE_AUDS_ID,
                "trigger_time": datetime(2026, 4, 25, 10, 0, 0),
            },
            {
                "id": 2,
                "client_id": 1,
                "event_type_id": EVENT_TYPE_WAYS_ID,
                "trigger_time": datetime(2026, 4, 25, 11, 0, 0),
            },
            {
                "id": 3,
                "client_id": 2,
                "event_type_id": EVENT_TYPE_WAYS_ID,
                "trigger_time": datetime(2026, 4, 26, 11, 0, 0),
            },
            {
                "id": 4,
                "client_id": 2,
                "event_type_id": EVENT_TYPE_SITE_ID,
                "trigger_time": datetime(2026, 4, 26, 12, 0, 0),
            },
            {
                "id": 5,
                "client_id": 3,
                "event_type_id": EVENT_TYPE_PLANS_ID,
                "trigger_time": datetime(2026, 4, 26, 12, 0, 0),
            },
        ]
