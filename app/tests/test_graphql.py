"""Smoke tests for GraphQL endpoint /api/graphql."""

from .base import client

ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def graphql_query(query: str, headers: dict = None, variables: dict = None):
    return client.post(
        "/api/graphql",
        json={"query": query, "variables": variables or {}},
        headers=headers or {},
    )


class TestGraphQLBasic:
    def test_200_graphql_endpoint_exists(self):
        response = graphql_query("{ __typename }", ADMIN_HEADERS)
        assert response.status_code == 200

    def test_200_graphql_introspection(self):
        response = graphql_query("{ __schema { queryType { name } } }", ADMIN_HEADERS)
        assert response.status_code == 200
        assert "data" in response.json()


class TestGraphQLNavConnections:
    def test_200_nav_locations_connection(self):
        query = """
        {
            navLocations(filter: {idSys: "AV"}, pagination: {limit: 10}) {
                nodes {
                    id
                    idSys
                    name
                }
                pageInfo {
                    hasNextPage
                }
                paginationInfo {
                    totalCount
                    currentPage
                    totalPages
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        payload = response.json()["data"]["navLocations"]
        assert payload["nodes"][0]["idSys"] == "AV"
        assert payload["paginationInfo"]["totalCount"] >= 1

    def test_200_nav_campuses_with_related_location(self):
        query = """
        {
            navCampuses(filter: {idSys: "av-test"}) {
                nodes {
                    id
                    idSys
                    locId
                    location {
                        id
                        idSys
                    }
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        campus = response.json()["data"]["navCampuses"]["nodes"][0]
        assert campus["idSys"] == "av-test"
        assert campus["location"]["idSys"] == "AV"

    def test_200_nav_floors_connection(self):
        query = """
        {
            navFloors(filter: {name: 1}) {
                nodes {
                    id
                    name
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        assert response.json()["data"]["navFloors"]["nodes"][0]["name"] == 1

    def test_200_nav_plans_with_related_entities(self):
        query = """
        {
            navPlans(filter: {idSys: "test-plan-1"}) {
                nodes {
                    id
                    idSys
                    corId
                    floorId
                    campus {
                        id
                        idSys
                    }
                    floor {
                        id
                        name
                    }
                    svg {
                        id
                        name
                    }
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        plan = response.json()["data"]["navPlans"]["nodes"][0]
        assert plan["idSys"] == "test-plan-1"
        assert plan["campus"]["idSys"] == "av-test"
        assert plan["floor"]["name"] == 1
        assert plan["svg"] is None

    def test_200_nav_types_connection(self):
        query = """
        {
            navTypes(filter: {name: "Учебная аудитория"}) {
                nodes {
                    id
                    name
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        assert response.json()["data"]["navTypes"]["nodes"][0]["name"] == "Учебная аудитория"

    def test_200_nav_auditories_with_related_entities(self):
        query = """
        {
            navAuditories(filter: {idSys: "test-101"}) {
                nodes {
                    id
                    idSys
                    typeId
                    planId
                    type {
                        id
                        name
                    }
                    plan {
                        id
                        idSys
                    }
                    photos {
                        id
                        link
                    }
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        auditory = response.json()["data"]["navAuditories"]["nodes"][0]
        assert auditory["idSys"] == "test-101"
        assert auditory["type"]["id"] == 1
        assert auditory["plan"]["idSys"] == "test-plan-1"
        assert auditory["photos"][0]["link"].startswith("/api/nav/auditory/photos/")

    def test_200_nav_auditory_photos_connection(self):
        query = """
        {
            navAuditoryPhotos(filter: {audId: 1}) {
                nodes {
                    id
                    audId
                    ext
                    link
                    auditory {
                        id
                        idSys
                    }
                }
                paginationInfo {
                    totalCount
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        payload = response.json()["data"]["navAuditoryPhotos"]
        assert payload["paginationInfo"]["totalCount"] >= 1
        assert payload["nodes"][0]["auditory"]["idSys"] == "test-101"

    def test_200_nav_statics_connection(self):
        query = """
        {
            navStatics(pagination: {limit: 5}) {
                nodes {
                    id
                    ext
                    path
                    name
                    link
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        assert isinstance(response.json()["data"]["navStatics"]["nodes"], list)


class TestGraphQLOtherQueries:
    def test_200_reviews_with_nested_entities(self):
        query = """
        {
            reviews(limit: 5) {
                id
                text
                problem {
                    id
                }
                client {
                    id
                    ident
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        assert "data" in response.json()

    def test_200_problems_query(self):
        query = """
        {
            problems {
                id
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        assert "data" in response.json()

    def test_200_endpoint_statistics_by_event_type(self):
        query = """
        {
            endpointStatistics(
                eventTypeId: 3,
                byDate: {start: "2026-04-25", end: "2026-04-26"}
            ) {
                period
                allVisits
                visitorCount
                uniqueVisitors
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        stats = response.json()["data"]["endpointStatistics"]
        assert stats == [
            {
                "period": "2026-04-25",
                "allVisits": 1,
                "visitorCount": 1,
                "uniqueVisitors": 1,
            },
            {
                "period": "2026-04-26",
                "allVisits": 1,
                "visitorCount": 1,
                "uniqueVisitors": 1,
            },
        ]

    def test_200_endpoint_statistics_avg(self):
        query = """
        {
            endpointStatisticsAvg(
                eventTypeId: 3,
                byDate: {start: "2026-04-25", end: "2026-04-26"}
            ) {
                totalVisits
                totalVisitorCount
                totalUnique
                avgVisits
                entriesCount
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        assert response.json()["data"]["endpointStatisticsAvg"] == {
            "totalVisits": 2,
            "totalVisitorCount": 2,
            "totalUnique": 2,
            "avgVisits": 1.0,
            "entriesCount": 2,
        }

    def test_200_event_dictionary_queries(self):
        query = """
        {
            eventTypes(filter: {codeName: "ways"}) {
                nodes {
                    id
                    codeName
                }
            }
            payloadTypes(filter: {codeName: "success"}) {
                nodes {
                    id
                    valueType {
                        name
                    }
                }
            }
            allowedPayloadRules(filter: {eventTypeId: 3}) {
                nodes {
                    eventTypeId
                    payloadTypeId
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["eventTypes"]["nodes"][0]["codeName"] == "ways"
        assert data["payloadTypes"]["nodes"][0]["valueType"]["name"] == "bool"
        assert len(data["allowedPayloadRules"]["nodes"]) >= 3

    def test_200_event_dictionary_crud_with_admin_rights(self):
        create_query = """
        mutation {
            createValueType(data: {
                id: 99,
                name: "json",
                description: "JSON-значение payload"
            }) {
                id
                name
                description
            }
        }
        """
        create_response = graphql_query(create_query, ADMIN_HEADERS)
        assert create_response.status_code == 200
        assert create_response.json()["data"]["createValueType"]["name"] == "json"

        update_query = """
        mutation {
            updateValueType(
                valueTypeId: 99,
                data: {description: "Структурированное JSON-значение payload"}
            ) {
                id
                description
            }
        }
        """
        update_response = graphql_query(update_query, ADMIN_HEADERS)
        assert update_response.status_code == 200
        assert update_response.json()["data"]["updateValueType"]["description"] == "Структурированное JSON-значение payload"

        delete_query = """
        mutation {
            deleteValueType(valueTypeId: 99)
        }
        """
        delete_response = graphql_query(delete_query, ADMIN_HEADERS)
        assert delete_response.status_code == 200
        assert delete_response.json()["data"]["deleteValueType"] is True

    def test_200_multiple_queries_in_one_request(self):
        query = """
        {
            navFloors(filter: {name: 1}) {
                nodes {
                    id
                    name
                }
            }
            navTypes(filter: {name: "Учебная аудитория"}) {
                nodes {
                    id
                    name
                }
            }
        }
        """
        response = graphql_query(query, ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()["data"]
        assert "navFloors" in data
        assert "navTypes" in data


class TestGraphQLUnauthorized:
    def test_401_graphql_without_token_returns_unauthorized(self):
        query = """
        {
            reviews {
                id
            }
        }
        """
        response = graphql_query(query)
        assert response.status_code == 401

    def test_401_graphql_nav_without_token(self):
        query = """
        {
            navLocations(filter: {idSys: "AV"}) {
                nodes {
                    id
                    name
                }
            }
        }
        """
        response = graphql_query(query)
        assert response.status_code == 401

    def test_401_graphql_endpoint_stats_without_token(self):
        query = """
        {
            endpointStatistics(
                endpoint: "site",
                byDate: {start: "2025-01-01", end: "2025-01-31"}
            ) {
                period
                allVisits
            }
        }
        """
        response = graphql_query(query)
        assert response.status_code == 401
