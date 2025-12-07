"""Утилиты для вычисления свободных аудиторий в расписании."""

from typing import Union

from app.schemas.filter import FilterSvobodn
from app.schemas.rasp.schedule import Auditory, Day, DayOut, RaspOut, Schedule, ScheduleOut


def svobodn_day(day: Day | None, filter_: FilterSvobodn) -> DayOut:
    """Возвращает словарь свободности по парам в выбранный день."""
    if filter_.para:
        para = str(filter_.para)
        if not day[para]:
            return {para: True}
        return {str(filter_.para): len(day[str(filter_.para)]) == 0}
    return {para: len(lesson) == 0 for para, lesson in day.items()}


def svobodn(schedule: Union[Auditory, None], filter_: FilterSvobodn) -> RaspOut:
    """Возвращает свободность расписания аудиторий по фильтрам."""
    days_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    if not schedule:
        if filter_.para:
            lessons = {str(filter_.para): True}
        else:
            lessons = {str(num): True for num in range(1, 8)}
        days = {day: lessons for day in days_names}
        if filter_.day:
            return {filter_.day.name: days.get(filter_.day.name)}
        else:
            return days
    if filter_.day:
        return {filter_.day.name: svobodn_day(schedule.rasp.__dict__[filter_.day.name], filter_)}
    return {day: svobodn_day(schedule.rasp.__dict__[day], filter_) for day in days_names}


def auditory_is_empty(schedule: Schedule, auds: list[str], filter_: FilterSvobodn) -> ScheduleOut:
    """Строит словарь свободности для набора аудиторий."""
    if len(auds) == 1:
        return svobodn(schedule.get(auds[0]), filter_)
    return {aud: svobodn(schedule.get(aud), filter_) for aud in auds}
