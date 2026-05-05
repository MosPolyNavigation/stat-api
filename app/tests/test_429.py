from time import sleep

from app.constants import EVENT_TYPE_AUDS_ID, PAYLOAD_TYPE_AUDITORY_ID

from .base import client


def test_429_stat_event():
    body = {
        "ident": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
        "event_type_id": EVENT_TYPE_AUDS_ID,
        "payloads": {PAYLOAD_TYPE_AUDITORY_ID: "a-100"},
    }
    sleep(1)
    _ = client.post("/api/stat/event", json=body)
    response = client.post("/api/stat/event", json=body)
    assert response.status_code == 429
    assert response.json() == {
        "detail": "Too many requests for this event type within one second"
    }
