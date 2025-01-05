from .base import client


def test_get_plans():
    response = client.get("/api/get/plans", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "page": 1,
        "size": 50
    })
    assert response.status_code == 200


def test_user_404_stat_plan():
    response = client.put("/api/stat/change-plan", json={
        "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1e1",
        "plan_id": "A-0"
    })
    assert response.status_code == 404
    assert response.json() == {"status": "User not found"}


def test_plan_404_stat_plan():
    response = client.put("/api/stat/change-plan", json={
        "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
        "plan_id": "A-6",
    })
    assert response.status_code == 404
    assert response.json() == {"status": "Changed plan not found"}


def test_stat_plan():
    response = client.put("/api/stat/change-plan", json={
        "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
        "plan_id": "A-0"
    })
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
