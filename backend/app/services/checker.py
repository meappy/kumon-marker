"""Worksheet validation service."""

import io
import re
from pathlib import Path

import fitz
import pytesseract
from PIL import Image

from app.models.schemas import ValidationResult


def _extract_sheet_id_with_ocr(image_bytes: bytes) -> str | None:
    """
    Extract sheet ID from image using Tesseract OCR.
    Focuses on top-left region where sheet ID is printed (e.g., "D166a").
    Returns normalized sheet ID or None if not found.
    """
    try:
        # Load image
        img = Image.open(io.BytesIO(image_bytes))

        # Crop to top-left region (roughly 25% width, 15% height)
        # This is where the sheet ID is typically printed
        width, height = img.size
        crop_box = (0, 0, int(width * 0.25), int(height * 0.15))
        top_left = img.crop(crop_box)

        # Run OCR on cropped region
        text = pytesseract.image_to_string(top_left, config='--psm 6')
        text_upper = text.upper()

        # Extract sheet ID pattern: Letter + 1-3 digits + optional a/b
        # E.g., "D166a", "B161", "C26A", "O5b"
        match = re.search(r'\b([A-Z]\s*\d{1,3}\s*[AB]?)\b', text_upper)
        if match:
            # Normalize: remove spaces, ensure uppercase
            sheet_id = re.sub(r'\s+', '', match.group(1))
            # Validate format
            if re.match(r'^[A-Z]\d{1,3}[AB]?$', sheet_id):
                return sheet_id

        # If not found in cropped region, try full image
        text = pytesseract.image_to_string(img, config='--psm 6')
        text_upper = text.upper()
        match = re.search(r'\b([A-Z]\s*\d{1,3}\s*[AB]?)\b', text_upper)
        if match:
            sheet_id = re.sub(r'\s+', '', match.group(1))
            if re.match(r'^[A-Z]\d{1,3}[AB]?$', sheet_id):
                return sheet_id

    except Exception as e:
        print(f"OCR extraction error: {e}")

    return None


def _extract_topic_with_ocr(image_bytes: bytes) -> str | None:
    """
    Extract topic from image using Tesseract OCR.
    Looks for keywords like "Reduction", "Addition", etc.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))

        # Crop to top region where topic is printed (below sheet ID)
        width, height = img.size
        crop_box = (0, 0, int(width * 0.5), int(height * 0.2))
        top_region = img.crop(crop_box)

        text = pytesseract.image_to_string(top_region, config='--psm 6')
        text_lower = text.lower()

        # Check for topic keywords
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
        ]

        for keyword, topic in topics:
            if keyword in text_lower:
                return topic

    except Exception as e:
        print(f"OCR topic extraction error: {e}")

    return None


def _validate_with_vision(image_bytes: bytes) -> ValidationResult:
    """
    Validate a scanned worksheet using vision model.
    Used as fallback when text extraction fails (image-only PDFs).
    """
    from app.core.config import get_effective_setting

    mode = get_effective_setting("claude_mode", "ollama")

    prompt = """Look at this image and determine if it's a Kumon worksheet.

The sheet ID is printed in the TOP LEFT corner (e.g., "D166a", "B161a", "C26a", "O5a").
It's a single letter followed by 1-3 digits, optionally followed by 'a' or 'b'.
The topic is printed below or near the sheet ID (e.g., "Reduction", "Addition", "Subtraction", "Division", "Multiplication", "Fractions", "Integration").
The student name is handwritten in the "Name" field.

If it IS a Kumon worksheet, respond with JSON:
{"is_kumon": true, "sheet_id": "<exact ID from top left like D166a>", "topic": "<topic name or null>", "student_name": "<handwritten name or null>"}

If it is NOT a Kumon worksheet, respond with:
{"is_kumon": false}

