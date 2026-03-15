"""API endpoints for worksheet operations."""

import asyncio
import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends

from fastapi.responses import FileResponse, Response

from app.models.schemas import (
    WorksheetSummary,
    GDriveFile,
    PageResult,
    HealthResponse,
    UploadedFile,
)
from app.services.checker import (
    validate_kumon_worksheet,
    validate_kumon_worksheet_from_bytes,
    extract_sheet_info,
)
from app.services.ocr import analyse_worksheet
from app.services.annotator import create_marked_pdf
from app.services.reporter import create_report
from app.services.gdrive import GDriveService, update_gdrive_cache_sheet_id
from app.services.queue import create_and_queue_job, is_queue_enabled
from app.core.config import settings, get_effective_setting
from app.core.session import (
    User,
    get_current_user,
    get_user_data_dir,
    get_user_token_path,
)

router = APIRouter()

# Semaphore to limit concurrent processing jobs
_job_semaphore: asyncio.Semaphore | None = None

# In-memory scan state per user: {user_id: {"status": "scanning"|"idle", "scanned_at": str|None}}
_scan_state: dict[str, dict] = {}
_scan_state_lock = threading.Lock()


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
            grade = (
                "A" if pct >= 90 else "B" if pct >= 70 else "C" if pct >= 50 else "D"
            )

            # Get sheet ID range (e.g. "C26" or "C26-C28")
            sheet_ids = [r.sheet_id for r in results if r.sheet_id]
            if sheet_ids:
                # Strip a/b suffix and get unique base IDs
                bases = []
                for sid in sheet_ids:
                    base = sid.rstrip("ab") if sid and sid[-1] in "ab" else sid
                    if base and base not in bases:
                        bases.append(base)
                sheet_id = (
                    f"{bases[0]}-{bases[-1]}"
                    if len(bases) > 1
                    else bases[0]
                    if bases
                    else None
                )
            else:
                sheet_id = None

            summaries.append(
                WorksheetSummary(
                    id=json_path.stem,
                    pdf_name=data["pdf_name"],
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    pages=len(results),
                    total_questions=total_q,
                    total_errors=total_e,
                    score_percentage=pct,
                    grade=grade,
                    has_marked_pdf=(
                        marked_dir / f"{json_path.stem}_marked.pdf"
                    ).exists(),
                    has_report=(reports_dir / f"{json_path.stem}_report.pdf").exists(),
                    student_name=data.get("student_name"),
                    sheet_id=sheet_id,
                )
            )
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
        subject = validation.subject or "maths"

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

        # Update GDrive cache with corrected sheet_id from vision model
        if validation.sheet_id:
            update_gdrive_cache_sheet_id(data_dir, worksheet_id, validation.sheet_id)

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


