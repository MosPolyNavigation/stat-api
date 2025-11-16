from app.helpers.errors import LookupException
from app.config import get_settings
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.routes import get, stat, review, check, auth, crud_users
from fastapi import FastAPI, HTTPException, Request
from app.state import AppState

settings = get_settings()

app = FastAPI()
app.state = AppState()

app.include_router(get.router)
app.include_router(stat.router)
app.include_router(review.router)
app.include_router(check.router)
app.include_router(auth.router)
app.include_router(crud_users.router)


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
