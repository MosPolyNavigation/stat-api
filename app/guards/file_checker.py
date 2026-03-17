import os

from fastapi import UploadFile, HTTPException, Request
from typing import Optional

class FileValidator:
    def __init__(
        self, 
        max_size: int = 10 * 1024 * 1024,
        allowed_types: Optional[list[str]] = None,
        request_overhead_multiplier: float = 2.0
    ):
        self.max_size = max_size
        self.allowed_types = allowed_types or []
        self.request_overhead_multiplier = request_overhead_multiplier
    
    async def __call__(
        self, 
        image: Optional[UploadFile],
        request: Request
    ) -> Optional[UploadFile]:
        if image is None:
            return None

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size * self.request_overhead_multiplier:
            raise HTTPException(
                status_code=413,
                detail=f"Request too large ({content_length} bytes)"
            )
        
        image.file.seek(0, 2)
        file_size = image.file.tell()
        image.file.seek(0)
        
        if file_size > self.max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({file_size} > {self.max_size})"
            )
        
        if self.allowed_types and image.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid type: {image.content_type}"
            )
        
        return image


class SVGValidator:
    def __init__(
        self, 
        max_size: int = 1024 * 1024,
        allowed_types: Optional[list[str]] = None,
    ):
        self.max_size = max_size
        self.allowed_types = allowed_types or []
    
    async def __call__(
        self, 
        file: UploadFile,
        request: Request
    ) -> UploadFile:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_size:
            raise HTTPException(
                status_code=413,
                detail=f"Request too large ({content_length} bytes)"
            )
        
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > self.max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({file_size} > {self.max_size})"
            )
        
        if self.allowed_types and file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid type: {file.content_type}"
            )
        
        return file


class PhotoValidator:
    """
    Валидатор для множественной загрузки изображений.
    Проверяет каждый файл в списке.
    """
    
    # Разрешённые MIME-типы
    ALLOWED_TYPES = [
        "image/jpeg",
        "image/png", 
        "image/webp"
    ]
    
    # Разрешённые расширения (для дополнительной проверки)
    ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]
    
    def __init__(
        self, 
        max_size_per_file: int = 10 * 1024 * 1024,
        max_total_size: int = 50 * 1024 * 1024,
        max_files: int = 10,
    ):
        self.max_size_per_file = max_size_per_file
        self.max_total_size = max_total_size
        self.max_files = max_files
    
    async def __call__(
        self, 
        photos: list[UploadFile],
        request: Request
    ) -> list[UploadFile]:
        # 1. Проверка количества файлов
        if len(photos) > self.max_files:
            raise HTTPException(
                status_code=413,
                detail=f"Too many files. Max: {self.max_files}, got: {len(photos)}"
            )
        
        # 2. Быстрая проверка Content-Length всего запроса
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_total_size:
            raise HTTPException(
                status_code=413,
                detail=f"Request too large. Max: {self.max_total_size} bytes"
            )
        
        # 3. Проверка каждого файла
        total_size = 0
        for i, photo in enumerate(photos):
            # Проверка Content-Type
            if not photo.content_type or photo.content_type not in self.ALLOWED_TYPES:
                raise HTTPException(
                    status_code=415,
                    detail=f"File {i+1} ({photo.filename}): Unsupported media type '{photo.content_type}'"
                )
            
            # Проверка размера файла
            photo.file.seek(0, 2)
            file_size = photo.file.tell()
            photo.file.seek(0)
            
            if file_size > self.max_size_per_file:
                raise HTTPException(
                    status_code=413,
                    detail=f"File {i+1} ({photo.filename}): Too large. Max: {self.max_size_per_file} bytes, got: {file_size}"
                )
            
            total_size += file_size
            
            if photo.filename:
                ext = os.path.splitext(photo.filename)[-1].lower().lstrip(".")
                if ext not in self.ALLOWED_EXTENSIONS:
                    raise HTTPException(
                        status_code=415,
                        detail=f"File {i+1} ({photo.filename}): Unsupported extension '.{ext}'"
                    )
        
        # 4. Проверка общего размера всех файлов
        if total_size > self.max_total_size:
            raise HTTPException(
                status_code=413,
                detail=f"Total size too large. Max: {self.max_total_size} bytes, got: {total_size}"
            )
        
        return photos


image_validator = FileValidator(
    max_size=10 * 1024 * 1024,
    allowed_types=["image/jpeg", "image/png", "image/gif"]
)

plan_validator = SVGValidator(
    max_size=1024 * 1024,
    allowed_types=["image/svg+xml"]
)

photo_validator = PhotoValidator(
    max_size_per_file=10 * 1024 * 1024,
    max_total_size=50 * 1024 * 1024,
    max_files=10
)