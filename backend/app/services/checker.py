"""Worksheet validation service."""

import re
from pathlib import Path

import fitz

from app.models.schemas import ValidationResult


def _validate_with_vision(image_bytes: bytes) -> ValidationResult:
    """
    Validate a scanned worksheet using vision model.
    Used as fallback when text extraction fails (image-only PDFs).
    """
    from app.core.config import get_effective_setting

    mode = get_effective_setting("claude_mode", "ollama")

    prompt = """Look at this image and determine if it's a Kumon worksheet.

If it IS a Kumon worksheet, respond with JSON:
{"is_kumon": true, "sheet_id": "<ID like B168a or C26a>", "topic": "<subtraction/addition/multiplication/division or null>", "student_name": "<name if visible or null>"}

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
    """Validate using Claude CLI."""
    import subprocess
    import tempfile
    import sys
    from app.core.config import get_effective_setting

    model = get_effective_setting("claude_model", "claude-sonnet-4-20250514")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(image_bytes)
        image_path = f.name

    try:
        print(f"Running claude CLI validation on {image_path} with model {model}...", flush=True)
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", model, image_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        print(f"Claude CLI returned: exit_code={result.returncode}", flush=True)
        if result.stderr:
            print(f"Claude CLI stderr: {result.stderr}", flush=True)
        if result.stdout:
            print(f"Claude CLI stdout (first 200 chars): {result.stdout[:200]}", flush=True)
        return _parse_vision_response(result.stdout)
    except Exception as e:
        print(f"Claude CLI error: {e}", file=sys.stderr, flush=True)
        raise
    finally:
        import os
        os.unlink(image_path)


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

        # If no text found (scanned PDF), use vision model
        if not text.strip() or "KUMON" not in text_upper:
            if not text.strip():
                print("No text layer found, using vision validation...")
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
    Validate that a PDF is a Kumon worksheet.
    First tries text extraction, falls back to vision model for scanned PDFs.
    """
    try:
        doc = fitz.open(pdf_path)
        text = doc[0].get_text()
        text_upper = text.upper()

        # If no text found (scanned PDF), use vision model
        if not text.strip() or "KUMON" not in text_upper:
            if not text.strip():
                print("No text layer found, using vision validation...")
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
            image_bytes = pix.tobytes("png")
            doc.close()
            return _validate_with_vision(image_bytes)

        doc.close()

        # Text-based validation (faster, no API cost)
        sheet_match = re.search(r'\b([A-Z]\s*\d+\s*[ab]?)\b', text_upper)
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
