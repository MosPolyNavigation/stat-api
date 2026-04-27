from os import path, makedirs

from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.state import AppState
from app.jobs import lifespan
from app.helpers.errors import LookupException
from app.helpers.spa_static_files import SPAStaticFiles
from app.routes import (
    get, stat, review,
    check, auth, graphql,
    jobs, free_aud, nav, admin
)

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
    },
    {
        "name": "nav",
        "description": "Эндпоинты для работы с данными навигации"
    },
    {
        "name": "check",
        "description": "Эндпоинты для проверки"
    },
    {
        "name": "admin",
        "description": "Эндпоинты для управления забаненными пользователями"
    },
]

settings = get_settings()
CURRENT_FILE_DIR = path.dirname(path.abspath(__file__))
PROJECT_DIR = path.dirname(CURRENT_FILE_DIR)
ADMIN_DIR = path.join(PROJECT_DIR, "dist-panel")
STATIC_DIR = path.join(settings.static_files, "images")
AUDITORY_STATIC_DIR = path.join(settings.static_files, "auditories")
PLANS_STATIC_DIR = path.join(settings.static_files, "plans")
THUMBNAILS_DIR = path.join(settings.static_files, "thumbnails")

if not path.exists(STATIC_DIR):
    makedirs(STATIC_DIR)
if not path.exists(AUDITORY_STATIC_DIR):
    makedirs(AUDITORY_STATIC_DIR)
if not path.exists(PLANS_STATIC_DIR):
    makedirs(PLANS_STATIC_DIR)
if not path.exists(THUMBNAILS_DIR):
    makedirs(THUMBNAILS_DIR)
if not path.exists(ADMIN_DIR):
    makedirs(ADMIN_DIR)

app = FastAPI(
    version="0.2.1",
    openapi_tags=tags_metadata,
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None,
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers
)
app.add_middleware(GZipMiddleware, minimum_size=1024)
add_pagination(app)
app.state = AppState()

app.include_router(get.router)
app.include_router(stat.router)
app.include_router(review.router)
app.include_router(check.router)
app.include_router(auth.router)
app.include_router(graphql.graphql_router, prefix="/api/graphql", tags=["graphql"])
app.include_router(jobs.router)
app.include_router(free_aud.router)
app.include_router(nav.router)
app.include_router(admin.router)
app.mount(
    "/admin/",
    SPAStaticFiles(
        directory=ADMIN_DIR,
        html=True
    ),
    "admin"
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
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
