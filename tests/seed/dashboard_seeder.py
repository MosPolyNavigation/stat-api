from app.seed.base_seeder import BaseSeeder
from app.models import Dashboard


class DashboardSeeder(BaseSeeder):
    model = Dashboard

    def gather_data(self):
        return [
            {
                "id": 1,
                "display_order": 1,
                "event_type_id": 1,
                "dashboard_type_id": 1,
                "title_text": "Главный дашборд"
            },
            {
                "id": 2,
                "display_order": 2,
                "event_type_id": 1,
                "dashboard_type_id": 1,
                "title_text": "Вторичный дашборд"
            }
        ]
