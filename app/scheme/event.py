from typing import Dict

from pydantic import BaseModel, Field


class EventCreateRequest(BaseModel):
    event_type_id: int
    payloads: Dict[int, str] = Field(min_length=1)


class EventTypeResponse(BaseModel):
    id: int
    name: str


class PayloadTypeResponse(BaseModel):
    id: int
    name: str
    data_type: str

