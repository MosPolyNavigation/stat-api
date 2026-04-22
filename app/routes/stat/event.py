from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.guards.governor import stat_rate_limiter
from app.models import AllowedPayload, ClientId, Event, EventType, Payload, PayloadType, ValueType
from app.scheme import EventCreateRequest, StatusResponse


def _normalize_payload_value(value: str, data_type: str, payload_type_id: int) -> str:
    if len(value) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payload value is too long for payload_type_id={payload_type_id}",
        )

    if data_type == "string":
        return value

    if data_type == "int":
        try:
            return str(int(value))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid int value for payload_type_id={payload_type_id}",
            ) from exc

    if data_type == "bool":
        normalized = value.lower()
        if normalized not in {"true", "false"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid bool value for payload_type_id={payload_type_id}",
            )
        return normalized

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported payload data type '{data_type}' for payload_type_id={payload_type_id}",
    )


async def _resolve_client(db: AsyncSession, request: Request, body: dict[str, Any]) -> ClientId | None:
    client_id = (
        getattr(request.state, "client_id", None)
        or body.get("client_id")
        or request.headers.get("X-Client-Id")
    )
    client_ident = (
        getattr(request.state, "client_ident", None)
        or body.get("client_ident")
        or body.get("ident")
        or request.headers.get("X-Client-Ident")
    )

    if client_id is not None:
        try:
            numeric_client_id = int(client_id)
        except (TypeError, ValueError):
            client_ident = str(client_id)
        else:
            by_id = (
                await db.execute(
                    select(ClientId).where(ClientId.id == numeric_client_id)
                )
            ).scalar_one_or_none()
            if by_id is not None:
                return by_id

    if client_ident is None:
        return None

    return (
        await db.execute(
            select(ClientId).where(ClientId.ident == str(client_ident))
        )
    ).scalar_one_or_none()


def register_endpoint(router: APIRouter):
    @router.post(
        "/event",
        response_model=StatusResponse,
        tags=["stat"],
        dependencies=[Depends(stat_rate_limiter)],
    )
    async def create_event(
        request: Request,
        db: AsyncSession = Depends(get_db),
    ) -> StatusResponse:
        try:
            body = await request.json()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON body",
            ) from exc

        try:
            data = EventCreateRequest.model_validate(body)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exc.errors(include_url=False),
            ) from exc

        client = await _resolve_client(db, request, body)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client was not found. Pass client_id/client_ident in request context or body.",
            )

        event_type = (
            await db.execute(
                select(EventType).where(EventType.id == data.event_type_id)
            )
        ).scalar_one_or_none()
        if event_type is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown event_type_id={data.event_type_id}",
            )

        allowed_rows = (
            await db.execute(
                select(PayloadType.id, ValueType.name)
                .join(AllowedPayload, AllowedPayload.payload_type_id == PayloadType.id)
                .join(ValueType, ValueType.id == PayloadType.value_type_id)
                .where(AllowedPayload.event_type_id == data.event_type_id)
            )
        ).all()
        allowed_payload_types = {
            int(row.id): str(row.name)
            for row in allowed_rows
        }

        normalized_payloads: list[tuple[int, str]] = []
        for payload_type_id, value in data.payloads.items():
            expected_type = allowed_payload_types.get(payload_type_id)
            if expected_type is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Payload type {payload_type_id} is not allowed "
                        f"for event_type_id={data.event_type_id}"
                    ),
                )
            normalized_payloads.append(
                (
                    payload_type_id,
                    _normalize_payload_value(value=value, data_type=expected_type, payload_type_id=payload_type_id),
                )
            )

        event = Event(
            client_id=client.id,
            event_type_id=data.event_type_id,
            trigger_time=datetime.utcnow(),
        )
        db.add(event)
        await db.flush()

        db.add_all(
            [
                Payload(
                    event_id=event.id,
                    type_id=payload_type_id,
                    value=normalized_value,
                )
                for payload_type_id, normalized_value in normalized_payloads
            ]
        )

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

        return StatusResponse(status="ok")
