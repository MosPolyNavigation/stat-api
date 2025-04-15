from pydantic import BaseModel
from typing import List, Tuple


class LocationData(BaseModel):
    id: str
    title: str
    short: str
    available: bool
    address: str
    crossings: List[Tuple[str, str, int]]
