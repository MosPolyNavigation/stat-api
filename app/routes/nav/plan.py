import json
import os

from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import Select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.nav.plan import Plan
from app.models.nav.location import Location
from app.models.nav.static import Static
from app.schemas.nav.plan import PlanNav
from app.schemas import Status
from app.config import get_settings
from app.helpers.permissions import require_rights
from app.helpers.svg import save_svg_bytes_to_disk
from app.handlers.insert import insert_floor_map

def register_endpoint(router: APIRouter):
    @router.get(
        "/plan",
        description="Получение навигационного плана",
        response_model=PlanNav,
        tags=["nav"],
    )
    async def get_plan(
        plan: str,
        db: AsyncSession = Depends(get_db),
    ) -> PlanNav:
        """
        Эндпоинт для получения плана:
        /api/nav/plan?plan={plan_id}

        Возвращает JSON формата {loc_id}{plan_id}.json
        """ 
        #  находим план по id_sys и подгружаем corpus, floor, svg
        stmt = (
            Select(Plan)
            .options(
                selectinload(Plan.corpus),
                selectinload(Plan.floor),
                selectinload(Plan.svg),
            )
            .filter(Plan.id_sys == plan)
        )

        plan_obj: Plan | None = (
            await db.execute(stmt)
        ).scalar_one_or_none()

        if plan_obj is None:
            raise HTTPException(status_code=404, detail="Plan not found" )

        # Находим кампус по loc_id корпуса
        location: Location | None = (
            await db.execute(
                Select(Location).filter(
                    Location.id == plan_obj.corpus.loc_id
                )
            )
        ).scalar_one_or_none()

        if location is None:
            raise HTTPException(
                status_code=500,
                detail="Локация для корпуса плана не найдена",
            )

        # Разбираем JSON-поля entrances и graph
        try:
            entrances = json.loads(plan_obj.entrances)
        except ValueError:
            entrances = []

        try:
            graph = json.loads(plan_obj.graph)
        except ValueError:
            graph = []

        svg_link: str | None = (
            plan_obj.svg.link if plan_obj.svg is not None else None
        )

        spaces: list = []

        return PlanNav(
            planName=plan_obj.id_sys,
            svgLink=svg_link,
            campus=location.id_sys,
            corpus=plan_obj.corpus.id_sys,
            floor=plan_obj.floor.name,
            entrances=entrances,
            graph=graph,
            spaces=spaces,
        )

    @router.post(
        "/upload_plan",
        tags=["nav"],
        description="Загрузка svg плана (multipart/form-data: PlanId, File)",
        response_model=Status,
        dependencies=[Depends(require_rights("nav_data", "edit", "create"))],
        responses={
            200: {"model": Status, "description": "SVG uploaded"},
            400: {"model": Status, "description": "Invalid SVG or file was not saved"},
            404: {"model": Status, "description": "Plan not found"},
            422: {"model": Status, "description": "Invalid plan_id"},
        },
    )
    async def upload_plan(
            plan_id: str = Form(..., alias="PlanId"),
            file: UploadFile = File(..., alias="File"),
            db: AsyncSession = Depends(get_db),
    ) -> Status:
        """
        Эндпоинт для загрузки svg-плана:
        POST /api/nav/upload_plan

        Принимает x-www-form-urlencoded форму:
        - PlanId: идентификатор плана (plan.id_sys)
        - File: svg плана (текст)

        Сохраняет svg на диск в директорию:
        {static_files}/plans/uuid.svg
        """
        # валидность plan_id
        plan_id = (plan_id or "").strip()
        if not plan_id or len(plan_id) > 20:
            raise HTTPException(status_code=422, detail="Invalid plan_id")

        # находим план + svg
        stmt = (
            Select(Plan)
            .options(selectinload(Plan.svg))
            .filter(Plan.id_sys == plan_id)
        )
        plan_obj: Plan | None = (await db.execute(stmt)).scalar_one_or_none()
        if plan_obj is None:
            raise HTTPException(status_code=404, detail="Plan not found")

        # базовая директория хранения планов
        base_path = os.path.join(get_settings().static_files, "plans")

        # backup старого плана, если он есть
        old_static: Static | None = plan_obj.svg
        backup_done = False
        old_disk_path = None
        backup_disk_path = None

        if old_static is not None:
            old_disk_path = os.path.join(
                get_settings().static_files,
                old_static.path,
                f"{old_static.name}.{old_static.ext}",
            )
            backup_disk_path = old_disk_path + ".bak"

            if os.path.exists(old_disk_path):
                os.replace(old_disk_path, backup_disk_path)
                backup_done = True

                # чтобы имя файла стало uuid.svg.bak:
                # было name=uuid, ext=svg; стало name=uuid.svg, ext=bak
                await db.execute(
                    update(Static)
                    .where(Static.id == old_static.id)
                    .values(name=f"{old_static.name}.{old_static.ext}", ext="bak")
                )
                await db.commit()

        # читаем и сохраняем новый svg (функция внутри проверяет что это svg)
        contents = await file.read()
        saved_file = await save_svg_bytes_to_disk(contents, base_path)
        if saved_file is None:
            # откатить backup
            if backup_done and old_disk_path and backup_disk_path and os.path.exists(backup_disk_path):
                os.replace(backup_disk_path, old_disk_path)

                if old_static is not None:
                    # вернуть name="uuid", ext="svg" (из "uuid.svg" + "bak")
                    name_back = old_static.name
                    if name_back.endswith(".svg"):
                        name_back = name_back[:-4]

                    await db.execute(
                        update(Static)
                        .where(Static.id == old_static.id)
                        .values(name=name_back, ext="svg")
                    )
                    await db.commit()

            raise HTTPException(status_code=400, detail="Invalid SVG or file was not saved")

        # saved_file == uuid.svg
        rel_dir = "plans"
        link = f"/api/nav/plan_svg?plan_id={plan_id}"

        # вставка в statics, вернёт id
        new_static_id = await insert_floor_map(
            db=db,
            full_file_name=saved_file,
            file_path=rel_dir,
            link=link,
        )

        # обновляем plans.svg_id
        await db.execute(
            update(Plan)
            .where(Plan.id == plan_obj.id)
            .values(svg_id=new_static_id)
        )
        await db.commit()

        return Status(status=f"Uploaded svg: {saved_file}")

    @router.get(
        "/plan_svg",
        tags=["nav"],
        description="Получение svg плана по plan_id",
        response_class=FileResponse,
        responses={
            200: {"description": "SVG file"},
            404: {"model": Status, "description": "Plan/SVG not found"},
            422: {"model": Status, "description": "Invalid plan_id"},
        },
        tags=["nav"],
    )
    async def plan_svg(
        plan_id: str,
        db: AsyncSession = Depends(get_db),
    ) -> FileResponse:
        """
        Эндпоинт для получения svg-плана:
        GET /api/nav/plan_svg?plan_id={plan_id}
        """
        # Валидируем plan_id
        plan_id = (plan_id or "").strip()
        if not plan_id or len(plan_id) > 20:
            raise HTTPException(status_code=422, detail="Invalid plan_id")

        # Ищем план и его svg-статику
        stmt = (
            Select(Plan)
            .options(selectinload(Plan.svg))
            .filter(Plan.id_sys == plan_id)
        )
        plan_obj: Plan | None = (await db.execute(stmt)).scalar_one_or_none()
        if plan_obj is None:
            raise HTTPException(status_code=404, detail="Plan not found")

        # Если svg не привязан или расширение не svg - считаем что svg нет
        if plan_obj.svg is None or plan_obj.svg.ext.lower() != "svg":
            raise HTTPException(status_code=404, detail="SVG not found")

        # Формируем путь до файла на диске
        file_path = os.path.join(
            get_settings().static_files,
            plan_obj.svg.path,
            f"{plan_obj.svg.name}.{plan_obj.svg.ext}",
        )
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="SVG not found")

        # имя файла для пользователя - plan_id.svg
        return FileResponse(
            path=file_path,
            media_type="image/svg+xml",
            filename=f"{plan_id}.svg",
        )