goals: dict[int, str] = {
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
    13: "client",
}

rights: dict[int, str] = {
    1: "view",
    2: "create",
    3: "edit",
    4: "delete",
}

roles: dict[int, str] = {
    1: "admin"
}

roles_rights_goals: list[tuple[int, int, int]] = [
    (1, 1, 1),
    (1, 2, 1),
    (1, 3, 1),
    (1, 4, 1),
    (1, 1, 2),
    (1, 1, 3),
    (1, 2, 3),
    (1, 3, 3),
    (1, 4, 3),
    (1, 1, 4),
    (1, 2, 4),
    (1, 3, 4),
    (1, 4, 4),
    (1, 1, 5),
    (1, 3, 5),
    (1, 1, 6),
    (1, 2, 6),
    (1, 3, 6),
    (1, 4, 6),
    (1, 1, 7),
    (1, 3, 7),
    (1, 1, 8),
    (1, 2, 8),
    (1, 3, 8),
    (1, 4, 8),
    (1, 3, 9),
    (1, 1, 10),
    (1, 3, 10),
    (1, 1, 11),
    (1, 3, 11),
    (1, 1, 12),
    (1, 3, 12),
    (1, 4, 12),
    (1, 2, 13),
]
