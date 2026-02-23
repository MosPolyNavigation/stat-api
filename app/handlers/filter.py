from datetime import datetime, time, timedelta
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
    if params.start_date is not None and params.end_date is not None:
        borders = (
            datetime.combine(params.start_date, start_time),
            datetime.combine(params.end_date + timedelta(days=1), start_time)
        )
    return borders


def filter_by_month(
        params: schemas.FilterQuery
) -> Optional[tuple[datetime, datetime]]:
    if params.start_month is None or params.end_month is None:
        return None

    start_month = datetime.strptime(params.start_month, "%Y-%m")
    end_month = datetime.strptime(params.end_month, "%Y-%m")
    if end_month.month == 12:
        end_exclusive = datetime(end_month.year + 1, 1, 1)
    else:
        end_exclusive = datetime(end_month.year, end_month.month + 1, 1)
    return start_month, end_exclusive


def filter_by_year(
        params: schemas.FilterQuery
) -> Optional[tuple[datetime, datetime]]:
    if params.start_year is None or params.end_year is None:
        return None

    start_year = datetime.strptime(params.start_year, "%Y")
    end_exclusive = datetime(int(params.end_year) + 1, 1, 1)
    return start_year, end_exclusive


def filter_lesson(lesson: Lesson | None, filter_: FilterSvobodn) -> Lesson:
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
    if not day:
        return dict({str(num): [] for num in range(1, 8)})
    if filter_.para:
        d = {str(filter_.para): filter_lesson(day.get(str(filter_.para)), filter_)}
    else:
        d = dict({str(num): filter_lesson(day.get(str(num)), filter_) for num in range(1, 8)})
    return d


def filter_auditory(aud: Auditory, filter_: FilterSvobodn) -> Auditory:
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
    return dict({aud: filter_auditory(auditory, filter_) for aud, auditory in schedule.items() if auditory})
