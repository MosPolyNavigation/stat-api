from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String
from .base import Base


class Auditory(Base):
    __tablename__ = "auditories"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    selected: Mapped[list["SelectAuditory"]] = relationship("SelectAuditory", back_populates="auditory")
