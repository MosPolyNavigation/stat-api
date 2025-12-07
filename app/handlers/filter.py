"""Фильтры для выборок по пользователям, датам и расписанию."""

from datetime import datetime, time
from typing import Any, Optional

from sqlalchemy import Select

from app import schemas
from app.schemas.filter import FilterSvobodn
from app.schemas.rasp.schedule import Auditory, Day, Lesson, Rasp, Schedule


def filter_by_user(data_model: Any, params: schemas.Filter) -> Select:
    """Добавляет фильтр по user_id, если он указан."""
    query = Select(data_model)
    if params.user_id is not None:
        query = query.filter_by(user_id=params.user_id)
    return query


def filter_by_date(params: schemas.FilterQuery) -> Optional[tuple[datetime, datetime]]:
    """Возвращает временной интервал по параметрам start_date/end_date."""
    borders: Optional[tuple[datetime, datetime]] = None
    start_time = time(0, 0, 0)
    end_time = time(23, 59, 59)
    if params.start_date is not None and params.end_date is not None:
        borders = (
            datetime.combine(params.start_date, start_time),
            datetime.combine(params.end_date, end_time),
        )
    elif params.start_date is not None and params.end_date is None:
        borders = (
            datetime.combine(params.start_date, start_time),
            datetime.combine(params.start_date, end_time),
        )
    return borders


def filter_lesson(lesson: Lesson | None, filter_: FilterSvobodn) -> Lesson:
    """Фильтрует варианты занятия по дате начала/окончания и номеру пары."""
    if not lesson:
        return []
    elif filter_.end_date:
        lesson = [
            variety
            for variety in lesson
            if filter_.start_date >= variety.df and filter_.end_date <= variety.dt
        ]
    elif len(lesson) > 1:
        lesson = [variety for variety in lesson if filter_.start_date >= variety.df]
    elif len(lesson) == 1:
        lesson = lesson if lesson[0].df <= filter_.start_date <= lesson[0].dt else []
    else:
        lesson = []
    return lesson


def filter_day(day: Day | None, filter_: FilterSvobodn) -> Day:
    """Фильтрует день расписания по параметрам запроса."""
    if not day:
        return {str(num): [] for num in range(1, 8)}
    if filter_.para:
        d = {str(filter_.para): filter_lesson(day.get(str(filter_.para)), filter_)}
    else:
        d = {str(num): filter_lesson(day.get(str(num)), filter_) for num in range(1, 8)}
    return d


def filter_auditory(aud: Auditory, filter_: FilterSvobodn) -> Auditory:
    """Фильтрует расписание конкретной аудитории."""
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
    """Возвращает расписание, отфильтрованное по дню/парам."""
    return {aud: filter_auditory(auditory, filter_) for aud, auditory in schedule.items() if auditory}
