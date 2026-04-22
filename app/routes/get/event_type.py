from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import EventType
from app.scheme import EventTypeResponse


def register_endpoint(router: APIRouter):
    @router.get(
        "/event_type",
        response_model=list[EventTypeResponse],
        tags=["get"],
    )
    async def get_event_types(db: AsyncSession = Depends(get_db)) -> list[EventTypeResponse]:
        rows = (
            await db.execute(
                select(EventType.id, EventType.code_name).order_by(EventType.id.asc())
            )
        ).all()
        return [EventTypeResponse(id=int(row.id), name=str(row.code_name)) for row in rows]

