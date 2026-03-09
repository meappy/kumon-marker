"""RabbitMQ worker for processing worksheet jobs."""

import json
import signal
import sys
from datetime import datetime, timezone

import pika

from app.core.config import settings
from app.core.session import get_user_data_dir
from app.models.job import JobStatus, init_db
from app.services.queue import QUEUE_NAME, update_job_status
from app.services.checker import validate_kumon_worksheet, extract_sheet_info
from app.services.gdrive import update_gdrive_cache_sheet_id
from app.services.ocr import (
    analyse_worksheet,
    extract_name_with_vision,
    pdf_page_to_image,
)
from app.services.annotator import create_marked_pdf
from app.services.reporter import create_report


# Global flags for graceful shutdown
_shutdown = False
_processing = False  # Track if a job is currently being processed


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global _shutdown
    print(f"Received signal {signum}, initiating graceful shutdown...")
    _shutdown = True
    if _processing:
        print("Waiting for current job to complete before shutting down...")
    else:
        print("No job in progress, shutting down immediately.")


def process_worksheet(
    job_id: str, worksheet_id: str, user_id: str, student_name: str | None = None
) -> None:
    """Process a worksheet job.

    Args:
        job_id: The job ID.
        worksheet_id: The worksheet to process.
        user_id: The user who submitted the job.
        student_name: Optional pre-extracted student name.
    """
    print(f"Processing job {job_id}: worksheet {worksheet_id} for user {user_id}")

    # Update status to processing
    update_job_status(job_id, JobStatus.PROCESSING, progress=0)

    try:
        # Get user's data directory
        data_dir = get_user_data_dir(user_id)
        pdf_path = data_dir / "scans" / f"{worksheet_id}.pdf"

        if not pdf_path.exists():
            raise FileNotFoundError(f"Worksheet PDF not found: {pdf_path}")

        # Update progress - starting validation
        update_job_status(job_id, JobStatus.PROCESSING, progress=10)

        # Validate and get sheet info
        validation = validate_kumon_worksheet(pdf_path)
        prefix, base_num = extract_sheet_info(
            validation.sheet_id if validation.is_kumon else None
        )
        subject = validation.subject or "maths"

        # Update progress - extracting name
        update_job_status(job_id, JobStatus.PROCESSING, progress=20)

        # Extract student name using vision model only if not provided
        if student_name is None:
            try:
                image_bytes = pdf_page_to_image(pdf_path, 0)
                student_name = extract_name_with_vision(image_bytes)
            except Exception as e:
                print(f"Name extraction error for job {job_id}: {e}")
        else:
            print(f"Using pre-extracted student name: {student_name}")

        # Update progress - starting OCR analysis
        update_job_status(job_id, JobStatus.PROCESSING, progress=30)

        # Progress callback for per-page updates
        # OCR phase spans 30% to 70% (40% total)
        def ocr_progress(current_page: int, total_pages: int):
            progress = 30 + int((current_page / total_pages) * 40)
            update_job_status(job_id, JobStatus.PROCESSING, progress=progress)

        # Analyse with vision model
        results = analyse_worksheet(
            pdf_path,
            sheet_prefix=prefix,
            base_num=base_num,
            progress_callback=ocr_progress,
            subject=subject,
        )

        # Save results
        results_dir = data_dir / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        results_path = results_dir / f"{worksheet_id}.json"

        result_data = {
            "pdf_name": pdf_path.name,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "student_name": student_name,
            "results": [r.model_dump() for r in results],
        }
        results_path.write_text(json.dumps(result_data, indent=2))

        # Update progress - generating marked PDF
        update_job_status(job_id, JobStatus.PROCESSING, progress=80)

        # Generate marked PDF
        marked_dir = data_dir / "marked"
        marked_dir.mkdir(parents=True, exist_ok=True)
        marked_path = marked_dir / f"{worksheet_id}_marked.pdf"
        create_marked_pdf(pdf_path, marked_path, results)

        # Update progress - generating report
        update_job_status(job_id, JobStatus.PROCESSING, progress=90)

        # Generate report
        reports_dir = data_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / f"{worksheet_id}_report.pdf"
        create_report(report_path, results, pdf_path.name, student_name)

        # Update GDrive cache with corrected sheet_id from vision model
        if validation.sheet_id:
            update_gdrive_cache_sheet_id(data_dir, worksheet_id, validation.sheet_id)

        # Mark as completed
        update_job_status(job_id, JobStatus.COMPLETED, progress=100)
        print(f"Job {job_id} completed successfully")

    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        update_job_status(job_id, JobStatus.FAILED, error=str(e))
        raise


def on_message(channel, method, properties, body):
    """Handle incoming messages from the queue."""
    global _shutdown, _processing

    if _shutdown:
        # Reject message and re-queue it so another worker can process it
        print("Shutdown in progress, re-queuing message...")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        return

    try:
        message = json.loads(body)
        job_id = message["job_id"]
        worksheet_id = message["worksheet_id"]
        user_id = message["user_id"]
        action = message.get("action", "process")
        student_name = message.get("student_name")

        if action != "process":
            print(f"Unknown action: {action}")
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Mark as processing to prevent premature shutdown
        _processing = True
        try:
            process_worksheet(job_id, worksheet_id, user_id, student_name)
            try:
                channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as ack_error:
                # Job completed but ack failed (connection lost) - this is OK
                print(f"Warning: Job completed but ack failed: {ack_error}")
        finally:
            _processing = False

    except Exception as e:
        print(f"Error processing message: {e}")
        _processing = False
        # Acknowledge to prevent infinite retries for bad messages
        try:
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            pass  # Connection already lost


def main():
    """Main worker entry point."""
    global _shutdown

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if not settings.rabbitmq_url:
        print("ERROR: RABBITMQ_URL not configured")
        sys.exit(1)

    if not settings.database_url:
        print("ERROR: DATABASE_URL not configured")
        sys.exit(1)

    # Initialise database
    print("Initialising database...")
    init_db()

    print(f"Connecting to RabbitMQ at {settings.rabbitmq_url.split('@')[-1]}...")
    params = pika.URLParameters(settings.rabbitmq_url)
    # Set heartbeat to keep connection alive during long processing
    params.heartbeat = 600  # 10 minutes
    params.blocked_connection_timeout = 300  # 5 minutes
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Set prefetch count to 1 (process one message at a time)
    channel.basic_qos(prefetch_count=1)

    # Start consuming
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)

    print(f"Worker started, waiting for messages on queue '{QUEUE_NAME}'...")

    try:
        while not _shutdown or _processing:
            # Process events with a timeout to allow checking shutdown flag
            # Continue running if processing a job, even after shutdown signal
            connection.process_data_events(time_limit=1)
            if _shutdown and _processing:
                # Still processing, keep the connection alive
                pass
            elif _shutdown and not _processing:
                # Shutdown requested and no job in progress
                break
    except KeyboardInterrupt:
        print("Worker interrupted")
        # Wait for current job to complete if interrupted
        if _processing:
            print("Waiting for current job to complete...")
            while _processing:
                try:
                    connection.process_data_events(time_limit=1)
                except Exception:
                    break
    finally:
        print("Closing connection...")
        try:
            channel.close()
            connection.close()
        except Exception:
            pass

    print("Worker shut down gracefully")


if __name__ == "__main__":
    main()
