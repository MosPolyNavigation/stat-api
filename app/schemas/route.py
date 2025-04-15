from pydantic import BaseModel, Field
from typing import List
from .graph import VertexType


class RouteOut(BaseModel):
    to: str = Field()
    from_: str = Field(serialization_alias="from")
    steps: List["StepOut"] = Field()
    fullDistance: int = Field()


class StepOut(BaseModel):
    plan: str = Field()
    way: List["WayOut"] = Field()
    distance: float = Field()
    pass


class WayOut(BaseModel):
    id: str = Field()
    x: float = Field()
    y: float = Field()
    type: VertexType = Field()
