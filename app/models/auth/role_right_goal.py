from sqlalchemy import Column, ForeignKey, Boolean, false
from sqlalchemy.orm import Mapped, relationship
from app.models.base import Base


class RoleRightGoal(Base):
    """Связь роли с правом и целью."""

    __tablename__ = "role_right_goals"

    role_id: int = Column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    right_id: int = Column(
        ForeignKey("rights.id", ondelete="CASCADE"),
        primary_key=True,
    )
    goal_id: int = Column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        primary_key=True,
    )
    can_grant: bool = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    role: Mapped["Role"] = relationship("Role", back_populates="role_right_goals")
    right: Mapped["Right"] = relationship("Right", back_populates="role_right_goals")
    goal: Mapped["Goal"] = relationship("Goal", back_populates="role_right_goals")

    def __repr__(self) -> str:
        return (
            "RoleRightGoal("
            f"role_id={self.role_id!r}, right_id={self.right_id!r}, goal_id={self.goal_id!r}, can_grant={self.can_grant!r}"
            ")"
        )
