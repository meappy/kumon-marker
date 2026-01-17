"""PDF annotation service for marking worksheets."""

import fitz
from pathlib import Path

from app.models.schemas import PageResult

GREEN = (0.133, 0.773, 0.369)
RED = (0.937, 0.267, 0.267)


def draw_circle(page: fitz.Page) -> None:
    """Draw a green circle around the entire page (all correct)."""
    rect = page.rect
    shape = page.new_shape()
    shape.draw_oval(fitz.Rect(30, 60, rect.width - 30, rect.height - 30))
    shape.finish(color=GREEN, width=3, stroke_opacity=0.8)
    shape.commit()


def draw_tick(page: fitz.Page, x: float, y: float) -> None:
    """Draw a red tick mark next to an incorrect answer."""
    shape = page.new_shape()
    shape.draw_line(fitz.Point(x, y), fitz.Point(x + 6, y + 9))
    shape.draw_line(fitz.Point(x + 6, y + 9), fitz.Point(x + 15, y - 5))
    shape.finish(color=RED, width=2.5, stroke_opacity=0.9)
    shape.commit()


def create_marked_pdf(
    input_path: Path,
    output_path: Path,
    results: list[PageResult]
) -> None:
    """Create a marked PDF with circles for correct pages and ticks for errors."""
    doc = fitz.open(input_path)
    errors_by_page = {r.page_num: r.errors for r in results}

    for i in range(len(doc)):
        page = doc[i]
        errors = errors_by_page.get(i, [])
        if errors:
            for e in errors:
                draw_tick(page, e.x, e.y)
        else:
            draw_circle(page)

    doc.save(output_path)
    doc.close()
