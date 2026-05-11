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

PAYLOAD_TYPE_IDS_BY_CODE: dict[str, int] = {
    "endpoint": PAYLOAD_TYPE_ENDPOINT_ID,
    "auditory_id": PAYLOAD_TYPE_AUDITORY_ID,
    "start_id": PAYLOAD_TYPE_START_ID,
    "end_id": PAYLOAD_TYPE_END_ID,
    "success": PAYLOAD_TYPE_SUCCESS_ID,
    "plan_id": PAYLOAD_TYPE_PLAN_ID,
}

ALLOWED_PAYLOADS: list[tuple[int, int]] = [
    (EVENT_TYPE_SITE_ID, PAYLOAD_TYPE_ENDPOINT_ID),
    (EVENT_TYPE_AUDS_ID, PAYLOAD_TYPE_AUDITORY_ID),
    (EVENT_TYPE_AUDS_ID, PAYLOAD_TYPE_SUCCESS_ID),
    (EVENT_TYPE_WAYS_ID, PAYLOAD_TYPE_START_ID),
    (EVENT_TYPE_WAYS_ID, PAYLOAD_TYPE_END_ID),
    (EVENT_TYPE_WAYS_ID, PAYLOAD_TYPE_SUCCESS_ID),
    (EVENT_TYPE_PLANS_ID, PAYLOAD_TYPE_PLAN_ID),
]

# =============================================================================
# КОНСТАНТЫ ТИПОВ ДАШБОРДОВ (DASHBOARD TYPES)
# =============================================================================
DASHBOARD_TYPE_CHART_ID = 1
DASHBOARD_TYPE_AVG_ID = 2

DASHBOARD_TYPE_IDS_BY_CODE: dict[str, int] = {
    "chart": DASHBOARD_TYPE_CHART_ID,
    "avg": DASHBOARD_TYPE_AVG_ID,
}

# =============================================================================
# КОНСТАНТЫ ТИПОВ ЗНАЧЕНИЙ (VALUE TYPES)
# =============================================================================
VALUE_TYPE_INT_ID = 1
VALUE_TYPE_STRING_ID = 2
VALUE_TYPE_BOOL_ID = 3

VALUE_TYPE_IDS_BY_NAME: dict[str, int] = {
    "int": VALUE_TYPE_INT_ID,
    "string": VALUE_TYPE_STRING_ID,
    "bool": VALUE_TYPE_BOOL_ID,
}

# =============================================================================
# КОНСТАНТЫ ПРАВ (RIGHTS)
# =============================================================================

# Имена прав
VIEW_RIGHT_NAME = "view"
CREATE_RIGHT_NAME = "create"
EDIT_RIGHT_NAME = "edit"
DELETE_RIGHT_NAME = "delete"
GRANT_RIGHT_NAME = "grant"

# ID прав
VIEW_RIGHT_ID = 1
CREATE_RIGHT_ID = 2
EDIT_RIGHT_ID = 3
DELETE_RIGHT_ID = 4
GRANT_RIGHT_ID = 5

# =============================================================================
# СЛОВАРИ ДЛЯ МАППИНГА (ID ↔ NAME)
# =============================================================================

GOALS_BY_ID: dict[int, str] = {
    STATS_GOAL_ID: STATS_GOAL_NAME,
    DASHBOARDS_GOAL_ID: DASHBOARDS_GOAL_NAME,
    USERS_GOAL_ID: USERS_GOAL_NAME,
    ROLES_GOAL_ID: ROLES_GOAL_NAME,
    TABLES_GOAL_ID: TABLES_GOAL_NAME,
    RESOURCES_GOAL_ID: RESOURCES_GOAL_NAME,
    TASKS_GOAL_ID: TASKS_GOAL_NAME,
    NAV_GOAL_ID: NAV_GOAL_NAME,
    USER_PASS_GOAL_ID: USER_PASS_GOAL_NAME,
    ADMIN_GOAL_ID: ADMIN_GOAL_NAME,
    REVIEWS_GOAL_ID: REVIEWS_GOAL_NAME,
    REFRESH_TOKEN_GOAL_ID: REFRESH_TOKEN_GOAL_NAME,
    CLIENT_GOAL_ID: CLIENT_GOAL_NAME
}

