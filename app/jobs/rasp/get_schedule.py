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
    Извлекает JSON-объект, присвоенный переменной globalListGroups.
    """
    pattern = r'\b(?:var|let|const)\s+globalListGroups\s*=\s*({.*?});'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        raise ValueError('Не удалось найти globalListGroups в HTML.')

    json_str = match.group(1).split("\n")[0].rstrip('.groups;')
    if json_str.count('{') != json_str.count('}'):
        raise ValueError('Несбалансированные фигурные скобки в JSON.')
    return json_str


async def get_groups() -> dict[str, dict[str, Any | None] | Any]:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(BASE_URL, headers={'User-Agent': USER_AGENT})
        r.raise_for_status()
    html = r.text
    json_str = extract_json_string(html)
    data = json.loads(json_str)
    return data


async def get_schedule() -> AsyncGenerator[tuple[str, Union[Dto, None]], None]:
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
                    (f"Ошибка парсинга расписания для группы {key}"
                     f"из-за ошибки получения расписания: {json_obj['message']}")
                )
                yield key, None
            except Exception as e:
                logger.warning(f"Ошибка получения расписания: {e}")
            await asyncio.sleep(DEFAULT_DELAY)
