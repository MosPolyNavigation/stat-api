from pydantic import BaseModel, Field

from app.scheme.event import EventCreateRequest


class EventTypeResponse(BaseModel):
    id: int
    name: str


class PayloadTypeResponse(BaseModel):
    id: int
    name: str
    data_type: str
