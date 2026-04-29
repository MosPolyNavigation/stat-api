from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.helpers.errors import LookupException
from app.scheme import ClientIdentRequest, ClientIdentResponse, EventCreateRequest


async def register_client_ident(
    db: AsyncSession,
    data: ClientIdentRequest,
) -> ClientIdentResponse:
    """Регистрирует клиентский ident, если он ещё не существует."""
    existing = (
        await db.execute(Select(models.ClientId).filter_by(ident=data.ident))
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client already exists",
        )

    client = models.ClientId(ident=data.ident, creation_date=datetime.now())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return ClientIdentResponse.model_validate(client)


async def create_event(
    db: AsyncSession,
    data: EventCreateRequest,
    client_error_name: str = "Client",
) -> schemas.Status:
    """Создаёт событие и связанные payload-строки в новой схеме."""
    client = (
        await db.execute(Select(models.ClientId).filter_by(ident=data.ident))
    ).scalar_one_or_none()
    if client is None:
        raise LookupException(client_error_name)

    event_type = (
        await db.execute(
            Select(models.EventType).filter_by(id=data.event_type_id)
        )
    ).scalar_one_or_none()
    if event_type is None:
        raise LookupException("EventType")

    payload_type_ids = {payload.type_id for payload in data.payloads}
    allowed_payload_type_ids = set(
        (
            await db.execute(
                select(models.AllowedPayload.payload_type_id).where(
                    models.AllowedPayload.event_type_id == data.event_type_id,
                    models.AllowedPayload.payload_type_id.in_(payload_type_ids),
                )
            )
        ).scalars()
    )
    forbidden_payloads = payload_type_ids - allowed_payload_type_ids
    if forbidden_payloads:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Payload type is not allowed for this event type",
        )

    event = models.Event(client=client, event_type=event_type, trigger_time=datetime.now())
    db.add(event)
    for payload in data.payloads:
        db.add(
            models.Payload(
                event=event,
                type_id=payload.type_id,
                value=payload.value,
            )
        )

    await db.commit()
    return schemas.Status()
