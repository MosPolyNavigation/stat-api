import os
import re
from typing import Optional
from urllib.parse import unquote

# Белый список разрешенных расширений для изображений
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg', 'heif'}


def validate_filename(filename: str) -> bool:
    """Проверка соответствия формату UUIDv4 + разрешенное расширение"""
    # UUID v4 (32 hex-символа) + расширение из белого списка
    pattern = r"""
        ^                    # Начало строки
        [0-9a-f]{32}         # 32 hex-символа (UUID v4 без дефисов)
        \.                  # Точка перед расширением
        (?:                 # Группа для расширений
            png|jpe?g|gif|webp|bmp|svg|heif
        )$                  # Конец строки
    """
    return re.fullmatch(pattern, filename, re.VERBOSE | re.IGNORECASE) is not None


def sanitize_image_filename(raw_name: str) -> Optional[str]:
    """Обработка имени файла с учетом специфики UUID + расширение"""
    # Декодируем URL-encoded символы (например, %2E -> '.')
    decoded_name = unquote(raw_name)

    # Приводим к нижнему регистру для единообразия
    normalized_name = decoded_name.lower()

    # Проверяем соответствие формату
    if not validate_filename(normalized_name):
        return None

    # Разделяем имя и расширение для дополнительной проверки
    name_part, ext = os.path.splitext(normalized_name)
    ext = ext[1:]  # Убираем точку в расширении

    if ext not in ALLOWED_EXTENSIONS:
        return None

    return normalized_name


def secure_image_path(base_dir: str, user_filename: str) -> Optional[str]:
    """Безопасное построение пути к файлу изображения"""
    # Валидация имени файла
    safe_filename = sanitize_image_filename(user_filename)
    if not safe_filename:
        return None

    # Формируем абсолютный путь
    base_dir = os.path.abspath(os.path.realpath(base_dir))
    target_path = os.path.abspath(os.path.join(base_dir, safe_filename))

    # Проверка на выход за пределы базовой директории
    if os.path.commonpath([base_dir]) != os.path.commonpath([base_dir, target_path]):
        return None

    return target_path

if __name__ == "__main__":
    print(secure_image_path("./static/", "e3f295a9311d490888ad4706ad39220b.png"))
    pass