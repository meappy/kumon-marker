"""Worksheet validation service."""

import io
import re
from pathlib import Path

import fitz

from app.models.schemas import ValidationResult


def validate_kumon_from_bytes(pdf_bytes: bytes, extract_name: bool = True) -> ValidationResult:
    """
    Validate that PDF bytes represent a Kumon worksheet by checking for KUMON text.
    Uses text extraction for validation, vision model for name extraction.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = doc[0].get_text()
        text_upper = text.upper()

        if "KUMON" not in text_upper:
            doc.close()
            return ValidationResult(is_kumon=False)

        # Extract sheet ID (e.g., "B161a", "C26a") from text
        sheet_match = re.search(r'\b([A-Z]\s*\d+\s*[ab]?)\b', text_upper)
        sheet_id = re.sub(r'\s+', '', sheet_match.group(1)) if sheet_match else None

        # Extract student name using vision model (handwriting recognition)
        student_name = None
        if extract_name:
            try:
                # Convert first page to image for vision model
                pix = doc[0].get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
                image_bytes = pix.tobytes("png")

                from app.services.ocr import extract_name_with_vision
                student_name = extract_name_with_vision(image_bytes)
            except Exception as e:
                print(f"Name extraction error: {e}")

        doc.close()

        # Detect subject/topic from keywords
        subject = "maths"
        topic = None
        text_lower = text.lower()
        if "subtraction" in text_lower:
            topic = "subtraction"
        elif "addition" in text_lower:
            topic = "addition"
        elif "multiplication" in text_lower:
            topic = "multiplication"
        elif "division" in text_lower:
            topic = "division"

        return ValidationResult(
            is_kumon=True,
            sheet_id=sheet_id,
            subject=subject,
            topic=topic,
            student_name=student_name,
        )

    except Exception as e:
        print(f"Validation error: {e}")
        return ValidationResult(is_kumon=False)


def validate_kumon_worksheet(pdf_path: Path) -> ValidationResult:
    """
    Validate that a PDF is a Kumon worksheet by checking for KUMON text.
    Uses text extraction - fast and doesn't use API credits.
    """
    try:
        doc = fitz.open(pdf_path)
        text = doc[0].get_text().upper()
        doc.close()

        if "KUMON" not in text:
            return ValidationResult(is_kumon=False)

        # Extract sheet ID (e.g., "B161a", "C26a") from text
        sheet_match = re.search(r'\b([A-Z]\s*\d+\s*[ab]?)\b', text)
        sheet_id = re.sub(r'\s+', '', sheet_match.group(1)) if sheet_match else None

        # Detect subject/topic from keywords
        subject = "maths"
        topic = None
        text_lower = text.lower()
        if "subtraction" in text_lower:
            topic = "subtraction"
        elif "addition" in text_lower:
            topic = "addition"
        elif "multiplication" in text_lower:
            topic = "multiplication"
        elif "division" in text_lower:
            topic = "division"

        return ValidationResult(
            is_kumon=True,
            sheet_id=sheet_id,
            subject=subject,
            topic=topic,
        )

    except Exception as e:
        print(f"Validation error: {e}")
        return ValidationResult(is_kumon=False)


def extract_sheet_info(sheet_id: str | None) -> tuple[str, int]:
    """Extract prefix and base number from sheet ID."""
    if not sheet_id:
        return "B", 161

    match = re.match(r'([A-Z])(\d+)', sheet_id)
    if match:
        return match.group(1), int(match.group(2))
    return "B", 161
