"""Smoke tests for GraphQL endpoint /api/graphql."""

from .base import client

ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def graphql_query(query: str, headers: dict = None):
    return client.post(
        "/api/graphql",
        json={"query": query},
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
                    name
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
        assert "data" in response.json()

    def test_200_problems_query(self):
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
        assert "data" in response.json()

    def test_200_site_stats_with_nested_user(self):
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
        assert "data" in response.json()

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
