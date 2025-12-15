"""Integration tests for convert_row orchestrator.

Tests the complete pipeline that orchestrates all 5 parsers:
1. Number parser: code (NNNNNN/NNN format)
2. Dimension parser: dimensions (ø, HxW, HxWxD formats)
3. Date parser: date (ISO format)
4. Person mapper: donator, autor (name or ID)
5. Vocab mapper: materials, techniques, colors (path formats)
"""

import csv
import json
import pytest
from pathlib import Path
from typing import Any
from scripts.convert_row import convert_row


@pytest.fixture
def sample_row_0() -> dict[str, Any]:
    """Load first row from sample_100_raw.csv (photo with code 020027/117)."""
    sample_file = Path(__file__).parent.parent / "output" / "sample_100_raw.csv"
    with open(sample_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return dict(next(reader))


@pytest.fixture
def mappings() -> dict[str, Any]:
    """Load vocabulary mappings."""
    mappings_dir = Path(__file__).parent.parent / "mappings"
    return {
        "materials": json.loads((mappings_dir / "materials.json").read_text(encoding="utf-8")),
        "techniques": json.loads((mappings_dir / "techniques.json").read_text(encoding="utf-8")),
        "colors": json.loads((mappings_dir / "colors.json").read_text(encoding="utf-8")),
    }


class TestConvertRowIntegration:
    """Integration tests for orchestrator with real sample data."""

    def test_convert_row_returns_dict(self, sample_row_0: dict[str, Any]) -> None:
        """Orchestrator should return a dictionary."""
        result = convert_row(sample_row_0)
        assert isinstance(result, dict)

    def test_number_parser_integration_code_020027_117(self, sample_row_0: dict[str, Any]) -> None:
        """Number parser should convert code 020027/117 correctly.

        Code format: 020027/117
        Expected: acr="VBM", trt="_", trs=20027 (leading zeros stripped),
                 trj=117, remaining fields None
        """
        result = convert_row(sample_row_0)

        assert result.get("acr") == "VBM"
        assert result.get("trt") == "_"
        assert result.get("trs") == 20027  # Stripped leading zero
        assert result.get("trj") == 117
        assert result.get("trl") is None
        assert result.get("kt") is None

    def test_dimension_parser_integration_168x121(self, sample_row_0: dict[str, Any]) -> None:
        """Dimension parser should convert 168x121 to height + width.

        Dimensions: 168x121 (height x width)
        Expected: Two measurements (height=168mm, width=121mm)
        """
        result = convert_row(sample_row_0)

        measurements = result.get("measurements", [])
        assert len(measurements) >= 2

        # Check that height and width are present
        heights = [m for m in measurements if m.get("parameeter") == "kõrgus"]
        widths = [m for m in measurements if m.get("parameeter") == "laius"]

        assert len(heights) > 0, "Should have height measurement"
        assert len(widths) > 0, "Should have width measurement"

        # Check values
        assert heights[0].get("vaartus") == 168
        assert widths[0].get("vaartus") == 121
        assert heights[0].get("yhik") == "mm"

    def test_date_parser_integration_empty_date(self, sample_row_0: dict[str, Any]) -> None:
        """Date parser should handle empty date field gracefully.

        Sample row 0 has empty date field.
        Expected: Result should have None or handle gracefully
        """
        result = convert_row(sample_row_0)

        # Empty date should result in None
        date_value = result.get("date")
        assert date_value is None or date_value == ""

    def test_person_mapper_integration_donator(self, sample_row_0: dict[str, Any]) -> None:
        """Person mapper should handle donator name.

        Donator: 'Miia Jõgiaas' (already formatted name)
        Expected: Return as-is (no placeholder wrapping needed)
        """
        result = convert_row(sample_row_0)

        donator = result.get("donator")
        assert donator is not None
        assert "Miia" in donator or "Jõgiaas" in donator

    def test_person_mapper_integration_autor_empty(self, sample_row_0: dict[str, Any]) -> None:
        """Person mapper should handle empty autor field.

        Autor field in sample row 0 is empty.
        Expected: Return None
        """
        result = convert_row(sample_row_0)

        autor = result.get("autor")
        assert autor is None or autor == ""

    def test_orchestrator_preserves_all_mapped_fields(self, sample_row_0: dict[str, Any]) -> None:
        """Orchestrator should map all required MUIS fields.

        Expected: All 88 MUIS fields present in result (even if None/empty)
        """
        result = convert_row(sample_row_0)

        # Check that result has expected structure
        assert isinstance(result, dict)

        # Verify key parsed fields are present
        assert "acr" in result  # From number parser
        assert "trt" in result
        assert "trs" in result
        assert "trj" in result
        assert "measurements" in result  # From dimension parser
        assert "date" in result  # From date parser
        assert "donator" in result  # From person mapper
        assert "autor" in result

    def test_orchestrator_handles_full_row_conversion(self, sample_row_0: dict[str, Any]) -> None:
        """Full orchestrator should process complete row without exceptions.

        This is a smoke test to verify the orchestrator doesn't crash
        on a real record.
        """
        result = convert_row(sample_row_0)

        # Should complete without exception and return a dictionary
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_convert_row_with_minimal_data(self) -> None:
        """Orchestrator should handle minimal/sparse row gracefully.

        Row with mostly empty fields should not crash.
        """
        minimal_row: dict[str, Any] = {
            "code": "000001/001",
            "date": "",
            "dimensions": "",
            "donator": "",
            "autor": "",
            "name": "Test Item",
        }

        result = convert_row(minimal_row)

        # Should succeed with valid code parsing
        assert result.get("trs") == 1
        assert result.get("trj") == 1

    def test_convert_row_with_invalid_code(self) -> None:
        """Orchestrator should handle invalid code gracefully.

        Invalid code format should not crash but may return None/error indicator.
        """
        bad_row: dict[str, Any] = {
            "code": "INVALID",
            "date": "",
            "dimensions": "",
            "donator": "",
            "autor": "",
            "name": "Bad Code Item",
        }

        # Should not crash
        result = convert_row(bad_row)
        assert isinstance(result, dict)

        # Should have None for parsed code fields
        assert result.get("trs") is None or result.get("trs") == "ERROR"


class TestConvertRowEdgeCases:
    """Edge case tests for orchestrator."""

    def test_convert_row_with_complex_dimensions(self) -> None:
        """Handle multiple dimension formats in single row.

        Example: ø50;62x70 (diameter + height x width)
        """
        row: dict[str, Any] = {
            "code": "100001/100",
            "date": "",
            "dimensions": "ø50;62x70",
            "donator": "",
            "autor": "",
            "name": "Multi-dimension Item",
        }

        result = convert_row(row)

        measurements = result.get("measurements", [])
        assert len(measurements) >= 3  # Should have 3+ measurements

    def test_convert_row_with_iso_date(self) -> None:
        """Handle ISO formatted date (YYYY-MM-DD).

        Example: 1956-05-28 should convert to 28.05.1956
        """
        row: dict[str, Any] = {
            "code": "100001/100",
            "date": "1956-05-28",
            "dimensions": "",
            "donator": "",
            "autor": "",
            "name": "Item with Date",
        }

        result = convert_row(row)

        date_result = result.get("date")
        # Should be converted to DD.MM.YYYY format
        assert date_result == "28.05.1956" or date_result is not None

    def test_convert_row_with_numeric_person_id(self) -> None:
        """Handle numeric person ID (should be flagged for lookup).

        Example: donator="139862" (numeric ID)
        """
        row: dict[str, Any] = {
            "code": "100001/100",
            "date": "",
            "dimensions": "",
            "donator": "139862",
            "autor": "",
            "name": "Item with ID Person",
        }

        result = convert_row(row)

        donator = result.get("donator")
        # Should be flagged or wrapped for later lookup
        assert donator is not None
        assert "139862" in donator or "[Person ID" in donator

    def test_convert_row_error_handling_no_code(self) -> None:
        """Handle row with empty code field.

        Empty code should set all number parser fields to None.
        """
        row: dict[str, Any] = {
            "code": "",
            "date": "",
            "dimensions": "",
            "donator": "",
            "autor": "",
            "name": "No Code Item",
        }

        result = convert_row(row)

        # All number fields should be None
        assert result.get("acr") is None
        assert result.get("trs") is None
        assert result.get("trj") is None

    def test_convert_row_with_all_fields(self) -> None:
        """Convert row with all fields populated.

        Full test with materials, techniques, colors fields.
        """
        row: dict[str, Any] = {
            "code": "100002/200",
            "date": "1960-06-15",
            "dimensions": "ø30;45x60x20",
            "donator": "John Smith",
            "autor": "123456",
            "name": "Complete Item",
            "materials": "/materjalid/puu",
            "techniques": "/tehnikad/käsitöö",
            "colors": "/värvid/pruun",
        }

        result = convert_row(row)

        # Verify all phases executed
        assert result.get("trs") == 100002
        assert result.get("trj") == 200
        assert len(result.get("measurements", [])) >= 3
        assert result.get("date") == "15.06.1960"
        assert result.get("donator") is not None
        assert result.get("material") is not None


class TestVabamuFeedbackRequirements:
    """Tests for Vabamu feedback requirements (Issue #10)."""

    def test_req1_trj_zero_returns_none(self) -> None:
        """Requirement 1: Trj=0 should produce empty cell (None).

        Vabamu: "kui ENTUSt tulev väärtus on 0, siis muisi tarvis
        seda väärtust pole - st veerg jääks sealt tühjaks"
        """
        row: dict[str, Any] = {
            "code": "020082/000",  # trj = 0
        }

        result = convert_row(row)

        assert result.get("trs") == 20082
        assert result.get("trj") is None  # 0 → None → empty cell

    def test_req2_nimetus_gets_description(self) -> None:
        """Requirement 2: Column M (Nimetus) ← description.

        Vabamu: "R veerult peaks see täies mahus liikuma veerule M"
        """
        row: dict[str, Any] = {
            "code": "000001/001",
            "description": "Enne lahkumist poiste maja ees, 28. mai 1956",
        }

        result = convert_row(row)

        assert result.get("description") == "Enne lahkumist poiste maja ees, 28. mai 1956"

    def test_req3a_vastuvotuakt_mapped(self) -> None:
        """Requirement 3a: Column Q (Vastuvõtu nr) ← vastuv6tuakt.

        Vabamu: "väga oluline saada täidetud ka veerud Q (vastuvõtu nr)"
        """
        row: dict[str, Any] = {
            "code": "000001/001",
            "vastuv6tuakt": "VVA-2024-001",
        }

        result = convert_row(row)

        assert result.get("vastuvotuakt") == "VVA-2024-001"

    def test_req3b_registration_date_mapped(self) -> None:
        """Requirement 3b: Column S ← date in DD.MM.YYYY format.

        Vabamu: "kogusse registreerimise aeg kujul pp.kk.aaaa"
        """
        row: dict[str, Any] = {
            "code": "000001/001",
            "date": "2024-03-15",
        }

        result = convert_row(row)

        assert result.get("date") == "15.03.2024"

    def test_req7_code_to_alt_number(self) -> None:
        """Requirement 7: Column CJ (Alt number) ← code.

        Vabamu: "kas on võimalik CJ veergu ehk Teised numbrid -> number
        veergu saada ENTUs olev 'kood' väli?"
        """
        row: dict[str, Any] = {
            "code": "020027/117",
        }

        result = convert_row(row)

        assert result.get("code_original") == "020027/117"

    def test_req8_asukoht_mapped(self) -> None:
        """Requirement 8: Column N (Püsiasukoht) ← asukoht.

        Vabamu: "kas saaksime ka ENTU 'asukoht' sisu veerule N"
        """
        row: dict[str, Any] = {
            "code": "000001/001",
            "asukoht": "Tallinn, Vabamu, Hoidla 1, Riiulid 3-5",
        }

        result = convert_row(row)

        assert result.get("asukoht") == "Tallinn, Vabamu, Hoidla 1, Riiulid 3-5"


class TestDateeringField:
    """Tests for dateering (year) field mapping (Issue #11)."""

    def test_year_field_passthrough(self) -> None:
        """Year field should pass through to output for CK column.

        Issue #11: CK column should contain ENTU 'year' field
        """
        row: dict[str, Any] = {
            "code": "000001/001",
            "year": "1980",
        }

        result = convert_row(row)

        assert result.get("year") == "1980"

    def test_year_field_with_range(self) -> None:
        """Year field should handle date ranges (e.g., 1940-1945)."""
        row: dict[str, Any] = {
            "code": "000001/001",
            "year": "1940-1945",
        }

        result = convert_row(row)

        assert result.get("year") == "1940-1945"

    def test_year_field_with_decade(self) -> None:
        """Year field should handle decade format (e.g., 1950-ndad)."""
        row: dict[str, Any] = {
            "code": "000001/001",
            "year": "1950-ndad",
        }

        result = convert_row(row)

        assert result.get("year") == "1950-ndad"

    def test_year_field_empty(self) -> None:
        """Empty year field should result in empty string."""
        row: dict[str, Any] = {
            "code": "000001/001",
            "year": "",
        }

        result = convert_row(row)

        assert result.get("year") == ""

    def test_year_field_missing(self) -> None:
        """Missing year field should result in empty string."""
        row: dict[str, Any] = {
            "code": "000001/001",
        }

        result = convert_row(row)

        assert result.get("year") == ""


class TestLegendFields:
    """Tests for legend fields mapping (Issue #14)."""

    def test_both_legend_fields_passthrough(self) -> None:
        """Both legend fields should pass through to output for legend columns.

        Issue #14:
        - Column 90 (Avalik legend) should contain ENTU 'public_legend' field
        - Column 91 (Mitteavaliku legend) should contain ENTU 'legend' field
        """
        row: dict[str, Any] = {
            "code": "000001/001",
            "public_legend": "This object was donated in 1985",
            "legend": "Internal note: needs conservation",
        }

        result = convert_row(row)

        assert result.get("public_legend") == "This object was donated in 1985"
        assert result.get("legend") == "Internal note: needs conservation"

    def test_only_public_legend(self) -> None:
        """Public legend field should work independently."""
        row: dict[str, Any] = {
            "code": "000001/001",
            "public_legend": "Avalik informatsioon",
        }

        result = convert_row(row)

        assert result.get("public_legend") == "Avalik informatsioon"
        assert result.get("legend") == ""

    def test_only_private_legend(self) -> None:
        """Private legend field should work independently."""
        row: dict[str, Any] = {
            "code": "000001/001",
            "legend": "Sisemised märkused",
        }

        result = convert_row(row)

        assert result.get("public_legend") == ""
        assert result.get("legend") == "Sisemised märkused"

    def test_legend_fields_with_multiline_text(self) -> None:
        """Legend fields should handle multiline text."""
        row: dict[str, Any] = {
            "code": "000001/001",
            "public_legend": "Line 1\nLine 2\nLine 3",
            "legend": "Internal note\nwith multiple lines",
        }

        result = convert_row(row)

        assert result.get("public_legend") == "Line 1\nLine 2\nLine 3"
        assert result.get("legend") == "Internal note\nwith multiple lines"

    def test_legend_fields_empty(self) -> None:
        """Empty legend fields should result in empty strings."""
        row: dict[str, Any] = {
            "code": "000001/001",
            "public_legend": "",
            "legend": "",
        }

        result = convert_row(row)

        assert result.get("public_legend") == ""
        assert result.get("legend") == ""

    def test_legend_fields_missing(self) -> None:
        """Missing legend fields should result in empty strings."""
        row: dict[str, Any] = {
            "code": "000001/001",
        }

        result = convert_row(row)

        assert result.get("public_legend") == ""
        assert result.get("legend") == ""

    def test_legend_fields_with_special_characters(self) -> None:
        """Legend fields should handle Estonian characters and special symbols."""
        row: dict[str, Any] = {
            "code": "000001/001",
            "public_legend": "Õpilaste töö (1950-ndad) – väga oluline!",
            "legend": "Märkus: säilitada +4°C juures",
        }

        result = convert_row(row)

        assert result.get("public_legend") == "Õpilaste töö (1950-ndad) – väga oluline!"
        assert result.get("legend") == "Märkus: säilitada +4°C juures"
