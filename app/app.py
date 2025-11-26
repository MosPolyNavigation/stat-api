from fastapi.middleware.cors import CORSMiddleware
from app.jobs import lifespan
from .helpers.errors import LookupException
from fastapi_pagination import add_pagination
from .config import get_settings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from .routes import get, stat, review, check, auth, graphql, crud_users, crud_roles, jobs, free_aud
from fastapi import FastAPI, Request, HTTPException
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
    },
    {
        "name": "graphql",
        "description": "Эндпоинт для запросов graphql"
    },
    {
        "name": "auth",
        "description": "Эндпоинты для аутентификации и авторизации"
    },
    {
        "name": "jobs",
        "description": "Эндпоинты для управления фоновыми задачами"
    },
    {
        "name": "free-aud",
        "description": "Эндпоинты для получения свободных аудиторий"
    }
]

settings = get_settings()
CURRENT_FILE_DIR = path.dirname(path.abspath(__file__))
PROJECT_DIR = path.dirname(CURRENT_FILE_DIR)
FRONT_DIR = path.join(PROJECT_DIR, "dist")
ADMIN_DIR = path.join(PROJECT_DIR, "dist-panel")
STATIC_DIR = path.join(settings.static_files, "images")

if not path.exists(STATIC_DIR):
    makedirs(STATIC_DIR)
if not path.exists(FRONT_DIR):
    makedirs(FRONT_DIR)
if not path.exists(ADMIN_DIR):
    makedirs(ADMIN_DIR)

app = FastAPI(
    version="0.2.0",
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
app.include_router(auth.router)
app.include_router(graphql.graphql_router, prefix="/api/graphql", tags=["graphql"])
app.include_router(crud_users.router)
app.include_router(crud_roles.router)
app.include_router(jobs.router)
app.include_router(free_aud.router)
app.mount(
    "/admin/",
    StaticFiles(
        directory=ADMIN_DIR,
        html=True
    ),
    "admin"
)
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
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers
)


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


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    """
    Обработчик всех HTTPException в проекте.

    Args:
        _: объект запроса;
        exc: исключение HTTPException.

    Returns:
        JSONResponse: JSON ответ с кодом ошибки и сообщением
    """
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})
