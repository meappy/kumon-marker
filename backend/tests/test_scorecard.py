"""Tests for the Kumon Score Report service."""

import uuid

import fitz
import pytest

from app.models.schemas import ErrorDetail, PageResult, ScoreEntry, WorksheetHeader
from app.services import scorecard


def page(sheet_id: str, page_num: int, wrong: tuple = (), questions: int = 8) -> PageResult:
    return PageResult(
        sheet_id=sheet_id,
        page_num=page_num,
        total_questions=questions,
        errors=[
            ErrorDetail(q=q, problem="p", student="s", correct="c") for q in wrong
        ],
    )


@pytest.fixture
def data_dir(tmp_path):
    return tmp_path


@pytest.fixture
def packet():
    """A five-worksheet packet with two mistakes on the second worksheet."""
    return [
        page("F96a", 0), page("F96b", 1),
        page("F97a", 2, (8,)), page("F97b", 3, (14,)),
        page("F98a", 4), page("F98b", 5),
        page("F99a", 6), page("F99b", 7),
        page("F100a", 8), page("F100b", 9),
    ]


@pytest.fixture
def header():
    return WorksheetHeader(
        student_name="Alex", date="28/8/26", time_started="3:32", time_finished="4:18"
    )


class TestBuildEntry:
    def test_reads_level_sheet_and_times(self, packet, header):
        entry = scorecard.build_entry(packet, header, "w1")
        assert (entry.level, entry.sheet_no) == ("F", "96")
        assert (entry.time_started, entry.time_finished) == ("3:32", "4:18")
        assert entry.time_used == "46"
        assert entry.worksheet_id == "w1"

    def test_date_is_trimmed_to_fit_the_column(self, packet, header):
        assert scorecard.build_entry(packet, header).date == "28/8"

    def test_one_mark_per_worksheet_not_per_page(self, packet, header):
        marks = scorecard.build_entry(packet, header).marks
        assert len(marks) == 5
        # F97 has 2 errors in 16 questions -> B; the rest are clean -> A
        assert marks == ["A", "B", "A", "A", "A"]

    def test_survives_a_missing_header(self, packet):
        entry = scorecard.build_entry(packet)
        assert entry.date == "" and entry.time_used == ""
        assert entry.level == "F"

    def test_caps_marks_at_the_number_of_columns(self, header):
        many = [page(f"F{96 + i}a", i) for i in range(15)]
        assert len(scorecard.build_entry(many, header).marks) == scorecard.MAX_MARKS


class TestMinutesBetween:
    @pytest.mark.parametrize(
        "started,finished,expected",
        [
            ("3:32", "4:18", "46"),
            ("11:50", "12:10", "20"),
            ("12:50", "1:20", "30"),  # 12-hour clock rollover
            ("4:18", "4:18", ""),  # no elapsed time recorded
            (None, "4:18", ""),
            ("4:18", None, ""),
            ("nonsense", "4:18", ""),
        ],
    )
    def test_elapsed(self, started, finished, expected):
        assert scorecard.minutes_between(started, finished) == expected


