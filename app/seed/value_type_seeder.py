from app.models.event import ValueType
from app.seed.base_seeder import BaseSeeder
from app.constants import VALUE_TYPE_INT_ID, VALUE_TYPE_STRING_ID, VALUE_TYPE_BOOL_ID


class ValueTypeSeeder(BaseSeeder):
    model = ValueType

    def gather_data(self) -> list[dict[str, int | str]]:
        return [
            {
                "id": VALUE_TYPE_INT_ID,
                "name": "int",
                "description": "Целочисленное значение",
            },
            {
                "id": VALUE_TYPE_STRING_ID,
                "name": "string",
                "description": "Строковое значение",
            },
            {
                "id": VALUE_TYPE_BOOL_ID,
                "name": "bool",
                "description": "Булево значение",
            },
        ]
