"""Фильтры для расписания и статистики, используемые в swagger-эндпоинтах."""

from datetime import datetime, time
from sqlalchemy import Select
from typing import Any, Optional
from app import schemas
from app.schemas.filter import FilterSvobodn
from app.schemas.rasp.schedule import Schedule, Auditory, Rasp, Day, Lesson


def filter_by_user(
        data_model: Any,
        params: schemas.Filter
) -> Select:
    """
    Строит Select с фильтром по user_id, если он передан в запросе.

    Используется Swagger-эндпоинтами статистики для точечного отбора данных.

    Args:
        data_model: SQLAlchemy модель или выражение, к которому применяется фильтрация.
        params: Параметры фильтра из Swagger (schemas.Filter).

    Returns:
        Select: Запрос, дополненный условием по user_id.
    """
    query = Select(data_model)
    if params.user_id is not None:
        query = query.filter_by(user_id=params.user_id)
    return query


def filter_by_date(
        params: schemas.FilterQuery
) -> Optional[tuple[datetime, datetime]]:
    """
    Определяет временные границы для фильтрации статистики по датам.

    Если указаны обе даты — задается закрытый интервал, если только начало —
    строится граница внутри одного дня.

    Args:
        params: Параметры фильтра из Swagger (start_date/end_date).

    Returns:
        Optional[tuple[datetime, datetime]]: Пара времен начала и конца периода либо None.
    """
    borders: Optional[tuple[datetime, datetime]] = None
    start_time = time(0, 0, 0)
    end_time = time(23, 59, 59)
    if params.start_date is not None and params.end_date is not None:
        borders = (
            datetime.combine(params.start_date, start_time),
            datetime.combine(params.end_date, end_time)
        )
    elif params.start_date is not None and params.end_date is None:
        borders = (
            datetime.combine(params.start_date, start_time),
            datetime.combine(params.start_date, end_time)
        )
    return borders


def filter_lesson(lesson: Lesson | None, filter_: FilterSvobodn) -> Lesson:
    """
    Оставляет только те варианты занятия, которые попадают в диапазон фильтра.

    Args:
        lesson: Список вариантов занятия для пары либо None.
        filter_: Параметры фильтрации (даты или номер пары).

    Returns:
        Lesson: Отфильтрованный список вариантов занятия.
    """
    if not lesson:
        return []
    elif filter_.end_date:
        lesson = list([variety for variety in lesson
                       if filter_.start_date >= variety.df
                       and filter_.end_date <= variety.dt])
    elif len(lesson) > 1:
        lesson = list([variety for variety in lesson if filter_.start_date >= variety.df])
    elif len(lesson) == 1:
        lesson = lesson if lesson[0].df <= filter_.start_date <= lesson[0].dt else []
    else:
        lesson = []
    return lesson


def filter_day(day: Day | None, filter_: FilterSvobodn) -> Day:
    """
    Отфильтровывает пары внутри одного дня по номеру пары или датам.

    Args:
        day: Расписание на день или None.
        filter_: Параметры фильтрации свободных аудиторий.

    Returns:
        Day: Словарь с номерами пар и списками доступных вариантов.
    """
    if not day:
        return dict({str(num): [] for num in range(1, 8)})
    if filter_.para:
        d = {str(filter_.para): filter_lesson(day.get(str(filter_.para)), filter_)}
    else:
        d = dict({str(num): filter_lesson(day.get(str(num)), filter_) for num in range(1, 8)})
    return d


def filter_auditory(aud: Auditory, filter_: FilterSvobodn) -> Auditory:
    """
    Применяет фильтр ко всем дням расписания выбранной аудитории.

    Args:
        aud: Данные аудитории с расписанием.
        filter_: Параметры фильтрации свободных аудиторий.

    Returns:
        Auditory: Аудитория с расписанием, где сохранены только подходящие пары.
    """
    if filter_.day:
        rasp_of_day = Rasp()
        rasp_of_day.__dict__[filter_.day.name] = filter_day(aud.rasp.__dict__[filter_.day.name], filter_)
        auditory = Auditory(id=aud.id, link=aud.link, rasp=rasp_of_day)
    else:
        rasp = Rasp()
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
            rasp.__dict__[day] = filter_day(aud.rasp.__dict__[day], filter_)
        auditory = Auditory(id=aud.id, link=aud.link, rasp=rasp)
    return auditory


def filter_svobodn(schedule: Schedule, filter_: FilterSvobodn) -> Schedule:
    """
    Применяет фильтр ко всему расписанию и возвращает только подходящие аудитории.

    Args:
        schedule: Полное расписание аудиторий.
        filter_: Параметры фильтрации свободных аудиторий.

    Returns:
        Schedule: Расписание, в котором оставлены только удовлетворяющие фильтру аудитории.
    """
    return dict({aud: filter_auditory(auditory, filter_) for aud, auditory in schedule.items() if auditory})
