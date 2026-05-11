from app.models.review_status import ReviewStatus
from app.seed.base_seeder import BaseSeeder
from app.constants import REVIEW_STATUSES


class ReviewStatusSeeder(BaseSeeder):
    model = ReviewStatus

    def gather_data(self) -> list[dict[str, int|str]]:
        return [{'id': k, 'name': v} for k, v in REVIEW_STATUSES.items()]
