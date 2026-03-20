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
}

RIGHTS_BY_ID: dict[int, str] = {
    1: "view",
    2: "create",
    3: "edit",
    4: "delete",
    5: "grant",
}

RIGHTS_BY_NAME: dict[str, int] = {
    "view": 1,
    "create": 2,
    "edit": 3,
    "delete": 4,
    "grant": 5,
}

# =============================================================================
# ХЕЛПЕРЫ ДЛЯ ПРОВЕРКИ ПРАВ (CORTEGES ID)
# =============================================================================

# Все права для каждой цели (для удобной проверки)
PERMISSIONS_BY_GOAL: dict[int, list[tuple[int, int]]] = {
    STATS_GOAL_ID: [
        (VIEW_RIGHT_ID, STATS_GOAL_ID),
        (CREATE_RIGHT_ID, STATS_GOAL_ID),
        (EDIT_RIGHT_ID, STATS_GOAL_ID),
        (DELETE_RIGHT_ID, STATS_GOAL_ID),
    ],
    DASHBOARDS_GOAL_ID: [
        (VIEW_RIGHT_ID, DASHBOARDS_GOAL_ID),
        (CREATE_RIGHT_ID, DASHBOARDS_GOAL_ID),
        (EDIT_RIGHT_ID, DASHBOARDS_GOAL_ID),
        (DELETE_RIGHT_ID, DASHBOARDS_GOAL_ID),
    ],
    USERS_GOAL_ID: [
        (VIEW_RIGHT_ID, USERS_GOAL_ID),
        (CREATE_RIGHT_ID, USERS_GOAL_ID),
        (EDIT_RIGHT_ID, USERS_GOAL_ID),
        (DELETE_RIGHT_ID, USERS_GOAL_ID),
    ],
    ROLES_GOAL_ID: [
        (VIEW_RIGHT_ID, ROLES_GOAL_ID),
        (CREATE_RIGHT_ID, ROLES_GOAL_ID),
        (EDIT_RIGHT_ID, ROLES_GOAL_ID),
        (DELETE_RIGHT_ID, ROLES_GOAL_ID),
        (GRANT_RIGHT_ID, ROLES_GOAL_ID),
    ],
    TABLES_GOAL_ID: [
        (VIEW_RIGHT_ID, TABLES_GOAL_ID),
        (CREATE_RIGHT_ID, TABLES_GOAL_ID),
        (EDIT_RIGHT_ID, TABLES_GOAL_ID),
        (DELETE_RIGHT_ID, TABLES_GOAL_ID),
    ],
    RESOURCES_GOAL_ID: [
        (VIEW_RIGHT_ID, RESOURCES_GOAL_ID),
        (CREATE_RIGHT_ID, RESOURCES_GOAL_ID),
        (EDIT_RIGHT_ID, RESOURCES_GOAL_ID),
        (DELETE_RIGHT_ID, RESOURCES_GOAL_ID),
    ],
    TASKS_GOAL_ID: [
        (VIEW_RIGHT_ID, TASKS_GOAL_ID),
        (CREATE_RIGHT_ID, TASKS_GOAL_ID),
        (EDIT_RIGHT_ID, TASKS_GOAL_ID),
        (DELETE_RIGHT_ID, TASKS_GOAL_ID),
    ],
    NAV_GOAL_ID: [
        (VIEW_RIGHT_ID, NAV_GOAL_ID),
        (CREATE_RIGHT_ID, NAV_GOAL_ID),
        (EDIT_RIGHT_ID, NAV_GOAL_ID),
        (DELETE_RIGHT_ID, NAV_GOAL_ID),
    ],
    USER_PASS_GOAL_ID: [
        (EDIT_RIGHT_ID, USER_PASS_GOAL_ID),
    ],
    ADMIN_GOAL_ID: [
        (VIEW_RIGHT_ID, ADMIN_GOAL_ID),
        (EDIT_RIGHT_ID, ADMIN_GOAL_ID),
    ],
    REVIEWS_GOAL_ID: [
        (VIEW_RIGHT_ID, REVIEWS_GOAL_ID),
        (EDIT_RIGHT_ID, REVIEWS_GOAL_ID),
    ]
}