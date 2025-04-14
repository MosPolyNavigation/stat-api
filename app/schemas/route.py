from pydantic import BaseModel, Field
from typing import List
from schemas.graph import VertexType


class RouteOut(BaseModel):
    to: str = Field()
    from_: str = Field(serialization_alias="from")
    steps: List["StepOut"] = Field()
    fullDistance: int = Field()


class StepOut(BaseModel):
    plan: str = Field()
    way: List["WayOut"] = Field()
    distance: int = Field()
    pass


class WayOut(BaseModel):
    id: str = Field()
    x: int = Field()
    y: int = Field()
    type: VertexType = Field()