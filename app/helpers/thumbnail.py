import os
from PIL import Image
from typing import Optional


def create_thumbnail(
    source_path: str,
    thumbnail_dir: str,
    size: tuple[int, int] = (200, 200),
    quality: int = 85
) -> Optional[str]:
    """
    Создает thumbnail для изображения и сохраняет его в директорию thumbnails.

    Args:
        source_path: Полный путь к оригинальному изображению
        thumbnail_dir: Директория для сохранения thumbnails
        size: Размер thumbnail (ширина, высота), по умолчанию (200, 200)
        quality: Качество JPEG сжатия (1-100), по умолчанию 85

    Returns:
        Имя файла thumbnail или None в случае ошибки

    Example:
        >>> create_thumbnail("/static/auditories/abc123.png", "/static/thumbnails")
        "abc123.jpg"
    """
    try:
        # Открываем изображение
        with Image.open(source_path) as img:
            # Конвертируем в RGB если необходимо (для PNG с прозрачностью)
            if img.mode in ("RGBA", "LA", "P"):
                # Создаем белый фон
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Создаем thumbnail с сохранением пропорций
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Получаем имя файла без расширения
            base_name = os.path.splitext(os.path.basename(source_path))[0]
            thumbnail_name = f"{base_name}.jpg"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_name)

            # Сохраняем как JPEG
            img.save(thumbnail_path, "JPEG", quality=quality, optimize=True)

            return thumbnail_name

    except Exception as e:
        # В случае ошибки возвращаем None
        print(f"Error creating thumbnail for {source_path}: {e}")
        return None


async def create_thumbnail_async(
    source_path: str,
    thumbnail_dir: str,
    size: tuple[int, int] = (200, 200),
    quality: int = 85
) -> Optional[str]:
    """
    Асинхронная обертка для создания thumbnail.
    Выполняет создание thumbnail в синхронном режиме, так как Pillow не поддерживает async.

    Args:
        source_path: Полный путь к оригинальному изображению
        thumbnail_dir: Директория для сохранения thumbnails
        size: Размер thumbnail (ширина, высота), по умолчанию (200, 200)
        quality: Качество JPEG сжатия (1-100), по умолчанию 85

    Returns:
        Имя файла thumbnail или None в случае ошибки
    """
    return create_thumbnail(source_path, thumbnail_dir, size, quality)
