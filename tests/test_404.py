import pytest

from app.constants import (
    EVENT_TYPE_AUDS_ID,
    PAYLOAD_TYPE_AUDITORY_ID,
    PAYLOAD_TYPE_ENDPOINT_ID,
)

from .base import client


def test_400_stat_event_unknown_client():
    response = client.post(
        "/api/stat/event",
        json={
            "ident": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1e1",
            "event_type_id": EVENT_TYPE_AUDS_ID,
            "payloads": {PAYLOAD_TYPE_AUDITORY_ID: "a-100"},
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unknown client ident=11e1a4b8-7fa7-4501-9faa-541a5e0ff1e1"
    }


def test_400_stat_event_payload_not_allowed():
    response = client.post(
        "/api/stat/event",
        json={
            "ident": "22e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
            "event_type_id": EVENT_TYPE_AUDS_ID,
            "payloads": {PAYLOAD_TYPE_ENDPOINT_ID: "/api/get/route"},
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Payload type 1 is not allowed for event_type_id=2"
    }


@pytest.mark.parametrize(
    "data, body",
    [
        (
            {"client_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1e1"},
            {"status": "Client not found"},
        ),
    ],
)
def test_404_check_client_id(data, body):
    response = client.get("/api/check/client-id", params=data)
    assert response.status_code == 404
    assert response.json() == body