Only respond with the JSON, nothing else."""

    try:
        if mode == "gemini":
            result = _vision_validate_gemini(image_bytes, prompt)
        elif mode == "ollama":
            result = _vision_validate_ollama(image_bytes, prompt)
        elif mode == "api":
            result = _vision_validate_api(image_bytes, prompt)
        else:  # cli
            result = _vision_validate_cli(image_bytes, prompt)

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


def _parse_vision_response(text: str) -> dict | None:
    """Parse JSON from vision model response."""
    import json
    # Try to extract JSON from response
    text = text.strip()
    # Handle markdown code blocks
    if "```" in text:
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            text = match.group(1)
    # Find JSON object
    match = re.search(r'\{[^{}]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def _vision_validate_gemini(image_bytes: bytes, prompt: str) -> dict | None:
    """Validate using Gemini vision."""
    from google import genai
    from PIL import Image
    from io import BytesIO
    from app.core.config import get_effective_setting

    api_key = get_effective_setting("gemini_api_key", "")
    model = get_effective_setting("gemini_model", "gemini-2.0-flash")

    if not api_key:
        return None

    client = genai.Client(api_key=api_key)
    image = Image.open(BytesIO(image_bytes))
    response = client.models.generate_content(model=model, contents=[prompt, image])
    return _parse_vision_response(response.text)


def _vision_validate_ollama(image_bytes: bytes, prompt: str) -> dict | None:
    """Validate using Ollama vision."""
    import base64
    import httpx
    from app.core.config import get_effective_setting

    base_url = get_effective_setting("ollama_base_url", "http://localhost:11434")
    model = get_effective_setting("ollama_model", "llava:7b")
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "images": [image_b64], "stream": False},
        )
        response.raise_for_status()
        return _parse_vision_response(response.json().get("response", ""))


def _vision_validate_api(image_bytes: bytes, prompt: str) -> dict | None:
    """Validate using Anthropic API."""
    import base64
    import anthropic
    from app.core.config import get_effective_setting

    api_key = get_effective_setting("anthropic_api_key", "")
    model = get_effective_setting("anthropic_model", "claude-haiku-3-5-20241022")

    if not api_key:
        return None

    client = anthropic.Anthropic(api_key=api_key)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.messages.create(
        model=model,
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_b64}},
                {"type": "text", "text": prompt}
            ]
        }]
    )
    return _parse_vision_response(response.content[0].text)


def _vision_validate_cli(image_bytes: bytes, prompt: str) -> dict | None:
    """Validate using Claude CLI - uses shared function from ocr.py."""
    from app.services.ocr import run_claude_cli

    output = run_claude_cli(prompt, image_bytes)
    if output:
        print(f"Claude CLI output (first 200 chars): {output[:200]}", flush=True)
        return _parse_vision_response(output)
    return None


def validate_kumon_from_bytes(pdf_bytes: bytes, extract_name: bool = True) -> ValidationResult:
    """
    Validate that PDF bytes represent a Kumon worksheet.
    First tries text extraction, falls back to vision model for scanned PDFs.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = doc[0].get_text()
        text_upper = text.upper()

        # Convert first page to image (needed for vision fallback and name extraction)
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
        image_bytes = pix.tobytes("png")
        doc.close()

        # If no text found (scanned PDF), try OCR first, then vision model
        if not text.strip() or "KUMON" not in text_upper:
            if not text.strip():
                print("No text layer found, trying OCR extraction...")

            # Try OCR first (faster, no API cost)
            ocr_sheet_id = _extract_sheet_id_with_ocr(image_bytes)
            ocr_topic = _extract_topic_with_ocr(image_bytes)

            if ocr_sheet_id:
                print(f"OCR found sheet_id: {ocr_sheet_id}, topic: {ocr_topic}")
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
                    sheet_id=ocr_sheet_id,
                    subject="maths",
                    topic=ocr_topic,
                    student_name=student_name,
                )

            # Fall back to vision model if OCR didn't find sheet ID
            print("OCR did not find sheet ID, falling back to vision model...")
            return _validate_with_vision(image_bytes)

        # Text-based validation (faster, no API cost)
        sheet_match = re.search(r'\b([A-Z]\s*\d+\s*[ab]?)\b', text_upper)
        sheet_id = re.sub(r'\s+', '', sheet_match.group(1)) if sheet_match else None

        # Extract student name using vision model (handwriting recognition)
        student_name = None
        if extract_name:
            try:
                from app.services.ocr import extract_name_with_vision
                student_name = extract_name_with_vision(image_bytes)
            except Exception as e:
                print(f"Name extraction error: {e}")

        # Detect subject/topic from keywords
        subject = "maths"
        topic = None
        text_lower = text.lower()
        if "subtraction" in text_lower or "subtracting" in text_lower:
            topic = "Subtraction"
        elif "addition" in text_lower or "adding" in text_lower:
            topic = "Addition"
        elif "multiplication" in text_lower or "multiply" in text_lower:
            topic = "Multiplication"
        elif "division" in text_lower or "dividing" in text_lower:
            topic = "Division"
        elif "reduction" in text_lower or "reduce" in text_lower:
            topic = "Reduction"
        elif "fraction" in text_lower:
            topic = "Fractions"
        elif "integration" in text_lower:
            topic = "Integration"

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
    Validate that a PDF is a Kumon worksheet.
    First tries text extraction, falls back to vision model for scanned PDFs.
    """
    try:
        doc = fitz.open(pdf_path)
        text = doc[0].get_text()
        text_upper = text.upper()

        # If no text found (scanned PDF), try OCR first, then vision model
        if not text.strip() or "KUMON" not in text_upper:
            if not text.strip():
                print("No text layer found, trying OCR extraction...")
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
            image_bytes = pix.tobytes("png")
            doc.close()

            # Try OCR first (faster, no API cost)
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
        sheet_match = re.search(r'\b([A-Z]\s*\d+\s*[ab]?)\b', text_upper)
        sheet_id = re.sub(r'\s+', '', sheet_match.group(1)) if sheet_match else None

        # Detect subject/topic from keywords
        subject = "maths"
        topic = None
        text_lower = text.lower()
        if "subtraction" in text_lower or "subtracting" in text_lower:
            topic = "Subtraction"
        elif "addition" in text_lower or "adding" in text_lower:
            topic = "Addition"
        elif "multiplication" in text_lower or "multiply" in text_lower:
            topic = "Multiplication"
        elif "division" in text_lower or "dividing" in text_lower:
            topic = "Division"
        elif "reduction" in text_lower or "reduce" in text_lower:
            topic = "Reduction"
        elif "fraction" in text_lower:
            topic = "Fractions"
        elif "integration" in text_lower:
            topic = "Integration"

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
