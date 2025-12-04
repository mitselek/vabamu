"""
Unit tests for ENTU number parser.

Tests cover:
- Happy path: Standard NNNNNN/NNN format
- Leading zeros: Parsing and stripping
- Edge cases: Null/empty input
- Error handling: Invalid formats
"""

import pytest
from scripts.parsers.number_parser import parse_entu_code


class TestParseEntuCode:
    """Unit tests for parse_entu_code function."""

    def test_happy_path_standard_format(self):
        """
        GIVEN: Valid ENTU code in standard format
        WHEN: parse_entu_code is called
        THEN: Returns dict with all 9 fields correctly parsed
        """
        result = parse_entu_code("020027/117")

        assert result["acr"] == "VBM"
        assert result["trt"] == "_"
        assert result["trs"] == 20027
        assert result["trj"] == 117
        assert result["trl"] is None
        assert result["kt"] is None
        assert result["ks"] is None
        assert result["kj"] is None
        assert result["kl"] is None

    def test_leading_zeros_stripped_from_series(self):
        """
        GIVEN: ENTU code with leading zeros
        WHEN: parse_entu_code is called
        THEN: Leading zeros are stripped from series (TRS)
        """
        result = parse_entu_code("006562/001")

        assert result["trs"] == 6562
        assert result["trj"] == 1

    def test_real_data_example(self):
        """
        GIVEN: Real data from sample_100_raw.csv
        WHEN: parse_entu_code is called
        THEN: Returns expected structure
        """
        result = parse_entu_code("020027/117")

        assert result["acr"] == "VBM"
        assert result["trs"] == 20027
        assert result["trj"] == 117

    def test_single_digit_components(self):
        """
        GIVEN: ENTU code with single-digit components
        WHEN: parse_entu_code is called
        THEN: Correctly parses as integers (not strings)
        """
        result = parse_entu_code("000001/001")

        assert result["trs"] == 1
        assert result["trj"] == 1
        assert isinstance(result["trs"], int)
        assert isinstance(result["trj"], int)

    def test_trj_zero_returns_none(self):
        """
        GIVEN: ENTU code with sub-series = 000 (zero)
        WHEN: parse_entu_code is called
        THEN: Returns trj=None (per Vabamu feedback: 0 → empty cell)
        
        Vabamu: "kui ENTUSt tulev väärtus on 0, siis muisi tarvis seda väärtust pole"
        """
        result = parse_entu_code("020082/000")

        assert result["trs"] == 20082
        assert result["trj"] is None  # 0 becomes None → empty cell in CSV

    def test_large_numbers(self):
        """
        GIVEN: ENTU code with large numbers
        WHEN: parse_entu_code is called
        THEN: Handles large integers correctly
        """
        result = parse_entu_code("999999/999")

        assert result["trs"] == 999999
        assert result["trj"] == 999

    def test_invalid_format_raises_error(self):
        """
        GIVEN: Invalid ENTU code format (missing slash)
        WHEN: parse_entu_code is called
        THEN: Raises ValueError with clear message
        """
        with pytest.raises(ValueError) as exc_info:
            parse_entu_code("020027")

        assert "Invalid" in str(exc_info.value) or "format" in str(
            exc_info.value
        ).lower()

    def test_non_numeric_raises_error(self):
        """
        GIVEN: ENTU code with non-numeric characters
        WHEN: parse_entu_code is called
        THEN: Raises ValueError with clear message
        """
        with pytest.raises(ValueError):
            parse_entu_code("ABC/XYZ")

    def test_empty_string_raises_error(self):
        """
        GIVEN: Empty string as input
        WHEN: parse_entu_code is called
        THEN: Raises ValueError or returns None
        """
        with pytest.raises(ValueError):
            parse_entu_code("")

    def test_none_input_raises_error(self):
        """
        GIVEN: None as input
        WHEN: parse_entu_code is called
        THEN: Raises appropriate error
        """
        with pytest.raises((ValueError, TypeError, AttributeError)):
            parse_entu_code(None)  # type: ignore[arg-type]
