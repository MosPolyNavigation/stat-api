"""Tests for 422 response for unprotected and protected endpoints"""

from .base import client


def test_422_stat_event():
    response = client.post("/api/stat/event", json={})
    assert response.status_code == 422
