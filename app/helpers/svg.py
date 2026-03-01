import os
import uuid
import aiofiles
from xml.etree import ElementTree

# Проверка, что файл svg
def is_valid_svg(svg_text: str) -> bool:
    # Пустое содержимое - точно не svg
    if not svg_text:
        return False

    # Проверяем, что это валидный XML
    try:
        root = ElementTree.fromstring(svg_text.strip())
    except ElementTree.ParseError:
        return False

    # Корневой тег должен быть <svg>
    tag = root.tag
    return tag == "svg" or tag.endswith("}svg")

# Сохранение svg
async def save_svg_to_disk(svg_text: str, base_path: str) -> str | None:
    if not is_valid_svg(svg_text):
        return None

    # Проверка, что директория существует
    os.makedirs(base_path, exist_ok=True)

    # Генерируем уникальное имя файла
    file_name = f"{uuid.uuid4().hex}.svg"
    file_path = os.path.join(base_path, file_name)

    # Пишем файл асинхронно
    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(svg_text.encode("utf-8"))
    except OSError:
        return None

    if not os.path.exists(file_path):
        return None

    return file_name