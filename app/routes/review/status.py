from typing import Union, Optional

from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Review, ReviewStatus
from app.helpers.permissions import require_rights_with_logging
from app.services.user_logger_service import UserLoggerService, get_user_logger_service
from app.models import User


def register_endpoint(router: APIRouter):
    @router.patch(
        "/{review_id}/status",
        description="Назначение статуса отзыву по ID статуса",
        tags=["review"],
        status_code=status.HTTP_200_OK,
    )
    async def set_review_status(
        review_id: int,
        status_id: int = Form(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(
            require_rights_with_logging(
                "reviews",
                "edit",
                error_text="Попытка смены статуса без прав",
            )
        ),
        logger: UserLoggerService = Depends(get_user_logger_service),
    ):
        """Эндпоинт для назначения статуса Review"""
        review: Union[Review, None] = (
            await db.execute(Select(Review).filter(Review.id == review_id))
        ).scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отзыв не найден",
            )

        status_obj: Optional[ReviewStatus] = (
            await db.execute(Select(ReviewStatus).filter(ReviewStatus.id == status_id))
        ).scalar_one_or_none()

        if not status_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Статус не найден",
            )

        review.review_status_id = status_obj.id
        status_name = status_obj.name
        await db.commit()
        await db.refresh(review)

        logger.log(current_user, f"Смена статуса отзыва {review_id} на {status_name}")
        return {
            "message": "Статус отзыва обновлён",
            "review_id": review.id,
            "status_id": review.review_status_id,
            "status_name": status_obj.name,
        }
