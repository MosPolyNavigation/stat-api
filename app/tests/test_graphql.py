"""Тесты для GraphQL эндпоинта /api/graphql"""

import pytest
from .base import client

# Токен администратора из base.py (пользователь с полными правами)
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def graphql_query(query: str, headers: dict = None):
    """Вспомогательная функция для выполнения GraphQL запросов"""
    response = client.post(
        "/api/graphql",
        json={"query": query},
        headers=headers or {}
    )
    return response


class TestGraphQLBasic:
    """Базовые тесты для GraphQL эндпоинта"""

    def test_200_graphql_endpoint_exists(self):
        """Проверка что GraphQL эндпоинт доступен"""
        query = "{ __typename }"
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200

    def test_200_graphql_introspection(self):
        """Проверка что интроспекция работает"""
        query = "{ __schema { queryType { name } } }"
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLNavLocations:
    """Тесты для nav_locations query"""

    def test_200_nav_locations_single_field(self):
        """Запрос nav_locations с одним полем (id)"""
        query = """
        {
            navLocations {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "navLocations" in data["data"]
        locations = data["data"]["navLocations"]
        assert isinstance(locations, list)
        if len(locations) > 0:
            assert "id" in locations[0]
            assert isinstance(locations[0]["id"], int)

    def test_200_nav_locations_all_fields(self):
        """Запрос nav_locations со всеми полями"""
        query = """
        {
            navLocations {
                id
                idSys
                name
                short
                ready
                address
                metro
                crossings
                comments
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        locations = data["data"]["navLocations"]
        if len(locations) > 0:
            location = locations[0]
            assert "id" in location
            assert "idSys" in location
            assert "name" in location
            assert "short" in location
            assert "ready" in location
            assert "address" in location
            assert "metro" in location


class TestGraphQLNavCampuses:
    """Тесты для nav_campuses query"""

    def test_200_nav_campuses_single_field(self):
        """Запрос nav_campuses с одним полем"""
        query = """
        {
            navCampuses {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "navCampuses" in data["data"]

    def test_200_nav_campuses_all_fields(self):
        """Запрос nav_campuses со всеми полями"""
        query = """
        {
            navCampuses {
                id
                idSys
                locId
                name
                ready
                stairGroups
                comments
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        campuses = data["data"]["navCampuses"]
        assert isinstance(campuses, list)


class TestGraphQLNavFloors:
    """Тесты для nav_floors query"""

    def test_200_nav_floors_single_field(self):
        """Запрос nav_floors с одним полем"""
        query = """
        {
            navFloors {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "navFloors" in data["data"]

    def test_200_nav_floors_all_fields(self):
        """Запрос nav_floors со всеми полями"""
        query = """
        {
            navFloors {
                id
                name
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLNavPlans:
    """Тесты для nav_plans query"""

    def test_200_nav_plans_single_field(self):
        """Запрос nav_plans с одним полем"""
        query = """
        {
            navPlans {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "navPlans" in data["data"]

    def test_200_nav_plans_all_fields(self):
        """Запрос nav_plans со всеми полями"""
        query = """
        {
            navPlans {
                id
                idSys
                corId
                floorId
                ready
                entrances
                graph
                svgId
                nearestEntrance
                nearestManWc
                nearestWomanWc
                nearestSharedWc
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        plans = data["data"]["navPlans"]
        assert isinstance(plans, list)


class TestGraphQLNavTypes:
    """Тесты для nav_types query"""

    def test_200_nav_types_single_field(self):
        """Запрос nav_types с одним полем"""
        query = """
        {
            navTypes {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "navTypes" in data["data"]

    def test_200_nav_types_all_fields(self):
        """Запрос nav_types со всеми полями"""
        query = """
        {
            navTypes {
                id
                name
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLNavAuditories:
    """Тесты для nav_auditories query"""

    def test_200_nav_auditories_single_field(self):
        """Запрос nav_auditories с одним полем"""
        query = """
        {
            navAuditories {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "navAuditories" in data["data"]

    def test_200_nav_auditories_all_fields(self):
        """Запрос nav_auditories со всеми полями"""
        query = """
        {
            navAuditories {
                id
                idSys
                typeId
                ready
                planId
                name
                textFromSign
                additionalInfo
                comments
                link
                photoId
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLNavStatics:
    """Тесты для nav_statics query"""

    def test_200_nav_statics_single_field(self):
        """Запрос nav_statics с одним полем"""
        query = """
        {
            navStatics {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "navStatics" in data["data"]

    def test_200_nav_statics_all_fields(self):
        """Запрос nav_statics со всеми полями"""
        query = """
        {
            navStatics {
                id
                idSys
                typeId
                planId
                name
                textFromSign
                additionalInfo
                comments
                link
                photoId
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLReviews:
    """Тесты для reviews query"""

    def test_200_reviews_single_field(self):
        """Запрос reviews с одним полем"""
        query = """
        {
            reviews {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "reviews" in data["data"]

    def test_200_reviews_all_fields(self):
        """Запрос reviews со всеми полями"""
        query = """
        {
            reviews(limit: 10) {
                id
                userId
                problemId
                text
                imageName
                creationDate
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_200_reviews_with_nested_entities(self):
        """Запрос reviews с вложенными сущностями (problem, user)"""
        query = """
        {
            reviews(limit: 5) {
                id
                text
                problem {
                    id
                    name
                    description
                }
                user {
                    id
                    userId
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLProblems:
    """Тесты для problems query"""

    def test_200_problems_single_field(self):
        """Запрос problems с одним полем"""
        query = """
        {
            problems {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "problems" in data["data"]

    def test_200_problems_all_fields(self):
        """Запрос problems со всеми полями"""
        query = """
        {
            problems {
                id
                name
                description
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLSiteStats:
    """Тесты для siteStats query"""

    def test_200_site_stats_single_field(self):
        """Запрос siteStats с одним полем"""
        query = """
        {
            siteStats(limit: 10) {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "siteStats" in data["data"]

    def test_200_site_stats_all_fields(self):
        """Запрос siteStats со всеми полями"""
        query = """
        {
            siteStats(limit: 10) {
                id
                userId
                dateTime
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_200_site_stats_with_nested_user(self):
        """Запрос siteStats с вложенной сущностью user"""
        query = """
        {
            siteStats(limit: 5) {
                id
                user {
                    id
                    userId
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLStartWays:
    """Тесты для startWays query"""

    def test_200_start_ways_single_field(self):
        """Запрос startWays с одним полем"""
        query = """
        {
            startWays(limit: 10) {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "startWays" in data["data"]

    def test_200_start_ways_all_fields(self):
        """Запрос startWays со всеми полями"""
        query = """
        {
            startWays(limit: 10) {
                id
                userId
                startId
                endId
                dateTime
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_200_start_ways_with_nested_user(self):
        """Запрос startWays с вложенной сущностью user"""
        query = """
        {
            startWays(limit: 5) {
                id
                startId
                endId
                user {
                    id
                    userId
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLSelectAuditories:
    """Тесты для selectAuditories query"""

    def test_200_select_auditories_single_field(self):
        """Запрос selectAuditories с одним полем"""
        query = """
        {
            selectAuditories(limit: 10) {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "selectAuditories" in data["data"]

    def test_200_select_auditories_all_fields(self):
        """Запрос selectAuditories со всеми полями"""
        query = """
        {
            selectAuditories(limit: 10) {
                id
                userId
                auditoryId
                dateTime
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_200_select_auditories_with_nested_user(self):
        """Запрос selectAuditories с вложенной сущностью user"""
        query = """
        {
            selectAuditories(limit: 5) {
                id
                auditoryId
                user {
                    id
                    userId
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLChangePlans:
    """Тесты для changePlans query"""

    def test_200_change_plans_single_field(self):
        """Запрос changePlans с одним полем"""
        query = """
        {
            changePlans(limit: 10) {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "changePlans" in data["data"]

    def test_200_change_plans_all_fields(self):
        """Запрос changePlans со всеми полями"""
        query = """
        {
            changePlans(limit: 10) {
                id
                userId
                planId
                dateTime
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_200_change_plans_with_nested_user(self):
        """Запрос changePlans с вложенной сущностью user"""
        query = """
        {
            changePlans(limit: 5) {
                id
                planId
                user {
                    id
                    userId
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLUserIds:
    """Тесты для userIds query"""

    def test_200_user_ids_single_field(self):
        """Запрос userIds с одним полем"""
        query = """
        {
            userIds(limit: 10) {
                userId
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "userIds" in data["data"]

    def test_200_user_ids_all_fields(self):
        """Запрос userIds со всеми полями"""
        query = """
        {
            userIds(limit: 10) {
                userId
                creationDate
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLEndpointStatistics:
    """Тесты для endpointStatistics query с фильтрами"""

    def test_200_endpoint_statistics_filter_site(self):
        """Запрос endpointStatistics с фильтром endpoint='site'"""
        query = """
        {
            endpointStatistics(endpoint: "site") {
                uniqueVisitors
                allVisits
                visitorCount
                period
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "endpointStatistics" in data["data"]
        stats = data["data"]["endpointStatistics"]
        assert isinstance(stats, list)
        if len(stats) > 0:
            stat = stats[0]
            assert "uniqueVisitors" in stat
            assert "allVisits" in stat
            assert "visitorCount" in stat
            assert "period" in stat

    def test_200_endpoint_statistics_filter_auds(self):
        """Запрос endpointStatistics с фильтром endpoint='auds'"""
        query = """
        {
            endpointStatistics(endpoint: "auds") {
                uniqueVisitors
                allVisits
                visitorCount
                period
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "endpointStatistics" in data["data"]

    def test_200_endpoint_statistics_filter_ways(self):
        """Запрос endpointStatistics с фильтром endpoint='ways'"""
        query = """
        {
            endpointStatistics(endpoint: "ways") {
                uniqueVisitors
                allVisits
                visitorCount
                period
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "endpointStatistics" in data["data"]

    def test_200_endpoint_statistics_filter_plans(self):
        """Запрос endpointStatistics с фильтром endpoint='plans'"""
        query = """
        {
            endpointStatistics(endpoint: "plans") {
                uniqueVisitors
                allVisits
                visitorCount
                period
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "endpointStatistics" in data["data"]

    def test_200_endpoint_statistics_single_field(self):
        """Запрос endpointStatistics с одним полем"""
        query = """
        {
            endpointStatistics(endpoint: "site") {
                period
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


class TestGraphQLUnauthorized:
    """Тесты на неавторизованный доступ к GraphQL"""

    def test_401_graphql_without_token_returns_unauthorized(self):
        """GraphQL требует авторизацию - возвращает 401 при отсутствии токена"""
        query = """
        {
            reviews {
                id
            }
        }
        """
        response = graphql_query(query)  # Без токена
        # FastAPI требует авторизацию для GraphQL через depends
        assert response.status_code == 401

    def test_401_graphql_nav_without_token(self):
        """Попытка получить nav данные без токена возвращает 401"""
        query = """
        {
            navLocations {
                id
                name
            }
        }
        """
        response = graphql_query(query)  # Без токена
        assert response.status_code == 401

    def test_401_graphql_endpoint_stats_without_token(self):
        """Попытка получить статистику без токена возвращает 401"""
        query = """
        {
            endpointStatistics(endpoint: "site") {
                period
                allVisits
            }
        }
        """
        response = graphql_query(query)  # Без токена
        assert response.status_code == 401


class TestGraphQLMultipleQueries:
    """Тесты на множественные запросы в одном GraphQL вызове"""

    def test_200_multiple_queries_in_one_request(self):
        """Несколько queries в одном запросе"""
        query = """
        {
            navFloors {
                id
                name
            }
            navTypes {
                id
                name
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "navFloors" in data["data"]
        assert "navTypes" in data["data"]

    def test_200_query_with_filters(self):
        """Запрос с использованием фильтров"""
        query = """
        {
            reviews(limit: 5) {
                id
                text
            }
            siteStats(limit: 3) {
                id
                dateTime
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
