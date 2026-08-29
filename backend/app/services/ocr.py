"""OCR service for worksheet analysis using pluggable vision providers.

Supports Anthropic, Google Gemini, Ollama, and OpenAI via the provider
abstraction in providers.py.
"""

import gc
import json
import re
import time
from pathlib import Path

import fitz

from app.models.schemas import PageResult, ErrorDetail, WorksheetHeader
from app.core.config import get_effective_setting
from app.services.providers import get_provider


def get_questions_per_page() -> int:
    """Get configured questions per page."""
    return int(get_effective_setting("questions_per_page", 10))


def cleanup_memory():
    """Force garbage collection to free memory."""
    gc.collect()
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


def get_default_prompt(sheet_id: str, page_num: int, questions_per_page: int) -> str:
    """Get the default prompt for worksheet analysis."""
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


def get_english_prompt(sheet_id: str, page_num: int) -> str:
    """Get the prompt for English worksheet analysis."""
    return f'''Mark this Kumon English worksheet page ({sheet_id}, page {page_num + 1}).

This is a Kumon English worksheet. The student has written answers in handwriting.

TASK - Check EVERY question carefully:
1. Find ALL numbered questions/exercises on this page
2. For EACH question:
   - Read the exercise instructions and any passage text
   - Determine the correct answer (from context, word boxes, grammar rules, or passage content)
   - Read the student's handwritten answer
   - Compare: is the student's answer CORRECT or WRONG?
3. Report ALL questions where the student's answer is WRONG

EXERCISE TYPES you may encounter:
- Fill-in-the-blank from a word box: check if the student chose the right word
- Sentence completion: check grammar, spelling, and meaning
- Vocabulary: check if the correct word/definition is given
- Grammar exercises: check verb tenses, word order, punctuation
- Reading comprehension: check if the answer matches what the passage says
- True/False: check against the passage content
- Sequencing: check if the order is correct

CRITICAL - Be thorough:
- Check EVERY single question, do not skip any
- Spelling must be exact (minor capitalisation differences are OK)
- Read handwriting carefully — messy letters can look similar
- For fill-in-the-blank, only the word from the word box is correct
- For comprehension, accept answers that capture the correct meaning even if worded differently

For each WRONG answer, estimate the position of the question on the page:
- x: horizontal position (0=left edge, ~595=right edge)
- y: vertical position (0=top, ~842=bottom)

Return ONLY this JSON:
{{"sheet_id": "{sheet_id}", "page_num": {page_num}, "total_questions": <ACTUAL COUNT>, "errors": [<WRONG answers only>]}}

For each WRONG answer:
{{"q": <number>, "problem": "<the exercise/question>", "student": "<student answer>", "correct": "<correct answer>", "x": <x position>, "y": <y position>}}

If ALL answers are correct:
{{"sheet_id": "{sheet_id}", "page_num": {page_num}, "total_questions": <ACTUAL COUNT>, "errors": []}}'''


def get_analysis_prompt(sheet_id: str, page_num: int, subject: str = "maths") -> str:
    """Get the prompt for worksheet analysis (uses custom prompt if configured)."""
    questions_per_page = get_questions_per_page()
    custom_prompt = get_effective_setting("custom_prompt", "")

    if custom_prompt:
        return custom_prompt.format(
            sheet_id=sheet_id, page_num=page_num, questions_per_page=questions_per_page
        )

    if subject == "english":
        return get_english_prompt(sheet_id, page_num)

    return get_default_prompt(sheet_id, page_num, questions_per_page)


def get_header_extraction_prompt() -> str:
    """Get prompt for extracting the handwritten header fields from a worksheet."""
    return """Look at this Kumon worksheet image. The top right has a header box with
"Name", "Date" and "Time" fields, all filled in by hand.

Read the HANDWRITTEN entries:
- name: the student's name
- date: the date, as written, in day/month/year order (e.g. "28/8/26")
- time_started: the time in the "Time" field before the word "to" (e.g. "3:32")
- time_finished: the time after the word "to" (e.g. "4:18")

Use null for any field that is blank or unreadable. Ignore any times written
elsewhere on the page — only the header "Time ... to ..." line counts.

Return ONLY a JSON object:
{"name": "<name>", "date": "<date>", "time_started": "<time>", "time_finished": "<time>"}

ONLY output the JSON, nothing else."""


def get_name_extraction_prompt() -> str:
    """Get prompt for extracting student name from worksheet.

    Kept for backwards compatibility; the header prompt returns the name too.
    """
    return get_header_extraction_prompt()


_TIME_RE = re.compile(r"^\s*(\d{1,2})\s*[:.]\s*(\d{2})\s*$")


def _clean_time(value) -> str | None:
    """Normalise a handwritten time to 'H:MM', or None if it isn't one."""
    if not isinstance(value, str):
        return None
    match = _TIME_RE.match(value)
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return f"{hour}:{minute:02d}"


def _clean_date(value) -> str | None:
    """Keep a handwritten date only if it looks like one."""
    if not isinstance(value, str):
        return None
    value = value.strip()
    return (
        value if re.match(r"^\d{1,2}\s*/\s*\d{1,2}(\s*/\s*\d{2,4})?$", value) else None
    )


