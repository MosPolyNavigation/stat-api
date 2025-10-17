from typing import Optional


def _validated_limit(limit: Optional[int]) -> Optional[int]:
    if limit is None:
        return None
    if limit <= 0:
        return 0
    return limit
