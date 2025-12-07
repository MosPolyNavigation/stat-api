from typing import Sequence
from fastapi import APIRouter, Depends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.nav.location import Location
from app.schemas.nav.campuses import CampusesLinks


def register_endpoint(router: APIRouter):
    """
    Эндпоинт для получения списка ссылок на кампусы навигации:
    /api/nav/campuses
    """

    @router.get(
        "/campuses",
        description="Получение ссылок на кампусы для навигации",
        response_model=CampusesLinks,
    )
    async def get_campuses(
        db: AsyncSession = Depends(get_db),
    ) -> CampusesLinks:
        # Берём только готовые локации
        result = await db.execute(
            Select(Location).filter(Location.ready.is_(True))
        )
        locations: Sequence[Location] = result.scalars().all()

        links = [f"/api/nav/campus?loc={loc.id_sys}" for loc in locations]

        return CampusesLinks(root=links)
