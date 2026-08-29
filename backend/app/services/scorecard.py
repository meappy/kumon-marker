"""Kumon Score Report service.

Keeps a per-student log of completed worksheet packets — one row per packet,
matching the columns on the Kumon Score Report card — and renders that log as
a printable PDF.

Two rendering modes:

* generated (default) — draws a clean card from scratch, so it always works.
* template overlay — if a scan of the student's real card is present, the rows
  are drawn onto it. The default geometry matches the standard Item 115 card
  (landscape, ~824 x 576pt, two forms side by side); override it via the
  ``scorecard_geometry`` runtime setting if your scan sits differently.
"""

import io
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import fitz
from reportlab.lib.colors import Color, black
from reportlab.pdfgen import canvas

from app.core.config import get_effective_setting
from app.models.schemas import PageResult, ScoreEntry, ScoreLog, WorksheetHeader

INK = Color(0.05, 0.15, 0.55)
RULE = Color(0.35, 0.35, 0.35)
FAINT = Color(0.72, 0.72, 0.72)

MAX_MARKS = 10
ROWS_PER_CARD = 25


# --------------------------------------------------------------------------
# storage
# --------------------------------------------------------------------------


def scorecard_dir(data_dir: Path) -> Path:
    """Directory holding a user's score log and optional card template."""
    return Path(data_dir) / "scorecard"


def log_path(data_dir: Path) -> Path:
    """Path to the score log JSON file."""
    return scorecard_dir(data_dir) / "log.json"


def template_path(data_dir: Path) -> Path | None:
    """Path to a scanned score card to overlay onto, if the user supplied one."""
    path = scorecard_dir(data_dir) / "template.pdf"
    return path if path.exists() else None


def load_log(data_dir: Path) -> dict[str, list[ScoreEntry]]:
    """Load every student's score rows, oldest first."""
    path = log_path(data_dir)
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}

    students: dict[str, list[ScoreEntry]] = {}
    for name, entries in raw.get("students", {}).items():
        parsed = []
        for entry in entries:
            try:
                parsed.append(ScoreEntry(**entry))
            except (TypeError, ValueError):
                continue
        students[name] = parsed
    return students


def save_log(data_dir: Path, students: dict[str, list[ScoreEntry]]) -> None:
    """Write the score log back to disk."""
    path = log_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "students": {
            name: [json.loads(e.model_dump_json()) for e in entries]
            for name, entries in students.items()
        }
    }
    path.write_text(json.dumps(payload, indent=2))


def get_student_log(data_dir: Path, student: str) -> ScoreLog:
    """Get one student's log."""
    return ScoreLog(student=student, entries=load_log(data_dir).get(student, []))


def add_entry(data_dir: Path, student: str, entry: ScoreEntry) -> ScoreEntry:
    """Append a row to a student's log.

    A row built from the same worksheet replaces the earlier one, so
    re-processing a scan does not duplicate it.
    """
    students = load_log(data_dir)
    entries = students.setdefault(student, [])

    if entry.worksheet_id:
        entries = [e for e in entries if e.worksheet_id != entry.worksheet_id]
        students[student] = entries

    entries.append(entry)
    save_log(data_dir, students)
    return entry


def update_entry(
    data_dir: Path, student: str, entry_id: str, fields: dict
) -> ScoreEntry | None:
    """Edit a row in place — the times and date often need correcting by hand."""
    students = load_log(data_dir)
    for entry in students.get(student, []):
        if entry.id == entry_id:
            updated = entry.model_copy(update=fields)
            students[student] = [
                updated if e.id == entry_id else e for e in students[student]
            ]
            save_log(data_dir, students)
            return updated
    return None


def delete_entry(data_dir: Path, student: str, entry_id: str) -> bool:
    """Remove a row."""
    students = load_log(data_dir)
    entries = students.get(student)
    if not entries:
        return False
    remaining = [e for e in entries if e.id != entry_id]
    if len(remaining) == len(entries):
        return False
    students[student] = remaining
    save_log(data_dir, students)
    return True


