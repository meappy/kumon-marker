"""Tests for worksheet header extraction and the printing service."""

import subprocess

import pytest

from app.services import printing
from app.services.ocr import extract_header_from_response, extract_name_from_response


class TestHeaderExtraction:
    def test_reads_all_four_fields(self):
        header = extract_header_from_response(
            '{"name": "alex", "date": "28/8/26", '
            '"time_started": "3:32", "time_finished": "4:18"}'
        )
        assert header.student_name == "Alex"  # title-cased
        assert header.date == "28/8/26"
        assert (header.time_started, header.time_finished) == ("3:32", "4:18")

    def test_ignores_prose_around_the_json(self):
        header = extract_header_from_response(
            'Here is the header:\n{"name": "Sam", "date": "28/8/26", '
            '"time_started": "4:50", "time_finished": "6:27"}\nHope that helps!'
        )
        assert header.student_name == "Sam"
        assert header.time_started == "4:50"

    def test_nulls_become_none(self):
        header = extract_header_from_response(
            '{"name": null, "date": null, "time_started": null, "time_finished": null}'
        )
        assert header.student_name is None
        assert header.date is None and header.time_started is None

    @pytest.mark.parametrize("value", ["not a time", "25:00", "3:99", "", "3"])
    def test_rejects_junk_times(self, value):
        header = extract_header_from_response(f'{{"time_started": "{value}"}}')
        assert header.time_started is None

    def test_rejects_a_non_string_time(self):
        assert extract_header_from_response('{"time_started": 332}').time_started is None

    def test_normalises_a_dotted_time(self):
        header = extract_header_from_response('{"time_started": "3.32"}')
        assert header.time_started == "3:32"

    @pytest.mark.parametrize("value", ["yesterday", "28-8-26", "28", ""])
    def test_rejects_junk_dates(self, value):
        assert extract_header_from_response(f'{{"date": "{value}"}}').date is None

    @pytest.mark.parametrize("value", ["28/8/26", "28/8", "5/12/2026"])
    def test_accepts_real_dates(self, value):
        assert extract_header_from_response(f'{{"date": "{value}"}}').date == value

    def test_malformed_response_is_not_fatal(self):
        header = extract_header_from_response("the model refused to answer")
        assert header.student_name is None and header.date is None

    def test_name_helper_still_works(self):
        assert extract_name_from_response('{"name": "alex"}') == "Alex"
        assert extract_name_from_response("nonsense") is None


class TestPrinting:
    def test_lists_printers_and_marks_the_default(self, monkeypatch):
        output = (
            "printer Brother_MFC is idle.  enabled since Thu\n"
            "printer Dell_1130n is idle.  enabled since Sun\n"
            "printer PDFwriter disabled since Tue -\n"
            "system default destination: Brother_MFC\n"
        )
        monkeypatch.setattr(printing, "printing_available", lambda: True)
        monkeypatch.setattr(printing, "_run", lambda *a, **k: output)

        printers = printing.list_printers()
        assert [p["name"] for p in printers] == [
            "Brother_MFC",
            "Dell_1130n",
            "PDFwriter",
        ]
        assert printers[0]["is_default"] is True
        assert printers[2]["enabled"] is False

    def test_returns_nothing_when_cups_is_absent(self, monkeypatch):
        monkeypatch.setattr(printing, "printing_available", lambda: False)
        assert printing.list_printers() == []

    def test_print_submits_a_fit_to_page_job(self, monkeypatch, tmp_path):
        pdf = tmp_path / "marked.pdf"
        pdf.write_bytes(b"%PDF-1.4\n")
        captured = {}

        def fake_run(args, timeout=15):
            captured["args"] = args
            return "request id is Brother-63 (1 file(s))"

        monkeypatch.setattr(printing, "_run", fake_run)
        monkeypatch.setattr(printing, "get_default_printer", lambda: "Brother")

        job = printing.print_pdf(pdf, copies=2, title="F96")
        assert job == "Brother-63"
        assert captured["args"][:2] == ["lp", "-d"]
        assert "fit-to-page" in captured["args"]
        assert "-n" in captured["args"] and "2" in captured["args"]

    def test_refuses_a_missing_file(self, tmp_path):
        with pytest.raises(printing.PrintError, match="not found"):
            printing.print_pdf(tmp_path / "nope.pdf")

    def test_respects_the_disable_switch(self, monkeypatch, tmp_path):
        pdf = tmp_path / "marked.pdf"
        pdf.write_bytes(b"%PDF-1.4\n")
        monkeypatch.setattr(
            printing, "get_effective_setting", lambda key, default=None: False
        )
        with pytest.raises(printing.PrintError, match="disabled"):
            printing.print_pdf(pdf)

    def test_surfaces_a_cups_failure(self, monkeypatch, tmp_path):
        pdf = tmp_path / "marked.pdf"
        pdf.write_bytes(b"%PDF-1.4\n")

        def failed(args, capture_output, text, timeout, check):
            return subprocess.CompletedProcess(
                args, 1, stdout="", stderr="lp: The printer is not responding."
            )

        monkeypatch.setattr(subprocess, "run", failed)
        monkeypatch.setattr(printing, "get_default_printer", lambda: "Brother")
        with pytest.raises(printing.PrintError, match="not responding"):
            printing.print_pdf(pdf)
