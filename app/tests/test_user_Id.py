import re

from .base import client


def test_get_user_id():
    response = client.get("/api/get/user-id")
    assert response.status_code == 200
    assert response.json()["user_id"] is not None
    assert re.match(r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}", response.json()["user_id"]) is not None