def _scan_gdrive_files_sync(
    user: User, force_refresh: bool = False
) -> tuple[list[GDriveFile], str]:
    """Synchronous helper to scan Google Drive files.

    Run in a thread pool to avoid blocking the event loop.
    Uses cached validation results to avoid re-downloading already validated files,
    unless force_refresh is True.
    """
    service = get_gdrive_service(user)
    folder = get_effective_setting("gdrive_folder", "From_BrotherDevice")
    files = service.list_pdfs(folder)

    # Load existing cache to reuse validation results (unless force_refresh)
    cached_files_by_id = {}
    if not force_refresh:
        existing_cache = load_gdrive_cache(user)
        if existing_cache and "files" in existing_cache:
            for cached in existing_cache["files"]:
                if isinstance(cached, dict) and cached.get("id"):
                    cached_files_by_id[cached["id"]] = cached

    # Validate each file, reusing cache where possible
    validated_files = []
    for f in files:
        # Check if we have a cached validation for this file (skip if force_refresh)
        cached = cached_files_by_id.get(f.id)
        if cached and cached.get("is_kumon") is not None:
            # Reuse cached validation
            validated_files.append(
                GDriveFile(
                    id=f.id,
                    name=f.name,
                    created_time=f.created_time,
                    size=f.size,
                    is_kumon=cached.get("is_kumon"),
                    sheet_id=cached.get("sheet_id"),
                    student_name=cached.get("student_name"),
                )
            )
            continue

        # Try to extract sheet_id from filename (e.g., "D166a - Reduction.pdf")
        filename_sheet_id = None
        filename_match = re.match(r"^([A-Z]\d{1,3}[ABab]?)", f.name.upper())
        if filename_match:
            filename_sheet_id = filename_match.group(1)
            print(f"Extracted sheet_id from filename '{f.name}': {filename_sheet_id}")
            # Filename has valid Kumon pattern - assume it's Kumon (no download needed)
            validated_files.append(
                GDriveFile(
                    id=f.id,
                    name=f.name,
                    created_time=f.created_time,
                    size=f.size,
                    is_kumon=True,
                    sheet_id=filename_sheet_id,
                    student_name=None,
                )
            )
            continue

        # No sheet_id in filename - extract from PDF text layer (fast, no OCR)
        try:
            import fitz

            pdf_bytes = service.download_file_bytes(f.id)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = doc[0].get_text().upper() if doc.page_count > 0 else ""
            doc.close()

            # Check for "KUMON" with common OCR misreadings (O→Q, O→0, etc.)
            is_kumon = bool(re.search(r"KUM[OQ0][NM]", text))
            print(
                f"Text check for '{f.name}': {'KUMON found' if is_kumon else 'not Kumon'}"
            )

            # Extract sheet_id from text layer (e.g., "D166A", "B 161", "C26 a")
            text_sheet_id = None
            student_name = None
            if is_kumon:
                # Look for sheet ID pattern: Letter + digits + optional a/b
                # Handle spaces that might be in scanned text
                sheet_match = re.search(r"\b([A-Z])\s*(\d{1,3})\s*([AB])?\b", text)
                if sheet_match:
                    letter = sheet_match.group(1)
                    number = sheet_match.group(2)
                    suffix = sheet_match.group(3) or ""
                    text_sheet_id = f"{letter}{number}{suffix}"
                    print(f"Extracted sheet_id from text layer: {text_sheet_id}")

            # If text layer failed and LLM validation is configured, use vision
            if not is_kumon and get_effective_setting("validation_method") == "llm":
                print(
                    f"Text layer empty/failed for '{f.name}', falling back to LLM vision"
                )
                try:
                    validation = validate_kumon_worksheet_from_bytes(pdf_bytes)
                    is_kumon = validation.is_kumon
                    text_sheet_id = validation.sheet_id
                    student_name = validation.student_name
                    print(
                        f"LLM vision result for '{f.name}': is_kumon={is_kumon}, sheet_id={text_sheet_id}"
                    )
                except Exception as vision_err:
                    print(f"LLM vision fallback failed for '{f.name}': {vision_err}")

            validated_files.append(
                GDriveFile(
                    id=f.id,
                    name=f.name,
                    created_time=f.created_time,
                    size=f.size,
                    is_kumon=is_kumon,
                    sheet_id=text_sheet_id,
                    student_name=student_name,
                )
            )
        except Exception as e:
            print(f"Error checking {f.name}: {e}")
            # Include file but mark as unknown
            validated_files.append(
                GDriveFile(
                    id=f.id,
                    name=f.name,
                    created_time=f.created_time,
                    size=f.size,
                    is_kumon=None,
                )
            )

    scanned_at = datetime.now().isoformat()
    return validated_files, scanned_at


def _get_scan_state(user_id: str) -> dict:
    """Get the scan state for a user, initialising if needed."""
    with _scan_state_lock:
        if user_id not in _scan_state:
            _scan_state[user_id] = {"status": "idle", "scanned_at": None}
        return _scan_state[user_id]


def _run_background_scan(user: User) -> None:
    """Run a Google Drive scan in a background thread and update state when done."""
    state = _get_scan_state(user.id)
    try:
        validated_files, scanned_at = _scan_gdrive_files_sync(user, force_refresh=True)
        save_gdrive_cache(user, validated_files, scanned_at)
        with _scan_state_lock:
            state["scanned_at"] = scanned_at
    except Exception as e:
        print(f"Background scan error for user {user.id}: {e}")
    finally:
        with _scan_state_lock:
            state["status"] = "idle"


@router.post("/gdrive/scan")
async def start_gdrive_scan(user: User = Depends(get_current_user)):
    """Start a background Google Drive scan. Returns immediately."""
    # Check if user has Google token
    token_path = get_user_token_path(user.id)
    if not token_path.exists():
        raise HTTPException(status_code=400, detail="Google Drive not connected")

    state = _get_scan_state(user.id)
    with _scan_state_lock:
        if state["status"] == "scanning":
            # Already scanning, just return current status
            return {"status": "scanning"}
        state["status"] = "scanning"

    # Run in a background thread so the endpoint returns immediately
    thread = threading.Thread(target=_run_background_scan, args=(user,), daemon=True)
    thread.start()

    return {"status": "scanning"}


@router.get("/gdrive/scan/status")
async def get_gdrive_scan_status(user: User = Depends(get_current_user)):
    """Get the current scan status for the user."""
    state = _get_scan_state(user.id)
    with _scan_state_lock:
        result = {"status": state["status"], "scanned_at": state["scanned_at"]}

    # If idle and we have a cache, include the cached scanned_at
    if result["scanned_at"] is None:
        cache = load_gdrive_cache(user)
        if cache:
            result["scanned_at"] = cache.get("scanned_at")

    return result


