from .base import client


ADMIN_HEADERS = {"Authorization": "Bearer 11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"}
VIEWER_HEADERS = {"Authorization": "Bearer 11e1a4b8-7fa7-4501-9faa-541a5e0ff1ee"}


def graphql_query(query: str, variables: dict | None = None, headers: dict | None = None):
    payload = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    return client.post("/api/graphql", json=payload, headers=headers or {})


def test_graphql_event_dictionary_crud_with_admin_rights():
    create_value = graphql_query(
        """
        mutation {
            createValueType(data: {id: 50, name: "decimal", description: "Decimal"}) {
                id
                name
            }
        }
        """,
        headers=ADMIN_HEADERS,
    )
    assert create_value.status_code == 200
    assert create_value.json()["data"]["createValueType"]["id"] == 50

    create_event = graphql_query(
        """
        mutation {
            createEventType(data: {id: 50, codeName: "custom", description: "Custom"}) {
                id
                codeName
            }
        }
        """,
        headers=ADMIN_HEADERS,
    )
    assert create_event.status_code == 200
    assert create_event.json()["data"]["createEventType"]["codeName"] == "custom"

    create_payload = graphql_query(
        """
        mutation {
            createPayloadType(
                data: {
                    id: 50,
                    codeName: "custom_payload",
                    description: "Custom payload",
                    valueTypeId: 50
                }
            ) {
                id
                codeName
                valueType { id name }
            }
        }
        """,
        headers=ADMIN_HEADERS,
    )
    assert create_payload.status_code == 200
    assert create_payload.json()["data"]["createPayloadType"]["valueType"]["id"] == 50

    create_rule = graphql_query(
        """
        mutation {
            createAllowedPayloadRule(data: {eventTypeId: 50, payloadTypeId: 50}) {
                eventTypeId
                payloadTypeId
            }
        }
        """,
        headers=ADMIN_HEADERS,
    )
    assert create_rule.status_code == 200
    assert create_rule.json()["data"]["createAllowedPayloadRule"]["payloadTypeId"] == 50

    query_rule = graphql_query(
        """
        {
            allowedPayloadRule(eventTypeId: 50, payloadTypeId: 50) {
                eventType { codeName }
                payloadType { codeName }
            }
        }
        """,
        headers=ADMIN_HEADERS,
    )
    assert query_rule.status_code == 200
    assert query_rule.json()["data"]["allowedPayloadRule"]["eventType"]["codeName"] == "custom"

    update_payload = graphql_query(
        """
        mutation {
            updatePayloadType(
                payloadTypeId: 50,
                data: {description: "Updated payload", valueTypeId: 50}
            ) {
                description
            }
        }
        """,
        headers=ADMIN_HEADERS,
    )
    assert update_payload.status_code == 200
    assert update_payload.json()["data"]["updatePayloadType"]["description"] == "Updated payload"

    for mutation in (
        "deleteAllowedPayloadRule(eventTypeId: 50, payloadTypeId: 50)",
        "deletePayloadType(payloadTypeId: 50)",
        "deleteEventType(eventTypeId: 50)",
        "deleteValueType(valueTypeId: 50)",
    ):
        response = graphql_query(
            f"mutation {{ {mutation} {{ success deletedId }} }}",
            headers=ADMIN_HEADERS,
        )
        assert response.status_code == 200
        assert response.json()["data"][mutation.split("(")[0]]["success"] is True


def test_graphql_event_dictionary_mutation_requires_stats_permission():
    response = graphql_query(
        """
        mutation {
            createValueType(data: {id: 51, name: "blocked"}) {
                id
            }
        }
        """,
        headers=VIEWER_HEADERS,
    )

    assert response.status_code == 200
    assert "errors" in response.json()
    assert "Недостаточно прав" in response.json()["errors"][0]["message"]
