"""OCR service for worksheet analysis - supports Anthropic API, Claude Code CLI, and Google Gemini."""

import base64
import gc
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

import fitz

from app.models.schemas import PageResult, ErrorDetail
from app.core.config import get_effective_setting

def get_questions_per_page() -> int:
    """Get configured questions per page."""
    return int(get_effective_setting("questions_per_page", 10))


def cleanup_memory():
    """Force garbage collection to free memory."""
    gc.collect()
    # Small delay to allow memory to be reclaimed
    time.sleep(1)


def pdf_page_count(pdf_path: Path) -> int:
    """Get the number of pages in a PDF."""
    doc = fitz.open(pdf_path)
    count = len(doc)
    doc.close()
    return count


def pdf_page_to_image(pdf_path: Path, page_num: int) -> bytes:
    """Convert a single PDF page to PNG image bytes."""
    doc = fitz.open(pdf_path)
    pix = doc[page_num].get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
    image_bytes = pix.tobytes("png")
    doc.close()
    return image_bytes


def run_claude_cli(prompt: str, image_bytes: bytes, model: str | None = None) -> str | None:
    """
    Shared function to call Claude CLI with an image.
    Used by both validation (checker.py) and marking (ocr.py).
    Returns the raw output text, or None on error.
    """
    if model is None:
        model = get_effective_setting("claude_model", "claude-sonnet-4-20250514")

    temp_image_path = None
    try:
        # Save image to temp file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(image_bytes)
            temp_image_path = f.name

        # Claude CLI uses the Read tool internally
        cli_prompt = f"Read the image at {temp_image_path} and then: {prompt}"

        # Call Claude Code CLI with memory limits
        env = os.environ.copy()
        env['NODE_OPTIONS'] = '--max-old-space-size=512'

        print(f"Running Claude CLI with model {model}...", flush=True)
        result = subprocess.run(
            [
                'claude',
                '-p', cli_prompt,
                '--output-format', 'text',
                '--max-turns', '3',
                '--model', model,
                '--allowedTools', 'Read',
                '--no-chrome',
                '--no-session-persistence',
                '--disable-slash-commands',
            ],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

        if result.returncode != 0:
            print(f"Claude CLI error: {result.stderr}", flush=True)
            return None

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        print("Claude CLI timeout", flush=True)
        return None
    except Exception as e:
        print(f"Claude CLI error: {e}", flush=True)
        return None
    finally:
        if temp_image_path:
            Path(temp_image_path).unlink(missing_ok=True)


def get_default_prompt(sheet_id: str, page_num: int, questions_per_page: int) -> str:
    """Get the default prompt for worksheet analysis."""
    # Note: questions_per_page is now just a hint, model should count actual questions
    return f'''Mark this Kumon worksheet page ({sheet_id}, page {page_num + 1}).

This is a Kumon maths worksheet. The student has written answers in handwriting.

TASK - Check EVERY question carefully:
1. Find ALL numbered questions on this page (they have numbers like (1), (2), etc.)
2. For EACH question:
   - Read the maths problem carefully
   - Calculate the correct answer yourself
   - Read the student's handwritten answer
   - Compare: is the student's answer CORRECT or WRONG?
3. Report ALL questions where the student's answer is WRONG

CRITICAL - Be thorough:
- Check EVERY single question, do not skip any
- Double-check your arithmetic
- Handwriting can be messy - look carefully at each digit
- Common mistakes: 6 vs 8, 1 vs 7, 4 vs 9

For each WRONG answer, estimate the position of the question number on the page:
- x: horizontal position (0=left edge, ~595=right edge). Left column questions ~480, right column ~660
- y: vertical position (0=top, ~842=bottom). First question ~280, then add ~35 for each row

Return ONLY this JSON:
{{"sheet_id": "{sheet_id}", "page_num": {page_num}, "total_questions": <ACTUAL COUNT>, "errors": [<WRONG answers only>]}}

For each WRONG answer include position:
{{"q": <number>, "problem": "<problem>", "student": "<student answer>", "correct": "<correct answer>", "x": <x position>, "y": <y position>}}

Example: Question (5) in left column, 5th row down:
{{"q": 5, "problem": "6 x 3", "student": "16", "correct": "18", "x": 480, "y": 420}}

If ALL answers are correct:
{{"sheet_id": "{sheet_id}", "page_num": {page_num}, "total_questions": <ACTUAL COUNT>, "errors": []}}'''


def get_analysis_prompt(sheet_id: str, page_num: int) -> str:
    """Get the prompt for worksheet analysis (uses custom prompt if configured)."""
    questions_per_page = get_questions_per_page()
    custom_prompt = get_effective_setting("custom_prompt", "")

    if custom_prompt:
        # Use custom prompt with placeholders replaced
        return custom_prompt.format(
            sheet_id=sheet_id,
            page_num=page_num,
            questions_per_page=questions_per_page
        )

    return get_default_prompt(sheet_id, page_num, questions_per_page)


def get_name_extraction_prompt() -> str:
    """Get prompt for extracting student name from worksheet."""
    return '''Look at this Kumon worksheet image. Find the "Name" field (usually top right area).

Read the HANDWRITTEN student name written in the Name field.

Return ONLY a JSON object:
{"name": "<the student's name>" }

If you cannot read the name or it's blank, return:
{"name": null}

ONLY output the JSON, nothing else.'''


def extract_name_from_response(output: str) -> str | None:
    """Extract name from vision model response."""
    try:
        match = re.search(r'\{[\s\S]*\}', output)
        if match:
            data = json.loads(match.group())
            name = data.get("name")
            if name and isinstance(name, str) and len(name.strip()) > 0:
                return name.strip().title()
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def extract_name_with_vision(image_bytes: bytes) -> str | None:
    """Extract student name from worksheet using vision model."""
    mode = get_effective_setting("claude_mode", "ollama")
    prompt = get_name_extraction_prompt()

    try:
        if mode == "gemini":
            return _extract_name_gemini(image_bytes, prompt)
        elif mode == "ollama":
            return _extract_name_ollama(image_bytes, prompt)
        elif mode == "api":
            return _extract_name_api(image_bytes, prompt)
        else:  # cli
            return _extract_name_cli(image_bytes, prompt)
    except Exception as e:
        print(f"Name extraction error: {e}")
        return None


def _extract_name_gemini(image_bytes: bytes, prompt: str) -> str | None:
    """Extract name using Gemini."""
    from google import genai
    from PIL import Image
    from io import BytesIO

    api_key = get_effective_setting("gemini_api_key", "")
    model = get_effective_setting("gemini_model", "gemini-2.0-flash")

    if not api_key:
        return None

    client = genai.Client(api_key=api_key)
    image = Image.open(BytesIO(image_bytes))
    response = client.models.generate_content(model=model, contents=[prompt, image])
    return extract_name_from_response(response.text)


def _extract_name_ollama(image_bytes: bytes, prompt: str) -> str | None:
    """Extract name using Ollama."""
    import httpx

    base_url = get_effective_setting("ollama_base_url", "http://localhost:11434")
    model = get_effective_setting("ollama_model", "llava:7b")
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "images": [image_b64], "stream": False},
        )
        response.raise_for_status()
        return extract_name_from_response(response.json().get("response", ""))


