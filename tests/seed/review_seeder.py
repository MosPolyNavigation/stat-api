from datetime import datetime
from app.models import Review
from app.seed.base_seeder import BaseSeeder


class ReviewSeeder(BaseSeeder):
    model = Review

    def gather_data(self) -> list[dict]:
        return [
            {
                "id": 1,
                "client_id": 1,
                "problem_id": "way",
                "text": "test review",
                "review_status_id": 1,
                "creation_date": datetime(2026, 4, 25, 12, 0, 0),
            },
            {
                "id": 2,
                "client_id": 1,
                "problem_id": "way",
                "text": "test review with keyword",
                "review_status_id": 2,
                "creation_date": datetime(2026, 4, 26, 10, 0, 0),
            },
            {
                "id": 3,
                "client_id": 2,
                "problem_id": "nav",
                "text": "another test case",
                "review_status_id": 2,
                "creation_date": datetime(2026, 4, 25, 10, 0, 0),
            },
            {
                "id": 4,
                "client_id": 1,
                "problem_id": "auth",
                "text": "no keyword here",
                "review_status_id": 1,
                "creation_date": datetime(2026, 4, 24, 10, 0, 0),
            },
        ]
