"""Утилиты для безопасной работы с именами файлов изображений."""

import os
import re
from typing import Optional
from urllib.parse import unquote

# Разрешенные расширения для загрузки изображений
ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif',
    'webp', 'bmp', 'svg', 'heif'
}


def validate_filename(filename: str) -> bool:
    """
    Проверяет, что имя файла соответствует UUIDv4 и допустимому расширению.

    Args:
        filename: Имя файла, полученное от пользователя.

    Returns:
        bool: True, если имя безопасно и соответствует шаблону.
    """
    pattern = r"""
        ^                    # начало строки
        [0-9a-f]{32}         # 32 hex-символа (UUID v4 без разделителей)
        \.                   # точка перед расширением
        (?:                  # разрешенное расширение
            png|jpe?g|gif|webp|bmp|svg|heif
        )$                   # конец строки
    """
    return re.fullmatch(
        pattern, filename, re.VERBOSE | re.IGNORECASE
    ) is not None


def sanitize_image_filename(raw_name: str) -> Optional[str]:
    """
    Нормализует имя файла из пользовательского ввода и проверяет его на безопасность.

    Args:
        raw_name: Имя файла из запроса (может быть URL-encoded).

    Returns:
        Optional[str]: Безопасное имя файла в нижнем регистре или None, если имя некорректно.
    """
    decoded_name = unquote(raw_name)
    normalized_name = decoded_name.lower()

    if not validate_filename(normalized_name):
        return None

    name_part, ext = os.path.splitext(normalized_name)
    ext = ext[1:]

    if ext not in ALLOWED_EXTENSIONS:
        return None

    return normalized_name


def secure_image_path(base_dir: str, user_filename: str) -> Optional[str]:
    """
    Формирует безопасный абсолютный путь к файлу, предотвращая выход за пределы каталога.

    Args:
        base_dir: Базовый каталог, куда сохраняется файл.
        user_filename: Имя файла, предоставленное пользователем.

    Returns:
        Optional[str]: Абсолютный путь к файлу либо None, если имя/путь небезопасен.
    """
    safe_filename = sanitize_image_filename(user_filename)
    if not safe_filename:
        return None

    base_dir = os.path.abspath(os.path.realpath(base_dir))
    target_path = os.path.abspath(os.path.join(base_dir, safe_filename))

    if os.path.commonpath([base_dir]) != os.path.commonpath(
            [base_dir, target_path]
    ):
        return None

    return target_path
