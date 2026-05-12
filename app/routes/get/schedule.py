from typing import Union

from fastapi import APIRouter, Request
from starlette.responses import Response

from app.schemas import Status
from app.schemas.rasp.schedule import Auditory, Schedule
from app.state import AppState


def register_endpoint(router: APIRouter):
    @router.get(
        "/schedule",
        tags=["get"],
        response_model=Union[Schedule, Auditory, Status],
        responses={
            404: {
                'model': Status,
                'description': "No schedule for auditory",
                'content': {
                    'application/json': {
                        'example': {
                            'status': 'No schedule for specified auditory'
                        }
                    }
                }
            },
            425: {
                'model': Status,
                'description': "Schedule is not loaded yet",
                'content': {
                    'application/json': {
                        'example': {
                            'status': "Schedule is not loaded yet. Try again later"
                        }
                    }
                }
            }
        }
    )
    async def get_schedule(
            request: Request,
            response: Response,
            auditory: Union[str, None] = None,
    ):
        state: AppState = request.app.state.app_state
        if not state.global_rasp:
            response.status_code = 425
            return Status(status="Schedule is not loaded yet. Try again later")
        if not auditory:
            return state.global_rasp
        aud_schedule = state.global_rasp[auditory]
        if aud_schedule:
            return aud_schedule
        response.status_code = 404
        return Status(status="No schedule for specified auditory")
