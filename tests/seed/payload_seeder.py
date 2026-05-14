from app.constants import (
    PAYLOAD_TYPE_AUDITORY_ID,
    PAYLOAD_TYPE_ENDPOINT_ID,
    PAYLOAD_TYPE_END_ID,
    PAYLOAD_TYPE_PLAN_ID,
    PAYLOAD_TYPE_START_ID,
    PAYLOAD_TYPE_SUCCESS_ID,
)
from app.models.event import Payload
from app.seed.base_seeder import BaseSeeder


class PayloadSeeder(BaseSeeder):
    model = Payload

    def gather_data(self) -> list[dict]:
        return [
            {
                "id": 1,
                "event_id": 1,
                "type_id": PAYLOAD_TYPE_AUDITORY_ID,
                "value": "a-100",
            },
            {
                "id": 2,
                "event_id": 1,
                "type_id": PAYLOAD_TYPE_SUCCESS_ID,
                "value": "true",
            },
            {
                "id": 3,
                "event_id": 2,
                "type_id": PAYLOAD_TYPE_START_ID,
                "value": "a-100",
            },
            {"id": 4, "event_id": 2, "type_id": PAYLOAD_TYPE_END_ID, "value": "a-101"},
            {
                "id": 5,
                "event_id": 2,
                "type_id": PAYLOAD_TYPE_SUCCESS_ID,
                "value": "true",
            },
            {
                "id": 6,
                "event_id": 3,
                "type_id": PAYLOAD_TYPE_START_ID,
                "value": "a-101",
            },
            {"id": 7, "event_id": 3, "type_id": PAYLOAD_TYPE_END_ID, "value": "a-102"},
            {
                "id": 8,
                "event_id": 3,
                "type_id": PAYLOAD_TYPE_SUCCESS_ID,
                "value": "false",
            },
            {
                "id": 9,
                "event_id": 4,
                "type_id": PAYLOAD_TYPE_ENDPOINT_ID,
                "value": "/api/get/route",
            },
            {"id": 10, "event_id": 5, "type_id": PAYLOAD_TYPE_PLAN_ID, "value": "A-3"},
        ]
