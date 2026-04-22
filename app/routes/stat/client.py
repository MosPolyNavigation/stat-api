from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.helpers.permissions import require_rights
from app.models import ClientId
from app.scheme import ClientIdentResponse, ClientRegisterRequest, StatusResponse


def register_endpoint(router: APIRouter):
    @router.get(
        "/client",
        response_model=ClientIdentResponse,
        tags=["stat"],
    )
    async def get_client_ident(request: Request) -> ClientIdentResponse:
        ident = (
            getattr(request.state, "client_ident", None)
            or request.headers.get("X-Client-Ident")
            or str(uuid4())
        )
        return ClientIdentResponse(ident=str(ident))

    @router.post(
        "/client",
        response_model=StatusResponse,
        tags=["stat"],
        dependencies=[Depends(require_rights("client", "create"))],
    )
    async def register_client(
        data: ClientRegisterRequest,
        db: AsyncSession = Depends(get_db),
    ) -> StatusResponse:
        client = (
            await db.execute(
                select(ClientId).where(ClientId.ident == data.ident)
            )
        ).scalar_one_or_none()

        if client is None:
            db.add(
                ClientId(
                    ident=data.ident,
                    creation_date=data.first_interaction_date,
                )
            )
            await db.commit()

        return StatusResponse(status="ok")
