from typing import Annotated
from pydantic import BaseModel, Field


PayloadValue = Annotated[str, Field(max_length=50)]


class EventCreateRequest(BaseModel):
    ident: str = Field(
        min_length=36,
        max_length=36,
    )
    event_type_id: int
    payloads: dict[int, PayloadValue] = Field(min_length=1)


class EventTypeResponse(BaseModel):
    id: int
    name: str


class PayloadTypeResponse(BaseModel):
    id: int
    name: str
    data_type: str
