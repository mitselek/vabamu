"""Tests for person name extraction (TDD)."""

import csv
from pathlib import Path
import pytest
from scripts.extract_person_names import (
    classify_entity,
    extract_persons,
    parse_multiline_names,
    write_registry_request,
)


class TestClassifyEntity:
    """Test entity type classification."""

    def test_person_lastname_firstname_format(self) -> None:
        """Comma-separated names are persons."""
        assert classify_entity("Tamm, Jaan") == "person"
        assert classify_entity("Jõgiaas, Miia") == "person"
        assert classify_entity("Lagle, Salme, Hans") == "person"

    def test_organization_with_museum_keyword(self) -> None:
        """Museum names are organizations."""
        assert classify_entity("Eesti Rahva Muuseum") == "organization"
        assert classify_entity("Tartu Ülikooli Museum") == "organization"

    def test_organization_with_company_suffix(self) -> None:
        """Company suffixes indicate organizations."""
        assert classify_entity("Kultuuripärandi OÜ") == "organization"
        assert classify_entity("Muinsuskaitse AS") == "organization"
        assert classify_entity("Fond SA") == "organization"

    def test_organization_with_institute_keyword(self) -> None:
        """Institute names are organizations."""
        assert classify_entity("Eesti Instituut") == "organization"
        assert classify_entity("Research Institute") == "organization"

    def test_default_to_person(self) -> None:
        """Unknown patterns default to person."""
        assert classify_entity("Unknown Entity") == "person"
        assert classify_entity("John Smith") == "person"


class TestParseMultilineNames:
    """Test parsing of multiline name fields."""

    def test_single_name(self) -> None:
        """Single name returns list with one element."""
        result = parse_multiline_names("Tamm, Jaan")
        assert result == ["Tamm, Jaan"]

    def test_multiline_names(self) -> None:
        """Newline-separated names are split."""
        text = "Tamm, Jaan\nKask, Mari\nLepp, Peeter"
        result = parse_multiline_names(text)
        assert len(result) == 3
        assert "Tamm, Jaan" in result
        assert "Kask, Mari" in result
        assert "Lepp, Peeter" in result

    def test_windows_line_endings(self) -> None:
        """CRLF line endings are handled."""
        text = "Tamm, Jaan\r\nKask, Mari"
        result = parse_multiline_names(text)
        assert len(result) == 2

    def test_empty_lines_filtered(self) -> None:
        """Empty lines are filtered out."""
        text = "Tamm, Jaan\n\n\nKask, Mari\n"
        result = parse_multiline_names(text)
        assert len(result) == 2
        assert "" not in result

    def test_whitespace_trimmed(self) -> None:
        """Leading/trailing whitespace is removed."""
        text = "  Tamm, Jaan  \n  Kask, Mari  "
        result = parse_multiline_names(text)
        assert result == ["Tamm, Jaan", "Kask, Mari"]


