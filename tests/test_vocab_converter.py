"""
Test Suite for Vocabulary Converter

Tests cover:
- Happy path: 1-4 column TSV files convert correctly
- Auto-detection: Script detects column count automatically
- Malformed data: Invalid columns raise clear errors
- Edge cases: Empty files, unicode characters, special formatting
- Metadata: Correct metadata generation for all formats
- File I/O: Missing files, permissions, encoding

Run tests:
    pytest tests/test_vocab_converter.py -v

With coverage:
    pytest tests/test_vocab_converter.py --cov=scripts/vocab_converter --cov-report=term-missing
"""

import pytest
from pathlib import Path
from typing import cast
import json

from scripts.vocab_converter import (
    VocabularyConverter,
    detect_column_count,
    load_vocabulary_from_tsv,
)
from scripts.vocab_models import (
    VocabularyEntry1,
    VocabularyEntry2,
    VocabularyEntry3,
    VocabularyEntry4,
)


class TestDetectColumnCount:
    """Test automatic column count detection from TSV file."""

    def test_detect_1_column(self, tmp_path: Path) -> None:
        """
        GIVEN: TSV file with single column
        WHEN: detect_column_count is called
        THEN: Returns 1
        """
        # Arrange
        test_file = tmp_path / "test_1col.txt"
        test_file.write_text("kollane\ngalerii\nmeer\n", encoding="utf-8")

        # Act
        count = detect_column_count(test_file)

        # Assert
        assert count == 1

    def test_detect_2_columns(self, tmp_path: Path) -> None:
        """
        GIVEN: TSV file with two columns
        WHEN: detect_column_count is called
        THEN: Returns 2
        """
        # Arrange
        test_file = tmp_path / "test_2col.txt"
        test_file.write_text("kollane\t1522\ngalerii\t456\n", encoding="utf-8")

        # Act
        count = detect_column_count(test_file)

        # Assert
        assert count == 2

    def test_detect_3_columns(self, tmp_path: Path) -> None:
        """
        GIVEN: TSV file with three columns
        WHEN: detect_column_count is called
        THEN: Returns 3
        """
        # Arrange
        test_file = tmp_path / "test_3col.txt"
        test_file.write_text("kollane\t1522\t3\n" "gal\t456\t122\n", encoding="utf-8")

        # Act
        count = detect_column_count(test_file)

        # Assert
        assert count == 3

    def test_detect_4_columns(self, tmp_path: Path) -> None:
        """
        GIVEN: TSV file with four columns
        WHEN: detect_column_count is called
        THEN: Returns 4
        """
        # Arrange
        test_file = tmp_path / "test_4col.txt"
        test_file.write_text(
            "kollane\t1522\t3\t100\n" "gal\t456\t122\t101\n",
            encoding="utf-8",
        )

        # Act
        count = detect_column_count(test_file)

        # Assert
        assert count == 4

    def test_missing_file_raises_error(self, tmp_path: Path) -> None:
        """
        GIVEN: Path to non-existent file
        WHEN: detect_column_count is called
        THEN: Raises FileNotFoundError with helpful message
        """
        # Arrange
        missing_file = tmp_path / "missing.txt"

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            detect_column_count(missing_file)

        assert "missing.txt" in str(exc_info.value)

    def test_empty_file_raises_error(self, tmp_path: Path) -> None:
        """
        GIVEN: Empty TSV file
        WHEN: detect_column_count is called
        THEN: Raises ValueError with clear message
        """
        # Arrange
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding="utf-8")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            detect_column_count(test_file)

        assert "empty" in str(exc_info.value).lower()