# --------------------------------------------------------------------------
# building a row from marking results
# --------------------------------------------------------------------------


def _base_sheet(sheet_id: str | None) -> str:
    """'F96a' -> 'F96'."""
    if not sheet_id:
        return ""
    return sheet_id[:-1] if sheet_id[-1] in "ab" else sheet_id


def grade_for(total_questions: int, total_errors: int) -> str:
    """Grade one worksheet from its question and error counts."""
    if total_questions <= 0:
        return "-"
    pct = (total_questions - total_errors) / total_questions * 100
    if pct >= 90:
        return "A"
    if pct >= 70:
        return "B"
    if pct >= 50:
        return "C"
    return "D"


def marks_from_results(results: list[PageResult]) -> list[str]:
    """One grade per worksheet (an a+b pair counts as a single worksheet)."""
    per_sheet: dict[str, list[int]] = {}
    order: list[str] = []
    for result in results:
        base = _base_sheet(result.sheet_id)
        if not base:
            continue
        if base not in per_sheet:
            per_sheet[base] = [0, 0]
            order.append(base)
        per_sheet[base][0] += result.total_questions
        per_sheet[base][1] += len(result.errors)

    return [grade_for(*per_sheet[base]) for base in order][:MAX_MARKS]


def minutes_between(started: str | None, finished: str | None) -> str:
    """Minutes from start to finish, allowing for a 12-hour clock rollover."""
    if not started or not finished:
        return ""
    try:
        sh, sm = (int(part) for part in started.split(":"))
        fh, fm = (int(part) for part in finished.split(":"))
    except (ValueError, AttributeError):
        return ""

    delta = (fh * 60 + fm) - (sh * 60 + sm)
    if delta < 0:
        delta += 12 * 60  # e.g. 11:50 to 12:10 on a 12-hour clock
    return str(delta) if 0 < delta < 12 * 60 else ""


def _split_sheet_id(sheet_id: str) -> tuple[str, str]:
    """'F96' -> ('F', '96')."""
    base = _base_sheet(sheet_id)
    letters = "".join(c for c in base if c.isalpha())
    digits = "".join(c for c in base if c.isdigit())
    return letters, digits


def build_entry(
    results: list[PageResult],
    header: WorksheetHeader | None = None,
    worksheet_id: str | None = None,
) -> ScoreEntry:
    """Build a score row from a packet's marking results and its header."""
    header = header or WorksheetHeader()
    first_sheet = next((r.sheet_id for r in results if r.sheet_id), "")
    level, sheet_no = _split_sheet_id(first_sheet)

    date = header.date or ""
    # The card's date column is narrow — day/month is what fits.
    parts = [p.strip() for p in date.split("/")] if date else []
    if len(parts) >= 2:
        date = f"{parts[0]}/{parts[1]}"

    return ScoreEntry(
        id=str(uuid.uuid4()),
        worksheet_id=worksheet_id,
        date=date,
        time_started=header.time_started or "",
        time_finished=header.time_finished or "",
        time_used=minutes_between(header.time_started, header.time_finished),
        level=level,
        sheet_no=sheet_no,
        marks=marks_from_results(results),
    )


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------


@dataclass
class FormGeometry:
    """Where the cells of a scanned score card sit, in PDF points.

    ``edges`` are the seven vertical rules from the left of the table to the
    start of the marks block: table left, then the right-hand edge of Date,
    Time Started, Time Finished, Time Used, Level and Sheet No.
    """

    edges: tuple[float, float, float, float, float, float, float]
    mark_width: float
    top: float
    row_height: float
    page_height: float = 576.0
    rows: int = ROWS_PER_CARD

    def baseline(self, row: int) -> float:
        """Text baseline for a data row, sitting just above its rule."""
        return self.page_height - (self.top + (row + 1) * self.row_height) + 5

    def text_x(self) -> list[float]:
        """Left-aligned text position for each of the six data columns."""
        return [edge + 2.0 for edge in self.edges[:6]]

    def mark_centre(self, index: int) -> float:
        return self.edges[6] + self.mark_width * (index + 0.5)


