from app.models import UserRole
from app.seed.base_seeder import BaseSeeder


class UserRoleSeeder(BaseSeeder):
    model = UserRole
    pk_fields = ("user_id", "role_id")

    def gather_data(self) -> list[dict]:
        return [{"user_id": 1, "role_id": 1}]