class TestLog:
    def test_round_trip(self, data_dir, packet, header):
        entry = scorecard.build_entry(packet, header, "w1")
        scorecard.add_entry(data_dir, "Alex", entry)

        stored = scorecard.get_student_log(data_dir, "Alex").entries
        assert len(stored) == 1
        assert stored[0].marks == entry.marks

    def test_reprocessing_replaces_rather_than_duplicates(self, data_dir, packet, header):
        scorecard.add_entry(data_dir, "Alex", scorecard.build_entry(packet, header, "w1"))
        scorecard.add_entry(data_dir, "Alex", scorecard.build_entry(packet, header, "w1"))
        assert len(scorecard.get_student_log(data_dir, "Alex").entries) == 1

    def test_rows_without_a_worksheet_are_kept_separately(self, data_dir, packet, header):
        scorecard.add_entry(data_dir, "Alex", scorecard.build_entry(packet, header))
        scorecard.add_entry(data_dir, "Alex", scorecard.build_entry(packet, header))
        assert len(scorecard.get_student_log(data_dir, "Alex").entries) == 2

    def test_students_are_kept_apart(self, data_dir, packet, header):
        scorecard.add_entry(data_dir, "Alex", scorecard.build_entry(packet, header, "w1"))
        scorecard.add_entry(data_dir, "Sam", scorecard.build_entry(packet, header, "w2"))
        assert set(scorecard.load_log(data_dir)) == {"Alex", "Sam"}

    def test_update_and_delete(self, data_dir, packet, header):
        entry = scorecard.add_entry(
            data_dir, "Alex", scorecard.build_entry(packet, header, "w1")
        )
        updated = scorecard.update_entry(data_dir, "Alex", entry.id, {"time_used": "26"})
        assert updated is not None and updated.time_used == "26"

        assert scorecard.delete_entry(data_dir, "Alex", entry.id) is True
        assert scorecard.delete_entry(data_dir, "Alex", entry.id) is False

    def test_missing_log_reads_as_empty(self, data_dir):
        assert scorecard.load_log(data_dir) == {}

    def test_corrupt_log_does_not_raise(self, data_dir):
        path = scorecard.log_path(data_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{not json")
        assert scorecard.load_log(data_dir) == {}


def row(**kwargs) -> ScoreEntry:
    return ScoreEntry(id=str(uuid.uuid4()), **kwargs)


class TestRender:
    def test_generated_card_carries_the_data(self, data_dir, packet, header):
        scorecard.add_entry(data_dir, "Alex", scorecard.build_entry(packet, header, "w1"))
        output = data_dir / "card.pdf"
        scorecard.render(data_dir, "Alex", output)

        with fitz.open(output) as doc:
            assert len(doc) == 1
            text = doc[0].get_text()
        assert "SCORE REPORT" in text
        assert "Alex" in text
        assert "96" in text and "28/8" in text

    def test_rows_paginate_onto_further_cards(self, data_dir):
        entries = [row(level="F", sheet_no=str(i)) for i in range(30)]
        output = data_dir / "bulk.pdf"
        scorecard.render_generated("Bulk", entries, output)

        with fitz.open(output) as doc:
            assert len(doc) == 2

    def test_empty_log_still_draws_a_blank_card(self, data_dir):
        output = data_dir / "blank.pdf"
        scorecard.render_generated("Nobody", [], output)

        with fitz.open(output) as doc:
            assert len(doc) == 1
            assert "SCORE REPORT" in doc[0].get_text()

    def test_template_overlay_writes_into_the_requested_row(self, data_dir, tmp_path):
        # stand in for a scanned card
        template = tmp_path / "template.pdf"
        doc = fitz.open()
        doc.new_page(width=824.4, height=576)
        doc.save(template)
        doc.close()

        output = data_dir / "overlaid.pdf"
        scorecard.render_onto_template(
            [row(date="28/8", level="C", sheet_no="156", marks=["A"] * 5)],
            template,
            output,
            page_index=0,
            start_row=14,
        )

        geo = scorecard.DEFAULT_GEOMETRY
        with fitz.open(output) as rendered:
            words = rendered[0].get_text("words")
        assert any(w[4] == "156" for w in words), "sheet number missing"

        # the row must land inside printed row 14, not somewhere else
        expected_y = geo.baseline(14)
        sheet_word = next(w for w in words if w[4] == "156")
        rendered_y = geo.page_height - sheet_word[3]
        assert abs(rendered_y - expected_y) < 4, (rendered_y, expected_y)

    def test_overlay_stops_at_the_end_of_the_form(self, data_dir, tmp_path):
        template = tmp_path / "template.pdf"
        doc = fitz.open()
        doc.new_page(width=824.4, height=576)
        doc.save(template)
        doc.close()

        output = data_dir / "overflow.pdf"
        entries = [row(sheet_no=str(100 + i)) for i in range(5)]
        scorecard.render_onto_template(
            entries, template, output, start_row=scorecard.ROWS_PER_CARD - 2
        )

        with fitz.open(output) as rendered:
            text = rendered[0].get_text()
        assert "100" in text and "101" in text
        assert "102" not in text, "rows were drawn past the bottom of the form"


class TestGrades:
    @pytest.mark.parametrize(
        "questions,errors,expected",
        [(10, 0, "A"), (10, 1, "A"), (10, 2, "B"), (10, 4, "C"), (10, 6, "D"), (0, 0, "-")],
    )
    def test_bands(self, questions, errors, expected):
        assert scorecard.grade_for(questions, errors) == expected
