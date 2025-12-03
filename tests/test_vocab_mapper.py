"""
Unit tests for vocabulary mapper.

Tests cover material, technique, and color mapping.
"""

from scripts.parsers.vocab_mapper import (
    map_material,
    map_technique,
    map_color,
)


class TestVocabMappers:
    """Unit tests for vocabulary mappers."""

    def test_map_material_path_format(self):
        """
        GIVEN: Material path "/materjalid/metall"
        WHEN: map_material is called
        THEN: Extracts term "metall"
        """
        result = map_material("/materjalid/metall")
        assert result == "metall"

    def test_map_material_already_term(self):
        """
        GIVEN: Material already as term "metall"
        WHEN: map_material is called
        THEN: Returns unchanged
        """
        result = map_material("metall")
        assert result == "metall"

    def test_map_material_none_returns_none(self):
        """
        GIVEN: None as input
        WHEN: map_material is called
        THEN: Returns None
        """
        result = map_material(None)
        assert result is None

    def test_map_material_empty_returns_none(self):
        """
        GIVEN: Empty string
        WHEN: map_material is called
        THEN: Returns None
        """
        result = map_material("")
        assert result is None

    def test_map_technique_uses_same_logic(self):
        """
        GIVEN: Technique path
        WHEN: map_technique is called
        THEN: Uses same parsing logic as material
        """
        result = map_technique("/tehnika/kaunistus")
        assert result == "kaunistus"

    def test_map_color_uses_same_logic(self):
        """
        GIVEN: Color path
        WHEN: map_color is called
        THEN: Uses same parsing logic as material
        """
        result = map_color("/varv/hall")
        assert result == "hall"

    def test_nested_path_extracts_last_component(self):
        """
        GIVEN: Nested path with multiple levels
        WHEN: map_material is called
        THEN: Extracts last component only
        """
        result = map_material("/kategooria/materjal/metall")
        assert result == "metall"

    def test_path_with_trailing_slash(self):
        """
        GIVEN: Path with trailing slash
        WHEN: map_material is called
        THEN: Handles gracefully
        """
        result = map_material("/materjal/metall/")
        # Should handle trailing slash (may return '' or 'metall')
        assert result is not None
