"""Tests for MUIS CSV writer.

Tests the conversion from orchestrator output to MUIS import format.
"""

import csv
import pytest
from pathlib import Path
from typing import Any
from scripts.muis_writer import (
    write_muis_csv,
    orchestrator_to_muis_row,
    MUIS_COLUMN_NAMES,
)


@pytest.fixture
def sample_orchestrator_output() -> dict[str, Any]:
    """Sample output from orchestrator for testing."""
    return {
        "acr": "VBM",
        "trt": "_",
        "trs": 20027,
        "trj": 117,
        "trl": None,
        "kt": None,
        "ks": None,
        "kj": None,
        "kl": None,
        "measurements": [
            {"parameeter": "kõrgus", "yhik": "mm", "vaartus": 168},
            {"parameeter": "laius", "yhik": "mm", "vaartus": 121},
        ],
        "date": None,
        "donator": "Miia Jõgiaas",
        "autor": None,
        "material": "puu",
        "technique": "käsitöö",
        "color": "pruun",
        "name": "Enne lahkumist",
        "description": "Photo from 1956",
        "donator_direct": "Miia Jõgiaas",
        "autor_direct": None,
    }


class TestOrchestratorToMuisRow:
    """Tests for converting orchestrator output to MUIS row."""

    def test_number_structure_conversion(self, sample_orchestrator_output: dict[str, Any]) -> None:
        """Number fields should map correctly."""
        muis_row = orchestrator_to_muis_row(sample_orchestrator_output)

        assert muis_row["Acr"] == "VBM"
        assert muis_row["Trt"] == "_"
        assert muis_row["Trs"] == 20027
        assert muis_row["Trj"] == 117

    def test_measurement_conversion(self, sample_orchestrator_output: dict[str, Any]) -> None:
        """Measurements should expand to separate columns."""
        muis_row = orchestrator_to_muis_row(sample_orchestrator_output)

        assert muis_row["Parameeter 1"] == "kõrgus"
        assert muis_row["Ühik 1"] == "mm"
        assert muis_row["Väärtus 1"] == 168

        assert muis_row["Parameeter 2"] == "laius"
        assert muis_row["Ühik 2"] == "mm"
        assert muis_row["Väärtus 2"] == 121

        # Empty slots
        assert muis_row["Parameeter 3"] is None
        assert muis_row["Parameeter 4"] is None

    def test_material_technique_color_conversion(
        self, sample_orchestrator_output: dict[str, Any]
    ) -> None:
        """Material, technique, and color fields should map."""
        muis_row = orchestrator_to_muis_row(sample_orchestrator_output)

        assert muis_row["Materjal 1"] == "puu"
        assert muis_row["Tehnika 1"] == "käsitöö"
        assert muis_row["Värvus"] == "pruun"

    def test_person_mapping_conversion(self, sample_orchestrator_output: dict[str, Any]) -> None:
        """Person fields should map correctly."""
        muis_row = orchestrator_to_muis_row(sample_orchestrator_output)

        assert muis_row["Üleandja"] == "Miia Jõgiaas"

    def test_system_columns_initialized(self, sample_orchestrator_output: dict[str, Any]) -> None:
        """System columns should be initialized as None/empty."""
        muis_row = orchestrator_to_muis_row(sample_orchestrator_output)

        assert muis_row["museaali_ID"] is None
        assert muis_row["Importimise staatus"] is None
        assert muis_row["Kommentaar"] is None

    def test_all_92_columns_present(self, sample_orchestrator_output: dict[str, Any]) -> None:
        """Result should have all 91 MUIS columns."""
        muis_row = orchestrator_to_muis_row(sample_orchestrator_output)

        assert len(muis_row) == 91
        for col in MUIS_COLUMN_NAMES:
            assert col in muis_row

    def test_empty_fields_handled(self) -> None:
        """Empty orchestrator output should produce valid MUIS row."""
        empty_output: dict[str, Any] = {
            "acr": None,
            "trt": None,
            "trs": None,
            "trj": None,
            "measurements": [],
            "name": "",
            "description": None,
        }

        muis_row = orchestrator_to_muis_row(empty_output)

        assert isinstance(muis_row, dict)
        assert len(muis_row) == 91

    def test_with_4_measurements(self) -> None:
        """Should handle maximum 4 measurements."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [
                {"parameeter": "kõrgus", "yhik": "mm", "vaartus": 100},
                {"parameeter": "laius", "yhik": "mm", "vaartus": 200},
                {"parameeter": "sügavus", "yhik": "mm", "vaartus": 50},
                {"parameeter": "läbimõõt", "yhik": "mm", "vaartus": 30},
            ],
            "name": "Test",
            "description": None,
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Väärtus 1"] == 100
        assert muis_row["Väärtus 2"] == 200
        assert muis_row["Väärtus 3"] == 50
        assert muis_row["Väärtus 4"] == 30


class TestWriteMuisCsv:
    """Tests for CSV file writing."""

    def test_write_muis_csv_creates_file(
        self, tmp_path: Path, sample_orchestrator_output: dict[str, Any]
    ) -> None:
        """CSV writer should create output file."""
        output_file = tmp_path / "test_output.csv"

        write_muis_csv([sample_orchestrator_output], output_file)

        assert output_file.exists()

    def test_muis_csv_structure(
        self, tmp_path: Path, sample_orchestrator_output: dict[str, Any]
    ) -> None:
        """CSV file should have correct structure (3-row header + data)."""
        output_file = tmp_path / "test_output.csv"

        write_muis_csv([sample_orchestrator_output], output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Should have header (3 rows) + data (1 row) = 4 total
        assert len(rows) == 4

    def test_muis_csv_header_rows(
        self, tmp_path: Path, sample_orchestrator_output: dict[str, Any]
    ) -> None:
        """CSV header should have 3 rows: metadata, names, validation."""
        output_file = tmp_path / "test_output.csv"

        write_muis_csv([sample_orchestrator_output], output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            metadata_row = next(reader)
            names_row = next(reader)
            validation_row = next(reader)

        # All header rows should have 91 columns
        assert len(metadata_row) == 91
        assert len(names_row) == 91
        assert len(validation_row) == 91

    def test_muis_csv_column_names(
        self, tmp_path: Path, sample_orchestrator_output: dict[str, Any]
    ) -> None:
        """Column names row should match MUIS_COLUMN_NAMES."""
        output_file = tmp_path / "test_output.csv"

        write_muis_csv([sample_orchestrator_output], output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            # Skip first 3 header rows
            for _ in range(3):
                next(f)
            # Read data with DictReader using MUIS column names as fieldnames
            reader = csv.DictReader(f, fieldnames=MUIS_COLUMN_NAMES)
            data_row = next(reader)

        # Check that data row is readable
        assert data_row is not None
        assert len(data_row) == 91

    def test_muis_csv_multiple_rows(
        self, tmp_path: Path, sample_orchestrator_output: dict[str, Any]
    ) -> None:
        """CSV writer should handle multiple data rows."""
        output_file = tmp_path / "test_multiple.csv"

        outputs = [sample_orchestrator_output] * 5

        write_muis_csv(outputs, output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # 3 header rows + 5 data rows = 8 total
        assert len(rows) == 8

    def test_muis_csv_encoding(
        self, tmp_path: Path, sample_orchestrator_output: dict[str, Any]
    ) -> None:
        """CSV should handle Estonian characters correctly."""
        output_file = tmp_path / "test_encoding.csv"

        write_muis_csv([sample_orchestrator_output], output_file)

        # Read with UTF-8 encoding
        content = output_file.read_text(encoding="utf-8")

        # Should contain Estonian characters from sample data
        assert "Miia Jõgiaas" in content
        assert "käsitöö" in content or "kõrgus" in content

    def test_muis_csv_data_mapping(
        self, tmp_path: Path, sample_orchestrator_output: dict[str, Any]
    ) -> None:
        """Data row should have correctly mapped values."""
        output_file = tmp_path / "test_mapping.csv"

        write_muis_csv([sample_orchestrator_output], output_file)

        # Read CSV with DictReader, skipping header rows
        with open(output_file, "r", encoding="utf-8") as f:
            for _ in range(3):  # Skip 3 header rows
                next(f)
            reader = csv.DictReader(f, fieldnames=MUIS_COLUMN_NAMES)
            data_row = next(reader)

        # Verify key fields are mapped
        assert data_row["Acr"] == "VBM"
        assert data_row["Trs"] == "20027"
        assert data_row["Üleandja"] == "Miia Jõgiaas"


class TestVabamuFeedbackColumnMappings:
    """Tests for Vabamu feedback column mappings (GitHub issue #10)."""

    def test_nimetus_from_description(self) -> None:
        """Nimetus column (M) should contain description/kirjeldus content."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Object Name",
            "description": "Full kirjeldus content goes here",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Nimetus"] == "Full kirjeldus content goes here"

    def test_pusiasukoht_from_asukoht(self) -> None:
        """Püsiasukoht column (N) should contain asukoht field."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "asukoht": "Storage Room A, Shelf 5",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Püsiasukoht"] == "Storage Room A, Shelf 5"

    def test_vastuvotu_nr_from_vastuvotuakt(self) -> None:
        """Vastuvõtu nr column (Q) should contain vastuvõtuakt field."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "vastuvotuakt": "VA-2024-001",  # orchestrator output key
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Vastuvõtu nr"] == "VA-2024-001"

    def test_registration_date_from_date(self) -> None:
        """Koguse registreerimise aeg column (S) should contain date field."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "date": "15.01.2024",  # orchestrator output key
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Koguse registreerimise aeg"] == "15.01.2024"

    def test_alt_number_from_code_original(self) -> None:
        """Alt number column (CJ) should contain code_original field."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "code_original": "OLD-123-456",  # orchestrator output key
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Alt number"] == "OLD-123-456"

    def test_trj_zero_results_in_empty(self) -> None:
        """Trj column should be empty when trj=0 or None."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": None,  # This should result in empty
            "measurements": [],
            "name": "Test",
            "description": None,
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Trj"] is None

    def test_all_vabamu_fields_together(self) -> None:
        """All Vabamu feedback fields should work together."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 20027,
            "trj": 117,
            "measurements": [],
            "name": "Object Name",
            "description": "Full description for Nimetus",
            "asukoht": "Storage Room B",
            "vastuvotuakt": "VA-2024-002",  # orchestrator output key
            "date": "20.02.2024",  # orchestrator output key
            "code_original": "LEGACY-789",  # orchestrator output key
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Nimetus"] == "Full description for Nimetus"
        assert muis_row["Püsiasukoht"] == "Storage Room B"
        assert muis_row["Vastuvõtu nr"] == "VA-2024-002"
        assert muis_row["Koguse registreerimise aeg"] == "20.02.2024"
        assert muis_row["Alt number"] == "LEGACY-789"


class TestDateeringColumnMapping:
    """Tests for CK column (Dateering) mapping (Issue #11)."""

    def test_dateering_from_year_field(self) -> None:
        """Dateering column (CK) should contain year field from orchestrator."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "year": "1980",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Dateering"] == "1980"

    def test_dateering_with_range(self) -> None:
        """Dateering should handle date ranges."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "year": "1940-1945",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Dateering"] == "1940-1945"

    def test_dateering_with_decade(self) -> None:
        """Dateering should handle decade format."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "year": "1950-ndad",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Dateering"] == "1950-ndad"

    def test_dateering_empty(self) -> None:
        """Dateering column should be None when year is empty."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "year": "",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Dateering"] == ""

    def test_dateering_missing(self) -> None:
        """Dateering column should be None when year field is missing."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Dateering"] is None

    def test_all_92_columns_present(self) -> None:
        """Result should have all 91 MUIS columns (including CK, CL, CM)."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "year": "2000",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert len(muis_row) == 91
        assert "Dateering" in muis_row
        for col in MUIS_COLUMN_NAMES:
            assert col in muis_row


