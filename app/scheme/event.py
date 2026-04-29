from typing import Annotated, Optional

from pydantic import BaseModel, Field


CodeName = Annotated[str, Field(min_length=1, max_length=20)]
Description = Annotated[Optional[str], Field(default=None, max_length=100)]
PayloadValue = Annotated[str, Field(max_length=50)]


class EventCreateRequest(BaseModel):
    ident: str = Field(min_length=36, max_length=36)
    event_type_id: int
    payloads: dict[int, PayloadValue] = Field(min_length=1)


class EventTypeFilter(BaseModel):
    id: Optional[int] = None
    code_name: Optional[CodeName] = None


class EventTypeCreate(BaseModel):
    id: Optional[int] = None
    code_name: CodeName
    description: Description = None


class EventTypeUpdate(BaseModel):
    code_name: Optional[CodeName] = None
    description: Description = None


class ValueTypeFilter(BaseModel):
    id: Optional[int] = None
    name: Optional[CodeName] = None


class ValueTypeCreate(BaseModel):
    id: Optional[int] = None
    name: CodeName
    description: Description = None


class ValueTypeUpdate(BaseModel):
    name: Optional[CodeName] = None
    description: Description = None


class PayloadTypeFilter(BaseModel):
    id: Optional[int] = None
    code_name: Optional[CodeName] = None
    value_type_id: Optional[int] = None


class PayloadTypeCreate(BaseModel):
    id: Optional[int] = None
    code_name: CodeName
    value_type_id: int
    description: Description = None


class PayloadTypeUpdate(BaseModel):
    code_name: Optional[CodeName] = None
    value_type_id: Optional[int] = None
    description: Description = None


class AllowedPayloadRuleFilter(BaseModel):
    event_type_id: Optional[int] = None
    payload_type_id: Optional[int] = None


class AllowedPayloadRuleCreate(BaseModel):
    event_type_id: int
    payload_type_id: int


class AllowedPayloadRuleUpdate(BaseModel):
    event_type_id: int
    payload_type_id: int
    new_event_type_id: int
    new_payload_type_id: int
