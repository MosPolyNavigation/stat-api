import pytest
from .base import client


@pytest.mark.parametrize("endpoint", [
    "/api/get/site",
    "/api/get/auds",
    "/api/get/ways",
    "/api/get/plans",
])
def test_401(endpoint):
    response = client.get(endpoint, headers={"Authorization": "Bearer 11e1a4b8-7fa7-4501-9faa-541a5e0ff1ec"})
    assert response.status_code == 401
