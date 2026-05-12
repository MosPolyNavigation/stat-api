import pickle

from .base import app, client
from .load_graph import graph_b


def test_get_popular():
    response = client.get("/api/get/popular")
    assert response.status_code == 200
    assert response.json()[:2] == [
        {"auditory_id": "a-100", "total_weight": 4},
        {"auditory_id": "a-101", "total_weight": 3},
    ]


def test_get_route():
    app.state.app_state.global_graph["BS"] = pickle.loads(graph_b)  # type: ignore[arg-type]
    response = client.get("/api/get/route?from_p=a-100&to_p=a-101&loc=campus_BS")
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data["way"]) == 10
    assert json_data["distance"] == 855
