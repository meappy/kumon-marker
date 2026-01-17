"""Report generation service."""

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.models.schemas import PageResult


def create_report(output_path: Path, results: list[PageResult], pdf_name: str, student_name: str | None = None) -> None:
    """Create a PDF report with scoring summary."""
    total_q = sum(r.total_questions for r in results)
    total_e = sum(len(r.errors) for r in results)
    correct = total_q - total_e
    pct = (correct / total_q * 100) if total_q > 0 else 100
    grade = 'A' if pct >= 90 else 'B' if pct >= 70 else 'C' if pct >= 50 else 'D'

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )
    content = []

    # Colours
    blue = colors.HexColor('#1e40af')
    green = colors.HexColor('#22c55e')
    red = colors.HexColor('#dc2626')
    grey = colors.HexColor('#6b7280')
    light_red = colors.HexColor('#fef2f2')
    score_color = green if pct >= 70 else red

    # Get sheet info
    sheet_ids = [r.sheet_id for r in results]
    sheets = []
    for sid in sheet_ids:
        base = sid.rstrip('ab') if sid and sid[-1] in 'ab' else sid
        if base not in sheets:
            sheets.append(base)
    sheets_range = f"{sheets[0]} - {sheets[-1]}" if len(sheets) > 1 else sheets[0] if sheets else "?"

    # Title
    title_table = Table([["KUMON WORKSHEET REPORT"]], colWidths=[170 * mm])
    title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 22),
        ('TEXTCOLOR', (0, 0), (-1, -1), blue),
    ]))
    content.append(title_table)
    content.append(Spacer(1, 15))

    # Info table
    today = datetime.now().strftime("%d %B %Y")
    info_data = [
        ["Date:", today],
        ["Worksheets:", f"{sheets_range} ({len(results)} pages)"],
    ]
    if student_name:
        info_data.insert(0, ["Student:", student_name])
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

    # Score section
    score_table = Table(
        [[f"{correct} / {total_q}"], [f"{pct:.1f}% — Grade {grade}"]],
        colWidths=[170 * mm],
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
    content.append(Paragraph(
        "Sheet Breakdown",
        ParagraphStyle('H2', fontSize=14, fontName='Helvetica-Bold')
    ))
    content.append(Spacer(1, 8))

    # Build sheet breakdown data
    sheet_data = [['Sheet', 'Questions', 'Correct', 'Mistakes', 'Grade', 'Status']]
    sheet_stats = {}
    for r in results:
        sid = r.sheet_id
        base = sid.rstrip('ab') if sid and sid[-1] in 'ab' else sid
        if base not in sheet_stats:
            sheet_stats[base] = {"questions": 0, "errors": 0}
        sheet_stats[base]["questions"] += r.total_questions
        sheet_stats[base]["errors"] += len(r.errors)

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
    # Alternate row colours
    for i in range(1, len(sheet_data)):
        bg = colors.white if i % 2 == 1 else colors.HexColor('#f9fafb')
        breakdown_table.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), bg)]))
    content.append(breakdown_table)
    content.append(Spacer(1, 25))

    # Errors table
    all_errors = []
    for r in results:
        for e in r.errors:
            all_errors.append({"sheet": r.sheet_id, **e.model_dump()})

    if all_errors:
        content.append(Paragraph(
            "Corrections Needed",
            ParagraphStyle('H2', fontSize=14, fontName='Helvetica-Bold')
        ))
        content.append(Spacer(1, 5))
        content.append(Paragraph(
            f"Please review and correct these {len(all_errors)} mistake{'s' if len(all_errors) > 1 else ''}:",
            ParagraphStyle('Msg', fontSize=10, textColor=grey)
        ))
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
            ('TEXTCOLOR', (3, 1), (3, -1), red),
            ('TEXTCOLOR', (4, 1), (4, -1), green),
            ('FONTNAME', (3, 1), (4, -1), 'Helvetica-Bold'),
        ]))
        content.append(err_table)
    else:
        # Perfect score message
        perfect_table = Table(
            [["PERFECT SCORE!"], ["All answers correct. Excellent work!"]],
            colWidths=[170 * mm],
            rowHeights=[25, 20]
        )
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
