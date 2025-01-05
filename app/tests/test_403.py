import pytest
from .base import client


@pytest.mark.parametrize("endpoint", [
    "/api/get/site",
    "/api/get/auds",
    "/api/get/ways",
    "/api/get/plans",
    "/api/get/stat"
])
def test_403(endpoint):
    response = client.get(endpoint, params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcde1"
    })
    assert response.status_code == 403
