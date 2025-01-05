"""Tests for 422 response for unprotected and protected endpoints"""

import pytest
from .base import client


@pytest.mark.parametrize("endpoint", [
    "/api/stat/site",
    "/api/stat/select-aud",
    "/api/stat/start-way",
    "/api/stat/change-plan"
])
def test_422_stat(endpoint):
    response = client.put(endpoint, json={})
    assert response.status_code == 422


@pytest.mark.parametrize("endpoint", [
    "/api/get/site",
    "/api/get/auds",
    "/api/get/ways",
    "/api/get/plans",
    "/api/get/stat"
])
def test_422_get_protected(endpoint):
    response = client.get(endpoint, params={
        "api_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "page": -1
    })
    assert response.status_code == 422
