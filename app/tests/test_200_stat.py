import pytest
from .base import client
from time import sleep


@pytest.mark.parametrize("endpoint, data", [
    ("/api/stat/site", {}),
    ("/api/stat/select-aud", {"auditory_id": "a-100", "success": True}),
    ("/api/stat/start-way", {"start_id": "a-100", "end_id": "a-101"}),
    ("/api/stat/change-plan", {"plan_id": "A-0"})
])
def test_200_stat(endpoint, data):
    if endpoint == "/api/stat/select-aud":
        sleep(1)
    response = client.put(endpoint, json={
        "user_id": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec",
        **data
    })
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
