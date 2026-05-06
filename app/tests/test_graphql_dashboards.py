"""Tests for Dashboard GraphQL CRUD operations.

Covers queries (list by type, ordering, get by id, not found),
mutations (create, update, delete with validation),
and permission checks (denied for users without required rights).
"""

import asyncio

from pwdlib import PasswordHash
from sqlalchemy import select

from app.constants import (
    CREATE_RIGHT_ID,
    DASHBOARDS_GOAL_ID,
    DELETE_RIGHT_ID,
    EDIT_RIGHT_ID,
    VIEW_RIGHT_ID,
)
from app.models import RoleRightGoal, User
from app.models.dashboard import DashboardType as DashboardTypeModel

from .base import client, test_session_maker

# =============================================================================
# Tokens / Headers
# =============================================================================

ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}

# Second user with NO dashboard permissions at all.
USER_NO_PERM_TOKEN = "33e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
USER_NO_PERM_HEADERS = {"Authorization": f"Bearer {USER_NO_PERM_TOKEN}"}


# =============================================================================
# Helpers
# =============================================================================


def graphql_query(query: str, headers: dict = None, variables: dict = None):
    """Send a GraphQL request to the test client."""
    return client.post(
        "/api/graphql",
        json={"query": query, "variables": variables or {}},
        headers=headers or {},
    )


def _seed_dashboard_test_data():
    """Ensure dashboard_types, admin CRUD permissions, and a no-perm user exist.

    Called once at module import time, after ``base.py`` has already created
    the test database, admin user, roles, rights, goals, and event_types.
    """

    async def _seed():
        async with test_session_maker() as session:
            # ── Dashboard types (id=1 "chart", id=2 "avg") ─────────────────
            existing_types = (
                await session.execute(
                    select(DashboardTypeModel).where(
                        DashboardTypeModel.id.in_([1, 2])
                    )
                )
            ).scalars().all()
            if not existing_types:
                session.add_all([
                    DashboardTypeModel(
                        id=1,
                        code_name="chart",
                        description="График статистики",
                    ),
                    DashboardTypeModel(
                        id=2,
                        code_name="avg",
                        description="Агрегированная статистика",
                    ),
                ])

            # ── Admin CRUD permissions for dashboards goal ─────────────────
            existing_perm = (
                await session.execute(
                    select(RoleRightGoal).where(
                        RoleRightGoal.role_id == 1,
                        RoleRightGoal.goal_id == DASHBOARDS_GOAL_ID,
                        RoleRightGoal.right_id == CREATE_RIGHT_ID,
                    )
                )
            ).scalar_one_or_none()
            if not existing_perm:
                session.add_all([
                    RoleRightGoal(
                        role_id=1,
                        right_id=CREATE_RIGHT_ID,
                        goal_id=DASHBOARDS_GOAL_ID,
                    ),
                    RoleRightGoal(
                        role_id=1,
                        right_id=EDIT_RIGHT_ID,
                        goal_id=DASHBOARDS_GOAL_ID,
                    ),
                    RoleRightGoal(
                        role_id=1,
                        right_id=DELETE_RIGHT_ID,
                        goal_id=DASHBOARDS_GOAL_ID,
                    ),
                ])

            # ── Second user with NO dashboard permissions ──────────────────
            existing_user = (
                await session.execute(
                    select(User).where(User.id == 2)
                )
            ).scalar_one_or_none()
            if not existing_user:
                user2 = User(
                    id=2,
                    login="noperm",
                    hash=PasswordHash.recommended().hash("noperm"),
                    token=USER_NO_PERM_TOKEN,
                )
                session.add(user2)
                # Intentionally no UserRole — zero permissions.

            await session.commit()

    asyncio.run(_seed())


_seed_dashboard_test_data()


# =============================================================================
# Query Tests
# =============================================================================


