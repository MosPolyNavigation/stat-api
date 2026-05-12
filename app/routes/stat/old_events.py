"""TODO: Удалить, как фронты перейдут на новую схему событий"""

from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, UTC

from app.database import get_db
from app.schemas import Status
from app.schemas.old_events import (
    SelectedAuditoryIn, ChangePlanIn, SiteStatIn, StartWayIn
)
from app.guards.governor import stat_rate_limiter
from app.models import ClientId, Event, Payload

from app.constants import (
    EVENT_TYPE_SITE_ID, EVENT_TYPE_AUDS_ID, EVENT_TYPE_WAYS_ID, EVENT_TYPE_PLANS_ID,
    PAYLOAD_TYPE_ENDPOINT_ID, PAYLOAD_TYPE_AUDITORY_ID, PAYLOAD_TYPE_START_ID,
    PAYLOAD_TYPE_END_ID, PAYLOAD_TYPE_SUCCESS_ID, PAYLOAD_TYPE_PLAN_ID
)


async def _create_event_from_legacy(
    db: AsyncSession,
    user_id: str,
    event_type_id: int,
    payloads: dict[int, tuple]
) -> Status:
    """Транслирует старые данные в новую структуру Event -> Payload."""
    # Ищем клиента по user_id (в старой системе он выступал идентификатором)
    client = (await db.execute(select(ClientId).where(ClientId.ident == user_id))).scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Создаём событие
    event = Event(
        client_id=client.id,
        event_type_id=event_type_id,
        trigger_time=datetime.now(UTC),
    )
    db.add(event)
    await db.flush()

    # Формируем пэйлоады с приведением типов к строкам (как в новой системе)
    db_payloads = []
    for p_type_id, (value, v_type) in payloads.items():
        if v_type == "bool":
            normalized = str(value).lower()
            if normalized not in {"true", "false"}:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid bool value for payload_type_id={p_type_id}"
                )
        else:
            normalized = str(value)
        db_payloads.append(Payload(event_id=event.id, type_id=p_type_id, value=normalized))

    db.add_all(db_payloads)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return Status(status="ok")


def register_endpoints(router: APIRouter):
    # ==================== /select-aud ====================
    @router.put(
        "/select-aud",
        description="Эндпоинт для добавления выбора аудитории",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(stat_rate_limiter)],
        responses={
            500: {
                'model': Status,
                'description': "Server side error",
                'content': {"application/json": {"example": {"status": "Some error"}}}
            },
            404: {
                'model': Status,
                'description': "Item not found",
                'content': {"application/json": {"example": {"status": "User not found"}}}
            },
            200: {
                'model': Status,
                "description": "Status of adding new object to db"
            },
            429: {
                "description": "Too many requests",
                'content': {
                    "application/json": {
                        "example": {"detail": "Too many requests for this user within one second"}
                    }
                }
            }
        }
    )
    async def add_selected_aud(
        data: SelectedAuditoryIn = Body(),
        db: AsyncSession = Depends(get_db),
    ):
        return await _create_event_from_legacy(
            db,
            user_id=data.user_id,
            event_type_id=EVENT_TYPE_AUDS_ID,
            payloads={
                PAYLOAD_TYPE_AUDITORY_ID: (data.auditory_id, "string"),
                PAYLOAD_TYPE_SUCCESS_ID: (data.success, "bool"),
            }
        )

    # ==================== /change-plan ====================
    @router.put(
        "/change-plan",
        description="Эндпоинт для добавления смены плана",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(stat_rate_limiter)],
        responses={
            500: {
                'model': Status,
                'description': "Server side error",
                'content': {"application/json": {"example": {"status": "Some error"}}}
            },
            404: {
                'model': Status,
                'description': "Item not found",
                'content': {"application/json": {"example": {"status": "User not found"}}}
            },
            200: {
                'model': Status,
                "description": "Status of adding new object to db"
            },
            429: {
                "description": "Too many requests",
                'content': {
                    "application/json": {
                        "example": {"detail": "Too many requests for this user within one second"}
                    }
                }
            }
        }
    )
    async def add_changed_plan(
        data: ChangePlanIn = Body(),
        db: AsyncSession = Depends(get_db),
    ):
        return await _create_event_from_legacy(
            db,
            user_id=data.user_id,
            event_type_id=EVENT_TYPE_PLANS_ID,
            payloads={
                PAYLOAD_TYPE_PLAN_ID: (data.plan_id, "string"),
            }
        )

    # ==================== /site ====================
    @router.put(
        "/site",
        description="Эндпоинт для добавления статистики посещений сайта",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(stat_rate_limiter)],
        responses={
            500: {
                'model': Status,
                'description': "Server side error",
                'content': {"application/json": {"example": {"status": "Some error"}}}
            },
            404: {
                'model': Status,
                'description': "Item not found",
                'content': {"application/json": {"example": {"status": "User not found"}}}
            },
            200: {
                'model': Status,
                "description": "Status of adding new object to db"
            },
            429: {
                "description": "Too many requests",
                'content': {
                    "application/json": {
                        "example": {"detail": "Too many requests for this user within one second"}
                    }
                }
            }
        }
    )
    async def add_site_stat(
        data: SiteStatIn = Body(),
        db: AsyncSession = Depends(get_db),
    ):
        return await _create_event_from_legacy(
            db,
            user_id=data.user_id,
            event_type_id=EVENT_TYPE_SITE_ID,
            payloads={
                PAYLOAD_TYPE_ENDPOINT_ID: (data.endpoint or "", "string"),
            }
        )

    # ==================== /start-way ====================
    @router.put(
        "/start-way",
        description="Эндпоинт для добавления начатого пути",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(stat_rate_limiter)],
        responses={
            500: {
                'model': Status,
                'description': "Server side error",
                'content': {"application/json": {"example": {"status": "Some error"}}}
            },
            404: {
                'model': Status,
                'description': "Item not found",
                'content': {"application/json": {"example": {"status": "User not found"}}}
            },
            200: {
                'model': Status,
                "description": "Status of adding new object to db"
            },
            429: {
                "description": "Too many requests",
                'content': {
                    "application/json": {
                        "example": {"detail": "Too many requests for this user within one second"}
                    }
                }
            }
        }
    )
    async def add_started_way(
        data: StartWayIn = Body(),
        db: AsyncSession = Depends(get_db),
    ):
        return await _create_event_from_legacy(
            db,
            user_id=data.user_id,
            event_type_id=EVENT_TYPE_WAYS_ID,
            payloads={
                PAYLOAD_TYPE_START_ID: (data.start_id, "string"),
                PAYLOAD_TYPE_END_ID: (data.end_id, "string"),
                PAYLOAD_TYPE_SUCCESS_ID: (data.success, "bool"),
            }
        )
