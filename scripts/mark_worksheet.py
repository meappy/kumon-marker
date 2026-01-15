#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pymupdf",
#     "reportlab",
#     "google-auth-oauthlib",
#     "google-api-python-client",
# ]
# ///
"""
Automated Kumon worksheet marker using Claude Code CLI.

Usage:
    ./scripts/mark_worksheet.py                     # Interactive: select files from Google Drive
    ./scripts/mark_worksheet.py --latest 2          # Process 2 most recent files
    ./scripts/mark_worksheet.py --list              # List files in Google Drive folder
    ./scripts/mark_worksheet.py --report            # Regenerate reports from cached results
    ./scripts/mark_worksheet.py ~/Downloads/file.pdf  # Mark a local file

First run: will open browser to authenticate with Google.
Uses your Claude Max subscription (no API credits needed).
Results are cached as JSON for quick report regeneration.
"""

import subprocess
import sys
import json
import re
import tempfile
import fitz
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER

# Google Drive imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

GREEN = (0.133, 0.773, 0.369)
RED = (0.937, 0.267, 0.267)

# Google Drive settings
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
GDRIVE_FOLDER = 'From_BrotherDevice'

# Default questions per worksheet page (Kumon standard)
QUESTIONS_PER_PAGE = 10


def get_google_creds(base_dir: Path) -> Credentials:
    """Get or refresh Google OAuth credentials."""
    creds = None
    token_path = base_dir / 'token.json'
    creds_path = base_dir / 'credentials.json'

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                print(f"\nGoogle Drive setup required!")
                print(f"1. Go to https://console.cloud.google.com/apis/credentials")
                print(f"2. Create OAuth 2.0 Client ID (Desktop app)")
                print(f"3. Download JSON and save as: {creds_path}")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        token_path.write_text(creds.to_json())

    return creds


def get_gdrive_service(base_dir: Path):
    """Get authenticated Google Drive service."""
    creds = get_google_creds(base_dir)
    return build('drive', 'v3', credentials=creds)


def find_gdrive_folder(service, folder_name: str) -> str | None:
    """Find folder ID by name."""
    results = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive',
        fields='files(id, name)'
    ).execute()

    files = results.get('files', [])
    return files[0]['id'] if files else None


def list_pdfs_in_folder(service, folder_id: str) -> list[dict]:
    """List PDF files in a folder, sorted by date (newest first)."""
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false",
        spaces='drive',
        fields='files(id, name, createdTime)',
        orderBy='createdTime desc'
    ).execute()

    return results.get('files', [])


def download_file(service, file_id: str, dest_path: Path) -> None:
    """Download a file from Google Drive."""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    dest_path.write_bytes(fh.getvalue())


def format_date(iso_date: str) -> str:
    """Format ISO date to friendly format."""
    date = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
    today = datetime.now(date.tzinfo)

    if date.date() == today.date():
        return "today"
    elif (today.date() - date.date()).days == 1:
        return "yesterday"
    else:
        return date.strftime("%d %b")


def list_gdrive_files(base_dir: Path) -> None:
    """List PDF files in Google Drive folder."""
    print("Connecting to Google Drive...")
    service = get_gdrive_service(base_dir)

    folder_id = find_gdrive_folder(service, GDRIVE_FOLDER)
    if not folder_id:
        print(f"Error: Folder '{GDRIVE_FOLDER}' not found")
        return

    files = list_pdfs_in_folder(service, folder_id)
    if not files:
        print(f"No PDF files in '{GDRIVE_FOLDER}'")
        return

    print(f"\nFiles in '{GDRIVE_FOLDER}':")
    print("-" * 50)
    for i, f in enumerate(files[:10], 1):
        date = format_date(f['createdTime'])
        print(f"  {i}. {f['name']} ({date})")


