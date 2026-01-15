#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pymupdf",
# ]
# ///
"""
Annotate a Kumon worksheet PDF with marking results.
- Perfect pages get a green circle around the content
- Incorrect answers get a red tick mark
"""

import fitz  # PyMuPDF
from pathlib import Path


# Marking results from analysis
# Format: {page_number: [(question_num, x, y), ...]} with exact positions
# Page size is 576 x 572 points
ERRORS_WITH_POSITIONS = {
    # B161a (page 0) - Q5 wrong: 150-50=106 (should be 100)
    # Q5 is bottom of left column, answer at approx y=480
    0: [(5, 180, 485)],

    # B167a (page 12) - Q6, Q8 wrong
    # Q6: 263-38=235 (should be 225) - 2nd in right column
    # Q8: 263-49=224 (should be 214) - 4th in right column
    12: [(6, 460, 285), (8, 460, 485)],

    # B168a (page 14) - Q5 wrong: 257-38=119 (should be 219)
    # Q5 is 1st in right column on this sheet
    14: [(5, 460, 185)],

    # B168b (page 15) - Q12 wrong: 354-26=338 (should be 328)
    # Q12 is 4th in left column
    15: [(12, 180, 385)],

    # B170a (page 18) - Q3 wrong: 253-36=227 (should be 217)
    # Q3 is 3rd in left column
    18: [(3, 180, 385)],
}

# Colours
GREEN = (0.133, 0.773, 0.369)  # #22c55e
RED = (0.937, 0.267, 0.267)    # #ef4444


def draw_circle_around_page(page: fitz.Page) -> None:
    """Draw a large green circle around the content area of the page."""
    rect = page.rect
    # Create an oval that fits within the page margins
    margin = 30
    circle_rect = fitz.Rect(
        margin,
        margin + 50,  # Account for header
        rect.width - margin,
        rect.height - margin
    )

    shape = page.new_shape()
    shape.draw_oval(circle_rect)
    shape.finish(
        color=GREEN,
        width=3,
        stroke_opacity=0.8,
    )
    shape.commit()


def draw_tick(page: fitz.Page, x: float, y: float) -> None:
    """Draw a red tick mark at the specified position."""
    shape = page.new_shape()

    # Draw a tick/check mark
    # Start point, down-left point, up-right point
    size = 15
    shape.draw_line(
        fitz.Point(x, y),
        fitz.Point(x + size * 0.4, y + size * 0.6)
    )
    shape.draw_line(
        fitz.Point(x + size * 0.4, y + size * 0.6),
        fitz.Point(x + size, y - size * 0.3)
    )

    shape.finish(
        color=RED,
        width=2.5,
        stroke_opacity=0.9,
    )
    shape.commit()


def annotate_pdf(input_path: Path, output_path: Path) -> None:
    """Annotate the PDF with marking results."""
    doc = fitz.open(input_path)

    for page_num in range(len(doc)):
        page = doc[page_num]

        if page_num in ERRORS_WITH_POSITIONS:
            # This page has errors - draw ticks next to wrong answers
            for q_num, x, y in ERRORS_WITH_POSITIONS[page_num]:
                draw_tick(page, x, y)
        else:
            # Perfect page - draw circle around it
            draw_circle_around_page(page)

    # Save the annotated PDF
    doc.save(output_path)
    doc.close()
    print(f"Annotated PDF saved to: {output_path}")


def main():
    input_pdf = Path("/Users/gerald/Downloads/20260114130247_001.pdf")
    output_pdf = Path("/Users/gerald/Projects/kumon-marker/marked/20260114130247_001_marked.pdf")

    # Create output directory if needed
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    annotate_pdf(input_pdf, output_pdf)

    # Print summary
    total_pages = 20
    perfect_pages = total_pages - len(ERRORS_WITH_POSITIONS)
    error_pages = len(ERRORS_WITH_POSITIONS)
    total_errors = sum(len(errs) for errs in ERRORS_WITH_POSITIONS.values())

    print(f"\n{'='*50}")
    print("MARKING SUMMARY")
    print(f"{'='*50}")
    print(f"Total pages: {total_pages}")
    print(f"Perfect pages (circled): {perfect_pages}")
    print(f"Pages with errors: {error_pages}")
    print(f"Total errors marked: {total_errors}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
