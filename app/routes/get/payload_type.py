from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import PayloadType, ValueType
from app.scheme import PayloadTypeResponse


def register_endpoint(router: APIRouter):
    @router.get(
        "/payload_type",
        response_model=list[PayloadTypeResponse],
        tags=["get"],
    )
    async def get_payload_types(
        db: AsyncSession = Depends(get_db),
    ) -> list[PayloadTypeResponse]:
        rows = (
            await db.execute(
                select(PayloadType.id, PayloadType.code_name, ValueType.name)
                .join(ValueType, ValueType.id == PayloadType.value_type_id)
                .order_by(PayloadType.id.asc())
            )
        ).all()

        return [
            PayloadTypeResponse(
                id=int(row.id),
                name=str(row.code_name),
                data_type=str(row.name),
            )
            for row in rows
        ]