class TestLegendColumns:
    """Tests for CL (Avalik legend) and CM (Mitteavaliku legend) columns - Issue #14."""

    def test_both_legend_fields_present(self) -> None:
        """Both legend fields should map to CL and CM columns."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "public_legend": "This is visible to the public",
            "legend": "This is internal information",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Avalik legend"] == "This is visible to the public"
        assert muis_row["Mitteavaliku legend"] == "This is internal information"

    def test_only_public_legend(self) -> None:
        """Only public_legend field should map to CL column."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "public_legend": "Public information only",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Avalik legend"] == "Public information only"
        assert muis_row["Mitteavaliku legend"] is None

    def test_only_private_legend(self) -> None:
        """Only legend field should map to CM column."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "legend": "Internal notes only",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Avalik legend"] is None
        assert muis_row["Mitteavaliku legend"] == "Internal notes only"

    def test_both_legend_fields_empty(self) -> None:
        """Empty legend fields should result in None values."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "public_legend": "",
            "legend": "",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Avalik legend"] == ""
        assert muis_row["Mitteavaliku legend"] == ""

    def test_both_legend_fields_missing(self) -> None:
        """Missing legend fields should result in None values."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
        }

        muis_row = orchestrator_to_muis_row(output)

        assert muis_row["Avalik legend"] is None
        assert muis_row["Mitteavaliku legend"] is None

    def test_legend_columns_in_column_names(self) -> None:
        """CL and CM columns should be in MUIS_COLUMN_NAMES."""
        assert "Avalik legend" in MUIS_COLUMN_NAMES
        assert "Mitteavaliku legend" in MUIS_COLUMN_NAMES

        # Check positions (90 and 91, 0-indexed 89 and 90)
        assert MUIS_COLUMN_NAMES[89] == "Avalik legend"
        assert MUIS_COLUMN_NAMES[90] == "Mitteavaliku legend"

    def test_all_92_columns_with_legends(self) -> None:
        """Result should have all 91 MUIS columns including legend columns."""
        output: dict[str, Any] = {
            "acr": "VBM",
            "trt": "_",
            "trs": 1,
            "trj": 1,
            "measurements": [],
            "name": "Test",
            "description": None,
            "public_legend": "Public",
            "legend": "Private",
        }

        muis_row = orchestrator_to_muis_row(output)

        assert len(muis_row) == 91
        assert "Avalik legend" in muis_row
        assert "Mitteavaliku legend" in muis_row
        for col in MUIS_COLUMN_NAMES:
            assert col in muis_row
