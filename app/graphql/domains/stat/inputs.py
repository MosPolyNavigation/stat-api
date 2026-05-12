from datetime import date
import strawberry


@strawberry.input
class EndpointStatisticsByDateInput:
    start: date
    end: date


@strawberry.input
class EndpointStatisticsByMonthInput:
    start: str
    end: str


@strawberry.input
class EndpointStatisticsByYearInput:
    start: str
    end: str
