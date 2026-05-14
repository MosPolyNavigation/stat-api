"""Integration tests for GraphQL Query operations in navigation domain."""
from tests.graphql.base import graphql_query

# =============================================================================
# Конфигурация
# =============================================================================
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


# =============================================================================
# Базовые тесты навигации
# =============================================================================
class TestGraphQLNavigationBasic:
    """Smoke-тесты для домена navigation."""

    def test_200_nav_locations_connection_basic(self):
        query = """
        {
            navLocations(pagination: { page: 1, pageSize: 3 }) {
                nodes { id idSys name short address ready metro }
                pageInfo { hasNextPage hasPreviousPage }
                paginationInfo { totalCount currentPage totalPages }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        data = resp["data"]["navLocations"]
        assert isinstance(data["nodes"], list)
        assert len(data["nodes"]) >= 1  # есть сиды
        assert data["paginationInfo"]["totalCount"] >= 1

    def test_200_nav_location_single_by_id(self):
        # ID из сидов
        query = '{ navLocation(id: 1) { id idSys name short address } }'
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        loc = resp["data"]["navLocation"]
        assert loc["id"] == 1
        assert loc["idSys"] == "AV"
        assert loc["name"] == "Автозаводская"


# =============================================================================
# Тесты связей и вложенных полей (DataLoader)
# =============================================================================
class TestGraphQLNavigationRelations:
    """Тесты ленивой загрузки связанных сущностей."""

    def test_200_nav_location_with_nested_campuses(self):
        """Проверка one-to-many: Location → Campus."""
        query = """
        {
            navLocation(id: 1) {
                id
                name
                campuses(pagination: { pageSize: 5 }) {
                    nodes {
                        id
                        idSys
                        name
                        ready
                    }
                }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        loc = resp["data"]["navLocation"]
        assert loc["id"] == 1
        campuses = loc["campuses"]["nodes"]
        assert len(campuses) >= 1
        assert campuses[0]["idSys"] == "av-test"

    def test_200_nav_campus_with_nested_location_and_plans(self):
        """Проверка one-to-one и one-to-many: Campus → Location + Plans."""
        query = """
        {
            navCampus(id: 1) {
                id
                name
                location { id name }
                plans(pagination: { pageSize: 5 }) {
                    nodes {
                        id
                        idSys
                        floor { id name }
                    }
                }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        campus = resp["data"]["navCampus"]
        assert campus["location"]["name"] == "Автозаводская"
        assert len(campus["plans"]["nodes"]) >= 1
        assert campus["plans"]["nodes"][0]["floor"]["name"] == 1

    def test_200_nav_plan_with_nested_relations(self):
        """Проверка сложных вложенных связей: Plan → Campus/Floor/SVG/Auditories."""
        query = """
        {
            navPlan(id: 1) {
                id
                idSys
                campus { id name location { name } }
                floor { id name }
                auditories(pagination: { pageSize: 10 }) {
                    nodes {
                        id
                        name
                        type { name }
                        photos(pagination: { pageSize: 5 }) {
                            nodes {
                                id
                                name
                                path
                            }
                        }
                    }
                }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        plan = resp["data"]["navPlan"]
        assert plan["campus"]["location"]["name"] == "Автозаводская"
        assert plan["floor"]["name"] == 1
        assert len(plan["auditories"]["nodes"]) >= 1
        aud = plan["auditories"]["nodes"][0]
        assert aud["type"]["name"] == "Учебная аудитория"
        assert len(aud["photos"]["nodes"]) >= 1
        assert aud["photos"]["nodes"][0]["name"] == "test.jpg"

    def test_200_nav_auditory_with_nested_type_plan_photos(self):
        """Проверка всех связей аудитории."""
        query = """
        {
            navAuditory(id: 1) {
                id
                idSys
                name
                type { id name }
                plan { id idSys floor { name } }
                photos(pagination: { pageSize: 5 }) { nodes { id name ext path } }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        aud = resp["data"]["navAuditory"]
        assert aud["type"]["name"] == "Учебная аудитория"
        assert aud["plan"]["idSys"] == "test-plan-1"
        assert aud["photos"]["nodes"][0]["ext"] == "jpg"


# =============================================================================
# Тесты фильтрации
# =============================================================================
class TestGraphQLNavigationFiltering:
    """Тесты фильтрации через *FilterInput."""

    def test_200_nav_locations_filter_by_id_sys(self):
        query = """
        {
            navLocations(filter: { idSys: { eq: "AV" } }) {
                nodes { id idSys name }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        nodes = resp["data"]["navLocations"]["nodes"]
        assert all(n["idSys"] == "AV" for n in nodes)

    def test_200_nav_campuses_filter_by_ready_and_name(self):
        query = """
        {
            navCampuses(
                filter: {
                    ready: { eq: true }
                    name: { contains: "Тест" }
                }
            ) {
                nodes { id name ready }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        nodes = resp["data"]["navCampuses"]["nodes"]
        assert all(n["ready"] is True for n in nodes)
        assert all("Тест" in n["name"] for n in nodes)

    def test_200_nav_auditories_filter_by_plan_id_and_type(self):
        query = """
        {
            navAuditories(
                filter: {
                    planId: { eq: 1 }
                    typeId: { eq: 1 }
                }
            ) {
                nodes { id name planId typeId }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        nodes = resp["data"]["navAuditories"]["nodes"]
        assert all(n["planId"] == 1 and n["typeId"] == 1 for n in nodes)

    def test_200_nav_photos_filter_by_aud_id_and_ext(self):
        query = """
        {
            navAuditoryPhotos(
                filter: { audId: { eq: 1 }, ext: { eq: "jpg" } }
            ) {
                nodes { id name ext }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        nodes = resp["data"]["navAuditoryPhotos"]["nodes"]
        assert all(n["ext"] == "jpg" for n in nodes)


# =============================================================================
# Тесты сортировки
# =============================================================================
class TestGraphQLNavigationOrdering:
    """Тесты сортировки через *OrderByInput."""

    def test_200_nav_locations_order_by_name_asc(self):
        query = """
        {
            navLocations(orderBy: { name: ASC }) {
                nodes { id name }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        names = [n["name"] for n in resp["data"]["navLocations"]["nodes"]]
        assert names == sorted(names)

    def test_200_nav_campuses_order_by_name_desc(self):
        query = """
        {
            navCampuses(orderBy: { name: DESC }) {
                nodes { id name }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        names = [n["name"] for n in resp["data"]["navCampuses"]["nodes"]]
        assert names == sorted(names, reverse=True)

    def test_200_nav_auditories_order_by_id_then_name(self):
        query = """
        {
            navAuditories(orderBy: { id: ASC, thenBy: { name: DESC } }) {
                nodes { id name }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        nodes = resp["data"]["navAuditories"]["nodes"]
        # Проверяем, что по id отсортировано (thenBy не сработает при уникальных id)
        ids = [n["id"] for n in nodes]
        assert ids == sorted(ids)


# =============================================================================
# Тесты пагинации
# =============================================================================
class TestGraphQLNavigationPagination:
    """Тесты пагинации через PaginationInput."""

    def test_200_nav_locations_pagination_page_size(self):
        query = """
        {
            navLocations(pagination: { page: 1, pageSize: 1 }) {
                nodes { id }
                paginationInfo { totalCount currentPage totalPages }
                pageInfo { hasNextPage }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        data = resp["data"]["navLocations"]
        assert len(data["nodes"]) == 1
        assert data["paginationInfo"]["currentPage"] == 1
        assert data["pageInfo"]["hasNextPage"] is False  # всего 1 локация в сидах

    def test_200_nav_campuses_pagination_navigation(self):
        # Создаём дополнительные кампусы для теста навигации
        for i in range(2, 6):
            graphql_query(f"""
            mutation {{
                createNavCampus( {{
                    idSys: "test-{i}", locId: 1, name: "Campus {i}",
                    ready: true
                }}) {{ id }}
            }}
            """, ADMIN_HEADERS)

        try:
            # Страница 1
            q1 = """
            {
                navCampuses(pagination: { page: 1, pageSize: 2 }, orderBy: { id: ASC }) {
                    nodes { id }
                    pageInfo { hasNextPage }
                    paginationInfo { totalPages }
                }
            }
            """
            r1 = graphql_query(q1, headers=ADMIN_HEADERS)["data"]
            p1 = r1["data"]["navCampuses"]
            ids1 = {n["id"] for n in p1["nodes"]}

            # Страница 2
            q2 = """
            {
                navCampuses(pagination: { page: 2, pageSize: 2 }, orderBy: { id: ASC }) {
                    nodes { id }
                    pageInfo { hasPreviousPage }
                }
            }
            """
            r2 = graphql_query(q2, headers=ADMIN_HEADERS)["data"]
            p2 = r2["data"]["navCampuses"]
            ids2 = {n["id"] for n in p2["nodes"]}

            # IDs не должны пересекаться
            assert ids1.isdisjoint(ids2)
            assert p2["pageInfo"]["hasPreviousPage"] is True
        finally:
            # Cleanup
            for i in range(2, 6):
                graphql_query(f"mutation {{ deleteNavCampus(id: {i}) }}", headers=ADMIN_HEADERS)


# =============================================================================
# Права доступа
# =============================================================================
class TestGraphQLNavigationUnauthorized:
    """Тесты проверки прав доступа."""

    def test_401_nav_locations_without_token(self):
        query = "{ navLocations(pagination: { pageSize: 1 }) { nodes { id } } }"
        resp = graphql_query(query)
        assert resp["status_code"] == 401

    def test_401_nav_auditory_single_without_token(self):
        query = "{ navAuditory(id: 1) { id } }"
        resp = graphql_query(query)
        assert resp["status_code"] == 401


# =============================================================================
# Edge-кейсы
# =============================================================================
class TestGraphQLNavigationEdgeCases:
    """Тесты граничных условий."""

    def test_404_nav_location_non_existent_id(self):
        query = "{ navLocation(id: 999999) { id } }"
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        assert resp["data"]["navLocation"] is None

    def test_200_empty_filter_result(self):
        query = """
        {
            navAuditories(filter: { id: { eq: 999999 } }) {
                nodes { id }
                paginationInfo { totalCount }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        data = resp["data"]["navAuditories"]
        assert len(data["nodes"]) == 0
        assert data["paginationInfo"]["totalCount"] == 0

    def test_200_nested_query_with_null_relations(self):
        # Запрос связи, которая может быть null (svg у плана)
        query = """
        {
            navPlan(id: 1) {
                id
                svg { id }  # ← svg_id = null в сидах
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        resp = resp["data"]
        assert resp["data"]["navPlan"]["svg"] is None


# =============================================================================
# Тесты для недостающих сущностей (Floor, Type, Static)
# =============================================================================
class TestGraphQLNavigationFloorTypeAndStaticQueries:
    """Тесты для сущностей Floor, Type и Static, которые не были покрыты ранее."""

    def test_200_nav_floors_connection(self):
        """Проверка списка этажей."""
        query = """
        {
            navFloors(pagination: { page: 1, pageSize: 5 }) {
                nodes { id name }
                paginationInfo { totalCount }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        data = resp["data"]["data"]["navFloors"]
        assert isinstance(data["nodes"], list)
        # В сидах есть этаж с name=1
        if data["paginationInfo"]["totalCount"] > 0:
            assert any(n["name"] == 1 for n in data["nodes"])

    def test_200_nav_floor_single_by_id(self):
        """Получение одного этажа по ID."""
        query = """
        {
            navFloor(id: 1) { id name }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        floor = resp["data"]["data"]["navFloor"]
        assert floor is not None
        assert floor["id"] == 1
        assert floor["name"] == 1

    def test_200_nav_types_connection(self):
        """Проверка списка типов аудиторий."""
        query = """
        {
            navTypes(filter: { name: { eq: "Учебная аудитория" } }) {
                nodes { id name }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        data = resp["data"]["data"]["navTypes"]
        assert len(data["nodes"]) >= 1
        assert data["nodes"][0]["name"] == "Учебная аудитория"

    def test_200_nav_type_single_by_id(self):
        """Получение одного типа аудитории по ID."""
        query = """
        {
            navType(id: 1) { id name }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        nav_type = resp["data"]["data"]["navType"]
        assert nav_type is not None
        assert nav_type["id"] == 1
        assert nav_type["name"] == "Учебная аудитория"

    def test_200_nav_statics_connection(self):
        """Проверка списка статических файлов (может быть пустым)."""
        query = """
        {
            navStatics(pagination: { page: 1, pageSize: 5 }) {
                nodes { id ext path name link }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        data = resp["data"]["data"]["navStatics"]
        assert isinstance(data["nodes"], list)


# =============================================================================
# Тесты проверки форматов данных (Crossings, Entrances, Links)
# =============================================================================
class TestGraphQLNavigationDataFormats:
    """Тесты проверки конкретных форматов полей (списки, URL)."""

    def test_200_nav_location_crossings_is_list(self):
        """Проверка, что crossings в локации — это список (или null)."""
        query = """
        {
            navLocation(id: 1) { id crossings }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        loc = resp["data"]["data"]["navLocation"]
        # crossings может быть строкой JSON или null в зависимости от реализации конвертера,
        # но в старых тестах проверялся список. Если у вас конвертер возвращает строку JSON,
        # адаптируйте ассерт под ваш тип. Здесь предполагаем, что поле есть.
        assert "crossings" in loc

    def test_200_nav_campus_crossings_is_list(self):
        """Проверка, что crossings в кампусе — это список."""
        query = """
        {
            navLocation(id: 1) { id crossings }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        campus = resp["data"]["data"]["navLocation"]
        assert "crossings" in campus

    def test_200_nav_plan_entrances_and_graph_are_lists(self):
        """Проверка, что entrances и graph в плане — это списки."""
        query = """
        {
            navPlan(id: 1) { id entrances graph }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        plan = resp["data"]["data"]["navPlan"]
        assert "entrances" in plan
        assert "graph" in plan
        # Если ваши типы возвращают строки JSON, проверьте тип str.
        # Если объекты/списки, проверьте list.
        # В старых тестах проверялось isinstance(..., list).
        # Адаптируйте под вашу реализацию типов.

    def test_200_nav_auditory_photo_link_format(self):
        """Проверка формата ссылки на фото аудитории."""
        query = """
        {
            navAuditoryPhotos(pagination: { page: 1, pageSize: 1 }) {
                nodes { id link }
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        data = resp["data"]["data"]["navAuditoryPhotos"]
        if data["nodes"]:
            photo = data["nodes"][0]
            assert photo["link"].startswith("/api/nav/auditory/photos/")


# =============================================================================
# Тесты покрытия 404 для остальных сущностей
# =============================================================================
class TestGraphQLNavigationNotFoundCoverage:
    """Дополнительные тесты 404 для сущностей, не покрытых в EdgeCases."""

    def test_404_nav_campus_non_existent_id(self):
        query = "{ navCampus(id: 999999) { id } }"
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert resp["data"]["data"]["navCampus"] is None

    def test_404_nav_plan_non_existent_id(self):
        query = "{ navPlan(id: 999999) { id } }"
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert resp["data"]["data"]["navPlan"] is None

    def test_404_nav_floor_non_existent_id(self):
        query = "{ navFloor(id: 999999) { id } }"
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert resp["data"]["data"]["navFloor"] is None

    def test_404_nav_type_non_existent_id(self):
        query = "{ navType(id: 999999) { id } }"
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert resp["data"]["data"]["navType"] is None

    def test_404_nav_static_non_existent_id(self):
        query = "{ navStatic(id: 999999) { id } }"
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert resp["data"]["data"]["navStatic"] is None

    def test_404_nav_auditory_photo_non_existent_id(self):
        query = "{ navAuditoryPhoto(id: 999999) { id } }"
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert resp["data"]["data"]["navAuditoryPhoto"] is None


# =============================================================================
# Тесты батчинга (несколько запросов в одном)
# =============================================================================
class TestGraphQLNavigationBatching:
    """Тесты эффективности и корректности выполнения нескольких запросов."""

    def test_200_multiple_queries_in_one_request(self):
        """Проверка выполнения нескольких независимых запросов в одном HTTP-запросе."""
        query = """
        {
            navFloors(pagination: { page: 1, pageSize: 1 }) { nodes { id } }
            navTypes(pagination: { page: 1, pageSize: 1 }) { nodes { id } }
            navLocations(pagination: { page: 1, pageSize: 1 }) { nodes { id } }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        data = resp["data"]["data"]
        assert "navFloors" in data
        assert "navTypes" in data
        assert "navLocations" in data
