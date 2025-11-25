from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import UserIdCheck, Status
from app.handlers.check import check_user_id


def register_endpoint(router: APIRouter):
    @router.get(
        "/user-id",
        description="Эндпоинт для получения уникального id пользователя",
        response_model=Status,
        tags=["check"],
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
            404: {
                'model': Status,
                'description': "Item not found",
                'content': {
                    "application/json": {
                        "example": {"status": "User not found"}
                    }
                }
            },
            200: {
                'model': Status,
                'description': "User found",
            }
        }
    )
    async def check_uuid(
        data: UserIdCheck = Depends(),
        db: AsyncSession = Depends(get_db)
    ):
        """
        Эндпоинт для проверки существования уникального идентификатора пользователя.

        Args:
            db: Сессия базы данных;
            data: Структура, содержащая user_id.

        Returns:
            Statys: Статус проверки существования.
        """
        return await check_user_id(db, data)
