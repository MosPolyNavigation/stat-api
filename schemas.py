from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class UUID(BaseModel):
    id: str = Field(title="id", description="Unique user id", min_length=36, max_length=36, pattern=r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{8}")
    creation_date: datetime | None = Field(default=None)
    model_config = ConfigDict(from_attributes=True)
