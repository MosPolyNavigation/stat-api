from fastapi import Request

from app.jobs.manager import JobManager


def get_job_manager(request: Request) -> JobManager:
    """Dependency: возвращает JobManager из lifespan state."""
    return request.state.job_manager
