from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from app.models import Base
from app.database import engine
from app.state import AppState
from app.routes import get
from app.routes import stat
from app.config import Settings

Base.metadata.create_all(bind=engine)

app = FastAPI()
add_pagination(app)
app.state = AppState()

app.include_router(get.router)
app.include_router(stat.router)

origins = [

]


@app.middleware("http")
async def token_auth_middleware(request: Request, call_next):
    if request.scope['path'] in ["/api/get/site", "/api/get/auds"]:
        token = request.query_params.get('api_key')
        if not token:
            return JSONResponse(status_code=403, content={"status": "no api_key"})
        if token != Settings().admin_key:
            return JSONResponse(status_code=403, content={"status": "Specified api_key is not present in app"})

    response = await call_next(request)
    return response
