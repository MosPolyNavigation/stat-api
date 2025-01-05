from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Statistics(BaseModel):
    unique_visitors: int
    all_visitors: int
    period: Optional[tuple[datetime, datetime]]
