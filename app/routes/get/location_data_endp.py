from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.schemas import DataDto, Status
from app.state import AppState


# Эндпоинт, возвращающий JSON-файл с данными о локациях/корпусах/планах/аудиториях
def register_endpoint(router: APIRouter):
    @router.get(
        "/locationData",
        tags=["get"],
        response_model=DataDto,
        responses={503: {"model": Status, "description": "locationData еще не сформирован"}},
    )
    async def get_location_data(request: Request):
        state: AppState = request.app.state.app_state
        if state.location_data_json is None:
            return JSONResponse(
                status_code=503,
                content=Status(status="locationData is not ready").model_dump(),
            )
        return state.location_data_json
