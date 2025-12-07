from pydantic import BaseModel
from typing import Union, Any


class AuditoryDto(BaseModel):
    title: str
    color: str


class VarietyDto(BaseModel):
    sbj: str
    teacher: str
    dts: str
    df: str
    dt: str
    auditories: list[AuditoryDto]
    shortRooms: list[str]
    location: str
    type: str
    week: str
    align: str
    e_link: Union[Any, None]


class GroupDto(BaseModel):
    title: str
    course: int
    dateFrom: str
    dateTo: str
    evening: int
    comment: str

type LessonDto = list[VarietyDto]
type DayDto = dict[str, LessonDto]

class Dto(BaseModel):
    status: str
    grid: dict[str, DayDto]
    group: GroupDto
    isSession: bool