class TestDashboardQueries:
    """GraphQL queries: dashboards (list) and dashboard (single)."""

    # ------------------------------------------------------------------
    # dashboards(list) – filtering & ordering
    # ------------------------------------------------------------------

    def test_get_dashboards_by_type(self):
        """Query dashboards filtered by dashboard_type_id, verify results."""
        # Create two dashboards of type=1 and one of type=2
        created_ids = []
        for order, dtype_id, title in [
            (10, 1, "Chart A"),
            (20, 1, "Chart B"),
            (30, 2, "Avg X"),
        ]:
            mutation = """
            mutation ($input: DashboardTypeInput!) {
                createDashboard(input: $input) {
                    id
                    displayOrder
                    eventTypeId
                    dashboardTypeId
                    titleText
                }
            }
            """
            resp = graphql_query(
                mutation,
                ADMIN_HEADERS,
                {
                    "input": {
                        "displayOrder": order,
                        "eventTypeId": 1,
                        "dashboardTypeId": dtype_id,
                        "titleText": title,
                    }
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "errors" not in data, data.get("errors")
            created_ids.append(data["data"]["createDashboard"]["id"])

        # Query type=1 → expect 2 results
        query = """
        query ($typeId: Int!) {
            dashboards(dashboardTypeId: $typeId) {
                id
                displayOrder
                dashboardTypeId
                titleText
            }
        }
        """
        resp = graphql_query(query, ADMIN_HEADERS, {"typeId": 1})
        assert resp.status_code == 200
        dashboards = resp.json()["data"]["dashboards"]
        assert len(dashboards) == 2
        for d in dashboards:
            assert d["dashboardTypeId"] == 1

        # Query type=2 → expect 1 result
        resp = graphql_query(query, ADMIN_HEADERS, {"typeId": 2})
        assert resp.status_code == 200
        dashboards = resp.json()["data"]["dashboards"]
        assert len(dashboards) == 1
        assert dashboards[0]["dashboardTypeId"] == 2
        assert dashboards[0]["titleText"] == "Avg X"

        # Cleanup
        for did in created_ids:
            del_resp = graphql_query(
                "mutation ($id: Int!) { deleteDashboard(id: $id) }",
                ADMIN_HEADERS,
                {"id": did},
            )
            assert del_resp.status_code == 200

    def test_get_dashboards_order_asc(self):
        """Verify default ASC ordering by display_order."""
        # Create dashboards with non-sequential display_order values
        created_ids = []
        for order, title in [(30, "Third"), (10, "First"), (20, "Second")]:
            mutation = """
            mutation ($input: DashboardTypeInput!) {
                createDashboard(input: $input) {
                    id
                    displayOrder
                    titleText
                }
            }
            """
            resp = graphql_query(
                mutation,
                ADMIN_HEADERS,
                {
                    "input": {
                        "displayOrder": order,
                        "eventTypeId": 1,
                        "dashboardTypeId": 1,
                        "titleText": title,
                    }
                },
            )
            assert resp.status_code == 200
            assert "errors" not in resp.json(), resp.json().get("errors")
            created_ids.append(resp.json()["data"]["createDashboard"]["id"])

        # Query with default ASC
        query = """
        query ($typeId: Int!) {
            dashboards(dashboardTypeId: $typeId) {
                displayOrder
                titleText
            }
        }
        """
        resp = graphql_query(query, ADMIN_HEADERS, {"typeId": 1})
        assert resp.status_code == 200
        dashboards = resp.json()["data"]["dashboards"]
        orders = [d["displayOrder"] for d in dashboards]
        assert orders == sorted(orders), f"Expected ASC, got {orders}"
        assert [d["titleText"] for d in dashboards] == ["First", "Second", "Third"]

        # Cleanup
        for did in created_ids:
            graphql_query(
                "mutation ($id: Int!) { deleteDashboard(id: $id) }",
                ADMIN_HEADERS,
                {"id": did},
            )

    def test_get_dashboards_order_desc(self):
        """Verify DESC ordering by display_order."""
        created_ids = []
        for order, title in [(10, "First"), (30, "Third"), (20, "Second")]:
            mutation = """
            mutation ($input: DashboardTypeInput!) {
                createDashboard(input: $input) {
                    id
                    displayOrder
                    titleText
                }
            }
            """
            resp = graphql_query(
                mutation,
                ADMIN_HEADERS,
                {
                    "input": {
                        "displayOrder": order,
                        "eventTypeId": 1,
                        "dashboardTypeId": 1,
                        "titleText": title,
                    }
                },
            )
            assert resp.status_code == 200
            assert "errors" not in resp.json(), resp.json().get("errors")
            created_ids.append(resp.json()["data"]["createDashboard"]["id"])

        # Query with explicit DESC
        query = """
        query ($typeId: Int!) {
            dashboards(dashboardTypeId: $typeId, orderBy: DESC) {
                displayOrder
                titleText
            }
        }
        """
        resp = graphql_query(query, ADMIN_HEADERS, {"typeId": 1})
        assert resp.status_code == 200
        dashboards = resp.json()["data"]["dashboards"]
        orders = [d["displayOrder"] for d in dashboards]
        assert orders == sorted(orders, reverse=True), (
            f"Expected DESC, got {orders}"
        )
        assert [d["titleText"] for d in dashboards] == ["Third", "Second", "First"]

        # Cleanup
        for did in created_ids:
            graphql_query(
                "mutation ($id: Int!) { deleteDashboard(id: $id) }",
                ADMIN_HEADERS,
                {"id": did},
            )

    # ------------------------------------------------------------------
    # dashboard (single)
    # ------------------------------------------------------------------

    def test_get_dashboard_by_id(self):
        """Get single dashboard by ID."""
        # Create
        mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
                displayOrder
                eventTypeId
                dashboardTypeId
                titleText
            }
        }
        """
        resp = graphql_query(
            mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 5,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "Single Dashboard",
                }
            },
        )
        assert resp.status_code == 200
        created = resp.json()["data"]["createDashboard"]
        dash_id = created["id"]

        # Query by ID
        query = """
        query ($id: Int!) {
            dashboard(id: $id) {
                id
                displayOrder
                eventTypeId
                dashboardTypeId
                titleText
            }
        }
        """
        resp = graphql_query(query, ADMIN_HEADERS, {"id": dash_id})
        assert resp.status_code == 200
        dashboard = resp.json()["data"]["dashboard"]
        assert dashboard["id"] == dash_id
        assert dashboard["displayOrder"] == 5
        assert dashboard["eventTypeId"] == 1
        assert dashboard["dashboardTypeId"] == 1
        assert dashboard["titleText"] == "Single Dashboard"

        # Cleanup
        graphql_query(
            "mutation ($id: Int!) { deleteDashboard(id: $id) }",
            ADMIN_HEADERS,
            {"id": dash_id},
        )

    def test_get_dashboard_not_found(self):
        """Verify error when dashboard doesn't exist."""
        query = """
        query ($id: Int!) {
            dashboard(id: $id) {
                id
            }
        }
        """
        resp = graphql_query(query, ADMIN_HEADERS, {"id": 99999})
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "не найден" in payload["errors"][0]["message"]


