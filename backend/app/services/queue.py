"""RabbitMQ queue publisher service."""

import json
from datetime import datetime, timezone

import pika

from app.core.config import settings
from app.models.job import Job, JobStatus, get_db, init_db


QUEUE_NAME = "worksheet_jobs"


def get_connection():
    """Get a RabbitMQ connection."""
    if not settings.rabbitmq_url:
        raise RuntimeError("RabbitMQ not configured (RABBITMQ_URL not set)")

    params = pika.URLParameters(settings.rabbitmq_url)
    return pika.BlockingConnection(params)


def ensure_queue(channel):
    """Ensure the job queue exists."""
    channel.queue_declare(queue=QUEUE_NAME, durable=True)


def publish_job(
    job_id: str, worksheet_id: str, user_id: str, student_name: str | None = None
) -> None:
    """Publish a job to the RabbitMQ queue.

    Args:
        job_id: Unique job identifier.
        worksheet_id: The worksheet to process.
        user_id: The user who submitted the job.
        student_name: Optional pre-extracted student name.
    """
    connection = get_connection()
    try:
        channel = connection.channel()
        ensure_queue(channel)

        message = json.dumps({
            "job_id": job_id,
            "worksheet_id": worksheet_id,
            "user_id": user_id,
            "action": "process",
            "student_name": student_name,
        })

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                content_type="application/json",
            ),
        )
    finally:
        connection.close()


def create_and_queue_job(
    worksheet_id: str, user_id: str, student_name: str | None = None
) -> Job:
    """Create a job record and publish it to the queue.

    Args:
        worksheet_id: The worksheet to process.
        user_id: The user who submitted the job.
        student_name: Optional pre-extracted student name.

    Returns:
        The created Job object.
    """
    # Initialise database tables if needed
    init_db()

    # Create job record
    db = get_db()
    try:
        job = Job(
            worksheet_id=worksheet_id,
            user_id=user_id,
            status=JobStatus.QUEUED.value,
            progress=0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Publish to RabbitMQ
        try:
            publish_job(job.id, worksheet_id, user_id, student_name)
        except Exception as e:
            # If publishing fails, update job status to failed
            job.status = JobStatus.FAILED.value
            job.error = f"Failed to queue job: {e}"
            db.commit()
            raise

        return job
    finally:
        db.close()


def get_job(job_id: str) -> Job | None:
    """Get a job by ID.

    Args:
        job_id: The job ID.

    Returns:
        The Job object or None if not found.
    """
    db = get_db()
    try:
        return db.query(Job).filter(Job.id == job_id).first()
    finally:
        db.close()


def get_user_jobs(user_id: str, limit: int = 50) -> list[Job]:
    """Get jobs for a user.

    Args:
        user_id: The user ID.
        limit: Maximum number of jobs to return.

    Returns:
        List of Job objects.
    """
    db = get_db()
    try:
        return (
            db.query(Job)
            .filter(Job.user_id == user_id)
            .order_by(Job.created_at.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()


def get_active_jobs(user_id: str, include_recent: bool = True) -> list[Job]:
    """Get active (queued or processing) jobs for a user.

    Also includes recently completed/failed jobs (within last 60 seconds)
    so the frontend can see status transitions.

    Args:
        user_id: The user ID.
        include_recent: If True, include jobs completed in the last 60 seconds.

    Returns:
        List of Job objects.
    """
    from datetime import timedelta

    db = get_db()
    try:
        # Get active jobs (queued or processing)
        active = (
            db.query(Job)
            .filter(
                Job.user_id == user_id,
                Job.status.in_([JobStatus.QUEUED.value, JobStatus.PROCESSING.value]),
            )
            .all()
        )

        # Also get recently completed/failed jobs so frontend sees the transition
        if include_recent:
            cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
            recent = (
                db.query(Job)
                .filter(
                    Job.user_id == user_id,
                    Job.status.in_([JobStatus.COMPLETED.value, JobStatus.FAILED.value]),
                    Job.completed_at >= cutoff,
                )
                .all()
            )
            active.extend(recent)

        # Sort by created_at
        active.sort(key=lambda j: j.created_at)
        return active
    finally:
        db.close()


def update_job_status(
    job_id: str,
    status: JobStatus,
    progress: int | None = None,
    error: str | None = None,
) -> Job | None:
    """Update a job's status.

    Args:
        job_id: The job ID.
        status: The new status.
        progress: Optional progress percentage (0-100).
        error: Optional error message.

    Returns:
        The updated Job object or None if not found.
    """
    db = get_db()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        job.status = status.value

        if progress is not None:
            job.progress = progress

        if error is not None:
            job.error = error

        if status == JobStatus.PROCESSING and job.started_at is None:
            job.started_at = datetime.now(timezone.utc)

        if status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            job.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()


def cancel_job(job_id: str, user_id: str) -> Job | None:
    """Cancel a job.

    Only queued or processing jobs can be cancelled.
    User must own the job.

    Args:
        job_id: The job ID.
        user_id: The user ID (for authorization).

    Returns:
        The cancelled Job object or None if not found/not authorized.
    """
    db = get_db()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        # Check ownership
        if job.user_id != user_id:
            return None

        # Can only cancel queued or processing jobs
        if job.status not in (JobStatus.QUEUED.value, JobStatus.PROCESSING.value):
            return None

        job.status = JobStatus.CANCELLED.value
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()


def is_queue_enabled() -> bool:
    """Check if the job queue is enabled (RabbitMQ and PostgreSQL configured)."""
    return bool(settings.rabbitmq_url and settings.database_url)
