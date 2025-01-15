from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

engine = create_engine(str(get_settings().sqlalchemy_database_url))
SessionLocal = sessionmaker(autoflush=True, autocommit=False, bind=engine)


def get_db():
    """
    Функция для получения сессии базы данных.

    Эта функция создает сессию базы данных и возвращает ее. После использования сессии она закрывается.

    Yields:
        Session: Сессия базы данных.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
