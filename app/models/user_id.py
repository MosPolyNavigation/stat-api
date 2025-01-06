from sqlalchemy import Column, String, DateTime
from datetime import datetime
from uuid import uuid4
from .base import Base


class UserId(Base):
    __tablename__ = "user_ids"

    user_id: str = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    creation_date: datetime = Column(DateTime, default=datetime.now, nullable=False)
