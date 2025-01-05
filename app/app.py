from sqlalchemy.exc import SQLAlchemyError
from fastapi.middleware.cors import CORSMiddleware
from app.helpers.errors import LookupException
from fastapi_pagination import add_pagination
from app.config import Settings, get_settings
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from app.state import AppState
from app.routes import get
from app.routes import stat
from datetime import datetime

app = FastAPI()
add_pagination(app)
app.state = AppState()

app.include_router(get.router)
app.include_router(stat.router)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_methods=settings.allowed_methods
)


@app.middleware("http")
async def token_auth_middleware(request: Request, call_next):
    if request.scope['path'] in ["/api/get/site", "/api/get/auds", "/api/get/ways", "/api/get/plans", "/api/get/stat"]:
        token = request.query_params.get('api_key')
        if not token:
            return JSONResponse(status_code=403, content={"status": "no api_key"})
        if token != Settings().admin_key:
            return JSONResponse(status_code=403, content={"status": "Specified api_key is not present in app"})
    return await call_next(request)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(status_code=500, content={"status": str(exc)})


@app.exception_handler(LookupException)
async def lookup_exception_handler(request: Request, exc: LookupException):
    return JSONResponse(status_code=404, content={"status": str(exc)})


@app.get("/healthcheck")
async def healthcheck():
    return JSONResponse(status_code=200, content={"current_time": str(datetime.now())})
