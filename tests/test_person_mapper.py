"""
Unit tests for person mapper stub.

Phase 1: Placeholder for person ID mapping.
Phase 2: Will implement full lookup table.
"""

from scripts.parsers.person_mapper import map_person


class TestMapPerson:
    """Unit tests for map_person stub function."""

    def test_none_returns_none(self):
        """
        GIVEN: None as input
        WHEN: map_person is called
        THEN: Returns None
        """
        result = map_person(None)
        assert result is None

    def test_empty_string_returns_none(self):
        """
        GIVEN: Empty string
        WHEN: map_person is called
        THEN: Returns None
        """
        result = map_person("")
        assert result is None

    def test_numeric_id_returns_placeholder(self):
        """
        GIVEN: Numeric person ID
        WHEN: map_person is called (Phase 1)
        THEN: Returns placeholder for Phase 2
        """
        result = map_person("139862")
        assert result is not None
        assert "139862" in result

    def test_already_formatted_name_returns_unchanged(self):
        """
        GIVEN: Name already in "Lastname, Firstname" format
        WHEN: map_person is called
        THEN: Returns unchanged
        """
        result = map_person("Jõgiaas, Miia")
        assert result == "Jõgiaas, Miia"

    def test_single_name_returns_unchanged(self):
        """
        GIVEN: Single name (no comma)
        WHEN: map_person is called
        THEN: Returns unchanged (stub behavior)
        """
        result = map_person("Smith")
        assert result == "Smith"
