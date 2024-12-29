from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from uuid import uuid4
from database import Base

class UUID(Base):
    __tablename__ = "uuids"

    id: str = Column(String(36), primary_key=True, default=str(uuid4()))
    creation_date: datetime = Column(DateTime, default=datetime.now())