def select_files_interactive(base_dir: Path) -> list[Path]:
    """Show files and let user select which to process."""
    print("Connecting to Google Drive...")
    service = get_gdrive_service(base_dir)

    folder_id = find_gdrive_folder(service, GDRIVE_FOLDER)
    if not folder_id:
        print(f"Error: Folder '{GDRIVE_FOLDER}' not found in Google Drive")
        return []

    files = list_pdfs_in_folder(service, folder_id)
    if not files:
        print(f"No PDF files found in '{GDRIVE_FOLDER}'")
        return []

    # Show available files
    print(f"\nFiles in '{GDRIVE_FOLDER}':")
    print("-" * 55)
    for i, f in enumerate(files[:10], 1):
        date = format_date(f['createdTime'])
        print(f"  {i}. {f['name']} ({date})")
    print("-" * 55)

    # Get user selection
    print("\nSelect files to process:")
    print("  - Enter numbers separated by commas (e.g., 1,2,3)")
    print("  - Enter a range (e.g., 1-3)")
    print("  - Enter 'all' for all files shown")
    print("  - Press Enter for latest file only")

    selection = input("\nSelection [1]: ").strip().lower()

    # Parse selection
    indices = []
    if not selection or selection == '1':
        indices = [0]
    elif selection == 'all':
        indices = list(range(min(10, len(files))))
    elif '-' in selection:
        # Range like "1-3"
        try:
            start, end = selection.split('-')
            indices = list(range(int(start) - 1, int(end)))
        except:
            print("Invalid range. Using latest file.")
            indices = [0]
    else:
        # Comma-separated like "1,2,3"
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
        except:
            print("Invalid selection. Using latest file.")
            indices = [0]

    # Download selected files
    scans_dir = base_dir / 'scans'
    scans_dir.mkdir(exist_ok=True)

    selected_paths = []
    for idx in indices:
        if 0 <= idx < len(files):
            f = files[idx]
            dest = scans_dir / f['name']

            if dest.exists():
                print(f"  Already downloaded: {f['name']}")
            else:
                print(f"  Downloading: {f['name']}...")
                download_file(service, f['id'], dest)

            selected_paths.append(dest)

    return selected_paths


def get_latest_files(base_dir: Path, count: int) -> list[Path]:
    """Download the N latest PDFs from Google Drive."""
    print("Connecting to Google Drive...")
    service = get_gdrive_service(base_dir)

    folder_id = find_gdrive_folder(service, GDRIVE_FOLDER)
    if not folder_id:
        print(f"Error: Folder '{GDRIVE_FOLDER}' not found in Google Drive")
        return []

    files = list_pdfs_in_folder(service, folder_id)
    if not files:
        print(f"No PDF files found in '{GDRIVE_FOLDER}'")
        return []

    # Download to scans folder
    scans_dir = base_dir / 'scans'
    scans_dir.mkdir(exist_ok=True)

    selected_paths = []
    for f in files[:count]:
        dest = scans_dir / f['name']

        if dest.exists():
            print(f"  Already downloaded: {f['name']}")
        else:
            print(f"  Downloading: {f['name']}...")
            download_file(service, f['id'], dest)

        selected_paths.append(dest)

    return selected_paths


def pdf_to_images(pdf_path: Path, temp_dir: Path) -> list[Path]:
    """Convert PDF pages to PNG images."""
    doc = fitz.open(pdf_path)
    images = []
    for i in range(len(doc)):
        pix = doc[i].get_pixmap(matrix=fitz.Matrix(150/72, 150/72))
        path = temp_dir / f"page_{i:03d}.png"
        pix.save(path)
        images.append(path)
    doc.close()
    return images


