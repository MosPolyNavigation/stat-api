from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


UUID_PATTERN = r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}"


class ClientIdentRequest(BaseModel):
    ident: str = Field(
        default_factory=lambda: str(uuid4()),
        min_length=36,
        max_length=36,
        pattern=UUID_PATTERN,
    )


class ClientIdentResponse(BaseModel):
    ident: str
    creation_date: datetime
    model_config = ConfigDict(from_attributes=True)


class EventPayloadRequest(BaseModel):
    type_id: int = Field(gt=0)
    value: str = Field(min_length=1, max_length=50)

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value(cls, value):
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)


class EventCreateRequest(BaseModel):
    ident: str = Field(
        min_length=36,
        max_length=36,
        pattern=UUID_PATTERN,
    )
    event_type_id: int = Field(gt=0)
    payloads: list[EventPayloadRequest] = Field(min_length=1)


class EventTypeFilter(BaseModel):
    id: Optional[int] = None
    code_name: Optional[str] = Field(default=None, min_length=1, max_length=20)


class EventTypeCreateRequest(BaseModel):
    id: Optional[int] = Field(default=None, gt=0)
    code_name: str = Field(min_length=1, max_length=20)
    description: Optional[str] = Field(default=None, max_length=100)


class EventTypeUpdateRequest(BaseModel):
    code_name: Optional[str] = Field(default=None, min_length=1, max_length=20)
    description: Optional[str] = Field(default=None, max_length=100)


class ValueTypeFilter(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=20)


class ValueTypeCreateRequest(BaseModel):
    id: Optional[int] = Field(default=None, gt=0)
    name: str = Field(min_length=1, max_length=20)
    description: Optional[str] = Field(default=None, max_length=100)


class ValueTypeUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=20)
    description: Optional[str] = Field(default=None, max_length=100)


class PayloadTypeFilter(BaseModel):
    id: Optional[int] = None
    code_name: Optional[str] = Field(default=None, min_length=1, max_length=20)
    value_type_id: Optional[int] = None


class PayloadTypeCreateRequest(BaseModel):
    id: Optional[int] = Field(default=None, gt=0)
    code_name: str = Field(min_length=1, max_length=20)
    description: Optional[str] = Field(default=None, max_length=100)
    value_type_id: int = Field(gt=0)


class PayloadTypeUpdateRequest(BaseModel):
    code_name: Optional[str] = Field(default=None, min_length=1, max_length=20)
    description: Optional[str] = Field(default=None, max_length=100)
    value_type_id: Optional[int] = Field(default=None, gt=0)


class AllowedPayloadRuleFilter(BaseModel):
    event_type_id: Optional[int] = None
    payload_type_id: Optional[int] = None


class AllowedPayloadRuleCreateRequest(BaseModel):
    event_type_id: int = Field(gt=0)
    payload_type_id: int = Field(gt=0)


class AllowedPayloadRuleUpdateRequest(BaseModel):
    event_type_id: int = Field(gt=0)
    payload_type_id: int = Field(gt=0)
