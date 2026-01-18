"""Pydantic schemas for the Kumon Marker API."""

from datetime import datetime
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """A single marking error on a worksheet."""
    q: int = Field(description="Question number")
    problem: str = Field(description="The maths problem")
    student: str | int = Field(description="Student's answer")
    correct: str | int = Field(description="Correct answer")
    x: float = Field(default=200, description="X position for tick mark")
    y: float = Field(default=300, description="Y position for tick mark")


class PageResult(BaseModel):
    """Analysis result for a single page."""
    sheet_id: str = Field(description="Sheet ID e.g. B161a")
    page_num: int = Field(description="Page number (0-indexed)")
    total_questions: int = Field(default=10, description="Total questions on page")
    errors: list[ErrorDetail] = Field(default_factory=list)


class WorksheetResult(BaseModel):
    """Complete analysis result for a worksheet PDF."""
    pdf_name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    results: list[PageResult]

    @property
    def total_questions(self) -> int:
        return sum(r.total_questions for r in self.results)

    @property
    def total_errors(self) -> int:
        return sum(len(r.errors) for r in self.results)

    @property
    def score_percentage(self) -> float:
        if self.total_questions == 0:
            return 100.0
        return (self.total_questions - self.total_errors) / self.total_questions * 100

    @property
    def grade(self) -> str:
        pct = self.score_percentage
        if pct >= 90:
            return "A"
        elif pct >= 70:
            return "B"
        elif pct >= 50:
            return "C"
        return "D"


class ValidationResult(BaseModel):
    """Result of validating a PDF is a Kumon worksheet."""
    is_kumon: bool
    sheet_id: str | None = None
    subject: str | None = None
    topic: str | None = None
    student_name: str | None = None


class WorksheetSummary(BaseModel):
    """Summary info for listing worksheets."""
    id: str = Field(description="Unique identifier (PDF stem)")
    pdf_name: str
    timestamp: datetime
    pages: int
    total_questions: int
    total_errors: int
    score_percentage: float
    grade: str
    has_marked_pdf: bool = False
    has_report: bool = False
    student_name: str | None = None
    sheet_id: str | None = None


class GDriveFile(BaseModel):
    """A file in Google Drive."""
    id: str
    name: str
    created_time: datetime
    size: int | None = None
    is_kumon: bool | None = None  # None = not checked yet
    sheet_id: str | None = None  # e.g. "C26a", "D116"
    student_name: str | None = None


class ProcessRequest(BaseModel):
    """Request to process a worksheet."""
    validate_worksheet: bool = Field(default=True, description="Validate is Kumon worksheet first")


class ConfigUpdate(BaseModel):
    """Configuration update request."""
    anthropic_api_key: str | None = None
    gdrive_folder: str | None = None
    auto_sync: bool | None = None
    sync_interval_minutes: int | None = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"


class UploadedFile(BaseModel):
    """An uploaded file in the scans directory."""
    id: str = Field(description="File ID (stem without extension)")
    filename: str = Field(description="Original filename")
    uploaded_at: datetime = Field(description="When the file was uploaded")
    size: int = Field(description="File size in bytes")
    is_kumon: bool | None = None
    sheet_id: str | None = None
    student_name: str | None = None
    is_processed: bool = Field(default=False, description="Whether this file has been marked")
