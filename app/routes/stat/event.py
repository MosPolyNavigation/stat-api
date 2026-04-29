from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import (
    EVENT_TYPE_AUDS_ID,
    EVENT_TYPE_PLANS_ID,
    EVENT_TYPE_SITE_ID,
    EVENT_TYPE_WAYS_ID,
    PAYLOAD_TYPE_AUDITORY_ID,
    PAYLOAD_TYPE_ENDPOINT_ID,
    PAYLOAD_TYPE_END_ID,
    PAYLOAD_TYPE_PLAN_ID,
    PAYLOAD_TYPE_START_ID,
    PAYLOAD_TYPE_SUCCESS_ID,
)
from app.database import get_db
from app.guards.governor import stat_event_rate_limiter, stat_rate_limiter
from app.handlers import create_client_id, create_event, register_client_ident
from app.scheme import ClientIdentRequest, ClientIdentResponse, EventCreateRequest
from app.schemas import Status


UUID_PATTERN = r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}"


class LegacyBaseStatRequest(BaseModel):
    user_id: str = Field(min_length=36, max_length=36, pattern=UUID_PATTERN)


class LegacySelectAudRequest(LegacyBaseStatRequest):
    auditory_id: str = Field(min_length=1, max_length=50)
    success: bool


class LegacyStartWayRequest(LegacyBaseStatRequest):
    start_id: str = Field(min_length=1, max_length=50)
    end_id: str = Field(min_length=1, max_length=50)
    success: bool


class LegacyChangePlanRequest(LegacyBaseStatRequest):
    plan_id: str = Field(min_length=1, max_length=50)


def _bool_to_payload(value: bool) -> str:
    return "true" if value else "false"


def register_endpoint(router: APIRouter):
    @router.get(
        "/client",
        response_model=ClientIdentResponse,
        tags=["stat"],
    )
    async def get_client(db: AsyncSession = Depends(get_db)):
        return await create_client_id(db)

    @router.post(
        "/client",
        response_model=ClientIdentResponse,
        tags=["stat"],
        responses={409: {"description": "Client already exists"}},
    )
    async def register_client(
        data: ClientIdentRequest,
        db: AsyncSession = Depends(get_db),
    ):
        return await register_client_ident(db, data)

    @router.post(
        "/event",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(stat_event_rate_limiter)],
    )
    async def add_event(
        data: EventCreateRequest,
        db: AsyncSession = Depends(get_db),
    ):
        return await create_event(db, data)

    @router.put(
        "/site",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(stat_rate_limiter)],
    )
    async def add_site_event(
        data: LegacyBaseStatRequest,
        db: AsyncSession = Depends(get_db),
    ):
        return await create_event(
            db,
            EventCreateRequest(
                ident=data.user_id,
                event_type_id=EVENT_TYPE_SITE_ID,
                payloads=[
                    {"type_id": PAYLOAD_TYPE_ENDPOINT_ID, "value": "site"},
                ],
            ),
            client_error_name="User",
        )

    @router.put(
        "/select-aud",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(stat_rate_limiter)],
    )
    async def add_select_aud_event(
        data: LegacySelectAudRequest,
        db: AsyncSession = Depends(get_db),
    ):
        return await create_event(
            db,
            EventCreateRequest(
                ident=data.user_id,
                event_type_id=EVENT_TYPE_AUDS_ID,
                payloads=[
                    {"type_id": PAYLOAD_TYPE_AUDITORY_ID, "value": data.auditory_id},
                    {"type_id": PAYLOAD_TYPE_SUCCESS_ID, "value": _bool_to_payload(data.success)},
                ],
            ),
            client_error_name="User",
        )

    @router.put(
        "/start-way",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(stat_rate_limiter)],
    )
    async def add_start_way_event(
        data: LegacyStartWayRequest,
        db: AsyncSession = Depends(get_db),
    ):
        return await create_event(
            db,
            EventCreateRequest(
                ident=data.user_id,
                event_type_id=EVENT_TYPE_WAYS_ID,
                payloads=[
                    {"type_id": PAYLOAD_TYPE_START_ID, "value": data.start_id},
                    {"type_id": PAYLOAD_TYPE_END_ID, "value": data.end_id},
                    {"type_id": PAYLOAD_TYPE_SUCCESS_ID, "value": _bool_to_payload(data.success)},
                ],
            ),
            client_error_name="User",
        )

    @router.put(
        "/change-plan",
        response_model=Status,
        tags=["stat"],
        dependencies=[Depends(stat_rate_limiter)],
    )
    async def add_change_plan_event(
        data: LegacyChangePlanRequest,
        db: AsyncSession = Depends(get_db),
    ):
        return await create_event(
            db,
            EventCreateRequest(
                ident=data.user_id,
                event_type_id=EVENT_TYPE_PLANS_ID,
                payloads=[
                    {"type_id": PAYLOAD_TYPE_PLAN_ID, "value": data.plan_id},
                ],
            ),
            client_error_name="User",
        )
