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
])
def test_422_get_protected(endpoint):
    response = client.get(endpoint, params={
        "page": -1
    }, headers={"Authorization": "Bearer 11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"})
    assert response.status_code == 422
