from app.models import Role
from app.seed.base_seeder import BaseSeeder


class RoleSeeder(BaseSeeder):
    model = Role

    def gather_data(self) -> list[dict[str, int | str]]:
        return [
            {"id": 1, "name": "admin"},
        ]
