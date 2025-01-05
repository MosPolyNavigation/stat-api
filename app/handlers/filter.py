from datetime import datetime, time
from sqlalchemy import Select, and_
from app import schemas
from typing import Any


async def filter_by_user(
        data_model: Any,
        params: schemas.Filter
) -> Select:
    query = Select(data_model)
    if params.user_id is not None:
        query = query.filter_by(user_id=params.user_id)
    return query


async def filter_by_date(params: schemas.FilterQuery) -> Select:
    model = params.model
    query = Select(model)
    start_time = time(0, 0, 0)
    end_time = time(23, 59, 59)
    if params.start_date is not None and params.end_date is not None:
        query = Select(model).filter(and_(
            model.visit_date >= datetime.combine(params.start_date, start_time),
            model.visit_date <= datetime.combine(params.end_date, end_time)
        ))
    elif params.start_date is not None and params.end_date is None:
        query = query.filter(and_(
            model.visit_date >= datetime.combine(params.start_date, start_time),
            model.visit_date <= datetime.combine(params.start_date, end_time)
        ))
    return query
