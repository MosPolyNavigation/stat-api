from dataclasses import dataclass, field
from typing import Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.services.permission_service import PermissionService
from app.services.user_logger_service import UserLoggerService


@dataclass
class GraphQLContext:
    db: AsyncSession
    current_user: User
    permission_service: PermissionService
    user_logger: UserLoggerService
    request: Any
    error_logs: List[str] = field(default_factory=list)
