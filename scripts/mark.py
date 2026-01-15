#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pymupdf",
#     "reportlab",
# ]
# ///
"""
Mark a Kumon worksheet PDF using errors identified by Claude Code.

Usage:
    1. Share the PDF with Claude Code for analysis
    2. Claude updates scripts/errors.py with the errors found
    3. Run: ./scripts/mark.py <input.pdf>

The script generates:
    - marked/<filename>_marked.pdf (worksheet with circles/ticks)
    - reports/<filename>_report.pdf (printable report)
"""

import sys
import fitz
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Import errors from the errors file (updated by Claude Code)
from errors import ERRORS, STUDENT_NAME, WORKSHEET_DATE, TOTAL_QUESTIONS, CORRECT_ANSWERS

# Colours
GREEN = (0.133, 0.773, 0.369)
RED = (0.937, 0.267, 0.267)


def draw_circle(page: fitz.Page) -> None:
    """Draw a green circle around the page content."""
    rect = page.rect
    margin = 30
    circle_rect = fitz.Rect(margin, margin + 30, rect.width - margin, rect.height - margin)
    shape = page.new_shape()
    shape.draw_oval(circle_rect)
    shape.finish(color=GREEN, width=3, stroke_opacity=0.8)
    shape.commit()


def draw_tick(page: fitz.Page, x: float, y: float) -> None:
    """Draw a red tick mark."""
    shape = page.new_shape()
    size = 15
    shape.draw_line(fitz.Point(x, y), fitz.Point(x + size * 0.4, y + size * 0.6))
    shape.draw_line(fitz.Point(x + size * 0.4, y + size * 0.6), fitz.Point(x + size, y - size * 0.3))
    shape.finish(color=RED, width=2.5, stroke_opacity=0.9)
    shape.commit()


def annotate_pdf(input_path: Path, output_path: Path) -> None:
    """Create marked PDF with circles and ticks."""
    doc = fitz.open(input_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        if page_num in ERRORS:
            for q_num, x, y in ERRORS[page_num]:
                draw_tick(page, x, y)
        else:
            draw_circle(page)

    doc.save(output_path)
    doc.close()


def create_report(output_path: Path) -> None:
    """Create printable PDF report."""
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                           rightMargin=20*mm, leftMargin=20*mm,
                           topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    content = []

    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
                                  fontSize=24, alignment=TA_CENTER,
                                  textColor=colors.HexColor('#1e40af'))
    content.append(Paragraph("KUMON WORKSHEET REPORT", title_style))
    content.append(Spacer(1, 20))

    # Score
    score_pct = (CORRECT_ANSWERS / TOTAL_QUESTIONS) * 100
    grade = 'A' if score_pct >= 90 else 'B' if score_pct >= 70 else 'C' if score_pct >= 50 else 'D'

    score_style = ParagraphStyle('Score', parent=styles['Normal'],
                                  fontSize=36, alignment=TA_CENTER,
                                  textColor=colors.HexColor('#22c55e'))
    content.append(Paragraph(f"{CORRECT_ANSWERS} / {TOTAL_QUESTIONS} ({score_pct:.1f}%) — Grade {grade}", score_style))
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"Student: {STUDENT_NAME} | Date: {WORKSHEET_DATE}",
                             ParagraphStyle('Info', alignment=TA_CENTER, fontSize=12)))
    content.append(Spacer(1, 30))

    # Errors table
    if ERRORS:
        content.append(Paragraph("Corrections Needed:", styles['Heading2']))
        error_data = [['Page', 'Question', 'Position']]
        for page_num, questions in sorted(ERRORS.items()):
            for q_num, x, y in questions:
                error_data.append([f"Page {page_num + 1}", f"Q{q_num}", f"({x}, {y})"])

        table = Table(error_data, colWidths=[80, 80, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),
        ]))
        content.append(table)

    doc.build(content)


def main():
    if len(sys.argv) < 2:
        print("Usage: ./scripts/mark.py <input.pdf>")
        print("\nWorkflow:")
        print("  1. Share PDF with Claude Code for analysis")
        print("  2. Claude updates scripts/errors.py")
        print("  3. Run this script to generate marked PDF + report")
        sys.exit(1)

    input_pdf = Path(sys.argv[1])
    if not input_pdf.exists():
        print(f"Error: File not found: {input_pdf}")
        sys.exit(1)

    # Create output directories
    base_dir = Path(__file__).parent.parent
    marked_dir = base_dir / "marked"
    reports_dir = base_dir / "reports"
    marked_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(exist_ok=True)

    # Output filenames
    stem = input_pdf.stem
    marked_pdf = marked_dir / f"{stem}_marked.pdf"
    report_pdf = reports_dir / f"{stem}_report.pdf"

    # Generate outputs
    print(f"Marking: {input_pdf.name}")
    annotate_pdf(input_pdf, marked_pdf)
    print(f"  → {marked_pdf}")

    create_report(report_pdf)
    print(f"  → {report_pdf}")

    print(f"\nScore: {CORRECT_ANSWERS}/{TOTAL_QUESTIONS} ({CORRECT_ANSWERS/TOTAL_QUESTIONS*100:.1f}%)")
    print(f"Errors: {sum(len(e) for e in ERRORS.values())} mistakes on {len(ERRORS)} pages")


if __name__ == "__main__":
    main()
