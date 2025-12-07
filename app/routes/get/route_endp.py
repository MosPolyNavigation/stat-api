"""Маршрут построения кратчайшего пути между вершинами графа."""

from fastapi import APIRouter, Depends, Response

import app.globals as globals_
from app.schemas import FilterRoute, Status
from app.schemas.graph.graph import ShortestWayOut, VertexOut


def register_endpoint(router: APIRouter):
    """Регистрирует ручку `/route`."""

    @router.get(
        "/route",
        tags=["get"],
        response_model=ShortestWayOut | Status,
        responses={
            200: {
                "model": ShortestWayOut,
                "description": "Маршрут между двумя вершинами графа",
            },
            400: {
                "model": Status,
                "description": "Маршрут построить невозможно",
                "content": {
                    "application/json": {
                        "example": {"status": "The requested route is impossible"}
                    }
                },
            },
            404: {
                "model": Status,
                "description": "Одна из вершин не найдена",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "You are trying to get a route along non-existent vertex"
                        }
                    }
                },
            },
            500: {
                "model": Status,
                "description": "Графы еще не загружены",
                "content": {"application/json": {"example": {"status": "No graphs loaded"}}},
            },
        },
    )
    async def get_route(
        response: Response,
        query: FilterRoute = Depends(),
    ):
        """Возвращает кратчайший путь или сообщение об ошибке."""
        try:
            graph_bs = globals_.global_graph[query.loc.removeprefix("campus_")]
        except KeyError:
            response.status_code = 500
            return Status(status="No graphs loaded")
        from_v = graph_bs.vertexes.get(query.from_p, None)
        to_v = graph_bs.vertexes.get(query.to_p, None)
        if from_v is None or to_v is None:
            response.status_code = 404
            return Status(status="You are trying to get a route along non-existent vertex")
        try:
            graph = graph_bs
            s_w = graph.get_shortest_way_from_to(query.from_p, query.to_p)
            return ShortestWayOut(
                way=[
                    VertexOut(id=x.id, type=x.type, x=x.x, y=x.y, neighborData=x.neighborData)
                    for x in s_w.way
                ],
                distance=s_w.distance,
            )
        except Exception as e:
            print(e)
            response.status_code = 400
            return Status(status="The requested route is impossible")
