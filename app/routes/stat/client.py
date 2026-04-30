from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers import create_client_id
from app.helpers.permissions import require_rights
from app.models import ClientId
from app.schemas import ClientIdentResponse, ClientRegisterRequest, Status


def register_endpoint(router: APIRouter):
    @router.get(
        "/client",
        response_model=ClientIdentResponse,
        tags=["stat"],
    )
    async def get_client_ident(
        db: AsyncSession = Depends(get_db),
    ) -> ClientIdentResponse:
        return await create_client_id(db)

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
