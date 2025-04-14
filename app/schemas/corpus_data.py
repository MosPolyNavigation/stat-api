from pydantic import BaseModel
from . import LocationData
from typing import List


class CorpusData(BaseModel):
    id: str
    title: str
    available: bool
    location: LocationData
    stairs: List[List[str]]
