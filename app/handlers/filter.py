from datetime import datetime, time
from sqlalchemy import Select, and_
from typing import Any, Optional
from app import schemas


def filter_by_user(
        data_model: Any,
        params: schemas.Filter
) -> Select:
    query = Select(data_model)
    if params.user_id is not None:
        query = query.filter_by(user_id=params.user_id)
    return query


def filter_by_date(params: schemas.FilterQuery) -> tuple[Select, Optional[tuple[datetime, datetime]]]:
    model = params.model
    query = Select(model.user_id)
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
    if borders is not None:
        query = query.filter(and_(model.visit_date >= borders[0], model.visit_date <= borders[1]))
    return query, borders
