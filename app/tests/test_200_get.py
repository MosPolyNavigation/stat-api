import pickle
import re

from .base import app, client
from .load_graph import graph_b


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
    app.state.app_state.global_graph["BS"] = pickle.loads(graph_b)
    response = client.get("/api/get/route?from_p=a-100&to_p=a-101&loc=campus_BS")
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data["way"]) == 10
    assert json_data["distance"] == 855
