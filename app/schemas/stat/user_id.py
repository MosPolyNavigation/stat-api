from pydantic import BaseModel, Field


class ClientIdCheck(BaseModel):
    client_id: str = Field(
        title="Client-id",
        description="Unique client id",
        min_length=36,
        max_length=36,
    )