def validate_kumon_worksheet(pdf_path: Path) -> dict | None:
    """
    Validate that a PDF is a Kumon worksheet by checking for KUMON text.
    Returns dict with sheet_id and subject, or None if not a Kumon worksheet.
    Uses text extraction - fast and doesn't use Claude credits.
    """
    try:
        doc = fitz.open(pdf_path)
        text = doc[0].get_text().upper()
        doc.close()

        if "KUMON" not in text:
            return None

        # Extract sheet ID (e.g., "B161a", "C26a") from text
        # Pattern: letter + numbers + optional letter (a/b)
        sheet_match = re.search(r'\b([A-Z]\s*\d+\s*[ab]?)\b', text)
        sheet_id = re.sub(r'\s+', '', sheet_match.group(1)) if sheet_match else "Unknown"

        # Try to detect subject/topic from common keywords
        subject = "maths"
        topic = ""
        text_lower = text.lower()
        if "subtraction" in text_lower:
            topic = "subtraction"
        elif "addition" in text_lower:
            topic = "addition"
        elif "multiplication" in text_lower:
            topic = "multiplication"
        elif "division" in text_lower:
            topic = "division"

        return {
            "is_kumon": True,
            "sheet_id": sheet_id,
            "subject": subject,
            "topic": topic
        }

    except Exception as e:
        print(f" validation error: {e}")
        return None


def analyse_with_claude(image_path: Path, page_num: int, sheet_id: str) -> dict:
    """Call Claude Code CLI to analyse a worksheet page."""

    prompt = f'''Analyse this Kumon worksheet page ({sheet_id}, page {page_num + 1}).

Count ALL the maths problems on this page and check each one against the student's handwritten answer.

IMPORTANT: You MUST return the actual count of questions on the page in "total_questions".
Most Kumon pages have 10 questions, but count them to be sure.

Return ONLY valid JSON in this exact format:
{{"sheet_id": "{sheet_id}", "page_num": {page_num}, "total_questions": <ACTUAL COUNT>, "errors": [<list of errors or empty>]}}

For each error, include: {{"q": <question number>, "problem": "<the problem>", "student": <student's answer>, "correct": <correct answer>, "x": <x position>, "y": <y position>}}

Position guide (page ~576x572 points):
- Left column questions: x=180
- Right column questions: x=460
- Row positions from top: y=185, 285, 385, 485

If ALL answers are correct, return:
{{"sheet_id": "{sheet_id}", "page_num": {page_num}, "total_questions": <ACTUAL COUNT>, "errors": []}}

ONLY output the JSON, nothing else.'''

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, str(image_path)],
            capture_output=True,
            text=True,
            timeout=180
        )

        output = result.stdout.strip()
        match = re.search(r'\{[\s\S]*\}', output)
        if match:
            data = json.loads(match.group())
            # Ensure total_questions has a sensible value
            if data.get("total_questions", 0) == 0:
                data["total_questions"] = QUESTIONS_PER_PAGE
            return data
    except Exception as e:
        print(f" error: {e}")

    # Default fallback
    return {"sheet_id": sheet_id, "page_num": page_num, "total_questions": QUESTIONS_PER_PAGE, "errors": []}


def draw_circle(page: fitz.Page) -> None:
    rect = page.rect
    shape = page.new_shape()
    shape.draw_oval(fitz.Rect(30, 60, rect.width - 30, rect.height - 30))
    shape.finish(color=GREEN, width=3, stroke_opacity=0.8)
    shape.commit()


def draw_tick(page: fitz.Page, x: float, y: float) -> None:
    shape = page.new_shape()
    shape.draw_line(fitz.Point(x, y), fitz.Point(x + 6, y + 9))
    shape.draw_line(fitz.Point(x + 6, y + 9), fitz.Point(x + 15, y - 5))
    shape.finish(color=RED, width=2.5, stroke_opacity=0.9)
    shape.commit()


