from pydantic import BaseModel, Field, model_validator, field_validator
from app.config import Settings
from typing import Any


class PaginationBase(BaseModel):
    api_key: str = Field(min_length=64,
                         max_length=64,
                         description="Api key for statistics gathering",
                         pattern=r"[a-f0-9]{64}")
    page: int | None = Field(default=None, ge=1, description="Page number, starting from 1")
    user_id: str | None = Field(default=None,
                                title="id",
                                description="Unique user id",
                                min_length=36,
                                max_length=36,
                                pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")

    per_page: int | None = Field(default=None, gt=0, le=100, description="Numbers of items per_page")

    @classmethod
    @field_validator('api_key')
    def check_key(cls, v: Any):
        if v != Settings().admin_key:
            raise ValueError("Specified api_key is not present in app")
        return v

    @model_validator(mode='after')
    def check_both(self):
        if (self.page is None) != (self.per_page is None):
            raise ValueError('Both page and per_page must be either set or None')
        return self
