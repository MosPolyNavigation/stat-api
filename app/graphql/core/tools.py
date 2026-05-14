from typing import Any


def _get_attr(obj: Any, path: str) -> Any:
    """Безопасное получение вложенного атрибута по строке (напр. 'user.login')."""
    for part in path.split("."):
        if obj is None:
            return None
        obj = getattr(obj, part, None)
    return obj


def _compare_values(val: Any, op: str, target: Any) -> bool:
    """Выполняет сравнение двух значений с учётом типов."""
    if val is None and target is None:
        return op in ("eq", "is_null")
    if val is None or target is None:
        return op in ("ne", "is_null") and val != target

    try:
        if op == "eq":
            return val == target
        elif op == "ne":
            return val != target
        elif op == "gt":
            return val > target
        elif op == "gte":
            return val >= target
        elif op == "lt":
            return val < target
        elif op == "lte":
            return val <= target
        elif op == "in":
            return val in target
        elif op == "not_in":
            return val not in target
        elif op == "between":
            return target[0] <= val <= target[1]
        elif op == "not_between":
            return not (target[0] <= val <= target[1])
        elif op == "contains":
            return str(target).lower() in str(val).lower()
        elif op == "starts_with":
            return str(val).lower().startswith(str(target).lower())
        elif op == "ends_with":
            return str(val).lower().endswith(str(target).lower())
        elif op == "like":
            # Простая эмуляция LIKE с % и _
            import re
            pattern = re.escape(str(target)).replace(r"\%", ".*").replace(r"\_", ".")
            return bool(re.fullmatch(pattern, str(val), re.IGNORECASE))
        elif op == "not_like":
            import re
            pattern = re.escape(str(target)).replace(r"\%", ".*").replace(r"\_", ".")
            return not re.fullmatch(pattern, str(val), re.IGNORECASE)
    except (TypeError, ValueError):
        return False
    return False
