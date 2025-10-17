import strawberry
from strawberry.extensions import QueryDepthLimiter
from .query import Query

schema = strawberry.Schema(
    query=Query,
    extensions=[QueryDepthLimiter(max_depth=4)]
)
