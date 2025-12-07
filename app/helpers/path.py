"""Утилиты для безопасной работы с путями и именами файлов изображений."""

import os
import re
from typing import Optional
from urllib.parse import unquote

# Разрешенные расширения изображений, которые можно отдавать пользователю.
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp",
    "bmp",
    "svg",
    "heif",
}


def validate_filename(filename: str) -> bool:
    """Проверяет, что имя соответствует UUIDv4 с допустимым расширением."""
    pattern = r"""
        ^                    # начало строки
        [0-9a-f]{32}         # 32 hex-символа (UUID v4 без дефисов)
        \.                   # точка перед расширением
        (?:png|jpe?g|gif|webp|bmp|svg|heif)$  # расширение
    """
    return re.fullmatch(pattern, filename, re.VERBOSE | re.IGNORECASE) is not None


def sanitize_image_filename(raw_name: str) -> Optional[str]:
    """Нормализует имя файла изображения, если оно соответствует нашим правилам."""
    decoded_name = unquote(raw_name).lower()
    if not validate_filename(decoded_name):
        return None

    _, ext = os.path.splitext(decoded_name)
    ext = ext[1:]
    if ext not in ALLOWED_EXTENSIONS:
        return None

    return decoded_name


def secure_image_path(base_dir: str, user_filename: str) -> Optional[str]:
    """Возвращает безопасный путь к файлу изображения внутри base_dir либо None."""
    safe_filename = sanitize_image_filename(user_filename)
    if not safe_filename:
        return None

    base_dir = os.path.abspath(os.path.realpath(base_dir))
    target_path = os.path.abspath(os.path.join(base_dir, safe_filename))

    if os.path.commonpath([base_dir]) != os.path.commonpath([base_dir, target_path]):
        return None

    return target_path
