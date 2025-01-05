from datetime import datetime, timedelta
from app.state import AppState


def check_user(state: AppState, user_id) -> float:
    state.user_access.setdefault(user_id, datetime.now() - timedelta(seconds=1))
    delta = datetime.now() - state.user_access[user_id]
    state.user_access[user_id] = datetime.now()
    return delta.total_seconds()
