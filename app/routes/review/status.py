from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.review import Review
from app.models.review_status import ReviewStatus
# from app.helpers.permissions import require_rights


def register_endpoint(router: APIRouter):
    "Эндпоинт для назначения статуса Review"

    @router.patch(
        "/{review_id}/status",
        description="Назначение статуса отзыву по ID статуса",
        status_code=status.HTTP_200_OK,
    )
    async def set_review_status(
        review_id: int,
        status_id: int = Form(...),
        db: AsyncSession = Depends(get_db),
    ):
        review: Union[Review, None] = (
            await db.execute(
                Select(Review).filter(Review.id == review_id)
            )
        ).scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отзыв не найден",
            )

        status_obj: Union[ReviewStatus, None] = (
            await db.execute(
                Select(ReviewStatus).filter(ReviewStatus.id == status_id)
            )
        ).scalar_one_or_none()

        if not status_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Статус не найден",
            )

        review.status_id = status_obj.id
        await db.commit()
        await db.refresh(review)

        return {
            "message": "Статус отзыва обновлён",
            "review_id": review.id,
            "status_id": status_obj.id,
            "status_name": status_obj.name,
        }

    @router.get(
        "/statuses",
        description="Список всех возможных статусов отзывов",
    )
    async def list_review_statuses(
        db: AsyncSession = Depends(get_db),
    ):
        result = await db.execute(Select(ReviewStatus))
        statuses = result.scalars().all()

        return [
            {"id": s.id, "name": s.name}
            for s in statuses
        ]
