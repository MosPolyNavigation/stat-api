import strawberry
from strawberry.extensions import QueryDepthLimiter
from .event_mutation import EventDictionaryMutation
from .mutation import Mutation as BaseMutation
from .query import Query


@strawberry.type
class Mutation(EventDictionaryMutation, BaseMutation):
    pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[QueryDepthLimiter(max_depth=4)]
)
