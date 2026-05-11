"""Integration tests for GraphQL Query operations in stat domain."""
from datetime import date, timedelta

from tests.graphql.base import graphql_query

# =============================================================================
# Конфигурация
# =============================================================================
ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


class TestStatsQueries:
    """Тесты для запросов статистики эндпоинтов."""

    def test_200_endpoint_statistics_by_date(self):
        """Успешное получение статистики по дням."""
        query = """
        query GetStats($byDate: EndpointStatisticsByDateInput) {
            endpointStatistics(byDate: $byDate) {
                uniqueVisitors
                allVisits
                visitorCount
                period
            }
        }
        """
        resp = graphql_query(
            query,
            variables={"byDate": {"start": "2024-01-01", "end": "2024-01-31"}},
            headers=ADMIN_HEADERS,
        )
        assert resp["status_code"] == 200
        result = resp["data"]["data"]["endpointStatistics"]
        assert isinstance(result, list)
        if result:
            assert "uniqueVisitors" in result[0]
            assert "period" in result[0]

    def test_200_endpoint_statistics_by_month(self):
        """Успешное получение статистики по месяцам."""
        query = """
        query GetStats($byMonth: EndpointStatisticsByMonthInput) {
            endpointStatistics(byMonth: $byMonth) {
                uniqueVisitors
                allVisits
                visitorCount
                period
            }
        }
        """
        resp = graphql_query(
            query,
            variables={"byMonth": {"start": "2024-01", "end": "2024-03"}},
            headers=ADMIN_HEADERS,
        )
        assert resp["status_code"] == 200
        result = resp["data"]["data"]["endpointStatistics"]
        assert isinstance(result, list)

    def test_200_endpoint_statistics_by_year(self):
        """Успешное получение статистики по годам."""
        query = """
        query GetStats($byYear: EndpointStatisticsByYearInput) {
            endpointStatistics(byYear: $byYear) {
                uniqueVisitors
                allVisits
                visitorCount
                period
            }
        }
        """
        resp = graphql_query(
            query,
            variables={"byYear": {"start": "2024", "end": "2024"}},
            headers=ADMIN_HEADERS,
        )
        assert resp["status_code"] == 200
        result = resp["data"]["data"]["endpointStatistics"]
        assert isinstance(result, list)

    def test_200_aggregated_endpoint_statistics(self):
        """Успешное получение агрегированной статистики."""
        query = """
        query GetAggStats($byDate: EndpointStatisticsByDateInput) {
            endpointStatisticsAvg(byDate: $byDate) {
                totalVisits
                totalUnique
                totalVisitorCount
                avgVisits
                avgUnique
                avgVisitorCount
                entriesCount
            }
        }
        """
        resp = graphql_query(
            query,
            variables={"byDate": {"start": "2024-01-01", "end": "2024-01-31"}},
            headers=ADMIN_HEADERS,
        )
        assert resp["status_code"] == 200
        result = resp["data"]["data"]["endpointStatisticsAvg"]
        assert "totalVisits" in result
        assert "avgVisits" in result
        assert isinstance(result["totalVisits"], int)
        assert isinstance(result["avgVisits"], float)

    def test_200_filter_by_event_type_id(self):
        """Фильтрация статистики по event_type_id."""
        query = """
        query GetStats($eventTypeId: Int, $byDate: EndpointStatisticsByDateInput) {
            endpointStatistics(eventTypeId: $eventTypeId, byDate: $byDate) {
                uniqueVisitors
                period
            }
        }
        """
        resp = graphql_query(
            query,
            variables={"eventTypeId": 1, "byDate": {"start": "2024-01-01", "end": "2024-01-31"}},
            headers=ADMIN_HEADERS,
        )
        assert resp["status_code"] == 200
        result = resp["data"]["data"]["endpointStatistics"]
        assert isinstance(result, list)

    # =============================================================================
    # Тесты валидации окон
    # =============================================================================
    def test_400_missing_window_filter(self):
        """Ошибка при отсутствии фильтра окна."""
        query = """
        query GetStats {
            endpointStatistics {
                uniqueVisitors
            }
        }
        """
        resp = graphql_query(query, headers=ADMIN_HEADERS)
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("ровно один фильтр" in e["message"].lower() for e in resp["data"]["errors"])

    def test_400_multiple_window_filters(self):
        """Ошибка при передаче нескольких фильтров окна."""
        query = """
        query GetStats($byDate: EndpointStatisticsByDateInput, $byMonth: EndpointStatisticsByMonthInput) {
            endpointStatistics(byDate: $byDate, byMonth: $byMonth) {
                uniqueVisitors
            }
        }
        """
        resp = graphql_query(
            query,
            variables={
                "byDate": {"start": "2024-01-01", "end": "2024-01-31"},
                "byMonth": {"start": "2024-01", "end": "2024-03"},
            },
            headers=ADMIN_HEADERS,
        )
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("ровно один фильтр" in e["message"].lower() for e in resp["data"]["errors"])

    def test_400_invalid_date_range(self):
        """Ошибка при start > end."""
        query = """
        query GetStats($byDate: EndpointStatisticsByDateInput) {
            endpointStatistics(byDate: $byDate) { uniqueVisitors }
        }
        """
        resp = graphql_query(
            query,
            variables={"byDate": {"start": "2024-02-01", "end": "2024-01-01"}},
            headers=ADMIN_HEADERS,
        )
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("меньше или равен" in e["message"].lower() for e in resp["data"]["errors"])

    def test_400_invalid_month_format(self):
        """Ошибка при неверном формате месяца."""
        query = """
        query GetStats($byMonth: EndpointStatisticsByMonthInput) {
            endpointStatistics(byMonth: $byMonth) { uniqueVisitors }
        }
        """
        resp = graphql_query(
            query,
            variables={"byMonth": {"start": "2024/01", "end": "2024-03"}},
            headers=ADMIN_HEADERS,
        )
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("YYYY-MM" in e["message"] for e in resp["data"]["errors"])

    def test_400_start_date_in_future(self):
        """Ошибка при start > сегодня."""
        future = date.today() + timedelta(days=10)
        query = """
        query GetStats($byDate: EndpointStatisticsByDateInput) {
            endpointStatistics(byDate: $byDate) { uniqueVisitors }
        }
        """
        resp = graphql_query(
            query,
            variables={"byDate": {"start": future.isoformat(), "end": (future + timedelta(days=5)).isoformat()}},
            headers=ADMIN_HEADERS,
        )
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("сегодняшней даты" in e["message"].lower() for e in resp["data"]["errors"])

    # =============================================================================
    # Тесты валидации фильтров событий
    # =============================================================================
    def test_400_both_endpoint_and_event_type_id(self):
        """Ошибка при передаче endpoint и event_type_id одновременно."""
        query = """
        query GetStats($endpoint: String, $eventTypeId: Int, $byDate: EndpointStatisticsByDateInput) {
            endpointStatistics(endpoint: $endpoint, eventTypeId: $eventTypeId, byDate: $byDate) {
                uniqueVisitors
            }
        }
        """
        resp = graphql_query(
            query,
            variables={
                "endpoint": "site",
                "eventTypeId": 1,
                "byDate": {"start": "2024-01-01", "end": "2024-01-31"},
            },
            headers=ADMIN_HEADERS,
        )
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("только один фильтр" in e["message"].lower() for e in resp["data"]["errors"])

    def test_400_unknown_endpoint_code(self):
        """Ошибка при неизвестном коде endpoint."""
        query = """
        query GetStats($endpoint: String, $byDate: EndpointStatisticsByDateInput) {
            endpointStatistics(endpoint: $endpoint, byDate: $byDate) { uniqueVisitors }
        }
        """
        resp = graphql_query(
            query,
            variables={
                "endpoint": "nonexistent_code",
                "byDate": {"start": "2024-01-01", "end": "2024-01-31"},
            },
            headers=ADMIN_HEADERS,
        )
        assert resp["status_code"] == 200
        assert "errors" in resp["data"]
        assert any("неизвестный код" in e["message"].lower() for e in resp["data"]["errors"])

    # =============================================================================
    # Тесты прав доступа
    # =============================================================================
    def test_401_unauthorized(self):
        """Ошибка при отсутствии токена."""
        query = """
        query GetStats($byDate: EndpointStatisticsByDateInput) {
            endpointStatistics(byDate: $byDate) { uniqueVisitors }
        }
        """
        resp = graphql_query(
            query,
            variables={"byDate": {"start": "2024-01-01", "end": "2024-01-31"}},
        )
        assert resp["status_code"] == 401
