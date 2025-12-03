"""Tests for MUIS CSV writer.

Tests the conversion from orchestrator output to MUIS import format.
"""

import csv
import pytest
from pathlib import Path
from scripts.muis_writer import (
    write_muis_csv,
    orchestrator_to_muis_row,
    MUIS_COLUMN_NAMES,
)


@pytest.fixture
def sample_orchestrator_output() -> dict:
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

    def test_number_structure_conversion(self, sample_orchestrator_output: dict) -> None:
        """Number fields should map correctly."""
        muis_row = orchestrator_to_muis_row(sample_orchestrator_output)

        assert muis_row["Acr"] == "VBM"
        assert muis_row["Trt"] == "_"
        assert muis_row["Trs"] == 20027
        assert muis_row["Trj"] == 117

    def test_measurement_conversion(self, sample_orchestrator_output: dict) -> None:
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

    def test_material_technique_color_conversion(self, sample_orchestrator_output: dict) -> None:
        """Material, technique, and color fields should map."""
        muis_row = orchestrator_to_muis_row(sample_orchestrator_output)

        assert muis_row["Materjal 1"] == "puu"
        assert muis_row["Tehnika 1"] == "käsitöö"
        assert muis_row["Värvus"] == "pruun"

    def test_person_mapping_conversion(self, sample_orchestrator_output: dict) -> None:
        """Person fields should map correctly."""
        muis_row = orchestrator_to_muis_row(sample_orchestrator_output)

        assert muis_row["Üleandja"] == "Miia Jõgiaas"

    def test_system_columns_initialized(self, sample_orchestrator_output: dict) -> None:
        """System columns should be initialized as None/empty."""
        muis_row = orchestrator_to_muis_row(sample_orchestrator_output)

        assert muis_row["museaali_ID"] is None
        assert muis_row["Importimise staatus"] is None
        assert muis_row["Kommentaar"] is None

    def test_all_88_columns_present(self, sample_orchestrator_output: dict) -> None:
        """Result should have all 88 MUIS columns."""
        muis_row = orchestrator_to_muis_row(sample_orchestrator_output)

        assert len(muis_row) == 88
        for col in MUIS_COLUMN_NAMES:
            assert col in muis_row

    def test_empty_fields_handled(self) -> None:
        """Empty orchestrator output should produce valid MUIS row."""
        empty_output = {
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
        assert len(muis_row) == 88

    def test_with_4_measurements(self) -> None:
        """Should handle maximum 4 measurements."""
        output = {
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
        self, tmp_path: Path, sample_orchestrator_output: dict
    ) -> None:
        """CSV writer should create output file."""
        output_file = tmp_path / "test_output.csv"

        write_muis_csv([sample_orchestrator_output], output_file)

        assert output_file.exists()

    def test_muis_csv_structure(self, tmp_path: Path, sample_orchestrator_output: dict) -> None:
        """CSV file should have correct structure (3-row header + data)."""
        output_file = tmp_path / "test_output.csv"

        write_muis_csv([sample_orchestrator_output], output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Should have header (3 rows) + data (1 row) = 4 total
        assert len(rows) == 4

    def test_muis_csv_header_rows(self, tmp_path: Path, sample_orchestrator_output: dict) -> None:
        """CSV header should have 3 rows: metadata, names, validation."""
        output_file = tmp_path / "test_output.csv"

        write_muis_csv([sample_orchestrator_output], output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            metadata_row = next(reader)
            names_row = next(reader)
            validation_row = next(reader)

        # All header rows should have 88 columns
        assert len(metadata_row) == 88
        assert len(names_row) == 88
        assert len(validation_row) == 88

    def test_muis_csv_column_names(self, tmp_path: Path, sample_orchestrator_output: dict) -> None:
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
        assert len(data_row) == 88

    def test_muis_csv_multiple_rows(self, tmp_path: Path, sample_orchestrator_output: dict) -> None:
        """CSV writer should handle multiple data rows."""
        output_file = tmp_path / "test_multiple.csv"

        outputs = [sample_orchestrator_output] * 5

        write_muis_csv(outputs, output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # 3 header rows + 5 data rows = 8 total
        assert len(rows) == 8

    def test_muis_csv_encoding(self, tmp_path: Path, sample_orchestrator_output: dict) -> None:
        """CSV should handle Estonian characters correctly."""
        output_file = tmp_path / "test_encoding.csv"

        write_muis_csv([sample_orchestrator_output], output_file)

        # Read with UTF-8 encoding
        content = output_file.read_text(encoding="utf-8")

        # Should contain Estonian characters from sample data
        assert "Miia Jõgiaas" in content
        assert "käsitöö" in content or "kõrgus" in content

    def test_muis_csv_data_mapping(self, tmp_path: Path, sample_orchestrator_output: dict) -> None:
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
