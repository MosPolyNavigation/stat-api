from sqlalchemy import Select
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