def extract_header_from_response(output: str) -> WorksheetHeader:
    """Extract the header fields from a vision model response."""
    try:
        match = re.search(r"\{[\s\S]*\}", output)
        if match:
            data = json.loads(match.group())
            name = data.get("name")
            if not (isinstance(name, str) and name.strip()):
                name = None
            return WorksheetHeader(
                student_name=name.strip().title() if name else None,
                date=_clean_date(data.get("date")),
                time_started=_clean_time(data.get("time_started")),
                time_finished=_clean_time(data.get("time_finished")),
            )
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return WorksheetHeader()


def extract_name_from_response(output: str) -> str | None:
    """Extract name from vision model response."""
    return extract_header_from_response(output).student_name


def extract_header_with_vision(image_bytes: bytes) -> WorksheetHeader:
    """Extract name, date and start/finish times using the configured provider."""
    try:
        provider = get_provider()
        output = provider.analyse_image(image_bytes, get_header_extraction_prompt())
        return extract_header_from_response(output)
    except Exception as e:
        print(f"Header extraction error: {e}")
        return WorksheetHeader()


def extract_name_with_vision(image_bytes: bytes) -> str | None:
    """Extract student name from worksheet using the configured vision provider."""
    return extract_header_with_vision(image_bytes).student_name


def calculate_tick_position(
    question_num: int, total_questions: int = 24
) -> tuple[float, float]:
    """Calculate tick position based on question number for standard Kumon layout."""
    half = total_questions // 2 if total_questions > 12 else total_questions

    if question_num <= half:
        x = 490
        row = question_num - 1
    else:
        x = 655
        row = question_num - half - 1

    y = 300 + (row * 32)
    return x, y


def parse_analysis_response(output: str, sheet_id: str, page_num: int) -> PageResult:
    """Parse the JSON response from the vision model."""
    match = re.search(r"\{[\s\S]*\}", output)
    if match:
        data = json.loads(match.group())
        total_q = data.get("total_questions", get_questions_per_page())

        errors = []
        for e in data.get("errors", []):
            if (
                "x" not in e
                or "y" not in e
                or (e.get("x") == 200 and e.get("y") == 300)
            ):
                q_num = e.get("q", 1)
                calc_x, calc_y = calculate_tick_position(q_num, total_q)
                e["x"] = e.get("x", calc_x) if e.get("x", 200) != 200 else calc_x
                e["y"] = e.get("y", calc_y) if e.get("y", 300) != 300 else calc_y
            errors.append(ErrorDetail(**e))

        return PageResult(
            sheet_id=sheet_id,
            page_num=page_num,
            total_questions=total_q,
            errors=errors,
        )
    raise ValueError("No valid JSON found in response")


def analyse_page(
    image_bytes: bytes,
    page_num: int,
    sheet_id: str,
    subject: str = "maths",
) -> PageResult:
    """Analyse a single worksheet page using the configured vision provider."""
    prompt = get_analysis_prompt(sheet_id, page_num, subject=subject)

    try:
        provider = get_provider()
        output = provider.analyse_image(image_bytes, prompt)
        return parse_analysis_response(output, sheet_id, page_num)
    except Exception as e:
        print(f"Analysis error on page {page_num}: {e}")

    return PageResult(
        sheet_id=sheet_id,
        page_num=page_num,
        total_questions=get_questions_per_page(),
        errors=[],
    )


def analyse_worksheet(
    pdf_path: Path,
    sheet_prefix: str = "B",
    base_num: int = 161,
    progress_callback: callable = None,
    subject: str = "maths",
) -> list[PageResult]:
    """Analyse all pages of a worksheet PDF.

    Uses the configured vision provider (vision_provider setting).
    Memory-efficient: loads and processes one page at a time.

    Args:
        pdf_path: Path to the PDF file.
        sheet_prefix: Prefix for sheet IDs (e.g., "B" for B161a).
        base_num: Base number for sheet IDs.
        progress_callback: Optional callback function(current_page, total_pages).
        subject: Worksheet subject ("maths" or "english").
    """
    num_pages = pdf_page_count(pdf_path)

    sheet_ids = [
        f"{sheet_prefix}{base_num + i // 2}{'a' if i % 2 == 0 else 'b'}"
        for i in range(num_pages)
    ]

    provider_name = get_effective_setting("vision_provider", "ollama")
    model_key = f"{provider_name}_model"
    model_name = get_effective_setting(model_key, "unknown")
    print(f"Using vision provider: {provider_name} (model: {model_name})")

    # Gemini rate limiting: free tier is 15 req/min
    needs_rate_limit = provider_name == "gemini"

    results = []
    for i, sheet_id in enumerate(sheet_ids):
        print(f"Analysing page {i + 1}/{num_pages} ({sheet_id})...")

        image_bytes = pdf_page_to_image(pdf_path, i)
        result = analyse_page(image_bytes, i, sheet_id, subject=subject)
        results.append(result)

        if progress_callback:
            progress_callback(i + 1, num_pages)

        # Rate limit for Gemini
        if needs_rate_limit and i < num_pages - 1:
            time.sleep(4)

        del image_bytes
        cleanup_memory()

    gc.collect()
    return results
