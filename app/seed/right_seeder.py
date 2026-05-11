from app.models.auth.right import Right
from app.seed.base_seeder import BaseSeeder
from app.constants import RIGHTS_BY_ID


class RightSeeder(BaseSeeder):
    model = Right

    def gather_data(self) -> list[dict[str, int | str]]:
        return [{"id": k, "name": v} for k, v in RIGHTS_BY_ID.items()]