def _extract_name_api(image_bytes: bytes, prompt: str) -> str | None:
    """Extract name using Anthropic API."""
    import anthropic

    api_key = get_effective_setting("anthropic_api_key", "")
    model = get_effective_setting("anthropic_model", "claude-sonnet-4-20250514")

    if not api_key:
        return None

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_b64}},
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return extract_name_from_response(response.content[0].text)


def _extract_name_cli(image_bytes: bytes, prompt: str) -> str | None:
    """Extract name using Claude CLI."""
    temp_image_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(image_bytes)
            temp_image_path = f.name

        cli_prompt = f"Read the image at {temp_image_path} and then: {prompt}"
        model = get_effective_setting("claude_model", "claude-sonnet-4-20250514")

        result = subprocess.run(
            ['claude', '-p', cli_prompt, '--output-format', 'text', '--max-turns', '2',
             '--model', model, '--allowedTools', 'Read', '--no-chrome'],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            return extract_name_from_response(result.stdout)
    finally:
        if temp_image_path:
            Path(temp_image_path).unlink(missing_ok=True)
    return None


def calculate_tick_position(question_num: int, total_questions: int = 24) -> tuple[float, float]:
    """Calculate tick position based on question number for standard Kumon layout.

    Kumon worksheets typically have 2 columns:
    - Left column: questions 1-12 (or 1-half)
    - Right column: questions 13-24 (or half+1-end)

    Position is to the LEFT of the question number (where the tick should go).
    """
    # Determine if left or right column
    half = total_questions // 2 if total_questions > 12 else total_questions

    if question_num <= half:
        # Left column - tick goes LEFT of question number "(1)", "(2)", etc.
        x = 490  # Left of the question number in left column
        row = question_num - 1
    else:
        # Right column
        x = 655  # Left of the question number in right column
        row = question_num - half - 1

    # Calculate y position
    # Account for page header (~100pt) and start questions lower
    # First question around y=300, ~32px per row for typical Kumon spacing
    y = 300 + (row * 32)

    return x, y


def parse_analysis_response(output: str, sheet_id: str, page_num: int) -> PageResult:
    """Parse the JSON response from Claude."""
    match = re.search(r'\{[\s\S]*\}', output)
    if match:
        data = json.loads(match.group())
        total_q = data.get("total_questions", get_questions_per_page())

        # Process errors, adding calculated positions if not provided
        errors = []
        for e in data.get("errors", []):
            # If x,y not provided or are defaults, calculate from question number
            if "x" not in e or "y" not in e or (e.get("x") == 200 and e.get("y") == 300):
                q_num = e.get("q", 1)
                calc_x, calc_y = calculate_tick_position(q_num, total_q)
                e["x"] = e.get("x", calc_x) if e.get("x", 200) != 200 else calc_x
                e["y"] = e.get("y", calc_y) if e.get("y", 300) != 300 else calc_y
            errors.append(ErrorDetail(**e))

        return PageResult(
            sheet_id=sheet_id,  # Always use the passed-in value
            page_num=page_num,  # Always use the passed-in value (for correct annotation)
            total_questions=total_q,
            errors=errors,
        )
    raise ValueError("No valid JSON found in response")


# ============================================================================
# Option 1: Anthropic API
# ============================================================================

def analyse_page_with_api(
    image_bytes: bytes,
    page_num: int,
    sheet_id: str,
    api_key: str,
    model: str = "claude-sonnet-4-20250514",
) -> PageResult:
    """Analyse a single worksheet page using Anthropic API."""
    import anthropic

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = get_analysis_prompt(sheet_id, page_num)

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        )

        output = response.content[0].text.strip()
        return parse_analysis_response(output, sheet_id, page_num)

    except Exception as e:
        print(f"API error on page {page_num}: {e}")

    return PageResult(
        sheet_id=sheet_id,
        page_num=page_num,
        total_questions=get_questions_per_page(),
        errors=[],
    )


