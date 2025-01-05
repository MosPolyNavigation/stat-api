import pytest
from .base import client
from time import sleep


def test_get_auds():
    response = client.get("/api/get/auds", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "page": 1,
        "size": 50
    })
    assert response.status_code == 200


def test_stat_aud():
    sleep(1)
    response = client.put("/api/stat/select-aud", json={
        "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
        "auditory_id": "a-100",
        "success": True
    })
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_429_stat_aud():
    sleep(1)
    _ = client.put("/api/stat/select-aud", json={
        "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
        "auditory_id": "a-100",
        "success": True
    })
    response = client.put("/api/stat/select-aud", json={
        "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
        "auditory_id": "a-100",
        "success": True
    })
    assert response.status_code == 429
    assert response.json() == {"status": "Too many requests for this user within one second"}
