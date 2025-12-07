import json
from typing import Sequence
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.nav.location import Location
from app.models.nav.corpus import Corpus
from app.models.nav.plan import Plan
from app.schemas.nav.campus import CampusNav, CorpusNav


def register_endpoint(router: APIRouter):
    """
    Эндпоинт для описания кампуса:
    /api/nav/campus?loc={loc_id}
    Возвращает JSON формата CAMPUS-{loc_id}.json
    """

    @router.get(
        "/campus",
        description="Получение навигационной структуры кампуса",
        response_model=CampusNav,
    )
    async def get_campus(
        loc: str,
        db: AsyncSession = Depends(get_db),
    ) -> CampusNav:
        # Проверяем, что локация существует по id_sys
        location: Location | None = (
            await db.execute(
                Select(Location).filter(Location.id_sys == loc)
            )
        ).scalar_one_or_none()

        if location is None:
            raise HTTPException(status_code=404, detail="Кампус не найден")

        # Берём корпуса этогоо кампуса
        corpuses_result = await db.execute(
            Select(Corpus).filter(
                Corpus.loc_id == location.id,
                Corpus.ready.is_(True),
            )
        )
        corpuses: Sequence[Corpus] = corpuses_result.scalars().all()

        # берём планы по этим корпусам
        corpus_ids = [c.id for c in corpuses]
        plans_by_corpus: dict[int, list[str]] = {cid: [] for cid in corpus_ids}

        if corpus_ids:
            plans_result = await db.execute(
                Select(Plan.cor_id, Plan.id_sys).filter(
                    Plan.cor_id.in_(corpus_ids),
                    Plan.ready.is_(True),
                )
            )
            for cor_id, plan_id_sys in plans_result.all():
                plans_by_corpus.setdefault(cor_id, []).append(plan_id_sys)

        # Собираем словарь corpuses для ответа
        corpuses_dict: dict[str, CorpusNav] = {}

        for corpus in corpuses:
            # Имена корпусов извлекаем из id_sys (после "-")
            # "AV-4" -> "4", "AV-1_2" -> "1_2"
            rus_name = corpus.id_sys
            if "-" in rus_name:
                rus_name = rus_name.split("-", 1)[1]

            # Ссылки на планы – на эндпоинт API
            plan_ids = plans_by_corpus.get(corpus.id, [])
            plan_links = [f"/api/nav/plan?plan={pid}" for pid in plan_ids]

            if corpus.stair_groups:
                try:
                    stairs_groups = json.loads(corpus.stair_groups)
                except ValueError:
                    stairs_groups = []
            else:
                stairs_groups = []

            corpuses_dict[corpus.id_sys] = CorpusNav(
                rusName=rus_name,
                planLinks=plan_links,
                stairsGroups=stairs_groups,
            )

        if location.crossings:
            try:
                crossings = json.loads(location.crossings)
            except ValueError:
                crossings = []
        else:
            crossings = []

        return CampusNav(
            id=location.id_sys,
            rusName=location.short,
            corpuses=corpuses_dict,
            crossings=crossings,
        )
