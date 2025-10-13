from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.handlers import filter_by_user
from app.helpers.permissions import require_rights
from app.schemas import ChangePlanOut, Filter
from app.routes.get.generate_resp import generate_resp


def register_endpoint(router: APIRouter):
    @router.get(
        "/plans",
        description="Эндпоинт для получения смененных планов",
        response_model=Page[ChangePlanOut],
        tags=["get"],
        responses=generate_resp(Page[ChangePlanOut])
    )
    async def get_plans(
            query: Filter = Depends(),
            db: Session = Depends(get_db),
            _: bool = Depends(require_rights("stats", "view"))
    ) -> Page[ChangePlanOut]:
        """
        Эндпоинт для получения смененных планов.

        Этот эндпоинт возвращает список найденных данных.

        Args:
            query: Параметры фильтрации;
            db: Сессия базы данных;
            _: параметр для авторизации.

        Returns:
            Страница с найденными данными.
        """
        return paginate(db, filter_by_user(models.ChangePlan, query))