GOALS_BY_NAME: dict[str, int] = {
    STATS_GOAL_NAME: STATS_GOAL_ID,
    DASHBOARDS_GOAL_NAME: DASHBOARDS_GOAL_ID,
    USERS_GOAL_NAME: USERS_GOAL_ID,
    ROLES_GOAL_NAME: ROLES_GOAL_ID,
    TABLES_GOAL_NAME: TABLES_GOAL_ID,
    RESOURCES_GOAL_NAME: RESOURCES_GOAL_ID,
    TASKS_GOAL_NAME: TASKS_GOAL_ID,
    NAV_GOAL_NAME: NAV_GOAL_ID,
    USER_PASS_GOAL_NAME: USER_PASS_GOAL_ID,
    ADMIN_GOAL_NAME: ADMIN_GOAL_ID,
    REVIEWS_GOAL_NAME: REVIEWS_GOAL_ID,
    REFRESH_TOKEN_GOAL_NAME: REFRESH_TOKEN_GOAL_ID,
    CLIENT_GOAL_NAME: CLIENT_GOAL_ID
}

RIGHTS_BY_ID: dict[int, str] = {
    VIEW_RIGHT_ID: VIEW_RIGHT_NAME,
    CREATE_RIGHT_ID: CREATE_RIGHT_NAME,
    EDIT_RIGHT_ID: EDIT_RIGHT_NAME,
    DELETE_RIGHT_ID: DELETE_RIGHT_NAME,
    GRANT_RIGHT_ID: GRANT_RIGHT_NAME,
}

RIGHTS_BY_NAME: dict[str, int] = {
    VIEW_RIGHT_NAME: VIEW_RIGHT_ID,
    CREATE_RIGHT_NAME: CREATE_RIGHT_ID,
    EDIT_RIGHT_NAME: EDIT_RIGHT_ID,
    DELETE_RIGHT_NAME: DELETE_RIGHT_ID,
    GRANT_RIGHT_NAME: GRANT_RIGHT_ID,
}

GOAL_RIGHTS: list[tuple[int, int]] = [
    (STATS_GOAL_ID, VIEW_RIGHT_ID),
    (STATS_GOAL_ID, CREATE_RIGHT_ID),
    (STATS_GOAL_ID, EDIT_RIGHT_ID),
    (STATS_GOAL_ID, DELETE_RIGHT_ID),
    (DASHBOARDS_GOAL_ID, VIEW_RIGHT_ID),
    (DASHBOARDS_GOAL_ID, CREATE_RIGHT_ID),
    (DASHBOARDS_GOAL_ID, EDIT_RIGHT_ID),
    (DASHBOARDS_GOAL_ID, DELETE_RIGHT_ID),
    (USERS_GOAL_ID, VIEW_RIGHT_ID),
    (USERS_GOAL_ID, CREATE_RIGHT_ID),
    (USERS_GOAL_ID, EDIT_RIGHT_ID),
    (USERS_GOAL_ID, DELETE_RIGHT_ID),
    (ROLES_GOAL_ID, VIEW_RIGHT_ID),
    (ROLES_GOAL_ID, CREATE_RIGHT_ID),
    (ROLES_GOAL_ID, EDIT_RIGHT_ID),
    (ROLES_GOAL_ID, DELETE_RIGHT_ID),
    (ROLES_GOAL_ID, GRANT_RIGHT_ID),
    (TABLES_GOAL_ID, VIEW_RIGHT_ID),
    (TABLES_GOAL_ID, EDIT_RIGHT_ID),
    (RESOURCES_GOAL_ID, VIEW_RIGHT_ID),
    (RESOURCES_GOAL_ID, CREATE_RIGHT_ID),
    (RESOURCES_GOAL_ID, EDIT_RIGHT_ID),
    (RESOURCES_GOAL_ID, DELETE_RIGHT_ID),
    (TASKS_GOAL_ID, VIEW_RIGHT_ID),
    (TASKS_GOAL_ID, CREATE_RIGHT_ID),
    (TASKS_GOAL_ID, EDIT_RIGHT_ID),
    (TASKS_GOAL_ID, DELETE_RIGHT_ID),
    (NAV_GOAL_ID, VIEW_RIGHT_ID),
    (NAV_GOAL_ID, CREATE_RIGHT_ID),
    (NAV_GOAL_ID, EDIT_RIGHT_ID),
    (NAV_GOAL_ID, DELETE_RIGHT_ID),
    (USER_PASS_GOAL_ID, EDIT_RIGHT_ID),
    (ADMIN_GOAL_ID, VIEW_RIGHT_ID),
    (ADMIN_GOAL_ID, EDIT_RIGHT_ID),
    (REVIEWS_GOAL_ID, VIEW_RIGHT_ID),
    (REVIEWS_GOAL_ID, EDIT_RIGHT_ID),
    (REFRESH_TOKEN_GOAL_ID, VIEW_RIGHT_ID),
    (REFRESH_TOKEN_GOAL_ID, EDIT_RIGHT_ID),
    (REFRESH_TOKEN_GOAL_ID, DELETE_RIGHT_ID),
    (CLIENT_GOAL_ID, CREATE_RIGHT_ID)
]

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