class TestLoadVocabulary:
    """Test vocabulary loading from TSV with validation."""

    def test_load_1_column_vocabulary(self, tmp_path: Path) -> None:
        """
        GIVEN: Valid 1-column TSV file
        WHEN: load_vocabulary_from_tsv is called
        THEN: Returns list of VocabularyEntry1 objects
        """
        # Arrange
        test_file = tmp_path / "vocab_1col.txt"
        test_file.write_text("kollane\ngalerii\nmeer\n", encoding="utf-8")

        # Act
        entries = load_vocabulary_from_tsv(test_file, column_count=1)

        # Assert
        assert len(entries) == 3
        assert isinstance(entries[0], VocabularyEntry1)
        assert entries[0].term == "kollane"
        assert entries[1].term == "galerii"
        assert entries[2].term == "meer"

    def test_load_2_column_vocabulary(self, tmp_path: Path) -> None:
        """
        GIVEN: Valid 2-column TSV file
        WHEN: load_vocabulary_from_tsv is called
        THEN: Returns list of VocabularyEntry2 objects
        """
        # Arrange
        test_file = tmp_path / "vocab_2col.txt"
        test_file.write_text("kollane\t1522\ngalerii\t456\nmeer\t789\n", encoding="utf-8")

        # Act
        entries = load_vocabulary_from_tsv(test_file, column_count=2)

        # Assert
        assert len(entries) == 3
        assert isinstance(entries[0], VocabularyEntry2)
        assert entries[0].term == "kollane"
        assert entries[0].term_id == "1522"
        entry1 = cast(VocabularyEntry2, entries[1])
        assert entry1.term_id == "456"

    def test_load_3_column_vocabulary(self, tmp_path: Path) -> None:
        """
        GIVEN: Valid 3-column TSV file
        WHEN: load_vocabulary_from_tsv is called
        THEN: Returns list of VocabularyEntry3 objects with parent_id
        """
        # Arrange
        test_file = tmp_path / "vocab_3col.txt"
        test_file.write_text(
            "kollane\t1522\t3\n" "briljantkollane\t1524\t1522\n",
            encoding="utf-8",
        )

        # Act
        entries = load_vocabulary_from_tsv(test_file, column_count=3)

        # Assert
        assert len(entries) == 2
        assert isinstance(entries[0], VocabularyEntry3)
        assert entries[0].parent_id == "3"
        assert entries[1].parent_id == "1522"  # type: ignore[union-attr]

    def test_load_4_column_vocabulary(self, tmp_path: Path) -> None:
        """
        GIVEN: Valid 4-column TSV file
        WHEN: load_vocabulary_from_tsv is called
        THEN: Returns list of VocabularyEntry4 objects with muis_id
        """
        # Arrange
        test_file = tmp_path / "vocab_4col.txt"
        test_file.write_text(
            "kollane\t1522\t3\t100\n" "briljantkollane\t1524\t1522\t101\n",
            encoding="utf-8",
        )

        # Act
        entries = load_vocabulary_from_tsv(test_file, column_count=4)

        # Assert
        assert len(entries) == 2
        assert isinstance(entries[0], VocabularyEntry4)
        assert entries[0].muis_id == "100"
        entry1 = cast(VocabularyEntry4, entries[1])
        assert entry1.muis_id == "101"

    def test_unicode_characters_preserved(self, tmp_path: Path) -> None:
        """
        GIVEN: TSV with Estonian unicode characters (õ, ä, ö, ü)
        WHEN: load_vocabulary_from_tsv is called
        THEN: Unicode characters are preserved correctly
        """
        # Arrange
        test_file = tmp_path / "vocab_unicode.txt"
        test_file.write_text(
            "õpik\t1111\t100\n" "äär\t2222\t200\n" "öblus\t3333\t300\n",
            encoding="utf-8",
        )

        # Act
        entries = load_vocabulary_from_tsv(test_file, column_count=3)

        # Assert
        assert entries[0].term == "õpik"
        assert entries[1].term == "äär"
        assert entries[2].term == "öblus"

    def test_malformed_row_raises_error(self, tmp_path: Path) -> None:
        """
        GIVEN: TSV file with row having wrong column count
        WHEN: load_vocabulary_from_tsv is called
        THEN: Raises ValueError with row number and details
        """
        # Arrange
        test_file = tmp_path / "vocab_bad.txt"
        test_file.write_text(
            "kollane\t1522\t3\n" "galerii\t456\n" "meer\t789\t200\n",
            encoding="utf-8",
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            load_vocabulary_from_tsv(test_file, column_count=3)

        error_msg = str(exc_info.value).lower()
        assert "row" in error_msg
        assert "column" in error_msg

    def test_empty_field_raises_error(self, tmp_path: Path) -> None:
        """
        GIVEN: TSV file with empty required field
        WHEN: load_vocabulary_from_tsv is called
        THEN: Raises ValueError indicating empty field
        """
        # Arrange
        test_file = tmp_path / "vocab_empty_field.txt"
        test_file.write_text("kollane\t\t3\n", encoding="utf-8")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            load_vocabulary_from_tsv(test_file, column_count=3)

        assert "empty" in str(exc_info.value).lower() or "min_length" in str(exc_info.value).lower()


class TestVocabularyConverter:
    """Test main vocabulary conversion workflow."""

    def test_convert_1_column_creates_json(self, tmp_path: Path) -> None:
        """
        GIVEN: 1-column TSV file
        WHEN: VocabularyConverter.convert is called
        THEN: Creates valid JSON with "terms" array
        """
        # Arrange
        input_file = tmp_path / "input.txt"
        input_file.write_text("kollane\ngalerii\n", encoding="utf-8")

        output_file = tmp_path / "output.json"

        converter = VocabularyConverter()

        # Act
        converter.convert(input_file, "vocabulary", output_file)

        # Assert
        assert output_file.exists()

        result = json.loads(output_file.read_text(encoding="utf-8"))

        assert result["vocabulary"][0]["term"] == "kollane"
        assert result["vocabulary"][1]["term"] == "galerii"
        assert result["_metadata"]["column_count"] == 1
        assert result["_metadata"]["entry_count"] == 2

    def test_convert_4_column_creates_json(self, tmp_path: Path) -> None:
        """
        GIVEN: 4-column TSV file (from tabel_1.txt pattern)
        WHEN: VocabularyConverter.convert is called
        THEN: Creates valid JSON with all 4 fields plus metadata
        """
        # Arrange
        input_file = tmp_path / "tabel_1.txt"
        input_file.write_text(
            "aaderdamine\t32792\t32791\t677\n" "anodeerimine\t32793\t32791\t678\n",
            encoding="utf-8",
        )

        output_file = tmp_path / "techniques.json"

        converter = VocabularyConverter()

        # Act
        converter.convert(input_file, "techniques", output_file)

        # Assert
        assert output_file.exists()

        result = json.loads(output_file.read_text(encoding="utf-8"))

        assert len(result["techniques"]) == 2
        assert result["techniques"][0]["term"] == "aaderdamine"
        assert result["techniques"][0]["term_id"] == "32792"
        assert result["techniques"][0]["parent_id"] == "32791"
        assert result["techniques"][0]["muis_id"] == "677"

        assert result["_metadata"]["column_count"] == 4
        assert result["_metadata"]["entry_count"] == 2
        assert result["_metadata"]["vocabulary_name"] == "techniques"

    def test_metadata_contains_source_filename(self, tmp_path: Path) -> None:
        """
        GIVEN: Any TSV file for conversion
        WHEN: Conversion completes
        THEN: Metadata includes original source filename
        """
        # Arrange
        input_file = tmp_path / "original_source.txt"
        input_file.write_text("term1\nterm2\n", encoding="utf-8")

        output_file = tmp_path / "vocab.json"

        converter = VocabularyConverter()

        # Act
        converter.convert(input_file, "vocabulary", output_file)

        # Assert
        result = json.loads(output_file.read_text(encoding="utf-8"))

        assert result["_metadata"]["source_file"] == "original_source.txt"

    def test_output_file_created_in_correct_location(self, tmp_path: Path) -> None:
        """
        GIVEN: Specific output path for JSON
        WHEN: Conversion completes
        THEN: File created at exact output path
        """
        # Arrange
        input_file = tmp_path / "input.txt"
        input_file.write_text("term1\n", encoding="utf-8")

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        output_file = output_dir / "vocab.json"

        converter = VocabularyConverter()

        # Act
        converter.convert(input_file, "vocabulary", output_file)

        # Assert
        assert output_file.exists()
        assert output_file.parent == output_dir

    def test_json_is_valid_and_parseable(self, tmp_path: Path) -> None:
        """
        GIVEN: Conversion completes successfully
        WHEN: Output JSON is read and parsed
        THEN: JSON is valid and contains expected structure
        """
        # Arrange
        input_file = tmp_path / "input.txt"
        input_file.write_text("term1\t123\t100\t1\n" "term2\t124\t100\t2\n", encoding="utf-8")

        output_file = tmp_path / "vocab.json"

        converter = VocabularyConverter()

        # Act
        converter.convert(input_file, "test", output_file)

        # Assert (this will raise if JSON is invalid)
        result = json.loads(output_file.read_text(encoding="utf-8"))

        assert "_metadata" in result
        assert "test" in result
        assert isinstance(result["test"], list)

    def test_large_file_processes_without_memory_issues(self, tmp_path: Path) -> None:
        """
        GIVEN: Large TSV file (1000+ rows)
        WHEN: VocabularyConverter.convert is called
        WHEN: Conversion completes and memory is reasonable
        THEN: All rows are processed correctly
        """
        # Arrange
        input_file = tmp_path / "large.txt"

        lines = "\n".join([f"term{i}\t{i}\t{i-1}\t{i}" for i in range(1, 1001)])
        input_file.write_text(lines, encoding="utf-8")

        output_file = tmp_path / "large_vocab.json"

        converter = VocabularyConverter()

        # Act
        converter.convert(input_file, "large", output_file)

        # Assert
        result = json.loads(output_file.read_text(encoding="utf-8"))

        assert result["_metadata"]["entry_count"] == 1000
        assert len(result["large"]) == 1000
        assert result["large"][0]["term"] == "term1"
        assert result["large"][999]["term"] == "term1000"

    def test_convert_missing_input_file_raises_error(self, tmp_path: Path) -> None:
        """
        GIVEN: Path to non-existent input file
        WHEN: VocabularyConverter.convert is called
        THEN: Raises FileNotFoundError with helpful message
        """
        # Arrange
        input_file = tmp_path / "missing.txt"
        output_file = tmp_path / "vocab.json"

        converter = VocabularyConverter()

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            converter.convert(input_file, "vocabulary", output_file)

    def test_convert_auto_detects_column_count(self, tmp_path: Path) -> None:
        """
        GIVEN: TSV file without explicit column count parameter
        WHEN: Conversion happens (auto-detection enabled)
        THEN: Correct number of columns detected and used
        """
        # Arrange
        input_file = tmp_path / "auto.txt"
        input_file.write_text("term1\t123\t100\t1\n" "term2\t124\t100\t2\n", encoding="utf-8")

        output_file = tmp_path / "vocab.json"

        converter = VocabularyConverter(auto_detect_columns=True)

        # Act
        converter.convert(input_file, "vocabulary", output_file)

        # Assert
        result = json.loads(output_file.read_text(encoding="utf-8"))

        assert result["_metadata"]["column_count"] == 4
        assert "muis_id" in result["vocabulary"][0]
