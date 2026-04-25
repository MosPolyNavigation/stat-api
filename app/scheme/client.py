from datetime import datetime

from pydantic import BaseModel, Field


class ClientIdentResponse(BaseModel):
    ident: str = Field(
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}",
    )


class ClientRegisterRequest(BaseModel):
    ident: str = Field(
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}",
    )
    first_interaction_date: datetime