# =============================================================================
# Mutation Tests
# =============================================================================


class TestDashboardMutations:
    """GraphQL mutations: create, update, delete with validation."""

    def test_create_dashboard(self):
        """Create a new dashboard, verify it's returned correctly."""
        mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
                displayOrder
                eventTypeId
                dashboardTypeId
                titleText
            }
        }
        """
        resp = graphql_query(
            mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "New Dashboard",
                }
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" not in payload, payload.get("errors")
        created = payload["data"]["createDashboard"]
        assert created["displayOrder"] == 1
        assert created["eventTypeId"] == 1
        assert created["dashboardTypeId"] == 1
        assert created["titleText"] == "New Dashboard"
        assert isinstance(created["id"], int)
        assert created["id"] > 0

        # Cleanup
        graphql_query(
            "mutation ($id: Int!) { deleteDashboard(id: $id) }",
            ADMIN_HEADERS,
            {"id": created["id"]},
        )

    def test_create_dashboard_invalid_order(self):
        """Verify error when display_order < 0."""
        mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": -1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "Bad Order",
                }
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "display_order должен быть >= 0" in payload["errors"][0]["message"]

    def test_create_dashboard_empty_title(self):
        """Verify error when title_text is empty/whitespace."""
        mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
            }
        }
        """
        # Test with empty string
        resp = graphql_query(
            mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "",
                }
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "title_text не может быть пустым" in payload["errors"][0]["message"]

        # Test with whitespace-only
        resp = graphql_query(
            mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "   ",
                }
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "title_text не может быть пустым" in payload["errors"][0]["message"]

    def test_update_dashboard(self):
        """Update an existing dashboard, verify changes."""
        # Create
        create_mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
                displayOrder
                eventTypeId
                dashboardTypeId
                titleText
            }
        }
        """
        resp = graphql_query(
            create_mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 10,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "Before Update",
                }
            },
        )
        assert resp.status_code == 200
        created = resp.json()["data"]["createDashboard"]
        dash_id = created["id"]

        # Update
        update_mutation = """
        mutation ($id: Int!, $input: DashboardTypeInput!) {
            updateDashboard(id: $id, input: $input) {
                id
                displayOrder
                eventTypeId
                dashboardTypeId
                titleText
            }
        }
        """
        resp = graphql_query(
            update_mutation,
            ADMIN_HEADERS,
            {
                "id": dash_id,
                "input": {
                    "displayOrder": 99,
                    "eventTypeId": 2,
                    "dashboardTypeId": 2,
                    "titleText": "After Update",
                },
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" not in payload, payload.get("errors")
        updated = payload["data"]["updateDashboard"]
        assert updated["id"] == dash_id
        assert updated["displayOrder"] == 99
        assert updated["eventTypeId"] == 2
        assert updated["dashboardTypeId"] == 2
        assert updated["titleText"] == "After Update"

        # Verify via query
        query = """
        query ($id: Int!) {
            dashboard(id: $id) {
                displayOrder
                eventTypeId
                dashboardTypeId
                titleText
            }
        }
        """
        resp = graphql_query(query, ADMIN_HEADERS, {"id": dash_id})
        assert resp.status_code == 200
        dashboard = resp.json()["data"]["dashboard"]
        assert dashboard["displayOrder"] == 99
        assert dashboard["titleText"] == "After Update"

        # Cleanup
        graphql_query(
            "mutation ($id: Int!) { deleteDashboard(id: $id) }",
            ADMIN_HEADERS,
            {"id": dash_id},
        )

    def test_delete_dashboard(self):
        """Delete a dashboard, verify it's removed."""
        # Create
        create_mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            create_mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "To Delete",
                }
            },
        )
        assert resp.status_code == 200
        dash_id = resp.json()["data"]["createDashboard"]["id"]

        # Delete
        delete_mutation = """
        mutation ($id: Int!) {
            deleteDashboard(id: $id)
        }
        """
        resp = graphql_query(delete_mutation, ADMIN_HEADERS, {"id": dash_id})
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" not in payload, payload.get("errors")
        assert payload["data"]["deleteDashboard"] is True

        # Verify it's gone
        query = """
        query ($id: Int!) {
            dashboard(id: $id) {
                id
            }
        }
        """
        resp = graphql_query(query, ADMIN_HEADERS, {"id": dash_id})
        assert resp.status_code == 200
        assert "errors" in resp.json()
        assert "не найден" in resp.json()["errors"][0]["message"]

    def test_delete_dashboard_not_found(self):
        """Verify error when deleting non-existent dashboard."""
        mutation = """
        mutation ($id: Int!) {
            deleteDashboard(id: $id)
        }
        """
        resp = graphql_query(mutation, ADMIN_HEADERS, {"id": 99999})
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "не найден" in payload["errors"][0]["message"]


