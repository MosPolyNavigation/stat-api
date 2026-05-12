from app.models import Problem
from app.seed.base_seeder import BaseSeeder
from app.constants import PROBLEMS


class ProblemSeeder(BaseSeeder):
    model = Problem

    def gather_data(self) -> list[dict[str, str]]:
        return [{"id": v, } for v in PROBLEMS]
