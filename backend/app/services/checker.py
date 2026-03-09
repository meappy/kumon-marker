"""Worksheet validation service.

Supports two validation methods (configurable via VALIDATION_METHOD):
- "ocr": Tesseract OCR for sheet ID extraction (fast, free, default)
- "llm": Vision provider for sheet ID extraction (more robust for scanned PDFs)
"""

import io
import re
from pathlib import Path

import fitz
import pytesseract
from PIL import Image

from app.models.schemas import ValidationResult
from app.core.config import get_effective_setting


def _preprocess_for_ocr(img: Image.Image) -> Image.Image:
    """Pre-process image for better OCR accuracy."""
    if img.mode != "L":
        img = img.convert("L")
    return img


def _extract_sheet_id_with_ocr(image_bytes: bytes) -> str | None:
    """Extract sheet ID from image using Tesseract OCR."""
    try:
        img = Image.open(io.BytesIO(image_bytes))

        width, height = img.size
        crop_box = (0, 0, int(width * 0.3), int(height * 0.12))
        top_left = img.crop(crop_box)
        top_left_processed = _preprocess_for_ocr(top_left)

        text = pytesseract.image_to_string(
            top_left_processed,
            config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ab",
        )
        text_upper = text.upper().strip()
        print(f"OCR raw text (top-left): '{text_upper}'", flush=True)

        match = re.search(r"([A-Z]\s*\d{1,3}\s*[AB]?)", text_upper)
        if match:
            sheet_id = re.sub(r"\s+", "", match.group(1))
            print(f"OCR matched sheet_id: '{sheet_id}'", flush=True)
            if re.match(r"^[A-Z]\d{1,3}[AB]?$", sheet_id):
                return sheet_id

        # Try with different PSM mode
        text = pytesseract.image_to_string(top_left_processed, config="--psm 6")
        text_upper = text.upper()
        print(f"OCR raw text (psm 6): '{text_upper[:100]}'", flush=True)

        match = re.search(r"([A-Z]\s*\d{1,3}\s*[AB]?)", text_upper)
        if match:
            sheet_id = re.sub(r"\s+", "", match.group(1))
            if re.match(r"^[A-Z]\d{1,3}[AB]?$", sheet_id):
                return sheet_id

        # Last resort: full image
        img_processed = _preprocess_for_ocr(img)
        text = pytesseract.image_to_string(img_processed, config="--psm 6")
        text_upper = text.upper()

        match = re.search(r"([A-Z]\s*\d{1,3}\s*[AB]?)", text_upper)
        if match:
            sheet_id = re.sub(r"\s+", "", match.group(1))
            if re.match(r"^[A-Z]\d{1,3}[AB]?$", sheet_id):
                return sheet_id

    except Exception as e:
        print(f"OCR extraction error: {e}", flush=True)

    return None


def _extract_topic_with_ocr(image_bytes: bytes) -> str | None:
    """Extract topic from image using Tesseract OCR."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
        crop_box = (0, 0, int(width * 0.5), int(height * 0.15))
        top_region = img.crop(crop_box)
        top_region_processed = _preprocess_for_ocr(top_region)

        text = pytesseract.image_to_string(top_region_processed, config="--psm 6")
        text_lower = text.lower()
        print(f"OCR topic text: '{text_lower[:100]}'", flush=True)

        topics = [
            ("reduction", "Reduction"),
            ("reduce", "Reduction"),
            ("subtraction", "Subtraction"),
            ("subtracting", "Subtraction"),
            ("addition", "Addition"),
            ("adding", "Addition"),
            ("multiplication", "Multiplication"),
            ("multiply", "Multiplication"),
            ("division", "Division"),
            ("dividing", "Division"),
            ("fraction", "Fractions"),
            ("integration", "Integration"),
            ("factori", "Factorisation"),
        ]

        for keyword, topic in topics:
            if keyword in text_lower:
                print(f"OCR found topic: {topic}", flush=True)
                return topic

    except Exception as e:
        print(f"OCR topic extraction error: {e}", flush=True)

    return None


def _detect_topic_from_text(text: str) -> str | None:
    """Detect topic from text keywords."""
    text_lower = text.lower()
    if "subtraction" in text_lower or "subtracting" in text_lower:
        return "Subtraction"
    elif "addition" in text_lower or "adding" in text_lower:
        return "Addition"
    elif "multiplication" in text_lower or "multiply" in text_lower:
        return "Multiplication"
    elif "division" in text_lower or "dividing" in text_lower:
        return "Division"
    elif "reduction" in text_lower or "reduce" in text_lower:
        return "Reduction"
    elif "fraction" in text_lower:
        return "Fractions"
    elif "integration" in text_lower:
        return "Integration"
    return None


def _validate_with_vision(image_bytes: bytes) -> ValidationResult:
    """Validate a scanned worksheet using a vision provider.

    Used as fallback when text extraction fails (image-only PDFs),
    or as the primary method when validation_method="llm".
    """
    from app.services.providers import get_validation_provider, parse_json_response

    prompt = """Look at this image and determine if it's a Kumon worksheet.

The sheet ID is printed in the TOP LEFT corner (e.g., "D166a", "B161a", "C26a", "B71a").
It consists of: one uppercase letter + 1 to 3 DIGITS + optionally 'a' or 'b'.
READ EVERY DIGIT CAREFULLY — do not skip or drop any digits. For example, "B71a" has TWO digits (7 and 1), not one.

