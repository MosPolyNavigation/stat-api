from typing import Tuple
from graphql import GraphQLError
from sqlalchemy.orm import Session
from strawberry import Info
from app.models import User

STATS_GOAL_NAME = "stats"
VIEW_RIGHT_NAME = "view"


def _get_session_and_user(info: Info) -> Tuple[Session, User]:
    try:
        session: Session = info.context["db"]
        current_user: User = info.context["current_user"]
    except KeyError as exc:
        raise GraphQLError("GraphQL context is missing required values") from exc
    return session, current_user


def ensure_stats_view_permission(info: Info) -> Session:
    session, current_user = _get_session_and_user(info)
    if not current_user.is_capable(session, STATS_GOAL_NAME, VIEW_RIGHT_NAME):
        raise GraphQLError("Недостаточно прав для просмотра статистики")
    return session
