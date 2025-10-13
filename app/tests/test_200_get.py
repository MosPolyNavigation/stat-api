import re
import pickle
import pytest
import app.globals as globals_
from .load_graph import graph_b
from .base import client


@pytest.mark.parametrize("endpoint", [
    "/api/get/site",
    "/api/get/auds",
    "/api/get/ways",
    "/api/get/plans"
])
def test_200_get(endpoint):
    response = client.get(endpoint, headers={"Authorization": "Bearer 11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"})
    assert response.status_code == 200


@pytest.mark.parametrize("target", ["site", "auds", "ways", "plans"])
def test_get_stat(target):
    response = client.get("/api/get/stat", params={
        "target": "site"
    }, headers={"Authorization": "Bearer 11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"})
    assert response.status_code == 200
    assert response.json()["unique_visitors"] == 1


def test_get_user_id():
    response = client.get("/api/get/user-id")
    assert response.status_code == 200
    assert response.json()["user_id"] is not None
    assert re.match(
        r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
        response.json()["user_id"]
    ) is not None


def test_get_popular():
    response = client.get("/api/get/popular")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_route():
    globals_.global_graph["BS"] = pickle.loads(graph_b)
    response = client.get("/api/get/route?from_p=a-100&to_p=a-101&loc=campus_BS")
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data["way"]) == 10
    assert json_data["distance"] == 855
