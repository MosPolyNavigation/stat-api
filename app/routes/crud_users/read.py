from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut
from app.helpers.permissions import require_rights


def register_endpoint(router: APIRouter):
    "Эндпоинты для просмотра пользователей"

    @router.get(
        "",
        description="Получение списка пользователей с пагинацией",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_rights("users", "view"))]
    )
    async def read_users(
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(10, ge=1, le=100, description="Количество пользователей на странице"),
        db: Session = Depends(get_db)
    ):
        total_users = db.query(User).count()
        offset = (page - 1) * limit
        users = db.query(User).offset(offset).limit(limit).all()

        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователи не найдены"
            )

        user_list = []
        for u in users:
            user_list.append(UserOut(
                login=u.login,
                is_active=u.is_active,
            ))

        return {
            "page": page,
            "limit": limit,
            "total": total_users,
            "pages": (total_users + limit - 1) // limit,
            "items": user_list
        }

    "Эндпоинты для просмотра определённого пользователя"

    @router.get(
        "/{user_id}",
        description="Получение данных конкретного пользователя",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_rights("users", "view"))]
    )
    async def read_user(user_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        return UserOut(
            login=user.login,
            is_active=user.is_active
        )
