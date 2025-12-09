"""Инициализация FastAPI приложения, настройка Swagger и регистрация маршрутов."""

from fastapi.middleware.cors import CORSMiddleware
from app.jobs import lifespan
from .helpers.errors import LookupException
from fastapi_pagination import add_pagination
from .config import get_settings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from .routes import get, stat, review, check, auth, graphql, crud_users, crud_roles, jobs, free_aud, nav
from fastapi import FastAPI, Request, HTTPException
from .state import AppState
from os import path, makedirs

tags_metadata = [
    {
        "name": "stat",
        "description": "Эндпоинты статистики использования сервисов, отраженные в Swagger."
    },
    {
        "name": "get",
        "description": "Запросы на получение справочной информации (маршруты, аудитории, карты)."
    },
    {
        "name": "review",
        "description": "Маршруты для работы с отзывами пользователей и проблемами."
    },
    {
        "name": "graphql",
        "description": "GraphQL API, описанное в Swagger и доступное по /api/graphql."
    },
    {
        "name": "auth",
        "description": "Авторизация и выдача токенов, используемые для защищенных Swagger-эндпоинтов."
    },
    {
        "name": "jobs",
        "description": "Системные задачи (крон/фоны) для обновления расписаний и графов."
    },
    {
        "name": "free-aud",
        "description": "Поиск свободных аудиторий согласно параметрам фильтра."
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
app.include_router(nav.router)
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
    Унифицированный обработчик ошибок SQLAlchemy для Swagger-эндпоинтов.

    При любом исключении SQLAlchemy формируем консистентный JSON-ответ,
    чтобы в документации было понятно, что сервис вернет код 500 и текст ошибки.

    Args:
        _: Request объект, переданный фреймворком (не используется напрямую).
        exc: Исключение SQLAlchemy, содержащее первичный текст ошибки.

    Returns:
        JSONResponse: Ответ с кодом 500 и полем `status`, понятным в Swagger.
    """
    return JSONResponse(status_code=500, content={"status": str(exc)})


@app.exception_handler(LookupException)
async def lookup_exception_handler(_, exc: LookupException):
    """
    Обработчик ошибок поиска доменных сущностей (LookupException).

    Преобразует доменное исключение в предсказуемый 404 ответ,
    чтобы Swagger описывал одинаковый формат ошибки.

    Args:
        _: Request объект, не используется напрямую.
        exc: Исключение LookupException с информацией о пропавшей сущности.

    Returns:
        JSONResponse: Ответ с кодом 404 и текстом статуса.
    """
    return JSONResponse(status_code=404, content={"status": str(exc)})


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    """
    Приведение стандартных HTTP исключений FastAPI к унифицированному ответу.

    Args:
        _: Request, передается фреймворком, но не используется напрямую.
        exc: HTTPException, поднятая в одном из обработчиков.

    Returns:
        JSONResponse: Ответ с исходным статус-кодом и текстом ошибки.
    """
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})
