from app.models.event import PayloadType
from app.seed.base_seeder import BaseSeeder
from app.constants import (
    PAYLOAD_TYPE_ENDPOINT_ID,
    PAYLOAD_TYPE_AUDITORY_ID,
    PAYLOAD_TYPE_START_ID,
    PAYLOAD_TYPE_END_ID,
    PAYLOAD_TYPE_SUCCESS_ID,
    PAYLOAD_TYPE_PLAN_ID,
    VALUE_TYPE_STRING_ID,
    VALUE_TYPE_BOOL_ID,
)


class PayloadTypeSeeder(BaseSeeder):
    model = PayloadType

    def gather_data(self) -> list[dict[str, int | str]]:
        return [
            {
                "id": PAYLOAD_TYPE_ENDPOINT_ID,
                "code_name": "endpoint",
                "description": "Посещённый endpoint сайта",
                "value_type_id": VALUE_TYPE_STRING_ID,
            },
            {
                "id": PAYLOAD_TYPE_AUDITORY_ID,
                "code_name": "auditory_id",
                "description": "Идентификатор выбранной аудитории",
                "value_type_id": VALUE_TYPE_STRING_ID,
            },
            {
                "id": PAYLOAD_TYPE_START_ID,
                "code_name": "start_id",
                "description": "Идентификатор начала маршрута",
                "value_type_id": VALUE_TYPE_STRING_ID,
            },
            {
                "id": PAYLOAD_TYPE_END_ID,
                "code_name": "end_id",
                "description": "Идентификатор назначения маршрута",
                "value_type_id": VALUE_TYPE_STRING_ID,
            },
            {
                "id": PAYLOAD_TYPE_SUCCESS_ID,
                "code_name": "success",
                "description": "Флаг успешности операции",
                "value_type_id": VALUE_TYPE_BOOL_ID,
            },
            {
                "id": PAYLOAD_TYPE_PLAN_ID,
                "code_name": "plan_id",
                "description": "Идентификатор выбранного плана",
                "value_type_id": VALUE_TYPE_STRING_ID,
            },
        ]
