from fastapi import APIRouter, Depends

from app.helpers.auth_utils import get_goal_rights_map
from app.helpers.permissions import require_rights
from app.schemas.allowed_payloads import AllowedPermissionsResponse
from app.constants import ROLES_GOAL_NAME, VIEW_RIGHT_NAME


def register_endpoint(router: APIRouter):
    @router.get(
        "/allowed_permissions",
        response_model=AllowedPermissionsResponse,
        summary="Получить допустимые права для целей",
        description="Возвращает маппинг ID целей к спискам допустимых ID прав, "
        "сформированный динамически из константы GOAL_RIGHTS. "
        "Доступно только пользователям с правом `roles:view`.",
        dependencies=[Depends(require_rights(ROLES_GOAL_NAME, VIEW_RIGHT_NAME))],
        tags=["auth"],
    )
    async def get_allowed_permissions() -> AllowedPermissionsResponse:
        """
        Возвращает системный маппинг допустимых прав для каждой цели.
        Данные формируются из константы GOAL_RIGHTS — единого источника истины.
        Служебные цели (refresh_token, client) исключаются из ответа.
        """
        return AllowedPermissionsResponse(allowed_permissions=get_goal_rights_map())
