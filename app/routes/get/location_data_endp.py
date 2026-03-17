from fastapi import APIRouter
from fastapi.responses import JSONResponse

import app.globals as globals_
from app.schemas import DataDto, Status


# Эндпоинт, возвращающий JSON-файл с данными о локациях/корпусах/планах/аудиториях
def register_endpoint(router: APIRouter):
    @router.get(
        "/locationData",
        tags=["get"],
        response_model=DataDto,
        responses={503: {"model": Status, "description": "locationData еще не сформирован"}},
    )
    async def get_location_data():
        if globals_.location_data_json is None:
            return JSONResponse(
                status_code=503,
                content=Status(status="locationData is not ready").model_dump(),
            )
        return globals_.location_data_json