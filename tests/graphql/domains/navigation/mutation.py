"""Integration tests for GraphQL Mutation operations in navigation domain."""
from tests.graphql.base import graphql_query

# =============================================================================
# Конфигурация
# =============================================================================
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


# =============================================================================
# NavLocation Mutations
# =============================================================================
class TestGraphQLMutationsNavLocation:
    def test_200_crud_nav_location_full_cycle(self):
        create_q = """
        mutation {
            createNavLocation(data: {
                idSys: "test-loc", name: "Test Location", short: "TL",
                ready: true, address: "Test St", metro: "Test Metro"
            }) { id idSys name }
        }
        """
        r = graphql_query(create_q, headers=ADMIN_HEADERS)
        assert r["status_code"] == 200
        r = r["data"]
        assert "errors" not in r
        loc = r["data"]["createNavLocation"]
        assert loc["idSys"] == "test-loc"
        loc_id = loc["id"]

        update_q = f"""
        mutation {{
            updateNavLocation(id: {loc_id}, data: {{ name: "Updated Location" }})
            {{ id name }}
        }}
        """
        r = graphql_query(update_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["updateNavLocation"]["name"] == "Updated Location"

        delete_q = f"mutation {{ deleteNavLocation(id: {loc_id}) }}"
        r = graphql_query(delete_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["deleteNavLocation"] is True

        verify_q = f"{{ navLocation(id: {loc_id}) {{ id }} }}"
        r = graphql_query(verify_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["navLocation"] is None

    def test_400_create_nav_location_validation(self):
        q = """
        mutation {
            createNavLocation(data: { name: "No idSys" }) { id }
        }
        """
        r = graphql_query(q, headers=ADMIN_HEADERS)["data"]
        assert "errors" in r


# =============================================================================
# NavCampus Mutations
# =============================================================================
class TestGraphQLMutationsNavCampus:
    def test_200_crud_nav_campus_full_cycle(self):
        create_q = """
        mutation {
            createNavCampus(data: {
                idSys: "test-campus", locId: 1, name: "Test Campus",
                ready: true
            }) { id idSys name }
        }
        """
        r = graphql_query(create_q, headers=ADMIN_HEADERS)["data"]
        assert "errors" not in r
        campus = r["data"]["createNavCampus"]
        campus_id = campus["id"]

        update_q = f"""
        mutation {{
            updateNavCampus(id: {campus_id}, data: {{ name: "Updated Campus" }})
            {{ name }}
        }}
        """
        r = graphql_query(update_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["updateNavCampus"]["name"] == "Updated Campus"

        delete_q = f"mutation {{ deleteNavCampus(id: {campus_id}) }}"
        r = graphql_query(delete_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["deleteNavCampus"] is True


# =============================================================================
# NavPlan Mutations (с валидацией JSON-полей)
# =============================================================================
class TestGraphQLMutationsNavPlan:
    def test_200_create_nav_plan_with_json_fields(self):
        # Упрощённый JSON для избежания конфликтов с GraphQL-парсером
        create_q = """
        mutation {
            createNavPlan(data: {
                idSys: "test-plan", corId: 1, floorId: 1, ready: true,
                entrances: "[1, 2]",
                graph: "[{}]"
            }) { id idSys entrances graph }
        }
        """
        r = graphql_query(create_q, headers=ADMIN_HEADERS)["data"]
        assert "errors" not in r
        plan = r["data"]["createNavPlan"]
        assert plan["entrances"] == "[1, 2]"

    def test_400_create_nav_plan_invalid_json(self):
        create_q = """
        mutation {
            createNavPlan(data: {
                idSys: "bad-plan", corId: 1, floorId: 1, ready: true,
                entrances: "not-json"
            }) { id }
        }
        """
        r = graphql_query(create_q, headers=ADMIN_HEADERS)["data"]
        assert "errors" in r
        assert any("entrances" in e["message"].lower() and "json" in e["message"].lower()
                   for e in r["errors"])


# =============================================================================
# NavAuditory Mutations
# =============================================================================
class TestGraphQLMutationsNavAuditory:
    def test_200_crud_nav_auditory_full_cycle(self):
        create_q = """
        mutation {
            createNavAuditory(data: {
                idSys: "test-aud", typeId: 1, planId: 1, ready: true,
                name: "Test Aud 101"
            }) { id idSys name }
        }
        """
        r = graphql_query(create_q, headers=ADMIN_HEADERS)["data"]
        assert "errors" not in r
        aud = r["data"]["createNavAuditory"]
        aud_id = aud["id"]

        update_q = f"""
        mutation {{
            updateNavAuditory(id: {aud_id}, data: {{ name: "Updated Aud" }})
            {{ name }}
        }}
        """
        r = graphql_query(update_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["updateNavAuditory"]["name"] == "Updated Aud"

        delete_q = f"mutation {{ deleteNavAuditory(id: {aud_id}) }}"
        r = graphql_query(delete_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["deleteNavAuditory"] is True


# =============================================================================
# NavStatic Mutations
# =============================================================================
class TestGraphQLMutationsNavStatic:
    def test_200_crud_nav_static_full_cycle(self):
        create_q = """
        mutation {
            createNavStatic(data: {
                ext: "png", path: "/files/test.png",
                name: "test.png", link: "/api/static/test.png"
            }) { id name path }
        }
        """
        r = graphql_query(create_q, headers=ADMIN_HEADERS)["data"]
        assert "errors" not in r
        static = r["data"]["createNavStatic"]
        static_id = static["id"]

        update_q = f"""
        mutation {{
            updateNavStatic(id: {static_id}, data: {{ name: "updated.png" }})
            {{ name }}
        }}
        """
        r = graphql_query(update_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["updateNavStatic"]["name"] == "updated.png"

        delete_q = f"mutation {{ deleteNavStatic(id: {static_id}) }}"
        r = graphql_query(delete_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["deleteNavStatic"] is True


# =============================================================================
# Права доступа для мутаций
# =============================================================================
class TestGraphQLMutationsNavUnauthorized:
    def test_401_create_without_token(self):
        q = """mutation {
                   createNavLocation(
                       data: {
                           idSys: "x",
                           name: "x",
                           short: "x",
                           ready: true,
                           address: "x",
                           metro: "x"
                       }
                   ) { id }
               }"""
        r = graphql_query(q)
        assert r["status_code"] == 401

    def test_401_update_without_token(self):
        q = 'mutation { updateNavLocation(id: 1, data: { name: "hack" }) { id } }'
        r = graphql_query(q)
        assert r["status_code"] == 401

    def test_401_delete_without_token(self):
        q = 'mutation { deleteNavLocation(id: 1) }'
        r = graphql_query(q)
        assert r["status_code"] == 401


# =============================================================================
# Edge-кейсы мутаций
# =============================================================================
class TestGraphQLMutationsNavEdgeCases:
    def test_404_update_non_existent_id(self):
        q = """
        mutation {
            updateNavLocation(id: 999999, data: { name: "ghost" }) { id }
        }
        """
        r = graphql_query(q, headers=ADMIN_HEADERS)["data"]
        assert "errors" in r
        assert any("not found" in e["message"].lower() for e in r["errors"])

    def test_200_create_without_fk_validation(self):
        """
        Примечание: Фабрика мутаций не валидирует FK автоматически.
        Мутация успешно создаёт запись, т.к. в CampusResource нет валидатора loc_id.
        """
        q = """
        mutation {
            createNavCampus(data: {
                idSys: "no-fk-check", locId: 999999, name: "Bad", ready: true
            }) { id }
        }
        """
        r = graphql_query(q, headers=ADMIN_HEADERS)["data"]
        assert "errors" not in r
        assert r["data"]["createNavCampus"]["id"] is not None


# =============================================================================
# NavFloor Mutations (дополнительно)
# =============================================================================
class TestGraphQLMutationsNavFloor:
    """Тесты CRUD для сущности Floor."""

    def test_200_crud_nav_floor_full_cycle(self):
        # CREATE
        create_q = """
        mutation {
            createNavFloor(data: { name: 5 }) { id name }
        }
        """
        r = graphql_query(create_q, headers=ADMIN_HEADERS)["data"]
        assert "errors" not in r
        floor = r["data"]["createNavFloor"]
        assert floor["name"] == 5
        floor_id = floor["id"]

        # UPDATE
        update_q = f"""
        mutation {{
            updateNavFloor(id: {floor_id}, data: {{ name: 10 }})
            {{ id name }}
        }}
        """
        r = graphql_query(update_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["updateNavFloor"]["name"] == 10

        # DELETE
        delete_q = f"mutation {{ deleteNavFloor(id: {floor_id}) }}"
        r = graphql_query(delete_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["deleteNavFloor"] is True

    def test_404_update_non_existent_floor(self):
        q = """
        mutation {
            updateNavFloor(id: 999999, data: { name: 999 }) { id }
        }
        """
        r = graphql_query(q, headers=ADMIN_HEADERS)["data"]
        assert "errors" in r
        assert any("not found" in e["message"].lower() for e in r["errors"])


# =============================================================================
# NavType Mutations (дополнительно)
# =============================================================================
class TestGraphQLMutationsNavType:
    """Тесты CRUD для сущности Type."""

    def test_200_crud_nav_type_full_cycle(self):
        # CREATE
        create_q = """
        mutation {
            createNavType(data: { name: "Test Type" }) { id name }
        }
        """
        r = graphql_query(create_q, headers=ADMIN_HEADERS)["data"]
        assert "errors" not in r
        nav_type = r["data"]["createNavType"]
        assert nav_type["name"] == "Test Type"
        type_id = nav_type["id"]

        # UPDATE
        update_q = f"""
        mutation {{
            updateNavType(id: {type_id}, data: {{ name: "Updated Type" }})
            {{ id name }}
        }}
        """
        r = graphql_query(update_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["updateNavType"]["name"] == "Updated Type"

        # DELETE
        delete_q = f"mutation {{ deleteNavType(id: {type_id}) }}"
        r = graphql_query(delete_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["deleteNavType"] is True

    def test_404_update_non_existent_type(self):
        q = """
        mutation {
            updateNavType(id: 999999, data: { name: "Ghost" }) { id }
        }
        """
        r = graphql_query(q, headers=ADMIN_HEADERS)["data"]
        assert "errors" in r
        assert any("not found" in e["message"].lower() for e in r["errors"])


# =============================================================================
# NavPlan Mutations (Update и Delete + Валидация)
# =============================================================================
class TestGraphQLMutationsNavPlanExtended:
    """Дополнительные тесты для Plan: Update, Delete и валидация JSON при обновлении."""

    def test_200_update_nav_plan_success(self):
        # Сначала создаем план
        create_q = """
        mutation {
            createNavPlan(data: {
                idSys: "test-plan-update",
                corId: 1,
                floorId: 1,
                ready: true,
                entrances: "[]",
                graph: "[]"
            }) { id idSys entrances graph }
        }
        """
        r = graphql_query(create_q, headers=ADMIN_HEADERS)["data"]
        assert "errors" not in r
        plan_id = r["data"]["createNavPlan"]["id"]

        # Обновляем план (в том числе JSON поля)
        update_q = f"""
        mutation {{
            updateNavPlan(id: {plan_id}, data: {{
                entrances: "[{{\\"id\\": \\"e1\\"}}]",
                graph: "[{{\\"from\\": \\"e1\\", \\"to\\": \\"e2\\"}}]"
            }}) {{ id entrances graph }}
        }}
        """
        r = graphql_query(update_q, headers=ADMIN_HEADERS)["data"]
        assert "errors" not in r
        updated_plan = r["data"]["updateNavPlan"]
        assert updated_plan["entrances"] == '[{"id": "e1"}]'
        assert updated_plan["graph"] == '[{"from": "e1", "to": "e2"}]'

        # Cleanup
        delete_q = f"mutation {{ deleteNavPlan(id: {plan_id}) }}"
        graphql_query(delete_q, headers=ADMIN_HEADERS)

    def test_400_update_nav_plan_invalid_json(self):
        # Создаем валидный план
        create_q = """
        mutation {
            createNavPlan(data: {
                idSys: "test-plan-update",
                corId: 1,
                floorId: 1,
                ready: true,
                entrances: "[]",
                graph: "[]"
            }) { id }
        }
        """
        r = graphql_query(create_q, headers=ADMIN_HEADERS)["data"]
        plan_id = r["data"]["createNavPlan"]["id"]

        # Пытаемся обновить с невалидным JSON
        update_q = f"""
        mutation {{
            updateNavPlan(id: {plan_id}, data: {{
                entrances: "not-json"
            }}) {{ id }}
        }}
        """
        r = graphql_query(update_q, headers=ADMIN_HEADERS)["data"]
        assert "errors" in r
        assert any("entrances" in e["message"].lower() and "json" in e["message"].lower()
                   for e in r["errors"])

        # Cleanup
        delete_q = f"mutation {{ deleteNavPlan(id: {plan_id}) }}"
        graphql_query(delete_q, headers=ADMIN_HEADERS)

    def test_200_delete_nav_plan_success(self):
        create_q = """
        mutation {
            createNavPlan(data: {
                idSys: "test-plan-update",
                corId: 1,
                floorId: 1,
                ready: true,
                entrances: "[]",
                graph: "[]"
            }) { id }
        }
        """
        r = graphql_query(create_q, headers=ADMIN_HEADERS)["data"]
        plan_id = r["data"]["createNavPlan"]["id"]

        delete_q = f"mutation {{ deleteNavPlan(id: {plan_id}) }}"
        r = graphql_query(delete_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["deleteNavPlan"] is True

        # Verify deletion
        verify_q = f"{{ navPlan(id: {plan_id}) {{ id }} }}"
        r = graphql_query(verify_q, headers=ADMIN_HEADERS)["data"]
        assert r["data"]["navPlan"] is None

    def test_404_update_non_existent_plan(self):
        q = """
        mutation {
            updateNavPlan(id: 999999, data: { ready: false }) { id }
        }
        """
        r = graphql_query(q, headers=ADMIN_HEADERS)["data"]
        assert "errors" in r
        assert any("not found" in e["message"].lower() for e in r["errors"])
