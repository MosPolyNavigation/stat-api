from .base import client


def test_get_sites():
    response = client.get("/api/get/site", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "page": 1,
        "size": 50
    })
    assert response.status_code == 200


def test_403_get_sites():
    response = client.get("/api/get/site", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcde1"
    })
    assert response.status_code == 403


def test_user_404_stat_site():
    response = client.put("/api/stat/site", json={
        "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1e1"
    })
    assert response.status_code == 404
    assert response.json() == {"status": "User not found"}


def test_stat_site():
    response = client.put("/api/stat/site", json={
        "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec"
    })
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
