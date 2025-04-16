from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.handlers import filter_by_user
from app.schemas import SiteStatOut, Filter
from app.routes.get.generate_resp import generate_resp


def register_endpoint(router: APIRouter):
    @router.get(
        "/site",
        description="Эндпоинт для получения посещений сайта",
        response_model=Page[SiteStatOut],
        tags=["get"],
        responses=generate_resp(Page[SiteStatOut])
    )
    async def get_sites(
        query: Filter = Depends(),
        db: Session = Depends(get_db)
    ) -> Page[SiteStatOut]:
        """
        Эндпоинт для получения посещений сайта.

        Этот эндпоинт возвращает список найденных данных.

        Args:
            query: Параметры фильтрации;
            db: Сессия базы данных.

        Returns:
            Page[SiteStatOut]: Страница с найденными данными.
        """
        return paginate(db, filter_by_user(models.SiteStat, query))
