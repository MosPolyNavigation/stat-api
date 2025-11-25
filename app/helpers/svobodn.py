from typing import Union
from app.schemas.filter import FilterSvobodn
from app.schemas.rasp.schedule import ScheduleOut, Schedule, RaspOut, Auditory, DayOut, Day


def svobodn_day(day: Day | None, filter_: FilterSvobodn) -> DayOut:
    if filter_.para:
        para = str(filter_.para)
        if not day[para]:
            return {para: True}
        return dict({str(filter_.para): len(day[str(filter_.para)]) == 0})
    return dict({para: len(lesson) == 0 for para, lesson in day.items()})


def svobodn(schedule: Union[Auditory, None], filter_: FilterSvobodn) -> RaspOut:
    if filter_.day:
        return {filter_.day.name: svobodn_day(schedule.rasp[filter_.day.name], filter_)}
    return dict({day: svobodn_day(schedule.rasp[day], filter_) for day in
                 ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]})


def auditory_is_empty(schedule: Schedule, auds: list[str], filter_: FilterSvobodn) -> ScheduleOut:
    if len(auds) == 1:
        return svobodn(schedule.get(auds[0]), filter_)
    return dict({aud: svobodn(schedule.get(aud), filter_) for aud in auds})
