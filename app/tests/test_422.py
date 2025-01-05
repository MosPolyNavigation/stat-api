"""Tests for 422 response for unprotected endpoints"""

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