@router.get("/gdrive/files")
async def list_gdrive_files(
    refresh: bool = False,
    user: User = Depends(get_current_user),
):
    """List cached PDF files from Google Drive.

    Returns cached files. Use POST /gdrive/scan to trigger a refresh.
    The refresh parameter is kept for backward compatibility but now
    triggers a background scan and returns cached data.
    """
    try:
        # If refresh requested, start a background scan (non-blocking)
        if refresh:
            token_path = get_user_token_path(user.id)
            if not token_path.exists():
                raise HTTPException(
                    status_code=400, detail="Google Drive not connected"
                )

            state = _get_scan_state(user.id)
            with _scan_state_lock:
                if state["status"] != "scanning":
                    state["status"] = "scanning"
                    thread = threading.Thread(
                        target=_run_background_scan, args=(user,), daemon=True
                    )
                    thread.start()

        # Always return cached data
        cache = load_gdrive_cache(user)
        if cache:
            return {
                "scanned_at": cache["scanned_at"],
                "files": cache["files"],
            }

        # No cache yet — if not scanning, start a scan
        if not refresh:
            token_path = get_user_token_path(user.id)
            if not token_path.exists():
                raise HTTPException(
                    status_code=400, detail="Google Drive not connected"
                )

        return {
            "scanned_at": None,
            "files": [],
        }
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Drive error: {e}")


@router.post("/gdrive/sync/{file_id}")
async def sync_from_gdrive(
    file_id: str, filename: str, user: User = Depends(get_current_user)
):
    """Download a file from Google Drive for the current user."""
    try:
        service = get_gdrive_service(user)
        data_dir = get_data_dir(user)

        scans_dir = data_dir / "scans"
        scans_dir.mkdir(parents=True, exist_ok=True)
        dest_path = scans_dir / filename

        if dest_path.exists():
            return {
                "message": "File already exists",
                "filename": filename,
                "id": dest_path.stem,
            }

        service.download_file(file_id, dest_path)
        return {
            "message": "File downloaded",
            "filename": filename,
            "id": dest_path.stem,
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {e}")


@router.get("/gdrive/preview/{file_id}")
async def preview_gdrive_file(file_id: str, user: User = Depends(get_current_user)):
    """Stream a PDF from Google Drive for preview."""
    try:
        service = get_gdrive_service(user)
        pdf_bytes = service.download_file_bytes(file_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview error: {e}")


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

    return {
        "message": "Worksheet deleted",
        "id": worksheet_id,
        "files_deleted": deleted_count,
    }


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


@router.get("/uploads", response_model=list[UploadedFile])
async def list_uploaded_files(user: User = Depends(get_current_user)):
    """List all uploaded files in the scans directory."""
    data_dir = get_data_dir(user)
    scans_dir = data_dir / "scans"
    results_dir = data_dir / "results"

    if not scans_dir.exists():
        return []

    uploaded_files = []
    for pdf_path in sorted(
        scans_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True
    ):
        stat = pdf_path.stat()
        file_id = pdf_path.stem

        # Check if this file has been processed (has results)
        is_processed = (results_dir / f"{file_id}.json").exists()

        # Get validation info if available
        sheet_id = None
        student_name = None
        is_kumon = None

        # Try to get cached validation info from results
        if is_processed:
            try:
                result_data = json.loads((results_dir / f"{file_id}.json").read_text())
                student_name = result_data.get("student_name")
                # Get sheet ID from first result
                if result_data.get("results"):
                    sheet_id = result_data["results"][0].get("sheet_id")
                is_kumon = True
            except (json.JSONDecodeError, KeyError):
                pass

        uploaded_files.append(
            UploadedFile(
                id=file_id,
                filename=pdf_path.name,
                uploaded_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                size=stat.st_size,
                is_kumon=is_kumon,
                sheet_id=sheet_id,
                student_name=student_name,
                is_processed=is_processed,
            )
        )

    return uploaded_files


@router.get("/uploads/{file_id}")
async def download_uploaded_file(
    file_id: str,
    download: bool = False,
    user: User = Depends(get_current_user),
):
    """Download an uploaded file (original PDF)."""
    data_dir = get_data_dir(user)
    pdf_path = data_dir / "scans" / f"{file_id}.pdf"

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{file_id}.pdf",
        content_disposition_type="attachment" if download else "inline",
    )


@router.delete("/uploads/{file_id}")
async def delete_uploaded_file(file_id: str, user: User = Depends(get_current_user)):
    """Delete an uploaded file (but keep any processed results)."""
    data_dir = get_data_dir(user)
    pdf_path = data_dir / "scans" / f"{file_id}.pdf"

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    pdf_path.unlink()
    return {"message": "File deleted", "id": file_id}
