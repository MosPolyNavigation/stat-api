from app.helpers.errors import LookupException
from app.config import Settings, get_settings
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.routes import get, stat, review, check
from fastapi import FastAPI, Request
from app.state import AppState

settings = get_settings()

app = FastAPI()
app.state = AppState()

app.include_router(get.router)
app.include_router(stat.router)
app.include_router(review.router)
app.include_router(check.router)


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