ALSO CHECK the TOP RIGHT corner — Kumon worksheets often print the letter and number again there (e.g., "B 71") which can help confirm the sheet ID.

The topic is printed below or near the sheet ID (e.g., "Reduction", "Addition", "Subtraction", "Division", "Multiplication", "Fractions", "Integration").
The student name is handwritten in the "Name" field.

If it IS a Kumon worksheet, respond with JSON:
{"is_kumon": true, "sheet_id": "<exact ID from top left like D166a>", "topic": "<topic name or null>", "student_name": "<handwritten name or null>"}

If it is NOT a Kumon worksheet, respond with:
{"is_kumon": false}

Only respond with the JSON, nothing else."""

    try:
        provider = get_validation_provider()
        output = provider.analyse_image(image_bytes, prompt)
        print(f"Vision validation output (first 200 chars): {output[:200]}", flush=True)
        result = parse_json_response(output)

        if result and result.get("is_kumon"):
            return ValidationResult(
                is_kumon=True,
                sheet_id=result.get("sheet_id"),
                subject="maths",
                topic=result.get("topic"),
                student_name=result.get("student_name"),
            )
    except Exception as e:
        print(f"Vision validation error: {e}")

    return ValidationResult(is_kumon=False)


def validate_kumon_from_bytes(
    pdf_bytes: bytes, extract_name: bool = True
) -> ValidationResult:
    """Validate that PDF bytes represent a Kumon worksheet.

    First tries text extraction, falls back to configured validation method.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = doc[0].get_text()
        text_upper = text.upper()

        # Use higher DPI (200) for validation to improve digit recognition
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(200 / 72, 200 / 72))
        image_bytes = pix.tobytes("png")
        doc.close()

        if not text.strip() or "KUMON" not in text_upper:
            if not text.strip():
                print("No text layer found, using vision model for validation...")
            else:
                print("No KUMON keyword in text, using vision model for validation...")
            return _validate_with_vision(image_bytes)

        # Text-based validation (faster, no API cost)
        sheet_match = re.search(r"\b([A-Z]\s*\d+\s*[ABab]?)\b", text_upper)
        sheet_id = re.sub(r"\s+", "", sheet_match.group(1)) if sheet_match else None

        # Extract student name using vision model (handwriting recognition)
        student_name = None
        if extract_name:
            try:
                from app.services.ocr import extract_name_with_vision

                student_name = extract_name_with_vision(image_bytes)
            except Exception as e:
                print(f"Name extraction error: {e}")

        return ValidationResult(
            is_kumon=True,
            sheet_id=sheet_id,
            subject="maths",
            topic=_detect_topic_from_text(text),
            student_name=student_name,
        )

    except Exception as e:
        print(f"Validation error: {e}")
        return ValidationResult(is_kumon=False)


def validate_kumon_worksheet(pdf_path: Path) -> ValidationResult:
    """Validate that a PDF is a Kumon worksheet.

    Respects the validation_method setting:
    - "ocr": Text layer -> Tesseract OCR -> vision fallback
    - "llm": Text layer -> vision provider directly (skips OCR)
    """
    validation_method = get_effective_setting("validation_method", "ocr")

    try:
        doc = fitz.open(pdf_path)
        text = doc[0].get_text()
        text_upper = text.upper()

        # If no text layer or no KUMON keyword, use configured fallback
        if not text.strip() or "KUMON" not in text_upper:
            if not text.strip():
                print("No text layer found...")
            # Use higher DPI (200) for validation to improve digit recognition
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(200 / 72, 200 / 72))
            image_bytes = pix.tobytes("png")
            doc.close()

            if validation_method == "llm":
                print("Using LLM vision provider for validation...")
                return _validate_with_vision(image_bytes)

            # OCR method: try Tesseract first, then vision fallback
            print("Trying OCR extraction...")
            ocr_sheet_id = _extract_sheet_id_with_ocr(image_bytes)
            ocr_topic = _extract_topic_with_ocr(image_bytes)

            if ocr_sheet_id:
                print(f"OCR found sheet_id: {ocr_sheet_id}, topic: {ocr_topic}")
                return ValidationResult(
                    is_kumon=True,
                    sheet_id=ocr_sheet_id,
                    subject="maths",
                    topic=ocr_topic,
                )

            # Fall back to vision model if OCR didn't find sheet ID
            print("OCR did not find sheet ID, falling back to vision model...")
            return _validate_with_vision(image_bytes)

        doc.close()

        # Text-based validation (faster, no API cost)
        sheet_match = re.search(r"\b([A-Z]\s*\d+\s*[ABab]?)\b", text_upper)
        sheet_id = re.sub(r"\s+", "", sheet_match.group(1)) if sheet_match else None

        return ValidationResult(
            is_kumon=True,
            sheet_id=sheet_id,
            subject="maths",
            topic=_detect_topic_from_text(text),
        )

    except Exception as e:
        print(f"Validation error: {e}")
        return ValidationResult(is_kumon=False)


def extract_sheet_info(sheet_id: str | None) -> tuple[str, int]:
    """Extract prefix and base number from sheet ID."""
    if not sheet_id:
        return "B", 161

    match = re.match(r"([A-Z])(\d+)", sheet_id)
    if match:
        return match.group(1), int(match.group(2))
    return "B", 161
