"""Extended tests for _decode_csv edge cases."""
import pytest

from src.service.master_data_service import _decode_csv


class TestDecodeCsvEdgeCases:
    """Edge case tests for _decode_csv."""

    def test_latin1_encoding(self) -> None:
        """Latin-1 encoded content with non-UTF8 byte."""
        content = "value,label\nt\xe9st,T\xe9st".encode("latin-1")
        text = _decode_csv(content)
        assert "value,label" in text

    def test_utf8_sig_encoding(self) -> None:
        """UTF-8 with BOM prefix."""
        content = b"\xef\xbb\xbfvalue,label\ntest,Test"
        text = _decode_csv(content)
        assert text.startswith("value")

    def test_plain_bytes(self) -> None:
        """Plain ASCII bytes."""
        text = _decode_csv(b"value,label\na,b")
        assert "value" in text

    def test_empty_bytes(self) -> None:
        """Empty byte content."""
        text = _decode_csv(b"")
        assert text == ""
