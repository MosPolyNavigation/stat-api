"""Помощники для расчета свободных аудиторий по расписанию."""

from typing import Union
from app.schemas.filter import FilterSvobodn
from app.schemas.rasp.schedule import ScheduleOut, Schedule, RaspOut, Auditory, DayOut, Day


def svobodn_day(day: Day | None, filter_: FilterSvobodn) -> DayOut:
    """
    Проверяет, свободны ли пары в конкретный день согласно фильтру.

    Args:
        day: Расписание на день или None.
        filter_: Параметры фильтрации (конкретная пара/день).

    Returns:
        DayOut: Словарь, где ключ — номер пары, значение — булево о свободности.
    """
    if filter_.para:
        para = str(filter_.para)
        if not day[para]:
            return {para: True}
        return dict({str(filter_.para): len(day[str(filter_.para)]) == 0})
    return dict({para: len(lesson) == 0 for para, lesson in day.items()})


def svobodn(schedule: Union[Auditory, None], filter_: FilterSvobodn) -> RaspOut:
    """
    Возвращает информацию о свободности аудиторий по всем дням согласно фильтру.

    Args:
        schedule: Расписание аудитории или None, если данных нет.
        filter_: Параметры фильтрации свободных аудиторий.

    Returns:
        RaspOut: Словарь по дням недели с булевыми значениями свободности по парам.
    """
    days_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    if not schedule:
        if filter_.para:
            lessons = {str(filter_.para): True}
        else:
            lessons = dict({str(num): True for num in range(1, 8)})
        days = dict({day: lessons for day in days_names})
        if filter_.day:
            return {filter_.day.name: days.get(filter_.day.name)}
        else:
            return days
    if filter_.day:
        return {filter_.day.name: svobodn_day(schedule.rasp.__dict__[filter_.day.name], filter_)}
    return dict({day: svobodn_day(schedule.rasp.__dict__[day], filter_) for day in days_names})


def auditory_is_empty(schedule: Schedule, auds: list[str], filter_: FilterSvobodn) -> ScheduleOut:
    """
    Проверяет, свободны ли указанные аудитории.

    Args:
        schedule: Полное расписание.
        auds: Список идентификаторов аудиторий.
        filter_: Параметры фильтрации свободных аудиторий.

    Returns:
        ScheduleOut: Результат проверки для каждой аудитории.
    """
    if len(auds) == 1:
        return svobodn(schedule.get(auds[0]), filter_)
    return dict({aud: svobodn(schedule.get(aud), filter_) for aud in auds})