# =============================================================================
# Permission Tests
# =============================================================================


class TestDashboardPermissions:
    """Verify that users without required rights get permission errors."""

    def test_create_dashboard_no_permission(self):
        """Verify permission denied for user without create right."""
        mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            mutation,
            USER_NO_PERM_HEADERS,
            {
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "No Perm",
                }
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "Недостаточно прав" in payload["errors"][0]["message"]

    def test_update_dashboard_no_permission(self):
        """Verify permission denied for user without edit right."""
        # First create a dashboard as admin
        create_mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            create_mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "For Perm Test",
                }
            },
        )
        assert resp.status_code == 200
        dash_id = resp.json()["data"]["createDashboard"]["id"]

        # Try to update as no-perm user
        update_mutation = """
        mutation ($id: Int!, $input: DashboardTypeInput!) {
            updateDashboard(id: $id, input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            update_mutation,
            USER_NO_PERM_HEADERS,
            {
                "id": dash_id,
                "input": {
                    "displayOrder": 2,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "Hacked",
                },
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "Недостаточно прав" in payload["errors"][0]["message"]

        # Cleanup as admin
        graphql_query(
            "mutation ($id: Int!) { deleteDashboard(id: $id) }",
            ADMIN_HEADERS,
            {"id": dash_id},
        )

    def test_delete_dashboard_no_permission(self):
        """Verify permission denied for user without delete right."""
        # First create a dashboard as admin
        create_mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            create_mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "For Delete Perm Test",
                }
            },
        )
        assert resp.status_code == 200
        dash_id = resp.json()["data"]["createDashboard"]["id"]

        # Try to delete as no-perm user
        delete_mutation = """
        mutation ($id: Int!) {
            deleteDashboard(id: $id)
        }
        """
        resp = graphql_query(delete_mutation, USER_NO_PERM_HEADERS, {"id": dash_id})
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "Недостаточно прав" in payload["errors"][0]["message"]

        # Cleanup as admin
        graphql_query(
            "mutation ($id: Int!) { deleteDashboard(id: $id) }",
            ADMIN_HEADERS,
            {"id": dash_id},
        )


# =============================================================================
# Fixture / FK Validation Tests
# =============================================================================


class TestDashboardForeignKeyValidation:
    """Verify that foreign key validation works correctly."""

    def test_create_dashboard_invalid_event_type(self):
        """Verify error when event_type_id does not exist."""
        mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 999,
                    "dashboardTypeId": 1,
                    "titleText": "Bad FK",
                }
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "EventType с id=999 не найден" in payload["errors"][0]["message"]

    def test_create_dashboard_invalid_dashboard_type(self):
        """Verify error when dashboard_type_id does not exist."""
        mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 999,
                    "titleText": "Bad FK",
                }
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "DashboardType с id=999 не найден" in payload["errors"][0]["message"]

    def test_update_dashboard_invalid_event_type(self):
        """Verify FK validation on update with non-existent event_type_id."""
        # Create a valid dashboard first
        create_mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            create_mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "Valid FK",
                }
            },
        )
        assert resp.status_code == 200
        dash_id = resp.json()["data"]["createDashboard"]["id"]

        # Try to update with invalid event_type_id
        update_mutation = """
        mutation ($id: Int!, $input: DashboardTypeInput!) {
            updateDashboard(id: $id, input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            update_mutation,
            ADMIN_HEADERS,
            {
                "id": dash_id,
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 999,
                    "dashboardTypeId": 1,
                    "titleText": "Bad FK Update",
                },
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "EventType с id=999 не найден" in payload["errors"][0]["message"]

        # Cleanup
        graphql_query(
            "mutation ($id: Int!) { deleteDashboard(id: $id) }",
            ADMIN_HEADERS,
            {"id": dash_id},
        )

    def test_update_dashboard_invalid_dashboard_type(self):
        """Verify FK validation on update with non-existent dashboard_type_id."""
        # Create a valid dashboard first
        create_mutation = """
        mutation ($input: DashboardTypeInput!) {
            createDashboard(input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            create_mutation,
            ADMIN_HEADERS,
            {
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 1,
                    "titleText": "Valid FK 2",
                }
            },
        )
        assert resp.status_code == 200
        dash_id = resp.json()["data"]["createDashboard"]["id"]

        # Try to update with invalid dashboard_type_id
        update_mutation = """
        mutation ($id: Int!, $input: DashboardTypeInput!) {
            updateDashboard(id: $id, input: $input) {
                id
            }
        }
        """
        resp = graphql_query(
            update_mutation,
            ADMIN_HEADERS,
            {
                "id": dash_id,
                "input": {
                    "displayOrder": 1,
                    "eventTypeId": 1,
                    "dashboardTypeId": 999,
                    "titleText": "Bad FK Update 2",
                },
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "errors" in payload
        assert "DashboardType с id=999 не найден" in payload["errors"][0]["message"]

        # Cleanup
        graphql_query(
            "mutation ($id: Int!) { deleteDashboard(id: $id) }",
            ADMIN_HEADERS,
            {"id": dash_id},
        )