class TestExtractPersons:
    """Test full extraction workflow."""

    @pytest.fixture
    def sample_csv(self, tmp_path: Path) -> Path:
        """Create sample CSV for testing."""
        csv_path = tmp_path / "sample.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["code", "donator", "represseeritu_o"]
            )
            writer.writeheader()
            writer.writerow(
                {"code": "001", "donator": "Tamm, Jaan", "represseeritu_o": ""}
            )
            writer.writerow(
                {
                    "code": "002",
                    "donator": "Tamm, Jaan",
                    "represseeritu_o": "Kask, Mari",
                }
            )
            writer.writerow(
                {
                    "code": "003",
                    "donator": "",
                    "represseeritu_o": "Eesti Rahva Muuseum",
                }
            )
        return csv_path

    @pytest.fixture
    def multiline_csv(self, tmp_path: Path) -> Path:
        """Create CSV with multiline name fields."""
        csv_path = tmp_path / "multiline.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["code", "donator", "represseeritu_o"]
            )
            writer.writeheader()
            writer.writerow(
                {
                    "code": "001",
                    "donator": "Tamm, Jaan",
                    "represseeritu_o": "Kask, Mari\nLepp, Peeter",
                }
            )
        return csv_path

    def test_extract_unique_names(self, sample_csv: Path) -> None:
        """Extract unique names with correct frequencies."""
        results = extract_persons(sample_csv)

        # Should have 3 unique entities
        assert len(results) == 3

        # Check Tamm, Jaan (appears twice in donator field)
        tamm_record = next(
            r for r in results if r["entu_value"] == "Tamm, Jaan"
        )
        assert tamm_record["frequency"] == 2
        assert tamm_record["entity_type"] == "person"
        assert tamm_record["entu_field"] == "donator"

        # Check Kask, Mari (appears once in represseeritu_o field)
        kask_record = next(
            r for r in results if r["entu_value"] == "Kask, Mari"
        )
        assert kask_record["frequency"] == 1
        assert kask_record["entity_type"] == "person"
        assert kask_record["entu_field"] == "represseeritu_o"

        # Check museum (organization)
        museum_record = next(
            r for r in results if "Muuseum" in str(r["entu_value"])
        )
        assert museum_record["entity_type"] == "organization"

    def test_sample_records_included(self, sample_csv: Path) -> None:
        """Sample record IDs are included."""
        results = extract_persons(sample_csv)
        tamm_record = next(
            r for r in results if r["entu_value"] == "Tamm, Jaan"
        )

        # Should include both record IDs
        sample_records_str = str(tamm_record["sample_records"])
        assert "001" in sample_records_str
        assert "002" in sample_records_str

    def test_sorted_by_frequency(self, sample_csv: Path) -> None:
        """Results are sorted by frequency (descending)."""
        results = extract_persons(sample_csv)

        # Tamm appears twice, so should be first
        assert results[0]["entu_value"] == "Tamm, Jaan"
        assert results[0]["frequency"] == 2

    def test_multiline_names_split(self, multiline_csv: Path) -> None:
        """Multiline name fields are properly split."""
        results = extract_persons(multiline_csv)

        # Should have 3 unique names
        assert len(results) == 3

        # Check all names are present
        names = [r["entu_value"] for r in results]
        assert "Tamm, Jaan" in names
        assert "Kask, Mari" in names
        assert "Lepp, Peeter" in names

        # Multiline names should reference same record
        kask = next(r for r in results if r["entu_value"] == "Kask, Mari")
        lepp = next(r for r in results if r["entu_value"] == "Lepp, Peeter")
        assert kask["sample_records"] == "001"
        assert lepp["sample_records"] == "001"

    def test_empty_fields_ignored(self, tmp_path: Path) -> None:
        """Empty and whitespace-only fields are ignored."""
        csv_path = tmp_path / "empty.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["code", "donator", "represseeritu_o"]
            )
            writer.writeheader()
            writer.writerow(
                {"code": "001", "donator": "", "represseeritu_o": "   "}
            )

        results = extract_persons(csv_path)
        assert len(results) == 0

    def test_estonian_characters_preserved(self, tmp_path: Path) -> None:
        """Estonian characters are preserved correctly."""
        csv_path = tmp_path / "estonian.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["code", "donator", "represseeritu_o"]
            )
            writer.writeheader()
            writer.writerow(
                {
                    "code": "001",
                    "donator": "Jõgiaas, Miia",
                    "represseeritu_o": "Tikerpäe, Asta",
                }
            )

        results = extract_persons(csv_path)

        names = [r["entu_value"] for r in results]
        assert "Jõgiaas, Miia" in names
        assert "Tikerpäe, Asta" in names


class TestWriteRegistryRequest:
    """Test CSV output generation."""

    def test_write_creates_file(self, tmp_path: Path) -> None:
        """Output file is created with correct structure."""
        output_path = tmp_path / "output.csv"
        results: list[dict[str, str | int]] = [
            {
                "entu_field": "donator",
                "entu_value": "Tamm, Jaan",
                "entity_type": "person",
                "frequency": 2,
                "sample_records": "001, 002",
            }
        ]

        write_registry_request(results, output_path)

        assert output_path.exists()

        # Check header
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            assert fieldnames == [
                "entu_field",
                "entu_value",
                "entity_type",
                "frequency",
                "sample_records",
                "muis_participant_id",
                "notes",
            ]

            # Check data row
            row = next(reader)
            assert row["entu_field"] == "donator"
            assert row["entu_value"] == "Tamm, Jaan"
            assert row["entity_type"] == "person"
            assert row["frequency"] == "2"
            assert row["sample_records"] == "001, 002"
            assert row["muis_participant_id"] == ""
            assert row["notes"] == ""

    def test_creates_parent_directory(self, tmp_path: Path) -> None:
        """Parent directories are created if they don't exist."""
        output_path = tmp_path / "subdir" / "output.csv"
        results: list[dict[str, str | int]] = [
            {
                "entu_field": "donator",
                "entu_value": "Test",
                "entity_type": "person",
                "frequency": 1,
                "sample_records": "001",
            }
        ]

        write_registry_request(results, output_path)

        assert output_path.exists()
        assert output_path.parent.exists()
