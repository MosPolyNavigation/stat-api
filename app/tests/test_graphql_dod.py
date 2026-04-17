"""Integration tests for DOD GraphQL navigation endpoints."""

from app.tests.base import client

ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def graphql_query(query: str):
    return client.post("/api/graphql", json={"query": query}, headers=ADMIN_HEADERS)


def test_200_dod_nav_queries_return_dod_seed_data():
    query = """
    {
        dodNavLocations(filter: {idSys: "DD"}) {
            nodes {
                id
                idSys
                name
                short
            }
        }
        dodNavCampuses(filter: {idSys: "dd-test"}) {
            nodes {
                id
                idSys
                name
                locId
                location {
                    idSys
                }
            }
        }
        dodNavPlans(filter: {idSys: "dod-plan-1"}) {
            nodes {
                id
                idSys
                corId
                floorId
                campus {
                    idSys
                }
            }
        }
        dodNavAuditories(filter: {idSys: "dod-101"}) {
            nodes {
                id
                idSys
                name
                planId
                typeId
                photos {
                    id
                    link
                }
            }
        }
        dodNavAuditoryPhotos(filter: {audId: 1}) {
            nodes {
                id
                audId
                auditory {
                    idSys
                }
            }
        }
    }
    """
    response = graphql_query(query)
    assert response.status_code == 200

    payload = response.json()
    assert "errors" not in payload
    assert payload["data"]["dodNavLocations"]["nodes"][0]["idSys"] == "DD"
    assert payload["data"]["dodNavCampuses"]["nodes"][0]["idSys"] == "dd-test"
    assert payload["data"]["dodNavCampuses"]["nodes"][0]["location"]["idSys"] == "DD"
    assert payload["data"]["dodNavPlans"]["nodes"][0]["idSys"] == "dod-plan-1"
    assert payload["data"]["dodNavPlans"]["nodes"][0]["campus"]["idSys"] == "dd-test"
    assert payload["data"]["dodNavAuditories"]["nodes"][0]["idSys"] == "dod-101"
    assert payload["data"]["dodNavAuditoryPhotos"]["nodes"][0]["auditory"]["idSys"] == "dod-101"


