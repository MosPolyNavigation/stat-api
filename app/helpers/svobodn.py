from typing import Optional
from app.schemas.filter import FilterSvobodn
from app.schemas.rasp.schedule import ScheduleOut, Schedule, RaspOut, Auditory, DayOut, Day


def svobodn_day(day: Optional[Day], filter_: FilterSvobodn) -> DayOut:
    """
    Определяет, свободна ли аудитория в конкретный день.

    Args:
        day: Расписание дня {para_number: [lessons]} или None
        filter_: Фильтр с опциональным номером пары

    Returns:
        {para_number_str: is_free_bool} — True если слот свободен
    """
    # Если расписания нет — считаем все слоты свободными
    if day is None:
        if filter_.para is not None:
            return {str(filter_.para): True}
        return {str(num): True for num in range(1, 8)}

    # Фильтр по конкретной паре
    if filter_.para is not None:
        para_key = str(filter_.para)
        # Если пары нет в расписании или список занятий пуст — слот свободен
        lessons = day.get(para_key)
        is_free = lessons is None or len(lessons) == 0
        return {para_key: is_free}

    # Проверяем все пары в дне
    return {
        para: (lessons is None or len(lessons) == 0)
        for para, lessons in day.items()
    }


def svobodn(schedule: Optional[Auditory], filter_: FilterSvobodn) -> RaspOut:
    """
    Определяет свободные слоты для одной аудитории.

    Args:
        schedule: Данные аудитории или None (если данных нет)
        filter_: Фильтр по дню/паре

    Returns:
        {day_name: {para: is_free}}
    """
    days_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

    # Если данных об аудитории нет — считаем всё свободным
    if schedule is None:
        default_lessons = (
            {str(filter_.para): True}
            if filter_.para is not None
            else {str(num): True for num in range(1, 8)}
        )
        days = {day: default_lessons for day in days_names}

        if filter_.day is not None:
            return {filter_.day.name: days.get(filter_.day.name, {})}
        return days

    # Есть расписание — проверяем каждый день
    if filter_.day is not None:
        day_name = filter_.day.name
        day_data = getattr(schedule.rasp, day_name, None)
        return {day_name: svobodn_day(day_data, filter_)}

    return {
        day: svobodn_day(getattr(schedule.rasp, day, None), filter_)
        for day in days_names
    }


def auditory_is_empty(
    schedule: Schedule,
    auds: list[str],
    filter_: FilterSvobodn
) -> ScheduleOut:
    """
    Проверяет свободность указанных аудиторий.

    Args:
        schedule: {aud_id: Auditory}
        auds: список id аудиторий для проверки
        filter_: фильтр

    Returns:
        RaspOut для одной аудитории ИЛИ {aud_id: RaspOut} для нескольких
    """
    if len(auds) == 1:
        aud_data = schedule.get(auds[0])
        return svobodn(aud_data, filter_)

    return {
        aud: svobodn(schedule.get(aud), filter_)
        for aud in auds
    }
