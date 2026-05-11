from app.models.dashboard import DashboardType
from app.seed.base_seeder import BaseSeeder
from app.constants import DASHBOARD_TYPE_CHART_ID, DASHBOARD_TYPE_AVG_ID


class DashboardTypeSeeder(BaseSeeder):
    model = DashboardType

    def gather_data(self) -> list[dict[str, int | str]]:
        return [
            {"id": DASHBOARD_TYPE_CHART_ID, "code_name": "chart", "description": "График статистики"},
            {"id": DASHBOARD_TYPE_AVG_ID, "code_name": "avg", "description": "Агрегированная статистика"},
        ]
