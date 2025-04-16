from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.handlers import filter_by_user
from app.schemas import SelectedAuditoryOut, Filter
from app.routes.get.generate_resp import generate_resp


def register_endpoint(router: APIRouter):
    @router.get(
        "/auds",
        description="Эндпоинт для получения выбранных аудиторий",
        response_model=Page[SelectedAuditoryOut],
        tags=["get"],
        responses=generate_resp(Page[SelectedAuditoryOut])
    )
    async def get_auds(
        query: Filter = Depends(),
        db: Session = Depends(get_db)
    ) -> Page[SelectedAuditoryOut]:
        """
        Эндпоинт для получения выбранных аудиторий.

        Этот эндпоинт возвращает список найденных данных.

        Args:
            query: Параметры фильтрации;
            db: Сессия базы данных.

        Returns:
            Page[SelectedAuditoryOut]: Страница с найденными данными.
        """
        return paginate(db, filter_by_user(models.SelectAuditory, query))
