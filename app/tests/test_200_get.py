import re
import pytest
from .base import client


@pytest.mark.parametrize("endpoint", [
    "/api/get/site",
    "/api/get/auds",
    "/api/get/ways",
    "/api/get/plans"
])
def test_200_get(endpoint):
    response = client.get(endpoint, params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    })
    assert response.status_code == 200


@pytest.mark.parametrize("target", ["site", "auds", "ways", "plans"])
def test_get_stat(target):
    response = client.get("/api/get/stat", params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "target": "site"
    })
    assert response.status_code == 200
    assert response.json()["unique_visitors"] == 1


def test_get_user_id():
    response = client.get("/api/get/user-id")
    assert response.status_code == 200
    assert response.json()["user_id"] is not None
    assert re.match(r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}", response.json()["user_id"]) is not None
