import pytest

from app.constants import (
    EVENT_TYPE_AUDS_ID,
    EVENT_TYPE_PLANS_ID,
    EVENT_TYPE_SITE_ID,
    EVENT_TYPE_WAYS_ID,
    PAYLOAD_TYPE_AUDITORY_ID,
    PAYLOAD_TYPE_ENDPOINT_ID,
    PAYLOAD_TYPE_END_ID,
    PAYLOAD_TYPE_PLAN_ID,
    PAYLOAD_TYPE_START_ID,
    PAYLOAD_TYPE_SUCCESS_ID,
)

from .base import client


CLIENT_IDENT = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec"


@pytest.mark.parametrize(
    "event_type_id,payloads",
    [
        (EVENT_TYPE_SITE_ID, {PAYLOAD_TYPE_ENDPOINT_ID: "/api/get/route"}),
        (
            EVENT_TYPE_AUDS_ID,
            {
                PAYLOAD_TYPE_AUDITORY_ID: "a-100",
                PAYLOAD_TYPE_SUCCESS_ID: "false",
            },
        ),
        (
            EVENT_TYPE_WAYS_ID,
            {
                PAYLOAD_TYPE_START_ID: "a-100",
                PAYLOAD_TYPE_END_ID: "a-101",
                PAYLOAD_TYPE_SUCCESS_ID: "false",
            },
        ),
        (EVENT_TYPE_PLANS_ID, {PAYLOAD_TYPE_PLAN_ID: "A-0"}),
    ],
)
def test_200_stat_event(event_type_id, payloads):
    response = client.post(
        "/api/stat/event",
        json={
            "ident": CLIENT_IDENT,
            "event_type_id": event_type_id,
            "payloads": payloads,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
