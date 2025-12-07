"""Главная точка входа FastAPI-приложения."""

from os import makedirs, path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from sqlalchemy.exc import SQLAlchemyError

from app.jobs import lifespan
from .config import get_settings
from .helpers.errors import LookupException
from .routes import auth, check, crud_roles, crud_users, free_aud, get, graphql, jobs, review, stat
from .state import AppState

tags_metadata = [
    {
        "name": "stat",
        "description": "Статистика использования сервисов (выбор аудиторий, построение маршрутов, смена планов).",
    },
    {
        "name": "get",
        "description": "Публичные GET-эндпоинты: расписание, популярные аудитории и маршруты.",
    },
    {
        "name": "review",
        "description": "Работа с отзывами пользователей и загрузкой изображений.",
    },
    {
        "name": "graphql",
        "description": "GraphQL API для выборки и фильтрации статистики.",
    },
    {
        "name": "auth",
        "description": "Авторизация и выдача access-токенов.",
    },
    {
        "name": "jobs",
        "description": "Запуск фоновых задач (обновление расписания, данных навигации).",
    },
    {
        "name": "free-aud",
        "description": "Поиск свободных аудиторий по аудитории, плану, корпусу или локации.",
    },
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
    lifespan=lifespan,
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
        html=True,
    ),
    "admin",
)
app.mount(
    "/",
    StaticFiles(
        directory=FRONT_DIR,
        html=True,
    ),
    "front",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(_, exc: SQLAlchemyError):
    """
    Единый обработчик ошибок SQLAlchemy.

    Возвращает JSON с текстом исключения и кодом 500,
    чтобы скрыть детали базы данных от клиента.
    """
    return JSONResponse(status_code=500, content={"status": str(exc)})


@app.exception_handler(LookupException)
async def lookup_exception_handler(_, exc: LookupException):
    """Преобразует LookupException в ответ 404 с понятным текстом."""
    return JSONResponse(status_code=404, content={"status": str(exc)})


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    """Унифицирует HTTPException: возвращает JSON с detail и кодом ошибки."""
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})
