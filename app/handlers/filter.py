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
    Функция для фильтрации по пользователю.

    Эта функция фильтрует данные по пользователю.

    Args:
        data_model: Модель данных;
        params: Параметры фильтрации.

    Returns:
        Select: Запрос с фильтром по пользователю.
    """
    query = Select(data_model)
    if params.user_id is not None:
        query = query.filter_by(user_id=params.user_id)
    return query


def filter_by_date(
        params: schemas.FilterQuery
) -> Optional[tuple[datetime, datetime]]:
    """
    Функция для фильтрации по дате.

    Эта функция фильтрует данные по дате.

    Args:
        params: Параметры фильтрации.

    Returns:
        Запрос с фильтром по дате и границы даты.
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


def filter_lesson(lesson: Lesson, filter_: FilterSvobodn) -> Lesson:
    if filter_.end_date:
        lesson = list([variety for variety in lesson
                       if filter_.start_date <= variety.df
                       and filter_.end_date >= variety.dt])
    elif len(lesson) > 1:
        lowerest_end_date = lesson[0].df
        lowerest_i = len(lesson)
        for i, variant in enumerate(lesson[1:]):
            if lowerest_end_date > variant.dt:
                lowerest_i = i
                lowerest_end_date = variant.dt
        lesson = [lesson[lowerest_i],]
    elif len(lesson) == 1:
        lesson = list(*lesson) if lesson[0].df >= filter_.start_date else []
    else:
        lesson = []
    return lesson


def filter_day(day: Day, filter_: FilterSvobodn) -> Day:
    if filter_.para:
        d = {str(filter_.para): filter_lesson(day[str(filter_.para)], filter_)}
    else:
        d = dict({num: filter_lesson(lesson, filter_) for num, lesson in day})
    return d


def filter_auditory(aud: Auditory, filter_: FilterSvobodn) -> Auditory:
    if filter_.day:
        rasp_of_day = Rasp()
        rasp_of_day[filter_.day.name] = filter_day(aud.rasp[filter_.day.name], filter_)
        auditory = Auditory(id=aud.id, link=aud.link, rasp=rasp_of_day)
    else:
        rasp = Rasp()
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
            rasp[day] = filter_day(aud.rasp[filter_.day.name], filter_)
        auditory = Auditory(id=aud.id, link=aud.link, rasp=rasp)
    return auditory


def filter_svobodn(schedule: Schedule, filter_: FilterSvobodn) -> Schedule:
    return dict({aud: filter_auditory(auditory, filter_) for aud, auditory in schedule if auditory})
