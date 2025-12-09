"""Регистрация эндпоинтов поиска свободных аудиторий."""

from fastapi import APIRouter
from .by_auditory import register_endpoint as register_by_auditory
from .by_plan import register_endpoint as register_by_plan
from .by_corpus import register_endpoint as register_by_corpus
from .by_location import register_endpoint as register_by_location

router = APIRouter(
    prefix="/api/free-aud",
    tags=["free-aud"]
)


register_by_auditory(router)
register_by_plan(router)
register_by_corpus(router)
register_by_location(router)
