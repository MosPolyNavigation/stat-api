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

# Проверка bytes (для multipart UploadFile)
def is_valid_svg_bytes(data: bytes) -> bool:
    if not data:
        return False

    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return False
    return is_valid_svg(text)

# Сохранение svg из bytes (для multipart UploadFile)
async def save_svg_bytes_to_disk(data: bytes, base_path: str) -> str | None:
    if not is_valid_svg_bytes(data):
        return None

    os.makedirs(base_path, exist_ok=True)

    file_name = f"{uuid.uuid4().hex}.svg"
    file_path = os.path.join(base_path, file_name)

    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)
    except OSError:
        return None

    if not os.path.exists(file_path):
        return None

    return file_name