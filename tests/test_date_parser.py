"""
Unit tests for ENTU date parser.

Tests cover ISO to Estonian date format conversion:
- ISO: "2002-12-22"
- Estonian: "22.12.2002"
"""

from scripts.parsers.date_parser import convert_date


class TestConvertDate:
    """Unit tests for convert_date function."""

    def test_iso_format_conversion(self):
        """
        GIVEN: Date in ISO format
        WHEN: convert_date is called
        THEN: Returns Estonian DD.MM.YYYY format
        """
        result = convert_date("2002-12-22")
        assert result == "22.12.2002"

    def test_real_data_example(self):
        """
        GIVEN: Real data from sample
        WHEN: convert_date is called
        THEN: Correctly converts to Estonian format
        """
        result = convert_date("1956-05-28")
        assert result == "28.05.1956"

    def test_january_date(self):
        """
        GIVEN: Date in January
        WHEN: convert_date is called
        THEN: Correctly formats month with leading zero
        """
        result = convert_date("2024-01-15")
        assert result == "15.01.2024"

    def test_none_returns_none(self):
        """
        GIVEN: None as input
        WHEN: convert_date is called
        THEN: Returns None
        """
        result = convert_date(None)
        assert result is None

    def test_empty_string_returns_none(self):
        """
        GIVEN: Empty string
        WHEN: convert_date is called
        THEN: Returns None
        """
        result = convert_date("")
        assert result is None

    def test_invalid_format_returns_none(self):
        """
        GIVEN: Invalid date format
        WHEN: convert_date is called
        THEN: Returns None (logs warning)
        """
        result = convert_date("invalid")
        assert result is None

    def test_leap_year_february(self):
        """
        GIVEN: Leap year February date
        WHEN: convert_date is called
        THEN: Correctly formats Feb 29
        """
        result = convert_date("2024-02-29")
        assert result == "29.02.2024"
