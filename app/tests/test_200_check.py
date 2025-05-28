import pytest
from .base import client


def test_get_route():
    response = client.get("/api/check/user-id?user_id=11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec")
    assert response.status_code == 200
