from fastapi import APIRouter, Depends, Response
import app.globals as globals_
from app.schemas import Status, WayOut, StepOut, RouteOut, Route, FilterRoute


def register_endpoint(router: APIRouter):
    @router.get(
        "/route",
        tags=["get"],
        responses={
            200: {
                'model': RouteOut,
                'description': "Route from one auditory to another",
                'content': {
                    'application/json': {
                        'example': {
                            "to": "a-101",
                            "from": "a-100",
                            "steps": [
                                {
                                    "plan": "A-1",
                                    "way": [
                                        {
                                            "id": "a-100",
                                            "x": 1567,
                                            "y": 1857,
                                            "type": "entrancesToAu"
                                        },
                                        {
                                            "id": "a-1_16",
                                            "x": 1460,
                                            "y": 1857,
                                            "type": "hallway"
                                        },
                                        {
                                            "id": "a-1-stair-2",
                                            "x": 1460,
                                            "y": 1703,
                                            "type": "stair"
                                        },
                                        {
                                            "id": "a-1_41",
                                            "x": 1451,
                                            "y": 1531,
                                            "type": "hallway"
                                        },
                                        {
                                            "id": "a-1_10",
                                            "x": 1441,
                                            "y": 1530,
                                            "type": "hallway"
                                        },
                                        {
                                            "id": "a-1_15",
                                            "x": 1374,
                                            "y": 1530,
                                            "type": "hallway"
                                        },
                                        {
                                            "id": "a-1_18",
                                            "x": 1267,
                                            "y": 1530,
                                            "type": "hallway"
                                        },
                                        {
                                            "id": "a-1_19",
                                            "x": 1189,
                                            "y": 1530,
                                            "type": "hallway"
                                        },
                                        {
                                            "id": "a-1_20",
                                            "x": 1080,
                                            "y": 1530,
                                            "type": "hallway"
                                        },
                                        {
                                            "id": "a-101",
                                            "x": 1080,
                                            "y": 1581,
                                            "type": "entrancesToAu"
                                        }
                                    ],
                                    "distance": 855.29
                                }
                            ],
                            "fullDistance": 855
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
        try:
            graph_bs = globals_.global_graph["BS"]
        except KeyError:
            response.status_code = 500
            return Status(
                status="No graphs loaded"
            )
        from_v = graph_bs.vertexes.get(query.from_, None)
        to_v = graph_bs.vertexes.get(query.to, None)
        if from_v is None or to_v is None:
            response.status_code = 404
            return Status(
                status="You are trying to get a route along non-existent vertex"
            )
        try:
            route = Route(from_=query.from_, to=query.to, graph=graph_bs)
            data = RouteOut(
                from_=route.from_,
                to=route.to,
                steps=[StepOut(
                    plan=x.plan.id,
                    distance=x.distance,
                    way=[WayOut(
                        id=v.id,
                        x=v.x,
                        y=v.y,
                        type=v.type
                    ) for v in x.way]
                ) for x in route.steps],
                fullDistance=route.fullDistance
            )
            return data
        except Exception as e:
            print(e)
            response.status_code = 400
            return Status(
                status="The requested route is impossible"
            )