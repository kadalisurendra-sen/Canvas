"""Tests for master data service layer."""
import pytest

from src.service.master_data_service import _decode_csv, _parse_csv


def test_decode_csv_utf8() -> None:
    """Should decode UTF-8 content."""
    text = _decode_csv(b"value,label\ntest,Test")
    assert "value,label" in text


def test_decode_csv_bom() -> None:
    """Should decode UTF-8 BOM content."""
    content = b"\xef\xbb\xbfvalue,label\ntest,Test"
    text = _decode_csv(content)
    assert text.startswith("value")


def test_parse_csv_valid_rows() -> None:
    """Should parse valid CSV rows."""
    text = "value,label,severity,description\ntest,Test,high,A desc"
    rows, errors = _parse_csv(text)
    assert len(rows) == 1
    assert rows[0]["value"] == "test"
    assert rows[0]["severity"] == "high"
    assert errors == []


def test_parse_csv_missing_required_fields() -> None:
    """Should report error for missing value or label."""
    text = "value,label\n,Missing Value"
    rows, errors = _parse_csv(text)
    assert len(rows) == 0
    assert len(errors) == 1
    assert errors[0]["row"] == 2


def test_parse_csv_invalid_severity() -> None:
    """Should report error for invalid severity."""
    text = "value,label,severity\ntest,Test,extreme"
    rows, errors = _parse_csv(text)
    assert len(rows) == 0
    assert len(errors) == 1
    assert "severity" in str(errors[0]["message"]).lower()


def test_parse_csv_empty_severity_ok() -> None:
    """Empty severity should be valid."""
    text = "value,label,severity\ntest,Test,"
    rows, errors = _parse_csv(text)
    assert len(rows) == 1
    assert rows[0]["severity"] is None


def test_parse_csv_empty_file() -> None:
    """Empty CSV should return error."""
    rows, errors = _parse_csv("")
    assert len(rows) == 0
    assert len(errors) == 1


def test_parse_csv_case_insensitive_headers() -> None:
    """Column names should be case-insensitive."""
    text = "VALUE,LABEL,Severity\ntest,Test,low"
    rows, errors = _parse_csv(text)
    assert len(rows) == 1
    assert rows[0]["severity"] == "low"


def test_parse_csv_extra_columns_ignored() -> None:
    """Unrecognized columns should be ignored."""
    text = "value,label,extra_col\ntest,Test,ignored"
    rows, errors = _parse_csv(text)
    assert len(rows) == 1
    assert "extra_col" not in rows[0]
