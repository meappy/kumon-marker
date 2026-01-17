"""API endpoints for worksheet operations."""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends

from fastapi.responses import FileResponse

from app.models.schemas import (
    WorksheetSummary,
    GDriveFile,
    PageResult,
    HealthResponse,
)
from app.services.checker import validate_kumon_worksheet, validate_kumon_from_bytes, extract_sheet_info
from app.services.ocr import analyse_worksheet
from app.services.annotator import create_marked_pdf
from app.services.reporter import create_report
from app.services.gdrive import GDriveService
from app.services.queue import create_and_queue_job, is_queue_enabled
from app.core.config import settings, get_effective_setting
from app.core.session import User, get_current_user, get_user_data_dir, get_user_token_path

router = APIRouter()

# Semaphore to limit concurrent processing jobs
_job_semaphore: asyncio.Semaphore | None = None


def get_job_semaphore() -> asyncio.Semaphore:
    """Get or create the job semaphore."""
    global _job_semaphore
    if _job_semaphore is None:
        _job_semaphore = asyncio.Semaphore(settings.max_concurrent_jobs)
    return _job_semaphore


def get_data_dir(user: User) -> Path:
    """Get the data directory for the current user."""
    return get_user_data_dir(user.id)


def get_gdrive_service(user: User) -> GDriveService:
    """Get Google Drive service instance for the current user."""
    token_path = get_user_token_path(user.id)
    return GDriveService(token_path=token_path)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint (no auth required)."""
    return HealthResponse()


@router.get("/worksheets", response_model=list[WorksheetSummary])
async def list_worksheets(user: User = Depends(get_current_user)):
    """List all processed worksheets for the current user."""
    data_dir = get_data_dir(user)
    results_dir = data_dir / "results"
    marked_dir = data_dir / "marked"
    reports_dir = data_dir / "reports"

    if not results_dir.exists():
        return []

    summaries = []
    for json_path in sorted(results_dir.glob("*.json"), reverse=True):
        try:
            data = json.loads(json_path.read_text())
            results = [PageResult(**r) for r in data["results"]]

            total_q = sum(r.total_questions for r in results)
            total_e = sum(len(r.errors) for r in results)
            pct = (total_q - total_e) / total_q * 100 if total_q > 0 else 100
            grade = 'A' if pct >= 90 else 'B' if pct >= 70 else 'C' if pct >= 50 else 'D'

            # Get sheet ID range (e.g. "C26" or "C26-C28")
            sheet_ids = [r.sheet_id for r in results if r.sheet_id]
            if sheet_ids:
                # Strip a/b suffix and get unique base IDs
                bases = []
                for sid in sheet_ids:
                    base = sid.rstrip('ab') if sid and sid[-1] in 'ab' else sid
                    if base and base not in bases:
                        bases.append(base)
                sheet_id = f"{bases[0]}-{bases[-1]}" if len(bases) > 1 else bases[0] if bases else None
            else:
                sheet_id = None

            summaries.append(WorksheetSummary(
                id=json_path.stem,
                pdf_name=data["pdf_name"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                pages=len(results),
                total_questions=total_q,
                total_errors=total_e,
                score_percentage=pct,
                grade=grade,
                has_marked_pdf=(marked_dir / f"{json_path.stem}_marked.pdf").exists(),
                has_report=(reports_dir / f"{json_path.stem}_report.pdf").exists(),
                student_name=data.get("student_name"),
                sheet_id=sheet_id,
            ))
        except (json.JSONDecodeError, KeyError):
            continue

    return summaries


@router.get("/worksheets/{worksheet_id}")
async def get_worksheet(worksheet_id: str, user: User = Depends(get_current_user)):
    """Get worksheet analysis results."""
    results_path = get_data_dir(user) / "results" / f"{worksheet_id}.json"

    if not results_path.exists():
        raise HTTPException(status_code=404, detail="Worksheet not found")

    data = json.loads(results_path.read_text())
    return data


@router.get("/worksheets/{worksheet_id}/marked")
async def get_marked_pdf(
    worksheet_id: str,
    download: bool = False,
    user: User = Depends(get_current_user),
):
    """Get the marked PDF (inline for preview, or as download)."""
    marked_path = get_data_dir(user) / "marked" / f"{worksheet_id}_marked.pdf"

    if not marked_path.exists():
        raise HTTPException(status_code=404, detail="Marked PDF not found")

    return FileResponse(
        marked_path,
        media_type="application/pdf",
        filename=f"{worksheet_id}_marked.pdf",
        content_disposition_type="attachment" if download else "inline",
    )


@router.get("/worksheets/{worksheet_id}/report")
async def get_report_pdf(
    worksheet_id: str,
    download: bool = False,
    user: User = Depends(get_current_user),
):
    """Get the report PDF (inline for preview, or as download)."""
    report_path = get_data_dir(user) / "reports" / f"{worksheet_id}_report.pdf"

    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        report_path,
        media_type="application/pdf",
        filename=f"{worksheet_id}_report.pdf",
        content_disposition_type="attachment" if download else "inline",
    )


@router.post("/upload")
async def upload_worksheet(
    user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    validate: bool = True,
):
    """Upload a worksheet PDF for processing."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Save uploaded file to user's directory
    data_dir = get_data_dir(user)
    scans_dir = data_dir / "scans"
    scans_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = scans_dir / file.filename

    content = await file.read()
    pdf_path.write_bytes(content)

    # Validate if requested
    if validate:
        validation = validate_kumon_worksheet(pdf_path)
        if not validation.is_kumon:
            pdf_path.unlink()  # Remove invalid file
            raise HTTPException(status_code=400, detail="Not a valid Kumon worksheet")

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "id": pdf_path.stem,
    }


