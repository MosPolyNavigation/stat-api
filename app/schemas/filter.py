from pydantic import BaseModel, Field


class Filter(BaseModel):
    api_key: str = Field(min_length=64,
                         max_length=64,
                         description="Api key for statistics gathering",
                         pattern=r"[a-f0-9]{64}")
    user_id: str | None = Field(default=None,
                                title="id",
                                description="Unique user id",
                                min_length=36,
                                max_length=36,
                                pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")
