from fastapi import APIRouter
from starlette.responses import Response
from typing import Union
from app.schemas import Status
from app.schemas.rasp.schedule import Schedule, Auditory
import app.globals as globals_


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
            response: Response,
            auditory: Union[str, None] = None,
    ):
        if not globals_.global_rasp:
            response.status_code = 425
            return Status(status="Schedule is not loaded yet. Try again later")
        if not auditory:
            return globals_.global_rasp
        aud_schedule = globals_.global_rasp[auditory]
        if aud_schedule:
            return aud_schedule
        response.status_code = 404
        return Status(status="No schedule for specified auditory")
