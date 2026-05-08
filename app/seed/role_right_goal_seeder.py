from app.models.auth.role_right_goal import RoleRightGoal
from app.seed.base_seeder import BaseSeeder
from app.constants import GOAL_RIGHTS


class RoleRightGoalSeeder(BaseSeeder):
    model = RoleRightGoal

    pk_fields = ("role_id", "right_id", "goal_id")

    def gather_data(self) -> list[dict[str, int|str]]:
        return [{"role_id": 1, "right_id": t[1], "goal_id": t[0], "can_grant": True} for t in GOAL_RIGHTS]