@router.post("/worksheets/{worksheet_id}/process")
async def process_worksheet(
    worksheet_id: str,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    student_name: str | None = None,
):
    """Process a worksheet (run OCR and generate outputs)."""
    data_dir = get_data_dir(user)
    scans_dir = data_dir / "scans"
    pdf_path = scans_dir / f"{worksheet_id}.pdf"

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Worksheet PDF not found")

    # Use RabbitMQ queue if enabled, otherwise fall back to in-process background task
    if is_queue_enabled():
        try:
            job = create_and_queue_job(worksheet_id, user.id, student_name=student_name)
            return {
                "message": "Job queued",
                "id": worksheet_id,
                "job_id": job.id,
                "queued": True,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to queue job: {e}")
    else:
        # Fall back to in-process background task with semaphore
        background_tasks.add_task(
            _process_worksheet_task,
            worksheet_id,
            pdf_path,
            data_dir,
            student_name,
        )
        return {"message": "Processing started", "id": worksheet_id, "queued": False}


async def _process_worksheet_task(
    worksheet_id: str, pdf_path: Path, data_dir: Path, student_name: str | None = None
):
    """Background task to process a worksheet (with concurrency limit)."""
    semaphore = get_job_semaphore()
    async with semaphore:
        await _do_process_worksheet(worksheet_id, pdf_path, data_dir, student_name)


async def _do_process_worksheet(
    worksheet_id: str, pdf_path: Path, data_dir: Path, student_name: str | None = None
):
    """Actual worksheet processing logic."""
    try:
        # Validate and get sheet info
        validation = validate_kumon_worksheet(pdf_path)
        prefix, base_num = extract_sheet_info(
            validation.sheet_id if validation.is_kumon else None
        )

        # Extract student name using vision model only if not provided
        if student_name is None:
            try:
                from app.services.ocr import extract_name_with_vision, pdf_page_to_image
                image_bytes = pdf_page_to_image(pdf_path, 0)
                student_name = extract_name_with_vision(image_bytes)
            except Exception as e:
                print(f"Name extraction error: {e}")

        # Analyse with vision model
        results = analyse_worksheet(
            pdf_path,
            sheet_prefix=prefix,
            base_num=base_num,
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

        # Generate marked PDF
        marked_dir = data_dir / "marked"
        marked_dir.mkdir(parents=True, exist_ok=True)
        marked_path = marked_dir / f"{worksheet_id}_marked.pdf"
        create_marked_pdf(pdf_path, marked_path, results)

        # Generate report with student name
        reports_dir = data_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / f"{worksheet_id}_report.pdf"
        create_report(report_path, results, pdf_path.name, student_name)

    except Exception as e:
        print(f"Error processing worksheet {worksheet_id}: {e}")


def get_gdrive_cache_path(user: User) -> Path:
    """Get the path to the Google Drive files cache for a user."""
    cache_dir = get_data_dir(user) / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "gdrive_files.json"


def load_gdrive_cache(user: User) -> dict | None:
    """Load cached Google Drive file list for a user."""
    cache_path = get_gdrive_cache_path(user)
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except (json.JSONDecodeError, IOError):
            return None
    return None


def save_gdrive_cache(user: User, files: list[GDriveFile], scanned_at: str):
    """Save Google Drive file list to cache for a user."""
    cache_path = get_gdrive_cache_path(user)
    cache_data = {
        "scanned_at": scanned_at,
        "files": [f.model_dump() for f in files],
    }
    cache_path.write_text(json.dumps(cache_data, indent=2, default=str))


@router.get("/gdrive/files")
async def list_gdrive_files(refresh: bool = False, user: User = Depends(get_current_user)):
    """List PDF files in Google Drive folder for the current user."""
    try:
        # Check cache first (unless refresh requested)
        if not refresh:
            cache = load_gdrive_cache(user)
            if cache:
                return {
                    "scanned_at": cache["scanned_at"],
                    "files": cache["files"],
                }

        # Check if user has Google token
        token_path = get_user_token_path(user.id)
        if not token_path.exists():
            raise HTTPException(status_code=400, detail="Google Drive not connected")

        # Scan Google Drive
        service = get_gdrive_service(user)
        folder = get_effective_setting("gdrive_folder", "From_BrotherDevice")
        files = service.list_pdfs(folder)

        # Validate each file to check if it's a Kumon worksheet
        validated_files = []
        for f in files:
            try:
                pdf_bytes = service.download_file_bytes(f.id)
                validation = validate_kumon_from_bytes(pdf_bytes)
                validated_files.append(GDriveFile(
                    id=f.id,
                    name=f.name,
                    created_time=f.created_time,
                    size=f.size,
                    is_kumon=validation.is_kumon,
                    sheet_id=validation.sheet_id,
                    student_name=validation.student_name,
                ))
            except Exception as e:
                print(f"Error validating {f.name}: {e}")
                # Include file but mark as unknown
                validated_files.append(GDriveFile(
                    id=f.id,
                    name=f.name,
                    created_time=f.created_time,
                    size=f.size,
                    is_kumon=None,
                ))

        # Save to cache
        scanned_at = datetime.now().isoformat()
        save_gdrive_cache(user, validated_files, scanned_at)

        return {
            "scanned_at": scanned_at,
            "files": [f.model_dump() for f in validated_files],
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Drive error: {e}")


@router.post("/gdrive/sync/{file_id}")
async def sync_from_gdrive(file_id: str, filename: str, user: User = Depends(get_current_user)):
    """Download a file from Google Drive for the current user."""
    try:
        service = get_gdrive_service(user)
        data_dir = get_data_dir(user)

        scans_dir = data_dir / "scans"
        scans_dir.mkdir(parents=True, exist_ok=True)
        dest_path = scans_dir / filename

        if dest_path.exists():
            return {"message": "File already exists", "filename": filename, "id": dest_path.stem}

        service.download_file(file_id, dest_path)
        return {"message": "File downloaded", "filename": filename, "id": dest_path.stem}

    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {e}")


@router.post("/worksheets/{worksheet_id}/regenerate-report")
async def regenerate_report(worksheet_id: str, user: User = Depends(get_current_user)):
    """Regenerate report from cached results."""
    data_dir = get_data_dir(user)
    results_path = data_dir / "results" / f"{worksheet_id}.json"

    if not results_path.exists():
        raise HTTPException(status_code=404, detail="Results not found")

    data = json.loads(results_path.read_text())
    results = [PageResult(**r) for r in data["results"]]

    reports_dir = data_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{worksheet_id}_report.pdf"

    create_report(report_path, results, data["pdf_name"], data.get("student_name"))

    return {"message": "Report regenerated", "id": worksheet_id}


@router.delete("/worksheets/{worksheet_id}")
async def delete_worksheet(worksheet_id: str, user: User = Depends(get_current_user)):
    """Delete a worksheet and all its associated files."""
    data_dir = get_data_dir(user)

    # Files to delete
    files_to_delete = [
        data_dir / "results" / f"{worksheet_id}.json",
        data_dir / "marked" / f"{worksheet_id}_marked.pdf",
        data_dir / "reports" / f"{worksheet_id}_report.pdf",
        data_dir / "scans" / f"{worksheet_id}.pdf",
    ]

    deleted_count = 0
    for file_path in files_to_delete:
        if file_path.exists():
            file_path.unlink()
            deleted_count += 1

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Worksheet not found")

    return {"message": "Worksheet deleted", "id": worksheet_id, "files_deleted": deleted_count}


@router.delete("/worksheets")
async def delete_all_worksheets(user: User = Depends(get_current_user)):
    """Delete all worksheets and their associated files for the current user."""
    data_dir = get_data_dir(user)

    # Directories to clear
    dirs_to_clear = [
        data_dir / "results",
        data_dir / "marked",
        data_dir / "reports",
        data_dir / "scans",
    ]

    deleted_count = 0
    for dir_path in dirs_to_clear:
        if dir_path.exists():
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    file_path.unlink()
                    deleted_count += 1

    return {"message": "All worksheets deleted", "files_deleted": deleted_count}
