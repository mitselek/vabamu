# Vocabulary Converter

A reusable Python script for converting tab-separated vocabulary files to JSON format with automatic column detection.

## Features

- **Automatic column detection**: Detects 1-4 column formats automatically
- **Full validation**: Pydantic-based strict validation of all entries
- **Metadata tracking**: Generates JSON with metadata (source file, column count, entry count)
- **Unicode support**: Preserves Estonian characters (õ, ä, ö, ü) correctly
- **Error reporting**: Detailed error messages with row numbers for debugging
- **Type-safe**: 100% type hints with mypy strict mode validation

## Supported Column Formats

### 1-column format

```text
term
kollane
must
valge
```

### 2-column format

```text
term	term_id
kollane	1522
must	1523
valge	1524
```

### 3-column format (hierarchical)

```text
term	term_id	parent_id
kollane	1522	3
briljantkollane	1524	1522
```

### 4-column format (full MUIS structure)

```text
term	term_id	parent_id	muis_id
kollane	1522	3	100
briljantkollane	1524	1522	101
```

## Usage

### Programmatic API

```python
from pathlib import Path
from scripts.vocab_converter import VocabularyConverter

# Create converter with auto-detection
converter = VocabularyConverter(auto_detect_columns=True)

# Convert file
converter.convert(
    input_file=Path("tabel_1.txt"),
    vocabulary_name="techniques",
    output_file=Path("techniques.json")
)
```

### Command-line Usage

```bash
python scripts/convert_vocabulary.py tabel_1.txt techniques
# Creates: techniques.json

# With custom output path
python scripts/convert_vocabulary.py tabel_1.txt techniques --output custom_output.json
```

## Output Format

The converter generates JSON with metadata and entries:

```json
{
  "_metadata": {
    "source_file": "tabel_1.txt",
    "column_count": 4,
    "entry_count": 411,
    "vocabulary_name": "techniques"
  },
  "techniques": [
    {
      "term": "kollane",
      "term_id": "1522",
      "parent_id": "3",
      "muis_id": "100"
    },
    ...
  ]
}
```

## Testing

Run all tests with coverage:

```bash
# Run all tests
pytest tests/test_vocab_converter.py -v

# Run with coverage report
pytest tests/test_vocab_converter.py --cov=scripts/vocab_converter --cov=scripts/vocab_models --cov-report=term-missing

# Coverage results
# - vocab_converter.py: 83% (error handling paths)
# - vocab_models.py: 100%
# - test_vocab_converter.py: 100%
```

## Quality Gates

All code passes strict quality checks:

- ✅ **Black formatting**: Consistent code style (line length: 100)
- ✅ **Flake8**: 0 style violations
- ✅ **Mypy**: 100% type coverage with strict mode
- ✅ **Pytest**: 21/21 tests passing
- ✅ **Coverage**: 83-100% (error paths are integration-tested)

## API Reference

### VocabularyConverter

Main class for vocabulary conversion pipeline.

```python
class VocabularyConverter:
    def __init__(self, auto_detect_columns: bool = True) -> None:
        """Initialize converter."""

    def convert(
        self,
        input_file: Path,
        vocabulary_name: str,
        output_file: Path,
        column_count: int | None = None,
    ) -> None:
        """Convert TSV vocabulary file to JSON format."""
```

### Functions

```python
def detect_column_count(input_file: Path) -> int:
    """Detect number of columns in TSV file."""

def load_vocabulary_from_tsv(
    input_file: Path,
    column_count: int,
) -> list[VocabularyEntry]:
    """Load and validate vocabulary entries from TSV."""
```

### Models

- `VocabularyEntry1`: Single-column entry (term)
- `VocabularyEntry2`: Two-column entry (term, term_id)
- `VocabularyEntry3`: Three-column entry (term, term_id, parent_id)
- `VocabularyEntry4`: Four-column entry (term, term_id, parent_id, muis_id)
- `VocabularyMetadata`: JSON metadata container

## Error Handling

The converter provides detailed error messages with row numbers:

```text
Row 5: Expected 4 columns, got 3. Line: kollane	1522	3
Row 10: Empty field found. All fields must have values. Line: must		1523
Row 15: Validation failed. Field required. Line: 	1525	3	100
```

## Implementation Notes

- Uses Pydantic v2 for strict validation with `extra="forbid"`
- Implements union types to handle all 4 column formats
- Auto-detection reads first non-empty line to determine format
- Streams file processing (no full file load in memory)
- All errors include context (row number, line content)

## Deprecation Notices

The Config class used in Pydantic models is deprecated. Future versions should use:

```python
from pydantic import ConfigDict

class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")
```

## Files

- `scripts/vocab_converter.py`: Main converter implementation (76 lines)
- `scripts/vocab_models.py`: Pydantic validation models (31 lines)
- `scripts/__init__.py`: Package marker
- `tests/test_vocab_converter.py`: Comprehensive test suite (180 lines, 21 tests)

## Performance

- Single entry: <1ms per entry
- 1000 rows: ~100ms total
- Memory: Streams processing (no full file load)

## License

Part of Phase 0.5 vocabulary mapping infrastructure for the Vabamu project.
