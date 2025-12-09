"""Загрузка расписания групп с rasp.dmami.ru."""

import asyncio
import httpx
import json
import logging
import re
from pydantic import ValidationError
from typing import Any, Union, AsyncGenerator
from app.schemas.rasp.dto import Dto

BASE_URL = "https://rasp.dmami.ru/"
dataUrl = f'{BASE_URL}site/group?group='
DEFAULT_DELAY = 0.001
USER_AGENT = 'Mozilla/5.0 (compatible; schedule-extractor/1.2; +https://github.com/MosPolyNavigation/stat-api)'

logger = logging.getLogger(f"uvicorn.{__name__}")


def extract_json_string(html: str) -> str:
    """
    Извлекает JSON-строку со списком групп из HTML.

    Args:
        html: HTML код страницы со скриптом globalListGroups.

    Returns:
        str: Сырый JSON со списком групп.
    """
    pattern = r'\b(?:var|let|const)\s+globalListGroups\s*=\s*({.*?});'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        raise ValueError('Не найден блок globalListGroups в HTML.')

    json_str = match.group(1).split("\n")[0].rstrip('.groups;')
    if json_str.count('{') != json_str.count('}'):
        raise ValueError('Нарушен баланс фигурных скобок в JSON.')
    return json_str


async def get_groups() -> dict[str, dict[str, Any | None] | Any]:
    """
    Получает список групп с основного сайта расписания.

    Returns:
        dict[str, dict[str, Any | None] | Any]: Словарь групп и сопутствующих данных.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(BASE_URL, headers={'User-Agent': USER_AGENT})
        r.raise_for_status()
    html = r.text
    json_str = extract_json_string(html)
    data = json.loads(json_str)
    return data


async def get_schedule() -> AsyncGenerator[tuple[str, Union[Dto, None]], None]:
    """
    Асинхронно загружает расписание для всех групп.

    Yields:
        tuple[str, Union[Dto, None]]: Пара (код_группы, DTO расписания или None при ошибке).
    """
    groups = (await get_groups())['groups']
    for key, value in groups.items():
        if value:
            yield key, None
            continue
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(
                f'{dataUrl}{key}',
                headers={'User-Agent': USER_AGENT, "Referer": "https://rasp.dmami.ru"})
            if r.status_code != 200:
                yield key, None
                continue
            json_obj = r.json()
            try:
                dto = Dto(**json_obj)
                yield key, dto
            except ValidationError:
                logger.warning(
                    (f"Не удалось разобрать расписание для группы {key}"
                     f" из-за ошибки в ответе: {json_obj['message']}")
                )
                yield key, None
            except Exception as e:
                logger.warning(f"Неожиданная ошибка при обработке расписания: {e}")
            await asyncio.sleep(DEFAULT_DELAY)
