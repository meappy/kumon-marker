#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "reportlab",
# ]
# ///
"""
Generate a printable PDF report for Kumon worksheet marking results.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pathlib import Path
from datetime import datetime


def create_report_pdf(output_path: Path):
    """Generate a printable PDF report."""

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor=colors.HexColor('#1e40af')
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#6b7280')
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#1f2937')
    )

    score_style = ParagraphStyle(
        'Score',
        parent=styles['Normal'],
        fontSize=48,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#22c55e'),
        spaceAfter=5
    )

    grade_style = ParagraphStyle(
        'Grade',
        parent=styles['Normal'],
        fontSize=36,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#22c55e'),
        spaceBefore=5,
        spaceAfter=20
    )

    # Build document content
    content = []

    # Title
    content.append(Paragraph("KUMON WORKSHEET REPORT", title_style))
    content.append(Paragraph("Subtraction of 3-Digit Numbers (B161-B170)", subtitle_style))

    # Student info table
    info_data = [
        ['Student:', 'Gemma'],
        ['Date:', '14 January 2026'],
        ['Worksheets:', 'B161 - B170 (20 pages)'],
    ]

    info_table = Table(info_data, colWidths=[80, 200])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    content.append(info_table)
    content.append(Spacer(1, 20))

    # Score display
    content.append(Paragraph("167 / 173", score_style))
    content.append(Paragraph("96.5% — Grade A", grade_style))
    content.append(Paragraph("EXCELLENT WORK! 🌟", ParagraphStyle(
        'Congrats',
        parent=styles['Normal'],
        fontSize=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#22c55e'),
        spaceAfter=25
    )))

    # Sheet breakdown
    content.append(Paragraph("Sheet Breakdown", heading_style))

    sheet_data = [
        ['Sheet', 'Questions', 'Correct', 'Mistakes', 'Grade', 'Status'],
        ['B161', '20', '19', '1', 'A', '1 error'],
        ['B162', '18', '18', '0', 'A', 'PERFECT ✓'],
        ['B163', '18', '18', '0', 'A', 'PERFECT ✓'],
        ['B164', '18', '18', '0', 'A', 'PERFECT ✓'],
        ['B165', '18', '18', '0', 'A', 'PERFECT ✓'],
        ['B166', '18', '18', '0', 'A', 'PERFECT ✓'],
        ['B167', '18', '16', '2', 'B', '2 errors'],
        ['B168', '18', '16', '2', 'B', '2 errors'],
        ['B169', '9', '9', '0', 'A', 'PERFECT ✓'],
        ['B170', '18', '17', '1', 'A', '1 error'],
    ]

    sheet_table = Table(sheet_data, colWidths=[50, 65, 55, 55, 45, 80])
    sheet_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),

        # Alternating row colours
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fef2f2')),  # Error row
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#fef2f2')),  # Error row
        ('BACKGROUND', (0, 8), (-1, 8), colors.HexColor('#fef2f2')),  # Error row
        ('BACKGROUND', (0, 9), (-1, 9), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (0, 10), (-1, 10), colors.HexColor('#fef2f2')),  # Error row

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    content.append(sheet_table)
    content.append(Spacer(1, 25))

    # Corrections needed
    content.append(Paragraph("Corrections Needed", heading_style))
    content.append(Paragraph(
        "Please review and correct these 6 mistakes:",
        ParagraphStyle('Intro', parent=styles['Normal'], fontSize=11, spaceAfter=10)
    ))

    corrections_data = [
        ['Sheet', 'Q#', 'Problem', 'Your Answer', 'Correct', 'How to Solve'],
        ['B161a', '5', '150 − 50', '106', '100', '15 tens − 5 tens = 10 tens'],
        ['B167a', '6', '263 − 38', '235', '225', '263 − 40 + 2 = 225'],
        ['B167a', '8', '263 − 49', '224', '214', '263 − 50 + 1 = 214'],
        ['B168a', '5', '257 − 38', '119', '219', '257 − 40 + 2 = 219'],
        ['B168b', '12', '354 − 26', '338', '328', '354 − 30 + 4 = 328'],
        ['B170a', '3', '253 − 36', '227', '217', '253 − 40 + 4 = 217'],
    ]

    corrections_table = Table(corrections_data, colWidths=[45, 25, 65, 65, 50, 120])
    corrections_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (4, -1), 'CENTER'),
        ('ALIGN', (5, 1), (5, -1), 'LEFT'),

        # Wrong answer highlight
        ('TEXTCOLOR', (3, 1), (3, -1), colors.HexColor('#dc2626')),
        ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),

        # Correct answer highlight
        ('TEXTCOLOR', (4, 1), (4, -1), colors.HexColor('#22c55e')),
        ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),

        # Alternating rows
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fef2f2')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.white),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#fef2f2')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.white),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#fef2f2')),
        ('BACKGROUND', (0, 6), (-1, 6), colors.white),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    content.append(corrections_table)
    content.append(Spacer(1, 30))

    # Footer message
    content.append(Paragraph(
        "Well done Gemma! Keep practising subtraction with borrowing. "
        "Most of your errors were in problems like 263 − 38 where you need to "
        "regroup from the tens column. Try rounding to the nearest 10, then adjusting!",
        ParagraphStyle(
            'Feedback',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#4b5563'),
            spaceBefore=10,
            borderColor=colors.HexColor('#22c55e'),
            borderWidth=1,
            borderPadding=10,
            backColor=colors.HexColor('#f0fdf4'),
        )
    ))

    # Build PDF
    doc.build(content)
    print(f"Report PDF saved to: {output_path}")


def main():
    output_path = Path("/Users/gerald/Projects/kumon-marker/reports/20260114130247_001_report.pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    create_report_pdf(output_path)


if __name__ == "__main__":
    main()
