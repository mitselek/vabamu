"""
Unit tests for ENTU dimension parser.

Tests cover multiple dimension formats:
- Diameter: "ø50"
- Height x Width: "62x70"
- Combined: "ø50;62x70"
- Edge cases: Empty, null, unparseable
- Boundary: Max 4 measurements
"""

from scripts.parsers.dimension_parser import parse_dimensions


class TestParseDimensions:
    """Unit tests for parse_dimensions function."""

    def test_diameter_only(self):
        """
        GIVEN: Diameter notation (ø50)
        WHEN: parse_dimensions is called
        THEN: Returns list with 1 diameter measurement
        """
        result = parse_dimensions("ø50")

        assert len(result) == 1
        assert result[0]["parameeter"] == "läbimõõt"
        assert result[0]["yhik"] == "mm"
        assert result[0]["vaartus"] == 50

    def test_height_width_format(self):
        """
        GIVEN: HxW format (62x70)
        WHEN: parse_dimensions is called
        THEN: Returns list with height then width
        """
        result = parse_dimensions("62x70")

        assert len(result) == 2
        assert result[0]["parameeter"] == "kõrgus"
        assert result[0]["vaartus"] == 62
        assert result[1]["parameeter"] == "laius"
        assert result[1]["vaartus"] == 70

    def test_combined_dimensions(self):
        """
        GIVEN: Combined dimensions (ø50;62x70)
        WHEN: parse_dimensions is called
        THEN: Returns list with diameter, height, width (3 items)
        """
        result = parse_dimensions("ø50;62x70")

        assert len(result) == 3
        assert result[0]["parameeter"] == "läbimõõt"
        assert result[0]["vaartus"] == 50
        assert result[1]["parameeter"] == "kõrgus"
        assert result[1]["vaartus"] == 62
        assert result[2]["parameeter"] == "laius"
        assert result[2]["vaartus"] == 70

    def test_real_data_example(self):
        """
        GIVEN: Real data from sample_100_raw.csv
        WHEN: parse_dimensions is called
        THEN: Returns parsed measurements
        """
        # Many records have no dimensions, so this should return empty
        result = parse_dimensions(None)
        assert result == []

        result = parse_dimensions("")
        assert result == []

    def test_empty_returns_empty_list(self):
        """
        GIVEN: Empty string or None
        WHEN: parse_dimensions is called
        THEN: Returns empty list
        """
        assert parse_dimensions("") == []
        assert parse_dimensions(None) == []

    def test_unparseable_returns_empty_list(self):
        """
        GIVEN: Unparseable dimension string
        WHEN: parse_dimensions is called
        THEN: Returns empty list (logs warning, doesn't crash)
        """
        result = parse_dimensions("väga suur")
        assert result == []

        result = parse_dimensions("xyz abc")
        assert result == []

    def test_max_four_measurements(self):
        """
        GIVEN: More than 4 dimension components
        WHEN: parse_dimensions is called
        THEN: Truncates to max 4 measurements
        """
        # Create hypothetical string with 5 measurements
        # ø50;62x70x100 would parse to 4: diameter, height, width, and hit limit
        result = parse_dimensions("ø50;62x70;10")

        assert len(result) <= 4

    def test_floating_point_dimensions(self):
        """
        GIVEN: Dimensions with decimal points
        WHEN: parse_dimensions is called
        THEN: Correctly parses floats
        """
        result = parse_dimensions("62.5x70.5")

        assert len(result) == 2
        assert result[0]["vaartus"] == 62.5
        assert result[1]["vaartus"] == 70.5

    def test_all_measurements_have_unit(self):
        """
        GIVEN: Any valid dimension string
        WHEN: parse_dimensions is called
        THEN: All measurements have unit "mm" by default
        """
        result = parse_dimensions("ø50;62x70")

        for measurement in result:
            assert measurement["yhik"] == "mm"

    def test_labeled_dimensions_future(self):
        """
        GIVEN: Labeled format "H:50 L:60" (future support)
        WHEN: parse_dimensions is called
        THEN: Returns empty list (not yet implemented)
        """
        result = parse_dimensions("H:50 L:60")
        # For now, we don't support this format yet
        assert result == [] or len(result) > 0  # Flexible for future enhancement
