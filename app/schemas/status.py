from pydantic import BaseModel, Field


class Status(BaseModel):
    status: str = Field(title="Procedure-status", description="Status of procedure", default="OK")
