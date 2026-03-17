# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List


class BanInfoOut(BaseModel):
    """Информация о бане пользователя."""
    user_id: str = Field(..., description="ID пользователя")
    banned: bool = Field(True, description="Флаг бана")
    ban_reason: Optional[str] = Field(None, description="Причина бана")
    ban_timestamp: Optional[str] = Field(None, description="Время бана (ISO 8601)")
    violation_count: int = Field(0, description="Количество нарушений")
    requests_count: int = Field(0, description="Количество запросов в истории")
    last_request: Optional[str] = Field(None, description="Время последнего запроса (ISO 8601)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "banned": True,
                "ban_reason": "Excessive violations (15 times)",
                "ban_timestamp": "2024-03-18T14:30:00",
                "violation_count": 15,
                "requests_count": 23,
                "last_request": "2024-03-18T14:29:55"
            }
        }


class BanListOut(BaseModel):
    """Пагинированный список банов."""
    items: List[BanInfoOut] = Field(..., description="Список забаненных пользователей")
    total: int = Field(..., description="Общее количество забаненных")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Размер страницы")
    pages: int = Field(..., description="Всего страниц")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "banned": True,
                        "ban_reason": "Burst attack detected",
                        "ban_timestamp": "2024-03-18T14:30:00",
                        "violation_count": 0,
                        "requests_count": 30,
                        "last_request": "2024-03-18T14:29:58"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 100,
                "pages": 1
            }
        }


class UnbanRequest(BaseModel):
    """Запрос на снятие бана (для аудита)."""
    reason: Optional[str] = Field(None, description="Причина разбана")
    
    class Config:
        json_schema_extra = {
            "example": {"reason": "False positive, user verified"}
        }