from datetime import datetime
from app.models.review import Review
from app.seed.base_seeder import BaseSeeder

class ReviewSeeder(BaseSeeder):
    model = Review

    def gather_data(self) -> list[dict]:
        return [{
            "id": 1, "client_id": 1, "problem_id": "way", "text": "test review",
            "review_status_id": 1, "creation_date": datetime(2026, 4, 25, 12, 0, 0)
        }]
