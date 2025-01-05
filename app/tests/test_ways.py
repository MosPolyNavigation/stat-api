from .base import client


def test_get_ways():
    response = client.get("/api/get/ways", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "page": 1,
        "size": 50
    })
    assert response.status_code == 200


def test_stat_way():
    response = client.put("/api/stat/start-way", json={
        "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
        "start_id": "a-100",
        "end_id": "a-101",
    })
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
