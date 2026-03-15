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
    # Maths topics
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
    # English topics
    elif "vocabulary" in text_lower:
        return "Vocabulary"
    elif "grammar" in text_lower:
        return "Grammar"
    elif "sentence" in text_lower:
        return "Sentence Building"
    elif "paragraph" in text_lower:
        return "Paragraph Building"
    elif "summar" in text_lower:
        return "Summarisation"
    elif "reading" in text_lower:
        return "Reading"
    return None


def _detect_subject_from_text(text: str) -> str:
    """Detect subject (maths or english) from text keywords."""
    text_lower = text.lower()
    maths_keywords = [
        "addition",
        "subtraction",
        "multiplication",
        "division",
        "reduction",
        "fraction",
        "integration",
        "factori",
        "subtract",
        "multiply",
        "divide",
        "add.",
    ]
    english_keywords = [
        "vocabulary",
        "grammar",
        "sentence",
        "paragraph",
        "reading",
        "summarisation",
        "read the",
        "fill in",
        "complete the sentence",
        "choose the word",
    ]
    maths_score = sum(1 for kw in maths_keywords if kw in text_lower)
    english_score = sum(1 for kw in english_keywords if kw in text_lower)
    return "english" if english_score > maths_score else "maths"


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

Determine the SUBJECT:
- "maths" if it contains arithmetic, equations, numbers, calculations
- "english" if it contains reading passages, vocabulary, grammar, sentence completion, fill-in-the-blank with words

The topic is printed below or near the sheet ID.
- Maths topics: "Reduction", "Addition", "Subtraction", "Division", "Multiplication", "Fractions", "Integration"
- English topics: "Reading", "Vocabulary", "Grammar", "Sentence Building", "Paragraph Building", "Summarisation"

The student name is handwritten in the "Name" field.

If it IS a Kumon worksheet, respond with JSON:
{"is_kumon": true, "sheet_id": "<exact ID from top left like D166a>", "subject": "maths or english", "topic": "<topic name or null>", "student_name": "<handwritten name or null>"}

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
                subject=result.get("subject", "maths"),
                topic=result.get("topic"),
                student_name=result.get("student_name"),
            )
    except Exception as e:
        print(f"Vision validation error: {e}")

    return ValidationResult(is_kumon=False)


def _fix_ocr_text(text: str) -> str:
    """Fix common OCR substitution errors in scanned text.

    Brother scanners often embed low-quality OCR that confuses similar chars.
    """
    replacements = {
        "I": "1",  # capital I → 1
        "l": "1",  # lowercase L → 1
        "O": "0",  # capital O → 0
        "S": "5",  # S → 5
        "Z": "2",  # Z → 2
    }
    result = []
    for ch in text:
        result.append(replacements.get(ch, ch))
    return "".join(result)


def _extract_sheet_id_from_text(text: str) -> str | None:
    """Extract Kumon sheet ID from PDF text layer.

    Handles poor OCR quality by checking the first line (where sheet ID
    always appears) and applying common OCR error corrections.
    """
    text_upper = text.upper()

    # Try the first line first — sheet ID is always at the top
    first_line = text_upper.split("\n")[0].strip()
    print(f"Text layer first line: {repr(first_line)}", flush=True)

    # Apply OCR corrections to first line and try to match
    fixed_first = _fix_ocr_text(first_line)
    match = re.match(r"^([A-Z])(\d{1,3})([AB]?)\b", fixed_first)
    if match:
        sheet_id = f"{match.group(1)}{match.group(2)}{match.group(3)}"
        print(f"Sheet ID from first line (OCR-corrected): {sheet_id}", flush=True)
        return sheet_id

    # Also try matching the original first line (in case OCR was fine)
    match = re.match(r"^([A-Z])\s*(\d{1,3})\s*([ABab]?)", first_line)
    if match:
        sheet_id = f"{match.group(1)}{match.group(2)}{match.group(3).upper()}"
        print(f"Sheet ID from first line: {sheet_id}", flush=True)
        return sheet_id

    # Fallback: search entire text (less reliable due to false matches)
    sheet_match = re.search(r"\b([A-Z]\s*\d+\s*[ABab]?)\b", text_upper)
    if sheet_match:
        sheet_id = re.sub(r"\s+", "", sheet_match.group(1))
        print(f"Sheet ID from full text search: {sheet_id}", flush=True)
        return sheet_id

    return None