# ============================================================================
# Option 2: Claude Code CLI
# ============================================================================

def analyse_page_with_cli(
    image_bytes: bytes,
    page_num: int,
    sheet_id: str,
    model: str = "claude-sonnet-4-20250514",
) -> PageResult:
    """Analyse a single worksheet page using Claude Code CLI."""
    prompt = get_analysis_prompt(sheet_id, page_num)

    output = run_claude_cli(prompt, image_bytes, model)
    if output:
        return parse_analysis_response(output, sheet_id, page_num)

    return PageResult(
        sheet_id=sheet_id,
        page_num=page_num,
        total_questions=get_questions_per_page(),
        errors=[],
    )


# ============================================================================
# Option 3: Google Gemini API
# ============================================================================

def analyse_page_with_gemini(
    image_bytes: bytes,
    page_num: int,
    sheet_id: str,
    api_key: str,
    model: str = "gemini-2.0-flash",
) -> PageResult:
    """Analyse a single worksheet page using Google Gemini API with retry logic."""
    from google import genai
    from PIL import Image
    from io import BytesIO

    prompt = get_analysis_prompt(sheet_id, page_num)
    max_retries = 3

    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=api_key)

            # Convert bytes to PIL Image for Gemini
            image = Image.open(BytesIO(image_bytes))

            response = client.models.generate_content(
                model=model,
                contents=[prompt, image],
            )
            output = response.text.strip()
            return parse_analysis_response(output, sheet_id, page_num)

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "resource_exhausted" in error_str.lower():
                # Rate limited - wait and retry
                wait_time = 5 * (attempt + 1)  # 5s, 10s, 15s
                print(f"Rate limited on page {page_num}, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"Gemini API error on page {page_num}: {e}")
                break

    return PageResult(
        sheet_id=sheet_id,
        page_num=page_num,
        total_questions=get_questions_per_page(),
        errors=[],
    )


# ============================================================================
# Option 4: Ollama (Local LLM)
# ============================================================================

def analyse_page_with_ollama(
    image_bytes: bytes,
    page_num: int,
    sheet_id: str,
    base_url: str = "http://localhost:11434",
    model: str = "moondream",
) -> PageResult:
    """Analyse a single worksheet page using Ollama local LLM."""
    import httpx

    prompt = get_analysis_prompt(sheet_id, page_num)
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "images": [image_b64],
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            output = data.get("response", "").strip()
            return parse_analysis_response(output, sheet_id, page_num)

    except Exception as e:
        print(f"Ollama error on page {page_num}: {e}")

    return PageResult(
        sheet_id=sheet_id,
        page_num=page_num,
        total_questions=get_questions_per_page(),
        errors=[],
    )


# ============================================================================
# Main entry point
# ============================================================================

def analyse_worksheet(
    pdf_path: Path,
    sheet_prefix: str = "B",
    base_num: int = 161,
    progress_callback: callable = None,
) -> list[PageResult]:
    """Analyse all pages of a worksheet PDF.

    Supports four modes based on configuration:
    - 'ollama': Uses local Ollama LLM (recommended - fast, no rate limits)
    - 'gemini': Uses Google Gemini API (free tier available)
    - 'api': Uses Anthropic API (requires credits)
    - 'cli': Uses Claude Code CLI (free with Max subscription, but high memory)

    Memory-efficient: loads and processes one page at a time.

    Args:
        pdf_path: Path to the PDF file.
        sheet_prefix: Prefix for sheet IDs (e.g., "B" for B161a).
        base_num: Base number for sheet IDs.
        progress_callback: Optional callback function(current_page, total_pages)
                          called after each page is processed.
    """
    num_pages = pdf_page_count(pdf_path)

    # Generate sheet IDs (e.g., B161a, B161b, B162a, B162b, ...)
    sheet_ids = [
        f"{sheet_prefix}{base_num + i // 2}{'a' if i % 2 == 0 else 'b'}"
        for i in range(num_pages)
    ]

    # Determine which mode to use
    mode = get_effective_setting("claude_mode", "ollama")  # Default to ollama now

    # Get API keys and settings
    anthropic_api_key = get_effective_setting("anthropic_api_key", "")
    anthropic_model = get_effective_setting("anthropic_model", "claude-sonnet-4-20250514")
    gemini_api_key = get_effective_setting("gemini_api_key", "")
    gemini_model = get_effective_setting("gemini_model", "gemini-2.0-flash")
    ollama_base_url = get_effective_setting("ollama_base_url", "http://host.docker.internal:11434")
    ollama_model = get_effective_setting("ollama_model", "moondream")
    claude_model = get_effective_setting("claude_model", "claude-sonnet-4-20250514")

    # Determine actual mode based on available credentials/settings
    if mode == "ollama":
        print(f"Using Ollama local LLM mode with model {ollama_model} at {ollama_base_url}")
        analysis_mode = "ollama"
    elif mode == "gemini" and gemini_api_key:
        print(f"Using Google Gemini API mode with model {gemini_model}")
        analysis_mode = "gemini"
    elif mode == "api" and anthropic_api_key:
        print(f"Using Anthropic API mode with model {anthropic_model}")
        analysis_mode = "api"
    else:
        print(f"Using Claude Code CLI mode with model {claude_model}")
        analysis_mode = "cli"

    results = []
    for i, sheet_id in enumerate(sheet_ids):
        print(f"Analysing page {i + 1}/{num_pages} ({sheet_id})...")

        # Load single page - memory efficient
        image_bytes = pdf_page_to_image(pdf_path, i)

        if analysis_mode == "ollama":
            result = analyse_page_with_ollama(image_bytes, i, sheet_id, ollama_base_url, ollama_model)
        elif analysis_mode == "gemini":
            result = analyse_page_with_gemini(image_bytes, i, sheet_id, gemini_api_key, gemini_model)
            # Rate limit: free tier is 15 req/min, so wait 4s between requests
            if i < num_pages - 1:
                time.sleep(4)
        elif analysis_mode == "api":
            result = analyse_page_with_api(image_bytes, i, sheet_id, anthropic_api_key, anthropic_model)
        else:
            result = analyse_page_with_cli(image_bytes, i, sheet_id, claude_model)

        results.append(result)

        # Report progress after each page
        if progress_callback:
            progress_callback(i + 1, num_pages)

        # Memory cleanup after each page
        del image_bytes
        cleanup_memory()

    gc.collect()
    return results