# Measured from the printed rules of a standard Item 115 card scanned at 150 DPI.
# Page 1's right-hand form and page 3's left-hand form of a two-up scan.
DEFAULT_GEOMETRY = FormGeometry(
    edges=(436.9, 464.7, 505.3, 544.4, 584.0, 613.3, 644.7),
    mark_width=16.39,
    top=80.9,
    row_height=18.85,
)


def load_geometry() -> FormGeometry:
    """Geometry for template overlay, from runtime settings if overridden."""
    override = get_effective_setting("scorecard_geometry", None)
    if isinstance(override, dict):
        try:
            fields = {**asdict(DEFAULT_GEOMETRY), **override}
            fields["edges"] = tuple(fields["edges"])
            return FormGeometry(**fields)
        except (TypeError, ValueError, KeyError) as e:
            print(f"Invalid scorecard_geometry setting, using defaults: {e}")
    return DEFAULT_GEOMETRY


def _draw_row(c: canvas.Canvas, geo: FormGeometry, row: int, entry: ScoreEntry) -> None:
    """Draw one entry into a row of a form."""
    y = geo.baseline(row)
    xs = geo.text_x()
    values = [
        entry.date,
        entry.time_started,
        entry.time_finished,
        entry.time_used,
        entry.level,
        entry.sheet_no,
    ]

    c.setFillColor(INK)
    for i, (x, value) in enumerate(zip(xs, values)):
        c.setFont("Helvetica", 8 if i == 0 else 9)
        c.drawString(x, y, value)

    c.setFont("Helvetica", 9)
    for i, mark in enumerate(entry.marks[:MAX_MARKS]):
        if mark:
            c.drawCentredString(geo.mark_centre(i), y, mark)


def render_onto_template(
    entries: list[ScoreEntry],
    template: Path,
    output_path: Path,
    page_index: int = 0,
    start_row: int = 0,
    geometry: FormGeometry | None = None,
) -> None:
    """Overlay rows onto a scanned score card."""
    geo = geometry or load_geometry()
    doc = fitz.open(str(template))
    try:
        if entries and 0 <= page_index < len(doc):
            page = doc[page_index]
            width, height = page.rect.width, page.rect.height

            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=(width, height))
            for offset, entry in enumerate(entries):
                row = start_row + offset
                if row >= geo.rows:
                    break
                _draw_row(c, geo, row, entry)
            c.save()
            buf.seek(0)

            overlay = fitz.open("pdf", buf.getvalue())
            try:
                page.show_pdf_page(page.rect, overlay, 0, overlay=True)
            finally:
                overlay.close()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
    finally:
        doc.close()


# Generated-card layout: A4 landscape.
GEN_WIDTH, GEN_HEIGHT = 842.0, 595.0
GEN_MARGIN = 40.0
GEN_COLS = [55.0, 60.0, 60.0, 55.0, 45.0, 55.0]  # date, ts, tf, used, level, sheet
GEN_HEADERS = [
    "Date",
    "Time\nStarted",
    "Time\nFinished",
    "Time Used",
    "Level",
    "Sheet No",
]
GEN_ROW_HEIGHT = 18.0
GEN_TABLE_TOP = 112.0  # top rule of the data rows, from the top of the page
GEN_HEAD_HEIGHT = 28.0  # height of the column-heading band above it


def _generated_geometry() -> FormGeometry:
    """Cell geometry of the card this module draws itself.

    ``top`` is measured downwards from the top of the page, matching the
    template geometry, so the same row maths serves both.
    """
    edges = [GEN_MARGIN]
    for width in GEN_COLS:
        edges.append(edges[-1] + width)
    mark_width = (GEN_WIDTH - GEN_MARGIN - edges[-1]) / MAX_MARKS
    return FormGeometry(
        edges=tuple(edges),
        mark_width=mark_width,
        top=GEN_TABLE_TOP,
        row_height=GEN_ROW_HEIGHT,
        page_height=GEN_HEIGHT,
    )


