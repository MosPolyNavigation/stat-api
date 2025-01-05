from .base import client


def test_403_get_stat():
    response = client.get("/api/get/stat", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcde1",
        "target": "site"
    })
    assert response.status_code == 403


def test_422_get_stat():
    response = client.get("/api/get/stat", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    })
    assert response.status_code == 422


def test_get_stat_site():
    response = client.get("/api/get/stat", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "target": "site"
    })
    assert response.status_code == 200
    assert response.json()["unique_visitors"] == 1


def test_get_stat_auds():
    response = client.get("/api/get/stat", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "target": "auds"
    })
    assert response.status_code == 200
    assert response.json()["unique_visitors"] == 1


def test_get_stat_ways():
    response = client.get("/api/get/stat", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "target": "ways"
    })
    assert response.status_code == 200
    assert response.json()["unique_visitors"] == 1


def test_get_stat_plans():
    response = client.get("/api/get/stat", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "target": "plans"
    })
    assert response.status_code == 200
    assert response.json()["unique_visitors"] == 1