def save_results(results_path: Path, results: list[dict], pdf_name: str) -> None:
    """Save analysis results to JSON for later report regeneration."""
    data = {
        "pdf_name": pdf_name,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    results_path.write_text(json.dumps(data, indent=2))


def load_results(results_path: Path) -> tuple[list[dict], str] | None:
    """Load analysis results from JSON. Returns (results, pdf_name) or None."""
    if not results_path.exists():
        return None
    try:
        data = json.loads(results_path.read_text())
        return data["results"], data["pdf_name"]
    except (json.JSONDecodeError, KeyError):
        return None


def create_marked_pdf(input_path: Path, output_path: Path, results: list[dict]) -> None:
    doc = fitz.open(input_path)
    errors_by_page = {r["page_num"]: r.get("errors", []) for r in results}

    for i in range(len(doc)):
        page = doc[i]
        errors = errors_by_page.get(i, [])
        if errors:
            for e in errors:
                draw_tick(page, e.get("x", 200), e.get("y", 300))
        else:
            draw_circle(page)

    doc.save(output_path)
    doc.close()


def create_report(output_path: Path, results: list[dict], pdf_name: str) -> None:
    """Create a PDF report with scoring summary."""
    total_q = sum(r.get("total_questions", QUESTIONS_PER_PAGE) for r in results)
    total_e = sum(len(r.get("errors", [])) for r in results)
    correct = total_q - total_e
    pct = (correct / total_q * 100) if total_q > 0 else 100
    grade = 'A' if pct >= 90 else 'B' if pct >= 70 else 'C' if pct >= 50 else 'D'

    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                           rightMargin=15*mm, leftMargin=15*mm,
                           topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    content = []

    # Colors
    blue = colors.HexColor('#1e40af')
    green = colors.HexColor('#22c55e')
    red = colors.HexColor('#dc2626')
    grey = colors.HexColor('#6b7280')
    light_green = colors.HexColor('#f0fdf4')
    light_red = colors.HexColor('#fef2f2')
    score_color = green if pct >= 70 else red

    # Get sheet info
    sheet_ids = [r.get("sheet_id", "?") for r in results]
    sheets = []
    for sid in sheet_ids:
        base = sid.rstrip('ab') if sid and sid[-1] in 'ab' else sid
        if base not in sheets:
            sheets.append(base)
    sheets_range = f"{sheets[0]} - {sheets[-1]}" if len(sheets) > 1 else sheets[0] if sheets else "?"

    # Title
    title_table = Table([["KUMON WORKSHEET REPORT"]], colWidths=[170*mm])
    title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 22),
        ('TEXTCOLOR', (0, 0), (-1, -1), blue),
    ]))
    content.append(title_table)
    content.append(Spacer(1, 15))

    # Info table (Date, Worksheets)
    today = datetime.now().strftime("%d %B %Y")
    info_data = [
        ["Date:", today],
        ["Worksheets:", f"{sheets_range} ({len(results)} pages)"],
    ]
    info_table = Table(info_data, colWidths=[70, 120])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), grey),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    content.append(info_table)
    content.append(Spacer(1, 20))

    # Score section - use table with plain strings
    score_table = Table(
        [[f"{correct} / {total_q}"], [f"{pct:.1f}% — Grade {grade}"]],
        colWidths=[170*mm],
        rowHeights=[50, 30]
    )
    score_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 42),
        ('FONTSIZE', (0, 1), (0, 1), 20),
        ('TEXTCOLOR', (0, 0), (-1, -1), score_color),
    ]))
    content.append(score_table)
    content.append(Spacer(1, 25))

    # Sheet Breakdown
    content.append(Paragraph("Sheet Breakdown",
                             ParagraphStyle('H2', fontSize=14, fontName='Helvetica-Bold')))
    content.append(Spacer(1, 8))

    # Build sheet breakdown data
    sheet_data = [['Sheet', 'Questions', 'Correct', 'Mistakes', 'Grade', 'Status']]
    sheet_stats = {}
    for r in results:
        sid = r.get("sheet_id", "?")
        base = sid.rstrip('ab') if sid and sid[-1] in 'ab' else sid
        if base not in sheet_stats:
            sheet_stats[base] = {"questions": 0, "errors": 0}
        sheet_stats[base]["questions"] += r.get("total_questions", QUESTIONS_PER_PAGE)
        sheet_stats[base]["errors"] += len(r.get("errors", []))

    for sheet, stats in sheet_stats.items():
        q = stats["questions"]
        e = stats["errors"]
        c = q - e
        p = (c / q * 100) if q > 0 else 100
        g = 'A' if p >= 90 else 'B' if p >= 70 else 'C' if p >= 50 else 'D'
        status = "PERFECT" if e == 0 else f"{e} error{'s' if e > 1 else ''}"
        sheet_data.append([sheet, str(q), str(c), str(e), g, status])

    breakdown_table = Table(sheet_data, colWidths=[50, 60, 50, 55, 45, 70])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 22),
    ]))
    # Alternate row colors
    for i in range(1, len(sheet_data)):
        bg = colors.white if i % 2 == 1 else colors.HexColor('#f9fafb')
        breakdown_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), bg)]))
    content.append(breakdown_table)
    content.append(Spacer(1, 25))

    # Errors table
    all_errors = []
    for r in results:
        for e in r.get("errors", []):
            all_errors.append({"sheet": r["sheet_id"], **e})

    if all_errors:
        content.append(Paragraph("Corrections Needed",
                                 ParagraphStyle('H2', fontSize=14, fontName='Helvetica-Bold')))
        content.append(Spacer(1, 5))
        content.append(Paragraph(f"Please review and correct these {len(all_errors)} mistake{'s' if len(all_errors) > 1 else ''}:",
                                 ParagraphStyle('Msg', fontSize=10, textColor=grey)))
        content.append(Spacer(1, 8))

        err_data = [['Sheet', 'Q#', 'Problem', 'Your Answer', 'Correct']]
        for e in all_errors:
            err_data.append([
                e.get('sheet', '?'),
                str(e.get('q', '?')),
                e.get('problem', '?'),
                str(e.get('student', '?')),
                str(e.get('correct', '?')),
            ])

        err_table = Table(err_data, colWidths=[50, 30, 80, 70, 70])
        err_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('BACKGROUND', (0, 1), (-1, -1), light_red),
            ('ROWHEIGHT', (0, 0), (-1, -1), 24),
            ('TEXTCOLOR', (3, 1), (3, -1), red),  # Your Answer in red
            ('TEXTCOLOR', (4, 1), (4, -1), green),  # Correct in green
            ('FONTNAME', (3, 1), (4, -1), 'Helvetica-Bold'),
        ]))
        content.append(err_table)
    else:
        # Perfect score message
        perfect_table = Table([["PERFECT SCORE!"], ["All answers correct. Excellent work!"]],
                              colWidths=[170*mm], rowHeights=[25, 20])
        perfect_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 18),
            ('FONTSIZE', (0, 1), (0, 1), 12),
            ('TEXTCOLOR', (0, 0), (0, 0), green),
            ('TEXTCOLOR', (0, 1), (0, 1), grey),
        ]))
        content.append(perfect_table)

    doc.build(content)


