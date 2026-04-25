from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.helpers.permissions import require_rights
from app.models import ClientId
from app.schemas import Status
from app.scheme import ClientIdentResponse, ClientRegisterRequest


def register_endpoint(router: APIRouter):
    @router.get(
        "/client",
        response_model=ClientIdentResponse,
        tags=["stat"],
    )
    async def get_client_ident(
        db: AsyncSession = Depends(get_db),
    ) -> ClientIdentResponse:
        ident = str(uuid4())
        db.add(ClientId(ident=ident, creation_date=datetime.utcnow()))
        await db.commit()
        return ClientIdentResponse(ident=ident)

    @router.post(
        "/client",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(require_rights("client", "create"))],
    )
    async def register_client(
        data: ClientRegisterRequest,
        db: AsyncSession = Depends(get_db),
    ) -> Status:
        client = (
            await db.execute(
                select(ClientId).where(ClientId.ident == data.ident)
            )
        ).scalar_one_or_none()

        if client is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Client already exists",
            )

        db.add(
            ClientId(
                ident=data.ident,
                creation_date=data.first_interaction_date,
            )
        )
        await db.commit()

        return Status(status="ok")