def _is_kumon_text(text_upper: str) -> bool:
    """Check if text contains Kumon markers, tolerating OCR errors."""
    # Exact match
    if "KUMON" in text_upper:
        return True
    # Common OCR misreads: KUMQN, KUM0N, KUMDN
    if re.search(r"KUM[O0Q][MN]", text_upper):
        return True
    # Check for Kumon-specific phrases
    if "KUMON INSTITUTE" in text_upper or "© 20" in text_upper:
        return True
    return False


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

        if not text.strip() or not _is_kumon_text(text_upper):
            if not text.strip():
                print("No text layer found, using vision model for validation...")
            else:
                print("No KUMON keyword in text, using vision model for validation...")
            return _validate_with_vision(image_bytes)

        # Text-based validation with OCR error correction
        sheet_id = _extract_sheet_id_from_text(text)

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
            subject=_detect_subject_from_text(text),
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
    - "llm": Always use vision provider (scanner OCR text is unreliable)
    """
    validation_method = get_effective_setting("validation_method", "ocr")

    try:
        doc = fitz.open(pdf_path)
        text = doc[0].get_text()
        text_upper = text.upper()

        # Use higher DPI (200) for validation to improve digit recognition
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(200 / 72, 200 / 72))
        image_bytes = pix.tobytes("png")
        doc.close()

        # When validation_method is "llm", always use vision model.
        # Scanner-embedded OCR is too unreliable (e.g. I→1, O→0, 7→6).
        if validation_method == "llm":
            print("Using LLM vision provider for validation...")
            return _validate_with_vision(image_bytes)

        # If no text layer or no KUMON keyword, use configured fallback
        if not text.strip() or not _is_kumon_text(text_upper):
            if not text.strip():
                print("No text layer found...")

            # OCR method: try Tesseract first, then vision fallback
            print("Trying OCR extraction...")
            ocr_sheet_id = _extract_sheet_id_with_ocr(image_bytes)
            ocr_topic = _extract_topic_with_ocr(image_bytes)

            if ocr_sheet_id:
                print(f"OCR found sheet_id: {ocr_sheet_id}, topic: {ocr_topic}")
                return ValidationResult(
                    is_kumon=True,
                    sheet_id=ocr_sheet_id,
                    subject="maths",  # OCR path is maths-only for now
                    topic=ocr_topic,
                )

            # Fall back to vision model if OCR didn't find sheet ID
            print("OCR did not find sheet ID, falling back to vision model...")
            return _validate_with_vision(image_bytes)

        # Text-based validation with OCR error correction
        sheet_id = _extract_sheet_id_from_text(text)

        return ValidationResult(
            is_kumon=True,
            sheet_id=sheet_id,
            subject=_detect_subject_from_text(text),
            topic=_detect_topic_from_text(text),
        )

    except Exception as e:
        print(f"Validation error: {e}")
        return ValidationResult(is_kumon=False)


def validate_kumon_worksheet_from_bytes(pdf_bytes: bytes) -> ValidationResult:
    """Validate a Kumon worksheet from in-memory PDF bytes.

    Used by GDrive scan when text layer check fails and LLM validation is enabled.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(200 / 72, 200 / 72))
        image_bytes = pix.tobytes("png")
        doc.close()
        return _validate_with_vision(image_bytes)
    except Exception as e:
        print(f"Validation from bytes error: {e}")
        return ValidationResult(is_kumon=False)


def extract_sheet_info(sheet_id: str | None) -> tuple[str, int]:
    """Extract prefix and base number from sheet ID."""
    if not sheet_id:
        return "B", 161

    match = re.match(r"([A-Z])(\d+)", sheet_id)
    if match:
        return match.group(1), int(match.group(2))
    return "B", 161