def mark_pdf(pdf_path: Path, base_dir: Path, validate: bool = True) -> bool:
    """
    Mark a PDF file.
    Returns True if successfully processed, False if skipped.
    """
    print(f"\nMarking: {pdf_path.name}")
    print("=" * 50)

    (base_dir / "marked").mkdir(exist_ok=True)
    (base_dir / "reports").mkdir(exist_ok=True)

    # Validate PDF is a Kumon worksheet (before converting to images)
    validation = None
    if validate:
        print("Validating worksheet...")
        validation = validate_kumon_worksheet(pdf_path)
        if not validation:
            print("  Not a valid Kumon worksheet - skipping")
            return False

        sheet_id = validation.get("sheet_id", "?")
        subject = validation.get("subject", "maths")
        topic = validation.get("topic", "")
        print(f"  Valid: {sheet_id} ({subject} - {topic})")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        print("Converting PDF to images...")
        images = pdf_to_images(pdf_path, tmp_path)
        print(f"  {len(images)} pages")

        # Generate sheet IDs based on detected first sheet or default
        # Extract base sheet number from validation if available
        if validate and validation:
            base_match = re.match(r'([A-Z])(\d+)', validation.get("sheet_id", "B161"))
            if base_match:
                prefix = base_match.group(1)
                base_num = int(base_match.group(2))
            else:
                prefix, base_num = "B", 161
        else:
            prefix, base_num = "B", 161

        sheet_ids = [f"{prefix}{base_num + i//2}{'a' if i%2==0 else 'b'}" for i in range(len(images))]

        print("\nAnalysing with Claude Code...")
        results = []
        for i, (img, sid) in enumerate(zip(images, sheet_ids)):
            print(f"  Page {i+1}/{len(images)} ({sid})...", end=" ", flush=True)
            r = analyse_with_claude(img, i, sid)
            results.append(r)
            errs = len(r.get("errors", []))
            total = r.get("total_questions", QUESTIONS_PER_PAGE)
            if errs:
                print(f"{errs} error(s)")
            else:
                print(f"OK ({total} questions)")

    # Save results to JSON for later regeneration
    results_dir = base_dir / "results"
    results_dir.mkdir(exist_ok=True)
    results_json = results_dir / f"{pdf_path.stem}.json"
    save_results(results_json, results, pdf_path.name)
    print(f"\nResults saved: {results_json}")

    # Generate outputs
    marked = base_dir / "marked" / f"{pdf_path.stem}_marked.pdf"
    report = base_dir / "reports" / f"{pdf_path.stem}_report.pdf"

    print("Generating marked PDF...")
    create_marked_pdf(pdf_path, marked, results)
    print(f"  {marked}")

    print("Generating report...")
    create_report(report, results, pdf_path.name)
    print(f"  {report}")

    # Summary
    total_q = sum(r.get("total_questions", QUESTIONS_PER_PAGE) for r in results)
    total_e = sum(len(r.get("errors", [])) for r in results)
    print("\n" + "=" * 50)
    print(f"Score: {total_q - total_e}/{total_q} ({(total_q-total_e)/total_q*100:.1f}%)")
    print(f"Errors: {total_e}")
    print("=" * 50)

    # Open PDFs
    subprocess.run(["open", str(marked), str(report)])

    return True


