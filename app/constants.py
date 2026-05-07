# =============================================================================
# КОНСТАНТЫ ЦЕЛЕЙ (GOALS)
# =============================================================================

# Имена целей
STATS_GOAL_NAME = "stats"
DASHBOARDS_GOAL_NAME = "dashboards"
USERS_GOAL_NAME = "users"
ROLES_GOAL_NAME = "roles"
TABLES_GOAL_NAME = "tables"
RESOURCES_GOAL_NAME = "resources"
TASKS_GOAL_NAME = "tasks"
NAV_GOAL_NAME = "nav_data"
USER_PASS_GOAL_NAME = "user_pass"
ADMIN_GOAL_NAME = "admin"
REVIEWS_GOAL_NAME = "reviews"
CLIENT_GOAL_NAME = "client"
REFRESH_TOKEN_GOAL_NAME = "refresh_token"

# ID целей
STATS_GOAL_ID = 1
DASHBOARDS_GOAL_ID = 2
USERS_GOAL_ID = 3
ROLES_GOAL_ID = 4
TABLES_GOAL_ID = 5
RESOURCES_GOAL_ID = 6
TASKS_GOAL_ID = 7
NAV_GOAL_ID = 8
USER_PASS_GOAL_ID = 9
ADMIN_GOAL_ID = 10
REVIEWS_GOAL_ID = 11
REFRESH_TOKEN_GOAL_ID = 12
CLIENT_GOAL_ID = 13

# =============================================================================
# КОНСТАНТЫ НОВОЙ СХЕМЫ СОБЫТИЙ
# =============================================================================

EVENT_TYPE_SITE_ID = 1
EVENT_TYPE_AUDS_ID = 2
EVENT_TYPE_WAYS_ID = 3
EVENT_TYPE_PLANS_ID = 4

EVENT_TYPE_IDS_BY_CODE: dict[str, int] = {
    "site": EVENT_TYPE_SITE_ID,
    "auds": EVENT_TYPE_AUDS_ID,
    "ways": EVENT_TYPE_WAYS_ID,
    "plans": EVENT_TYPE_PLANS_ID,
}

PAYLOAD_TYPE_ENDPOINT_ID = 1
PAYLOAD_TYPE_AUDITORY_ID = 2
PAYLOAD_TYPE_START_ID = 3
PAYLOAD_TYPE_END_ID = 4
PAYLOAD_TYPE_SUCCESS_ID = 5
PAYLOAD_TYPE_PLAN_ID = 6

# =============================================================================
# КОНСТАНТЫ ПРАВ (RIGHTS)
# =============================================================================

# Имена прав
VIEW_RIGHT_NAME = "view"
CREATE_RIGHT_NAME = "create"
EDIT_RIGHT_NAME = "edit"
DELETE_RIGHT_NAME = "delete"

# ID прав
VIEW_RIGHT_ID = 1
CREATE_RIGHT_ID = 2
EDIT_RIGHT_ID = 3
DELETE_RIGHT_ID = 4

# =============================================================================
# СЛОВАРИ ДЛЯ МАППИНГА (ID ↔ NAME)
# =============================================================================

GOALS_BY_ID: dict[int, str] = {
    1: "stats",
    2: "dashboards",
    3: "users",
    4: "roles",
    5: "tables",
    6: "resources",
    7: "tasks",
    8: "nav_data",
    9: "user_pass",
    10: "admin",
    11: "reviews",
    12: "refresh_token",
    13: "client"
}

GOALS_BY_NAME: dict[str, int] = {
    "stats": 1,
    "dashboards": 2,
    "users": 3,
    "roles": 4,
    "tables": 5,
    "resources": 6,
    "tasks": 7,
    "nav_data": 8,
    "user_pass": 9,
    "admin": 10,
    "reviews": 11,
    "refresh_token": 12,
    "client": 13
}

RIGHTS_BY_ID: dict[int, str] = {
    1: "view",
    2: "create",
    3: "edit",
    4: "delete",
}

RIGHTS_BY_NAME: dict[str, int] = {
    "view": 1,
    "create": 2,
    "edit": 3,
    "delete": 4,
}

# =============================================================================
# КОНСТАНТЫ проблем (Problems)
# =============================================================================

# Названия
WAY_PROBLEM_NAME = "way"
OTHER_PROBLEM_NAME = "other"
PLAN_PROBLEM_NAME = "plan"
WORK_PROBLEM_NAME = "work"

# =============================================================================
# СЛОВАРИ ДЛЯ МАППИНГА ПРОБЛЕМ
# =============================================================================

PROBLEMS: list[str] = [
    WAY_PROBLEM_NAME,
    OTHER_PROBLEM_NAME,
    PLAN_PROBLEM_NAME,
    WORK_PROBLEM_NAME,
]

# =============================================================================
# СЛОВАРИ ДЛЯ МАППИНГА СТАТУСОВ ОТЗЫВОВ
# =============================================================================

REVIEW_STATUSES: dict[int, str] = {
    1: "бэклог",
    2: "на рассмотрении",
    3: "принят в работу",
    4: "ждет проверки",
    5: "исправлен",
    6: "не требует исправления",
    7: "исправление отложено",
}
