from fastapi.middleware.cors import CORSMiddleware
from .handlers.schedule import lifespan
from .helpers.errors import LookupException
from fastapi_pagination import add_pagination
from .config import Settings, get_settings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from .routes import get, stat, review, check
from fastapi import FastAPI, Request
from .state import AppState
from os import path, makedirs

tags_metadata = [
    {
        "name": "stat",
        "description": "Эндпоинты для внесения статистики"
    },
    {
        "name": "get",
        "description": "Эндпоинты для получения статистики"
    },
    {
        "name": "review",
        "description": "Эндпоинты для работы с отзывами"
    }
]

settings = get_settings()
CURRENT_FILE_DIR = path.dirname(path.abspath(__file__))
PROJECT_DIR = path.dirname(CURRENT_FILE_DIR)
FRONT_DIR = path.join(PROJECT_DIR, "dist")
STATIC_DIR = path.join(settings.static_files, "images")

if not path.exists(STATIC_DIR):
    makedirs(STATIC_DIR)
if not path.exists(FRONT_DIR):
    makedirs(FRONT_DIR)

app = FastAPI(
    openapi_tags=tags_metadata,
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None,
    lifespan=lifespan
)
add_pagination(app)
app.state = AppState()

app.include_router(get.router)
app.include_router(stat.router)
app.include_router(review.router)
app.include_router(check.router)
app.mount(
    "/",
    StaticFiles(
        directory=FRONT_DIR,
        html=True
    ),
    "front"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_methods=settings.allowed_methods
)


@app.middleware("http")
async def token_auth_middleware(request: Request, call_next):
    if request.scope['path'] in [
        "/api/get/site",
        "/api/get/auds",
        "/api/get/ways",
        "/api/get/plans",
        "/api/get/stat",
        "/api/review/get"
    ]:
        token = request.query_params.get('api_key')
        if not token:
            return JSONResponse(
                status_code=403,
                content={"status": "no api_key"}
            )
        if token != Settings().admin_key:
            return JSONResponse(
                status_code=403,
                content={"status": "Specified api_key is not present in app"}
            )
    return await call_next(request)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(_, exc: SQLAlchemyError):
    """
    Обработчик исключений SQLAlchemy.

    Этот обработчик вызывается, когда происходит исключение SQLAlchemy.
    Он возвращает JSON ответ с кодом статуса 500 и сообщением об ошибке.

    Args:
        _: Объект запроса (не используется в функции);
        exc: Исключение SQLAlchemy.

    Returns:
        JSONResponse: JSON ответ с кодом статуса 500 и сообщением об ошибке.
    """
    return JSONResponse(status_code=500, content={"status": str(exc)})


@app.exception_handler(LookupException)
async def lookup_exception_handler(_, exc: LookupException):
    """
    Обработчик исключений LookupException.

    Этот обработчик вызывается, когда происходит исключение LookupException.
    Он возвращает JSON ответ с кодом статуса 404 и сообщением об ошибке.

    Args:
        _: Объект запроса (не используется в функции);
        exc: Исключение LookupException.

    Returns:
        JSONResponse: JSON ответ с кодом статуса 404 и сообщением об ошибке.
    """
    return JSONResponse(status_code=404, content={"status": str(exc)})
