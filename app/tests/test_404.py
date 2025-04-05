import pytest
from .base import client
from time import sleep


def test_404_stat_site():
    response = client.put("/api/stat/site", json={
        "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1e1"
    })
    assert response.status_code == 404
    assert response.json() == {"status": "User not found"}


@pytest.mark.parametrize("data, body", [
    (
        {
            "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1e1",
            "auditory_id": "a-100",
        },
        {"status": "User not found"}
    ),
    (
        {
            "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
            "auditory_id": "a-12122",
        },
        {"status": "Auditory not found"}
    )
])
def test_404_stat_aud(data, body):
    sleep(1)
    response = client.put("/api/stat/select-aud", json={
        "success": True,
        **data
    })
    assert response.status_code == 404
    assert response.json() == body


@pytest.mark.parametrize("data, body", [
    (
        {
            "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1e1",
            "start_id": "a-100",
            "end_id": "a-101"
        },
        {"status": "User not found"}
    ),
    (
        {
            "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
            "start_id": "a-10011",
            "end_id": "a-101",
        },
        {"status": "Start auditory not found"}
    ),
    (
        {
            "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
            "start_id": "a-100",
            "end_id": "a-10111",
        },
        {"status": "End auditory not found"}
    )
])
def test_404_stat_way(data, body):
    response = client.put("/api/stat/start-way", json={
        **data
    })
    assert response.status_code == 404
    assert response.json() == body


@pytest.mark.parametrize("data, body", [
    (
        {
            "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1e1",
            "plan_id": "A-0"
        },
        {"status": "User not found"}
    ),
    (
        {
            "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
            "plan_id": "A-6",
        },
        {"status": "Changed plan not found"}
    )
])
def test_404_stat_plan(data, body):
    response = client.put("/api/stat/change-plan", json={
        **data
    })
    assert response.status_code == 404
    assert response.json() == body
