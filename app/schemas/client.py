from datetime import datetime

from pydantic import BaseModel, Field


class ClientIdentResponse(BaseModel):
    ident: str = Field(
        min_length=36,
        max_length=36,
    )
    creation_date: datetime


class ClientRegisterRequest(BaseModel):
    ident: str = Field(
        min_length=36,
        max_length=36,
    )
    first_interaction_date: datetime
