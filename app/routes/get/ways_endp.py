from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.handlers import filter_by_user
from app.helpers.permissions import require_rights
from app.schemas import StartWayOut, Filter
from app.routes.get.generate_resp import generate_resp


def register_endpoint(router: APIRouter):
    @router.get(
        "/ways",
        description="Эндпоинт для получения начатых путей",
        response_model=Page[StartWayOut],
        tags=["get"],
        responses=generate_resp(Page[StartWayOut])
    )
    async def get_ways(
            query: Filter = Depends(),
            db: Session = Depends(get_db),
            _: bool = Depends(require_rights("stats", "view"))
    ) -> Page[StartWayOut]:
        """
        Эндпоинт для получения начатых путей.

        Этот эндпоинт возвращает список найденных данных.

        Args:
            query: Данные для фильтрации получаемых данных;
            db: Сессия базы данных;
            _: параметр для авторизации.

        Returns:
            Page[StartWayOut]: Страница с найденными данными.
        """
        return paginate(db, filter_by_user(models.StartWay, query))
