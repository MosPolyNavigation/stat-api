from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String
from .base import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)

    changed: Mapped[list["ChangePlan"]] = relationship("ChangePlan", back_populates="plan")
