from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import Status
from app.database import get_db
from app.handlers import get_popular_auds


def register_endpoint(router: APIRouter):
    @router.get(
        "/popular",
        tags=["get"],
        responses={
            500: {
                'model': Status,
                'description': "Server side error",
                'content': {
                    "application/json": {
                        "example": {"status": "Some error"}
                    }
                }
            },
            200: {
                'description': 'Popular auditories in descending order',
                'content': {
                    'application/json': {
                        "example": ["a-100", "a-101", "a-103", "a-102"]
                    }
                }
            }
        }
    )
    async def get_popular(
            db: AsyncSession = Depends(get_db)
    ) -> JSONResponse:
        data = await get_popular_auds(db)
        return JSONResponse(data, status_code=200)
