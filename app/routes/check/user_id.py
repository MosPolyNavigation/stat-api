from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers.check import check_client_id
from app.schemas import ClientIdCheck, Status


def register_endpoint(router: APIRouter):
    @router.get(
        "/client-id",
        description="Endpoint for checking that a client id exists",
        response_model=Status,
        tags=["check"],
        responses={
            500: {
                "model": Status,
                "description": "Server side error",
                "content": {
                    "application/json": {
                        "example": {"status": "Some error"}
                    }
                },
            },
            404: {
                "model": Status,
                "description": "Item not found",
                "content": {
                    "application/json": {
                        "example": {"status": "Client not found"}
                    }
                },
            },
            200: {
                "model": Status,
                "description": "Client found",
            },
        },
    )
    async def check_client(
        data: ClientIdCheck = Depends(),
        db: AsyncSession = Depends(get_db),
    ):
        return await check_client_id(db, data)
