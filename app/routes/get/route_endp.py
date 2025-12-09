"""Маршрут для получения кратчайшего пути между точками."""

from fastapi import APIRouter, Depends, Response
import app.globals as globals_
from app.schemas import Status, FilterRoute
from app.schemas.graph.graph import ShortestWayOut, VertexOut


def register_endpoint(router: APIRouter):
    """
    Регистрирует эндпоинт `/route` (Swagger tag `get`), возвращающий кратчайший путь.

    Args:
        router: Экземпляр APIRouter, в который добавляется эндпоинт.

    Returns:
        APIRouter: Тот же роутер с добавленным обработчиком.
    """

    @router.get(
        "/route",
        tags=["get"],
        responses={
            200: {
                'model': ShortestWayOut,
                'description': "Route from one auditory to another",
                'content': {
                    'application/json': {
                        'example': {
                            "way": [
                                {
                                    "id": "a-109",
                                    "x": 884,
                                    "y": 1480,
                                    "type": "entrancesToAu",
                                    "neighborData": [
                                        [
                                            "a-1_22",
                                            50
                                        ]
                                    ]
                                },
                                {
                                    "id": "a-1_22",
                                    "x": 884,
                                    "y": 1530,
                                    "type": "hallway",
                                    "neighborData": [
                                        [
                                            "a-1_21",
                                            6
                                        ],
                                        [
                                            "a-1_23",
                                            100
                                        ],
                                        [
                                            "a-109",
                                            50
                                        ]
                                    ]
                                },
                                {
                                    "id": "a-1_21",
                                    "x": 890,
                                    "y": 1530,
                                    "type": "hallway",
                                    "neighborData": [
                                        [
                                            "a-1_20",
                                            190
                                        ],
                                        [
                                            "a-1_22",
                                            6
                                        ],
                                        [
                                            "a-102",
                                            51
                                        ]
                                    ]
                                },
                                {
                                    "id": "a-102",
                                    "x": 890,
                                    "y": 1581,
                                    "type": "entrancesToAu",
                                    "neighborData": [
                                        [
                                            "a-1_21",
                                            51
                                        ]
                                    ]
                                }
                            ],
                            "distance": 107
                        }
                    }
                }
            },
            400: {
                'model': Status,
                'description': "Route from one auditory to another",
                'content': {
                    'application/json': {
                        'example': {
                            'status': 'The requested route is impossible'
                        }
                    }
                }
            },
            404: {
                'model': Status,
                'description': "Route from one auditory to another",
                'content': {
                    'application/json': {
                        'example': {
                            'status': 'You are trying to get a route along non-existent vertex'
                        }
                    }
                }
            }
        }
    )
    async def get_route(
            response: Response,
            query: FilterRoute = Depends()
    ):
        """
        Строит кратчайший путь на графе между двумя вершинами.

        Args:
            response: Объект Response для управления статус-кодом.
            query: Параметры запроса (from, to, loc).

        Returns:
            ShortestWayOut | Status: Результат расчета пути либо описание ошибки.
        """
        try:
            graph_bs = globals_.global_graph[query.loc.removeprefix("campus_")]
        except KeyError:
            response.status_code = 500
            return Status(
                status="No graphs loaded"
            )
        from_v = graph_bs.vertexes.get(query.from_p, None)
        to_v = graph_bs.vertexes.get(query.to_p, None)
        if from_v is None or to_v is None:
            response.status_code = 404
            return Status(
                status="You are trying to get a route along non-existent vertex"
            )
        try:
            graph = graph_bs
            s_w = graph.get_shortest_way_from_to(query.from_p, query.to_p)
            return ShortestWayOut(
                way=[VertexOut(
                    id=x.id,
                    type=x.type,
                    x=x.x,
                    y=x.y,
                    neighborData=x.neighborData
                ) for x in s_w.way],
                distance=s_w.distance
            )
        except Exception as e:
            print(e)
            response.status_code = 400
            return Status(
                status="The requested route is impossible"
            )

    return router
