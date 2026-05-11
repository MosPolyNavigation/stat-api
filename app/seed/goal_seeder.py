from app.models.auth.goal import Goal
from app.seed.base_seeder import BaseSeeder
from app.constants import GOALS_BY_ID


class GoalSeeder(BaseSeeder):
    model = Goal

    def gather_data(self) -> list[dict[str, int|str]]:
        return [{"id": k, "name": v} for k, v in GOALS_BY_ID.items()]