def test_200_dod_nav_mutations_full_crud_flow():
    create_mutation = """
    mutation {
        createDodNavFloor(data: {name: 9}) { id name }
        createDodNavLocation(
            data: {
                idSys: "D2"
                name: "DOD Location 2"
                short: "D2"
                ready: true
                address: "dod address 2"
                metro: "dod metro 2"
                comments: "created"
            }
        ) { id idSys name }
        createDodNavType(data: {name: "DOD Type 2"}) { id name }
        createDodNavStatic(
            data: {
                ext: "svg"
                path: "/dod/2.svg"
                name: "dod-static-2"
                link: "/static/dod-2.svg"
            }
        ) { id name path }
    }
    """
    create_response = graphql_query(create_mutation)
    assert create_response.status_code == 200

    create_payload = create_response.json()
    assert "errors" not in create_payload

    floor_id = create_payload["data"]["createDodNavFloor"]["id"]
    loc_id = create_payload["data"]["createDodNavLocation"]["id"]
    type_id = create_payload["data"]["createDodNavType"]["id"]
    static_id = create_payload["data"]["createDodNavStatic"]["id"]

    create_campus = f"""
    mutation {{
        createDodNavCampus(
            data: {{
                idSys: "dd-2"
                locId: {loc_id}
                name: "DOD Campus 2"
                ready: true
                comments: "new"
            }}
        ) {{ id idSys locId }}
    }}
    """
    campus_response = graphql_query(create_campus)
    assert campus_response.status_code == 200
    campus_payload = campus_response.json()
    assert "errors" not in campus_payload
    campus_id = campus_payload["data"]["createDodNavCampus"]["id"]

    create_plan = f"""
    mutation {{
        createDodNavPlan(
            data: {{
                idSys: "dod-plan-2"
                corId: {campus_id}
                floorId: {floor_id}
                ready: true
                nearestEntrance: "entry-2"
            }}
        ) {{ id idSys corId floorId nearestEntrance }}
    }}
    """
    plan_response = graphql_query(create_plan)
    assert plan_response.status_code == 200
    plan_payload = plan_response.json()
    assert "errors" not in plan_payload
    plan_id = plan_payload["data"]["createDodNavPlan"]["id"]

    create_auditory = f"""
    mutation {{
        createDodNavAuditory(
            data: {{
                idSys: "dod-aud-2"
                typeId: {type_id}
                ready: true
                planId: {plan_id}
                name: "D-202"
                comments: "created"
            }}
        ) {{ id idSys name planId typeId }}
    }}
    """
    auditory_response = graphql_query(create_auditory)
    assert auditory_response.status_code == 200
    auditory_payload = auditory_response.json()
    assert "errors" not in auditory_payload
    auditory_id = auditory_payload["data"]["createDodNavAuditory"]["id"]

    update_mutation = f"""
    mutation {{
        updateDodNavFloor(id: {floor_id}, data: {{name: 10}}) {{ id name }}
        updateDodNavLocation(id: {loc_id}, data: {{name: "DOD Location 2 Updated"}}) {{ id name }}
        updateDodNavCampus(id: {campus_id}, data: {{comments: "updated"}}) {{ id comments }}
        updateDodNavType(id: {type_id}, data: {{name: "DOD Type 2 Updated"}}) {{ id name }}
        updateDodNavPlan(id: {plan_id}, data: {{nearestEntrance: "entry-2-updated"}}) {{ id nearestEntrance }}
        updateDodNavAuditory(id: {auditory_id}, data: {{name: "D-203"}}) {{ id name }}
        updateDodNavStatic(id: {static_id}, data: {{path: "/dod/2-updated.svg"}}) {{ id path }}
    }}
    """
    update_response = graphql_query(update_mutation)
    assert update_response.status_code == 200
    update_payload = update_response.json()
    assert "errors" not in update_payload

    verify_query = f"""
    {{
        dodNavLocations(filter: {{id: {loc_id}}}) {{
            nodes {{
                id
                name
            }}
        }}
        dodNavCampuses(filter: {{id: {campus_id}}}) {{
            nodes {{
                id
                comments
            }}
        }}
        dodNavTypes(filter: {{id: {type_id}}}) {{
            nodes {{
                id
                name
            }}
        }}
        dodNavPlans(filter: {{id: {plan_id}}}) {{
            nodes {{
                id
                nearestEntrance
            }}
        }}
        dodNavAuditories(filter: {{id: {auditory_id}}}) {{
            nodes {{
                id
                name
            }}
        }}
        dodNavStatics(filter: {{id: {static_id}}}) {{
            nodes {{
                id
                path
            }}
        }}
    }}
    """
    verify_response = graphql_query(verify_query)
    assert verify_response.status_code == 200
    verify_payload = verify_response.json()
    assert "errors" not in verify_payload
    assert verify_payload["data"]["dodNavLocations"]["nodes"][0]["name"] == "DOD Location 2 Updated"
    assert verify_payload["data"]["dodNavCampuses"]["nodes"][0]["comments"] == "updated"
    assert verify_payload["data"]["dodNavTypes"]["nodes"][0]["name"] == "DOD Type 2 Updated"
    assert verify_payload["data"]["dodNavPlans"]["nodes"][0]["nearestEntrance"] == "entry-2-updated"
    assert verify_payload["data"]["dodNavAuditories"]["nodes"][0]["name"] == "D-203"
    assert verify_payload["data"]["dodNavStatics"]["nodes"][0]["path"] == "/dod/2-updated.svg"


def test_200_dod_and_default_nav_data_are_isolated():
    query = """
    {
        navLocations(filter: {idSys: "AV"}) {
            nodes {
                idSys
            }
        }
        dodFromAv: dodNavLocations(filter: {idSys: "AV"}) {
            nodes {
                idSys
            }
        }
        dodFromDd: dodNavLocations(filter: {idSys: "DD"}) {
            nodes {
                idSys
            }
        }
    }
    """
    response = graphql_query(query)
    assert response.status_code == 200

    payload = response.json()
    assert "errors" not in payload
    assert payload["data"]["navLocations"]["nodes"] == [{"idSys": "AV"}]
    assert payload["data"]["dodFromAv"]["nodes"] == []
    assert payload["data"]["dodFromDd"]["nodes"] == [{"idSys": "DD"}]
