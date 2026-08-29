"""API endpoints for the Kumon Score Report card and printing."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from app.core.session import ViewContext, get_view_context, get_user_data_dir
from app.models.schemas import PrintRequest, ScoreEntry, ScoreLog
from app.services import scorecard
from app.services.printing import (
    PrintError,
    list_printers,
    print_pdf,
    printing_available,
)

router = APIRouter()


def _data_dir(context: ViewContext) -> Path:
    return get_user_data_dir(context.data_user_id)


def _require_write(context: ViewContext) -> None:
    if context.read_only:
        raise HTTPException(status_code=403, detail="This dashboard is read-only")


@router.get("/scorecard", response_model=list[ScoreLog])
async def get_scorecards(context: ViewContext = Depends(get_view_context)):
    """List every student's score rows."""
    students = scorecard.load_log(_data_dir(context))
    return [
        ScoreLog(student=name, entries=entries)
        for name, entries in sorted(students.items())
    ]


@router.get("/scorecard/{student}", response_model=ScoreLog)
async def get_scorecard(student: str, context: ViewContext = Depends(get_view_context)):
    """Get one student's score rows."""
    return scorecard.get_student_log(_data_dir(context), student)


@router.post("/scorecard/{student}/entries", response_model=ScoreEntry)
async def create_entry(
    student: str,
    entry: ScoreEntry,
    context: ViewContext = Depends(get_view_context),
):
    """Add a row by hand — for packets marked away from the app."""
    _require_write(context)
    return scorecard.add_entry(_data_dir(context), student, entry)


@router.patch("/scorecard/{student}/entries/{entry_id}", response_model=ScoreEntry)
async def patch_entry(
    student: str,
    entry_id: str,
    fields: dict,
    context: ViewContext = Depends(get_view_context),
):
    """Correct a row — handwritten times are the usual reason."""
    _require_write(context)
    allowed = {
        "date",
        "time_started",
        "time_finished",
        "time_used",
        "level",
        "sheet_no",
        "marks",
    }
    updates = {k: v for k, v in fields.items() if k in allowed}
    updated = scorecard.update_entry(_data_dir(context), student, entry_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Entry not found")
    return updated


@router.delete("/scorecard/{student}/entries/{entry_id}")
async def remove_entry(
    student: str,
    entry_id: str,
    context: ViewContext = Depends(get_view_context),
):
    """Delete a row."""
    _require_write(context)
    if not scorecard.delete_entry(_data_dir(context), student, entry_id):
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "deleted"}


def _render_for(context: ViewContext, student: str, use_template: bool | None) -> Path:
    data_dir = _data_dir(context)
    if not scorecard.get_student_log(data_dir, student).entries:
        raise HTTPException(status_code=404, detail=f"No score rows for {student}")

    safe = "".join(c for c in student if c.isalnum() or c in "-_") or "student"
    output = scorecard.scorecard_dir(data_dir) / f"{safe}_scorecard.pdf"
    return scorecard.render(data_dir, student, output, use_template=use_template)


@router.get("/scorecard/{student}/pdf")
async def get_scorecard_pdf(
    student: str,
    use_template: bool | None = None,
    context: ViewContext = Depends(get_view_context),
):
    """Download a student's score card as a PDF."""
    path = _render_for(context, student, use_template)
    return FileResponse(
        path, media_type="application/pdf", filename=f"{student}_scorecard.pdf"
    )


@router.post("/scorecard/template")
async def upload_template(
    file: UploadFile = File(...),
    context: ViewContext = Depends(get_view_context),
):
    """Upload a scan of the real score card to overlay rows onto."""
    _require_write(context)
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Template must be a PDF")

    directory = scorecard.scorecard_dir(_data_dir(context))
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "template.pdf").write_bytes(await file.read())
    return {"status": "uploaded"}


@router.get("/printers")
async def get_printers(_: ViewContext = Depends(get_view_context)):
    """List printers CUPS knows about."""
    return {"available": printing_available(), "printers": list_printers()}


@router.post("/print/scorecard/{student}")
async def print_scorecard(
    student: str,
    request: PrintRequest = PrintRequest(),
    use_template: bool | None = None,
    context: ViewContext = Depends(get_view_context),
):
    """Print a student's score card."""
    path = _render_for(context, student, use_template)
    try:
        job_id = print_pdf(
            path, request.printer, request.copies, title=f"Score Report - {student}"
        )
    except PrintError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return {"status": "queued", "job_id": job_id}


@router.post("/print/worksheet/{worksheet_id}")
async def print_worksheet(
    worksheet_id: str,
    request: PrintRequest = PrintRequest(),
    document: str = "marked",
    context: ViewContext = Depends(get_view_context),
):
    """Print a marked worksheet or its report ('marked' or 'report')."""
    data_dir = _data_dir(context)
    if document == "report":
        path = data_dir / "reports" / f"{worksheet_id}_report.pdf"
    elif document == "marked":
        path = data_dir / "marked" / f"{worksheet_id}_marked.pdf"
    else:
        raise HTTPException(
            status_code=400, detail="document must be 'marked' or 'report'"
        )

    if not path.exists():
        raise HTTPException(
            status_code=404, detail=f"No {document} PDF for {worksheet_id}"
        )

    try:
        job_id = print_pdf(
            path, request.printer, request.copies, title=f"{worksheet_id} ({document})"
        )
    except PrintError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return {"status": "queued", "job_id": job_id}
