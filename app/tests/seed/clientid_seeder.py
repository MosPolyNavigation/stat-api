from datetime import datetime
from app.models.event import ClientId
from app.seed.base_seeder import BaseSeeder

class ClientIdSeeder(BaseSeeder):
    model = ClientId

    def gather_data(self) -> list[dict[str, int | str | datetime]]:
        return [
            {"id": 1, "ident": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec", "creation_date": datetime(2026, 4, 25, 9, 0, 0)},
            {"id": 2, "ident": "22e1a4b8-7fa7-4501-9faa-541a5e0ff1ec", "creation_date": datetime(2026, 4, 26, 9, 0, 0)},
        ]
