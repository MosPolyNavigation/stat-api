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


image_validator = FileValidator(
    max_size=10 * 1024 * 1024,
    allowed_types=["image/jpeg", "image/png", "image/gif"]
)

plan_validator = SVGValidator(
    max_size=1024 * 1024,
    allowed_types=["image/svg+xml"]
)