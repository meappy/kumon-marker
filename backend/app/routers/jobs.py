"""API endpoints for job management."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.session import User, get_current_user
from app.services.queue import (
    get_job,
    get_user_jobs,
    get_active_jobs,
    is_queue_enabled,
    cancel_job,
)


router = APIRouter()


class JobResponse(BaseModel):
    """Job status response."""
    id: str
    worksheet_id: str
    user_id: str
    status: str
    progress: int
    error: str | None
    created_at: str | None
    started_at: str | None
    completed_at: str | None


class JobsResponse(BaseModel):
    """Multiple jobs response."""
    jobs: list[JobResponse]
    queue_enabled: bool


class QueueStatusResponse(BaseModel):
    """Queue status response."""
    enabled: bool
    active_count: int
    jobs: list[JobResponse]


@router.get("/jobs", response_model=JobsResponse)
async def list_jobs(
    active_only: bool = False,
    limit: int = 50,
    user: User = Depends(get_current_user),
):
    """List jobs for the current user.

    Args:
        active_only: If True, only return queued and processing jobs.
        limit: Maximum number of jobs to return.
    """
    if not is_queue_enabled():
        return JobsResponse(jobs=[], queue_enabled=False)

    try:
        if active_only:
            jobs = get_active_jobs(user.id)
        else:
            jobs = get_user_jobs(user.id, limit=limit)

        return JobsResponse(
            jobs=[JobResponse(**job.to_dict()) for job in jobs],
            queue_enabled=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {e}")


@router.get("/jobs/status", response_model=QueueStatusResponse)
async def get_queue_status(user: User = Depends(get_current_user)):
    """Get queue status for the current user.

    Returns the number of active jobs and their details.
    """
    if not is_queue_enabled():
        return QueueStatusResponse(enabled=False, active_count=0, jobs=[])

    try:
        active_jobs = get_active_jobs(user.id)
        return QueueStatusResponse(
            enabled=True,
            active_count=len(active_jobs),
            jobs=[JobResponse(**job.to_dict()) for job in active_jobs],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch queue status: {e}")


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str, user: User = Depends(get_current_user)):
    """Get status of a specific job.

    Args:
        job_id: The job ID to look up.
    """
    if not is_queue_enabled():
        raise HTTPException(status_code=503, detail="Job queue not enabled")

    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Ensure user owns this job
    if job.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return JobResponse(**job.to_dict())


@router.delete("/jobs/{job_id}", response_model=JobResponse)
async def cancel_job_endpoint(job_id: str, user: User = Depends(get_current_user)):
    """Cancel a job.

    Only queued or processing jobs can be cancelled.

    Args:
        job_id: The job ID to cancel.
    """
    if not is_queue_enabled():
        raise HTTPException(status_code=503, detail="Job queue not enabled")

    job = cancel_job(job_id, user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")

    return JobResponse(**job.to_dict())
