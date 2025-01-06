from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Statistics(BaseModel):
    unique_visitors: int
    visitor_count: int
    all_visits: int
    period: Optional[tuple[datetime, datetime]]
