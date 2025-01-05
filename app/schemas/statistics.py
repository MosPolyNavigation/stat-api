from pydantic import BaseModel
from datetime import datetime


class Statistics(BaseModel):
    unique_visitors: int
    visitor_count: int
    all_visits: int
    period: tuple[datetime, datetime] | None