def _draw_generated_form(c: canvas.Canvas, student: str, geo: FormGeometry) -> None:
    """Draw the blank card — title, column headings and the grid."""
    left, right = GEN_MARGIN, GEN_WIDTH - GEN_MARGIN
    data_top = GEN_HEIGHT - geo.top  # top rule of the data rows
    data_bottom = data_top - geo.rows * geo.row_height
    head_top = data_top + GEN_HEAD_HEIGHT

    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(GEN_WIDTH / 2, GEN_HEIGHT - 45, "SCORE REPORT")

    c.setFont("Helvetica", 10)
    c.drawString(left, GEN_HEIGHT - 72, "Student's Name")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left + 85, GEN_HEIGHT - 72, student)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(left + 80, GEN_HEIGHT - 76, left + 300, GEN_HEIGHT - 76)

    # column headings, one or two lines each, sitting in the heading band
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 7)
    for i, label in enumerate(GEN_HEADERS):
        centre = (geo.edges[i] + geo.edges[i + 1]) / 2
        lines = label.split("\n")
        for j, line in enumerate(lines):
            baseline = data_top + 10 + (len(lines) - 1 - j) * 8
            c.drawCentredString(centre, baseline, line)

    marks_centre = (geo.edges[6] + right) / 2
    c.drawCentredString(marks_centre, data_top + 18, "Mark Scored Before Correction")
    c.setFont("Helvetica", 6)
    for i in range(MAX_MARKS):
        c.drawCentredString(geo.mark_centre(i), data_top + 6, str(i + 1))

    # grid: outer box, column rules, then the faint row and mark rules
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    c.rect(left, data_bottom, right - left, head_top - data_bottom, stroke=1, fill=0)
    c.line(left, data_top, right, data_top)
    for edge in geo.edges[1:]:
        c.line(edge, data_bottom, edge, head_top)

    c.setStrokeColor(FAINT)
    c.setLineWidth(0.4)
    for i in range(1, MAX_MARKS):
        x = geo.edges[6] + geo.mark_width * i
        c.line(x, data_bottom, x, data_top + 12)
    for row in range(1, geo.rows):
        y = data_top - row * geo.row_height
        c.line(left, y, right, y)


def render_generated(
    student: str, entries: list[ScoreEntry], output_path: Path
) -> None:
    """Draw a clean score card, paginating when a card fills up."""
    geo = _generated_geometry()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=(GEN_WIDTH, GEN_HEIGHT))

    pages = [entries[i : i + geo.rows] for i in range(0, len(entries), geo.rows)] or [
        []
    ]
    for page_entries in pages:
        _draw_generated_form(c, student, geo)
        for row, entry in enumerate(page_entries):
            _draw_row(c, geo, row, entry)
        c.setFillColor(FAINT)
        c.setFont("Helvetica-Oblique", 7)
        c.drawRightString(
            GEN_WIDTH - GEN_MARGIN,
            20,
            f"Kumon Marker — generated {datetime.now().astimezone().strftime('%d %b %Y')}",
        )
        c.showPage()
    c.save()


def render(
    data_dir: Path,
    student: str,
    output_path: Path,
    use_template: bool | None = None,
    page_index: int = 0,
    start_row: int = 0,
) -> Path:
    """Render a student's score card.

    Overlays onto ``scorecard/template.pdf`` when one is present (unless
    ``use_template`` says otherwise); otherwise draws a clean card.
    """
    entries = get_student_log(data_dir, student).entries
    template = template_path(data_dir)

    if use_template is None:
        use_template = template is not None

    if use_template and template:
        render_onto_template(
            entries, template, output_path, page_index=page_index, start_row=start_row
        )
    else:
        render_generated(student, entries, output_path)
    return output_path
