from pydantic import BaseModel, Field
from datetime import date
from typing import Union


class Variety(BaseModel):
    groupNames: list[str]
    groupType: str
    discipline: str
    teachers: list[str]
    dt: date
    df: date
    dts: str


type Lesson = list[Variety]
type Day = dict[str, Lesson]


class Rasp(BaseModel):
    monday: Union[Day, None] = Field(default=None)
    tuesday: Union[Day, None] = Field(default=None)
    wednesday: Union[Day, None] = Field(default=None)
    thursday: Union[Day, None] = Field(default=None)
    friday: Union[Day, None] = Field(default=None)
    saturday: Union[Day, None] = Field(default=None)

    def merge_day(self, day_name: str):
        day_schedule: Union[Day, None] = getattr(self, day_name)
        if day_schedule is None:
            return
        for lesson_key, lesson_list in day_schedule.items():
            variety_map: dict[tuple[str, date, date, str], Variety] = {}

            for var in lesson_list:
                key = (
                    var.discipline,
                    var.dt,
                    var.df,
                    var.dts
                )

                if key in variety_map:
                    existing = variety_map[key]
                    for group_name in var.groupNames:
                        if group_name not in existing.groupNames:
                            existing.groupNames.append(group_name)
                else:
                    variety_map[key] = var

            day_schedule[lesson_key] = list(variety_map.values())

    def merge(self):
        for day_name in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
            self.merge_day(day_name)


class Auditory(BaseModel):
    id: str
    rasp: Rasp
    link: Union[str, None] = Field(default=None)


type Schedule = dict[str, Auditory]
