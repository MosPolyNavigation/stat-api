from dataclasses import dataclass, field
from strawberry.fastapi import BaseContext
from typing import Any, List, Dict
from strawberry.dataloader import DataLoader
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.services.permission_service import PermissionService
from app.services.user_logger_service import UserLoggerService


@dataclass
class GraphQLContext(BaseContext):
    db: AsyncSession
    current_user: User
    permission_service: PermissionService
    user_logger: UserLoggerService
    request: Any
    error_logs: List[str] = field(default_factory=list)
    loaders: Dict[str, DataLoader] = field(default_factory=dict)