def regenerate_reports(base_dir: Path) -> None:
    """Regenerate all reports from cached JSON results."""
    results_dir = base_dir / "results"
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(exist_ok=True)

    if not results_dir.exists():
        print("No cached results found. Run analysis first.")
        return

    json_files = list(results_dir.glob("*.json"))
    if not json_files:
        print("No cached results found. Run analysis first.")
        return

    print(f"Found {len(json_files)} cached result(s)")
    print("-" * 50)

    for json_path in sorted(json_files):
        loaded = load_results(json_path)
        if not loaded:
            print(f"  {json_path.stem}: invalid JSON, skipping")
            continue

        results, pdf_name = loaded
        report = reports_dir / f"{json_path.stem}_report.pdf"

        print(f"  {json_path.stem}...", end=" ")
        create_report(report, results, pdf_name)
        print("done")

    print("-" * 50)
    print("Reports regenerated.")


def main():
    base_dir = Path(__file__).parent.parent

    # Parse arguments
    if len(sys.argv) < 2:
        # No args: interactive file selection
        pdf_paths = select_files_interactive(base_dir)
        for pdf_path in pdf_paths:
            mark_pdf(pdf_path, base_dir)

    elif sys.argv[1] == '--latest':
        # Process N latest files
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        pdf_paths = get_latest_files(base_dir, count)
        for pdf_path in pdf_paths:
            mark_pdf(pdf_path, base_dir)

    elif sys.argv[1] == '--list':
        # List files in Google Drive
        list_gdrive_files(base_dir)

    elif sys.argv[1] == '--report':
        # Regenerate reports from cached results
        regenerate_reports(base_dir)

    elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
        print(__doc__)

    else:
        # Mark a local file
        pdf_path = Path(sys.argv[1]).expanduser().resolve()
        if not pdf_path.exists():
            print(f"Error: {pdf_path} not found")
            sys.exit(1)
        mark_pdf(pdf_path, base_dir)


if __name__ == "__main__":
    main()
