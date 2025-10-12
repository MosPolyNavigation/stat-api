import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.helpers.auth_utils import get_current_active_user

# Будет использоваться рекомендуемый алгоритм хэширования паролей
password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class Token(BaseModel):
    """Схема ответа при выдаче токена"""

    access_token: str
    token_type: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """проверка введённого пароля"""
    """метод verify проверяет, совпадает ли введённый пароль с хэшированным.
    Метод автоматически определяет алгоритм, использованный при хэшировании."""
    return password_hash.verify(plain_password, hashed_password)


# Пока что нигде не используется (создание пароля)
# def get_password_hash(password):
#     """Создание хэша пароля"""
#     return password_hash.hash(password)


def get_user_by_login(db: Session, login: str) -> Optional[User]:
    """Получить пользователя по логину"""
    return db.execute(select(User).filter_by(login=login)).scalar()


def authenticate_user(db: Session, login: str, password: str):
    """проверка, существует ли пользователь и правильный ли пароль"""
    user = get_user_by_login(db, login)
    if not user or not verify_password(password, user.hash):
        return None
    return user


def create_token(user: User, db: Session):
    """Создать токен для пользователя (просто UUID)"""
    token = str(uuid.uuid4())
    user.token = token
    db.add(user)
    db.commit()
    db.refresh(user)
    return token


def register_endpoint(router: APIRouter):
    """Эндпоинт для аутентификации и выдачи токена пользователя"""

    @router.post(
        "/token",
        description="Эндпоинт для получения токена аутентификации",
        response_model=Token,
        tags=["auth"],
    )
    async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db)
    ):
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Некорректный логин или пароль")

        # Создание токена (UUID)
        access_token = create_token(user, db)
        return Token(access_token=access_token, token_type="bearer")

    """Эндпоинт для получения данных пользователя по токену"""

    @router.get(
        "/me",
        description="Эндпоинт для получения данных текущего пользователя по токену",
        response_model=UserOut,
        tags=["auth"],
    )
    async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Session = Depends(get_db),
    ):
        """Возвращает актуальные данные текущего пользователя"""
        db.refresh(current_user)
        return current_user

    # # Создал для того, чтобы проверить /me с активным/неактивным пользователем
    # @router.post(
    #     "/deactivate",
    #     description="Эндпоинт для деактивации текущего пользователя",
    #     tags=["auth"],
    # )
    # async def deactivate_user(
    #         current_user: Annotated[User, Depends(get_current_user)],
    #         db: Session = Depends(get_db)
    # ):
    #     """Деактивирует текущего пользователя"""
    #     if not current_user.is_active:
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Пользователь уже неактивен"
    #         )
    #
    #     current_user.is_active = False
    #     db.add(current_user)
    #     db.commit()
    #     db.refresh(current_user)
    #
    #     return {"message": f"Пользователь {current_user.login} деактивирован", "is_active": current_user.is_active}
