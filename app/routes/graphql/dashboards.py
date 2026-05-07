from enum import Enum
from typing import List

import strawberry
from graphql import GraphQLError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry import Info

from app.helpers.db import _exists
from app.models.dashboard import Dashboard, DashboardType as DashboardTypeModel
from app.models.event import EventType

from .permissions import (
    _ensure_dashboards_view_permission,
    _ensure_dashboards_create_permission,
    _ensure_dashboards_edit_permission,
    _ensure_dashboards_delete_permission,
)


# =============================================================================
# Strawberry Enum
# =============================================================================


@strawberry.enum
class OrderBy(Enum):
    ASC = "ASC"
    DESC = "DESC"


# =============================================================================
# Strawberry Types
# =============================================================================


@strawberry.type
class DashboardType:
    """GraphQL type representing a dashboard."""
    id: int
    display_order: int
    event_type_id: int
    dashboard_type_id: int
    title_text: str


def _to_dashboard(model: Dashboard) -> DashboardType:
    return DashboardType(
        id=model.id,
        display_order=model.display_order,
        event_type_id=model.event_type_id,
        dashboard_type_id=model.dashboard_type_id,
        title_text=model.title_text,
    )


# =============================================================================
# Strawberry Inputs
# =============================================================================


@strawberry.input
class DashboardTypeInput:
    """Input type for creating/updating dashboards."""
    display_order: int
    event_type_id: int
    dashboard_type_id: int
    title_text: str


# =============================================================================
# Validation Helpers
# =============================================================================


def _validate_dashboard_input(data: DashboardTypeInput) -> None:
    """Validate dashboard input fields."""
    if data.display_order < 0:
        raise GraphQLError("display_order должен быть >= 0")

    if not data.title_text.strip():
        raise GraphQLError("title_text не может быть пустым")


async def _validate_foreign_keys(
    session: AsyncSession,
    event_type_id: int,
    dashboard_type_id: int,
) -> None:
    """Validate that foreign key references exist."""
    if not await _exists(session, EventType, event_type_id):
        raise GraphQLError(f"EventType с id={event_type_id} не найден")

    if not await _exists(session, DashboardTypeModel, dashboard_type_id):
        raise GraphQLError(f"DashboardType с id={dashboard_type_id} не найден")


# =============================================================================
# Query Resolvers
# =============================================================================


async def resolve_dashboards(
    info: Info,
    dashboard_type_id: int,
    order_by: OrderBy = OrderBy.ASC,
) -> List[DashboardType]:
    """List dashboards filtered by dashboard_type_id, sorted by display_order."""
    session = await _ensure_dashboards_view_permission(info)

    order_column = (
        Dashboard.display_order.asc()
        if order_by == OrderBy.ASC
        else Dashboard.display_order.desc()
    )

    statement = (
        select(Dashboard)
        .where(Dashboard.dashboard_type_id == dashboard_type_id)
        .order_by(order_column)
    )

    records = (await session.execute(statement)).scalars().all()
    return [_to_dashboard(record) for record in records]


async def resolve_dashboard(
    info: Info,
    id: int,
) -> DashboardType:
    """Get single dashboard by ID."""
    session = await _ensure_dashboards_view_permission(info)

    statement = select(Dashboard).where(Dashboard.id == id)
    record = (await session.execute(statement)).scalar_one_or_none()

    if record is None:
        raise GraphQLError(f"Dashboard с id={id} не найден")

    return _to_dashboard(record)


# =============================================================================
# Mutation Resolvers
# =============================================================================


async def create_dashboard(
    info: Info,
    input: DashboardTypeInput,
) -> DashboardType:
    """Create a new dashboard."""
    session = await _ensure_dashboards_create_permission(info)

    _validate_dashboard_input(input)
    await _validate_foreign_keys(session, input.event_type_id, input.dashboard_type_id)

    dashboard = Dashboard(
        display_order=input.display_order,
        event_type_id=input.event_type_id,
        dashboard_type_id=input.dashboard_type_id,
        title_text=input.title_text.strip(),
    )
    session.add(dashboard)
    await session.commit()
    await session.refresh(dashboard)

    return _to_dashboard(dashboard)


async def create_dashboards(
    info: Info,
    inputs: List[DashboardTypeInput],
) -> List[DashboardType]:
    """Create multiple dashboards in a single operation."""
    session = await _ensure_dashboards_create_permission(info)

    if not inputs:
        raise GraphQLError("inputs не может быть пустым")

    # Validate each input
    for i, input_data in enumerate(inputs):
        _validate_dashboard_input(input_data)

    # Collect unique foreign key IDs and validate them
    unique_event_type_ids = {inp.event_type_id for inp in inputs}
    unique_dashboard_type_ids = {inp.dashboard_type_id for inp in inputs}

    for event_type_id in unique_event_type_ids:
        if not await _exists(session, EventType, event_type_id):
            raise GraphQLError(f"EventType с id={event_type_id} не найден")

    for dashboard_type_id in unique_dashboard_type_ids:
        if not await _exists(session, DashboardTypeModel, dashboard_type_id):
            raise GraphQLError(
                f"DashboardType с id={dashboard_type_id} не найден"
            )

    # Build all dashboard objects
    dashboards = [
        Dashboard(
            display_order=inp.display_order,
            event_type_id=inp.event_type_id,
            dashboard_type_id=inp.dashboard_type_id,
            title_text=inp.title_text.strip(),
        )
        for inp in inputs
    ]

    # Bulk insert
    session.add_all(dashboards)
    await session.commit()

    # Refresh to get generated IDs
    for dashboard in dashboards:
        await session.refresh(dashboard)

    return [_to_dashboard(d) for d in dashboards]


async def update_dashboard(
    info: Info,
    id: int,
    input: DashboardTypeInput,
) -> DashboardType:
    """Update an existing dashboard."""
    session = await _ensure_dashboards_edit_permission(info)

    _validate_dashboard_input(input)
    await _validate_foreign_keys(session, input.event_type_id, input.dashboard_type_id)

    statement = select(Dashboard).where(Dashboard.id == id)
    dashboard = (await session.execute(statement)).scalar_one_or_none()

    if dashboard is None:
        raise GraphQLError(f"Dashboard с id={id} не найден")

    dashboard.display_order = input.display_order
    dashboard.event_type_id = input.event_type_id
    dashboard.dashboard_type_id = input.dashboard_type_id
    dashboard.title_text = input.title_text.strip()

    await session.commit()
    await session.refresh(dashboard)

    return _to_dashboard(dashboard)


async def delete_dashboard(
    info: Info,
    id: int,
) -> bool:
    """Delete a dashboard."""
    session = await _ensure_dashboards_delete_permission(info)

    statement = select(Dashboard).where(Dashboard.id == id)
    dashboard = (await session.execute(statement)).scalar_one_or_none()

    if dashboard is None:
        raise GraphQLError(f"Dashboard с id={id} не найден")

    await session.delete(dashboard)
    await session.commit()

    return True
