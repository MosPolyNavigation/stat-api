from datetime import datetime

from pydantic import BaseModel


class ClientIdentResponse(BaseModel):
    ident: str


class ClientRegisterRequest(BaseModel):
    ident: str
    first_interaction_date: datetime

