# Convert Single Sample Row to MUIS Format

## Overview

Implement end-to-end conversion pipeline to transform a single ENTU sample record into valid MUIS 85-column format. This will serve as a proof-of-concept before processing the full 80K+ records.

## Context

**Source**: `/output/sample_100_raw.csv` - First row with complete data
**Target**: MUIS import CSV with 85-88 columns matching `reference/muis_example_format.csv` structure
**Documentation**: See `/docs/FIELD_MAPPINGS.md` for complete field mappings

## Objectives

1. Create modular conversion pipeline with subscripts for each transformation type
2. Process one complete sample record through entire pipeline
3. Validate output against MUIS reference format
4. Identify edge cases and missing mappings for Phase 2

## Architecture

### Script Structure

```text
scripts/
├── convert_row.py          # Main orchestration script (new)
├── parsers/                # Transformation subscripts (new directory)
│   ├── __init__.py
│   ├── number_parser.py    # Parse ENTU code → 9 MUIS columns
│   ├── dimension_parser.py # Parse dimensions → 12 measurement columns
│   ├── date_parser.py      # ISO dates → DD.MM.YYYY format
│   ├── person_mapper.py    # Person IDs → Name format (stub for now)
│   └── vocab_mapper.py     # Material/technique lookups
├── models.py               # Already exists (EntuEksponaat, MuisMuseaal)
└── muis_writer.py          # CSV writer with 3-row header
```

### Data Flow

```text
┌─────────────────────┐
│ sample_100_raw.csv  │
│  (row 1)            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  convert_row.py     │  ← Main orchestrator
│  - Load sample row  │
│  - Call subscripts  │
│  - Validate output  │
└──────────┬──────────┘
           │
           ├──────────────────────┐
           │                      │
           ▼                      ▼
┌──────────────────┐    ┌──────────────────┐
│ Parsers/         │    │ Vocab Lookups    │
│ - number_parser  │    │ - materials.json │
│ - dimension_...  │    │ - techniques.json│
│ - date_parser    │    │ - colors.json    │
└──────────┬───────┘    └────────┬─────────┘
           │                     │
           └──────────┬──────────┘
                      ▼
           ┌──────────────────┐
           │ MuisMuseaal      │
           │ (Pydantic model) │
           └──────────┬───────┘
                      │
                      ▼
           ┌──────────────────┐
           │  muis_writer.py  │
           └──────────┬───────┘
                      │
                      ▼
           ┌──────────────────┐
           │ output/          │
           │ sample_1_muis.csv│
           └──────────────────┘
```

## Implementation Tasks

### Task 1: Create Number Parser (scripts/parsers/number_parser.py)

**Input**: ENTU `code` field (e.g., `"020027/117"`)
**Output**: Dictionary with 9 MUIS number fields

```python
def parse_entu_code(code: str) -> dict:
    """
    Parse ENTU object number into MUIS structure.
    
    ENTU format: "NNNNNN/NNN" or variations
    MUIS output: ACR, TRT, TRS, TRJ, TRL, KT, KS, KJ, KL
    
    Args:
        code: ENTU object number (e.g., "020027/117")
    
    Returns:
        {
            'acr': 'VBM',      # Always "VBM" for Vabamu
            'trt': '_',         # Always underscore
            'trs': 20027,       # Main series (parse leading zeros)
            'trj': 117,         # Sub-series
            'trl': None,        # Empty
            'kt': None,         # From kuuluvus (handle in convert_row)
            'ks': None,         # Empty
            'kj': None,         # Empty
            'kl': None          # Empty
        }
    
    Examples:
        >>> parse_entu_code("020027/117")
        {'acr': 'VBM', 'trt': '_', 'trs': 20027, 'trj': 117, ...}
        
        >>> parse_entu_code("006562/001")
        {'acr': 'VBM', 'trt': '_', 'trs': 6562, 'trj': 1, ...}
    
    Raises:
        ValueError: If code format is invalid
    """
    pass  # Implement parsing logic
```

**Edge cases to handle**:

- Leading zeros: `"020027"` → `20027` (integer)
- Missing slash: `"123456"` → TRS only, TRJ = 1
- Non-standard formats: Log warning and attempt parse

**Tests**: Write 5+ test cases in `tests/test_number_parser.py`

---

### Task 2: Create Dimension Parser (scripts/parsers/dimension_parser.py)

**Input**: ENTU `dimensions` field (e.g., `"168x121"`, `"ø50;62x70"`)
**Output**: List of measurement dictionaries (up to 4)

```python
def parse_dimensions(dim_str: str) -> list[dict]:
    """
    Parse ENTU dimensions into MUIS measurement sets.
    
    ENTU patterns:
    - "ø50" → diameter
    - "62x70" → height x width
    - "H:50 L:60 S:70" → labeled dimensions
    - "ø50;62x70" → multiple measurements (semicolon separator)
    
    MUIS output: Up to 4 sets of (parameeter, yhik, vaartus)
    
    Args:
        dim_str: ENTU dimensions string
    
    Returns:
        [
            {'parameeter': 'laius', 'yhik': 'mm', 'vaartus': 168},
            {'parameeter': 'kõrgus', 'yhik': 'mm', 'vaartus': 121}
        ]
    
    Examples:
        >>> parse_dimensions("168x121")
        [
            {'parameeter': 'laius', 'yhik': 'mm', 'vaartus': 168},
            {'parameeter': 'kõrgus', 'yhik': 'mm', 'vaartus': 121}
        ]
        
        >>> parse_dimensions("ø50")
        [{'parameeter': 'läbimõõt', 'yhik': 'mm', 'vaartus': 50}]
        
        >>> parse_dimensions("ø50;62x70")
        [
            {'parameeter': 'läbimõõt', 'yhik': 'mm', 'vaartus': 50},
            {'parameeter': 'kõrgus', 'yhik': 'mm', 'vaartus': 62},
            {'parameeter': 'laius', 'yhik': 'mm', 'vaartus': 70}
        ]
    
    Notes:
        - Default unit is "mm" unless specified
        - Return empty list if unparseable (log warning)
        - Max 4 measurements (MUIS constraint)
    
    Raises:
        ValueError: If format is completely unparseable
    """
    pass  # Implement parsing logic
```

**Dimension type mapping**:

- `ø` or `d:` → `läbimõõt` (diameter)
- First number in `HxW` → `kõrgus` (height)
- Second number in `HxW` → `laius` (width)
- `H:` → `kõrgus`
- `L:` → `laius`
- `S:` → `sügavus` (depth)

**Tests**: Write 8+ test cases covering all patterns

---

### Task 3: Create Date Parser (scripts/parsers/date_parser.py)

**Input**: ENTU date fields (ISO format or variations)
**Output**: Estonian format `DD.MM.YYYY`

```python
from datetime import datetime
from typing import Optional

def convert_date(date_str: Optional[str]) -> Optional[str]:
    """
    Convert ENTU date to MUIS format.
    
    ENTU: ISO format "YYYY-MM-DD" or variations
    MUIS: Estonian format "DD.MM.YYYY"
    
    Args:
        date_str: Date string or None
    
    Returns:
        Formatted date string or None if input is None
    
    Examples:
        >>> convert_date("2002-12-22")
        "22.12.2002"
        
        >>> convert_date("1956-05-28")
        "28.05.1956"
        
        >>> convert_date(None)
        None
        
        >>> convert_date("invalid")
        None  # Log warning
    
    Raises:
        ValueError: If date is invalid (log and return None)
    """
    if not date_str:
        return None
    
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%d.%m.%Y")
    except ValueError as e:
        # Log warning and return None
        return None
```

**Tests**: Write 5+ test cases (valid dates, None, invalid formats)

---

### Task 4: Create Person Mapper Stub (scripts/parsers/person_mapper.py)

**Input**: ENTU person IDs or names
**Output**: MUIS person format (stub for now)

```python
def map_person(person_id_or_name: Optional[str]) -> Optional[str]:
    """
    Map ENTU person to MUIS format.
    
    ENTU: Numeric ID (e.g., "139862") or name
    MUIS: "Lastname, Firstname" format
    
    Phase 1 (current): Return placeholder or parse if already name
    Phase 2: Implement full person lookup table
    
    Args:
        person_id_or_name: ENTU person identifier
    
    Returns:
        MUIS formatted name or None
    
    Examples:
        >>> map_person("139862")
        "[Person ID: 139862]"  # Placeholder for Phase 1
        
        >>> map_person("Jõgiaas, Miia")
        "Jõgiaas, Miia"  # Already correct format
        
        >>> map_person(None)
        None
    
    Notes:
        - Phase 1: Just handle existing names, flag IDs
        - Phase 2: Implement person_ids.csv lookup
    """
    if not person_id_or_name:
        return None
    
    # Check if already in "Lastname, Firstname" format
    if ',' in person_id_or_name and not person_id_or_name.isdigit():
        return person_id_or_name
    
    # Numeric ID - placeholder for now
    if person_id_or_name.isdigit():
        return f"[Person ID: {person_id_or_name}]"
    
    return person_id_or_name
```

**Tests**: Write 4+ test cases (IDs, names, None)

---

### Task 5: Create Vocabulary Mapper (scripts/parsers/vocab_mapper.py)

**Input**: ENTU vocabulary paths (e.g., `"/materjalid/metall"`)
**Output**: MUIS vocabulary terms using converted vocabularies

```python
import json
from pathlib import Path
from typing import Optional

# Load vocabulary mappings
VOCAB_DIR = Path(__file__).parent.parent.parent / "mappings"

def load_vocabulary(vocab_name: str) -> dict:
    """Load vocabulary mapping from JSON file."""
    vocab_file = VOCAB_DIR / f"{vocab_name}.json"
    if not vocab_file.exists():
        return {}
    
    with open(vocab_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Return the vocabulary list (skip _metadata)
        return {item['term_id']: item['term'] 
                for item in data.get(vocab_name, [])}

MATERIALS = load_vocabulary('materials')
TECHNIQUES = load_vocabulary('techniques')
COLORS = load_vocabulary('colors')

def map_material(material_path: Optional[str]) -> Optional[str]:
    """
    Map ENTU material path to MUIS material term.
    
    Args:
        material_path: ENTU path like "/materjalid/metall"
    
    Returns:
        MUIS material term or None
    
    Examples:
        >>> map_material("/materjalid/metall")
        "metall"
        
        >>> map_material("metall")  # Already term
        "metall"
    """
    if not material_path:
        return None
    
    # If it's a path, extract last part
    if material_path.startswith('/'):
        term = material_path.split('/')[-1]
        return term
    
    return material_path

def map_technique(technique_path: Optional[str]) -> Optional[str]:
    """Map ENTU technique to MUIS term (same logic as material)."""
    return map_material(technique_path)  # Same parsing logic

def map_color(color_path: Optional[str]) -> Optional[str]:
    """Map ENTU color to MUIS term (same logic as material)."""
    return map_material(color_path)
```

**Tests**: Write 5+ test cases (paths, direct terms, None)

---

### Task 6: Create Main Orchestrator (scripts/convert_row.py)

**Input**: CSV row from sample_100_raw.csv
**Output**: MuisMuseaal Pydantic model + CSV file

```python
"""
Convert single ENTU row to MUIS format.

Usage:
    python -m scripts.convert_row --input output/sample_100_raw.csv --row-index 0
"""

import argparse
import csv
from pathlib import Path
import sys

from scripts.models import EntuEksponaat, MuisMuseaal
from scripts.parsers.number_parser import parse_entu_code
from scripts.parsers.dimension_parser import parse_dimensions
from scripts.parsers.date_parser import convert_date
from scripts.parsers.person_mapper import map_person
from scripts.parsers.vocab_mapper import map_material, map_technique, map_color
from scripts.muis_writer import MuisWriter


def load_sample_row(csv_path: Path, row_index: int = 0) -> dict:
    """
    Load a single row from ENTU sample CSV.
    
    Args:
        csv_path: Path to sample_100_raw.csv
        row_index: Which row to load (0-based, after header)
    
    Returns:
        Dictionary with ENTU field values
    """
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i == row_index:
                return row
    raise ValueError(f"Row index {row_index} not found in {csv_path}")


def convert_entu_to_muis(entu_row: dict) -> MuisMuseaal:
    """
    Transform ENTU row to MUIS record.
    
    This is the main conversion logic that orchestrates all parsers.
    
    Args:
        entu_row: Raw ENTU CSV row as dictionary
    
    Returns:
        Validated MUIS record
    
    Raises:
        ValidationError: If MUIS record is invalid
    """
    # Parse number structure
    number_fields = parse_entu_code(entu_row.get('code', ''))
    
    # Parse dimensions
    measurements = parse_dimensions(entu_row.get('dimensions', ''))
    
    # Pad measurements to 4 sets (MUIS requires 4)
    while len(measurements) < 4:
        measurements.append({'parameeter': None, 'yhik': None, 'vaartus': None})
    
    # Convert dates
    registration_date = convert_date(entu_row.get('date'))
    publishing_date = convert_date(entu_row.get('publishing_date'))
    
    # Map persons
    donator = map_person(entu_row.get('donator'))
    
    # Map vocabularies
    material_1 = map_material(entu_row.get('material'))
    
    # Map collection code (kuuluvus → KT)
    kuuluvus = entu_row.get('kuuluvus', '')
    kt = 'D' if 'dokument' in kuuluvus else 'E'  # Simple logic for now
    
    # Build MUIS record
    muis_record = MuisMuseaal(
        # System fields (empty)
        museaali_id=None,
        importimise_staatus=None,
        kommentaar=None,
        
        # Number structure
        acr=number_fields['acr'],
        trt=number_fields['trt'],
        trs=number_fields['trs'],
        trj=number_fields['trj'],
        trl=number_fields.get('trl'),
        kt=kt,
        ks=None,
        kj=None,
        kl=None,
        
        # Basic info
        nimetus=entu_row.get('name', 'Nimetu objekt'),
        pysiasukoht=entu_row.get('asukoht'),
        tulmelegend=entu_row.get('legend'),
        originaal='',  # Default empty
        
        # Acquisition
        vastuv6tu_nr=entu_row.get('vastuv6tuakt'),
        esmane_yldinfo=None,
        kogusse_registreerimise_aeg=registration_date,
        yleandja=donator,
        muuseumile_omandamise_viis=None,
        
        # Measurements (4 sets)
        parameeter_1=measurements[0]['parameeter'],
        yhik_1=measurements[0]['yhik'],
        vaartus_1=measurements[0]['vaartus'],
        parameeter_2=measurements[1]['parameeter'],
        yhik_2=measurements[1]['yhik'],
        vaartus_2=measurements[1]['vaartus'],
        parameeter_3=measurements[2]['parameeter'],
        yhik_3=measurements[2]['yhik'],
        vaartus_3=measurements[2]['vaartus'],
        parameeter_4=measurements[3]['parameeter'],
        yhik_4=measurements[3]['yhik'],
        vaartus_4=measurements[3]['vaartus'],
        
        # Materials (3 sets)
        materjal_1=material_1,
        materjali_1_kommentaar=entu_row.get('m2rks6nad'),
        materjal_2=None,
        materjali_2_kommentaar=None,
        materjal_3=None,
        materjali_3_kommentaar=None,
        
        # Color & technique
        varvus=map_color(entu_row.get('color')),
        tehnika_1=map_technique(entu_row.get('technique')),
        tehnika_1_kommentaar=None,
        tehnika_2=None,
        tehnika_2_kommentaar=None,
        tehnika_3=None,
        tehnika_3_kommentaar=None,
        
        # Type/nature
        olemus_1=entu_row.get('tyyp'),
        olemus_2=None,
        
        # References
        seotud_objekt=None,
        seotud_objekti_seos=None,
        
        # Archaeological/archive
        arhiivi_viitenumber=None,
        objekti_nr_kompleksis=None,
        arheoloogiline_objekt_kontekst=None,
        leiunumber_kood=None,
        
        # Condition
        seisund=entu_row.get('condition'),
        kahjustused=None,
        
        # Event 1 (leave empty for now)
        syndmuse_liik_1=None,
        toimumiskoha_tapsustus_kohanimi_1=None,
        toimumiskoha_tapsustus_selgitus_1=None,
        dateering_algus_1=None,
        on_ekr_1='',
        dateeringu_lopp_1=None,
        riik_1=None,
        eesti_admin_yksus_1=None,
        osaleja_1=None,
        osaleja_roll_1=None,
        osaleja_tapsustus_1=None,
        
        # Event 2 (leave empty for now)
        syndmuse_liik_2=None,
        toimumiskoha_tapsustus_kohanimi_2=None,
        toimumiskoha_tapsustus_selgitus_2=None,
        dateering_algus_2=None,
        on_ekr_2='',
        dateeringu_lopp_2=None,
        riik_2=None,
        eesti_admin_yksus_2=None,
        osaleja_2=None,
        osaleja_roll_2=None,
        osaleja_tapsustus_2=None,
        
        # Publication
        avalik='y',  # Default public
        avalikusta_praegused_andmed='y',
        
        # Description
        teksti_tyup_1='kirjeldus',
        tekst_1=entu_row.get('description'),
        teksti_tyup_2=None,
        tekst_2=entu_row.get('note'),
        
        # Alternative names/numbers
        alternatiivne_nimetus_1=None,
        alternatiivse_nimetuse_1_tyup=None,
        alternatiivne_number_1=None,
        alternatiivse_numbri_1_tyup=None,
    )
    
    return muis_record


def main():
    parser = argparse.ArgumentParser(
        description='Convert single ENTU row to MUIS format'
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path('output/sample_100_raw.csv'),
        help='Input CSV file'
    )
    parser.add_argument(
        '--row-index',
        type=int,
        default=0,
        help='Row index to convert (0-based)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('output/sample_1_muis.csv'),
        help='Output CSV file'
    )
    
    args = parser.parse_args()
    
    print(f"Loading row {args.row_index} from {args.input}")
    entu_row = load_sample_row(args.input, args.row_index)
    
    print(f"Converting ENTU → MUIS...")
    muis_record = convert_entu_to_muis(entu_row)
    
    print(f"Validation: {'✓ PASSED' if muis_record else '✗ FAILED'}")
    
    print(f"Writing to {args.output}")
    writer = MuisWriter(args.output)
    writer.write_records([muis_record])
    
    print(f"✓ Conversion complete!")
    print(f"\nOutput file: {args.output}")
    print(f"Record: {muis_record.nimetus}")
    print(f"Number: {muis_record.acr}{muis_record.trt}{muis_record.trs}/{muis_record.trj}")


if __name__ == '__main__':
    main()
```

---

### Task 7: Update MUIS Writer (scripts/muis_writer.py)

Ensure the existing writer correctly outputs the 3-row header and 85-88 columns:

```python
"""
MUIS CSV Writer with 3-row header.

Reference: reference/muis_example_format.csv
"""

import csv
from pathlib import Path
from typing import List
from scripts.models import MuisMuseaal, create_muis_header


class MuisWriter:
    """Write MUIS import CSV with correct structure."""
    
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def write_records(self, records: List[MuisMuseaal]) -> None:
        """
        Write MUIS records to CSV with 3-row header.
        
        Args:
            records: List of validated MUIS records
        """
        with open(self.output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Write 3-row header
            header_rows = create_muis_header()
            for row in header_rows:
                writer.writerow(row)
            
            # Write data rows
            for record in records:
                row = self._record_to_row(record)
                writer.writerow(row)
        
        print(f"Wrote {len(records)} records to {self.output_path}")
    
    def _record_to_row(self, record: MuisMuseaal) -> List[str]:
        """Convert Pydantic model to CSV row in correct column order."""
        # Use model_dump() to get all fields
        data = record.model_dump()
        
        # Convert None to empty string, keep other values
        row = [
            '' if data[field] is None else str(data[field])
            for field in MuisMuseaal.model_fields.keys()
        ]
        
        return row
```

**Update**: Ensure `create_muis_header()` in `models.py` returns exactly 3 rows matching reference format.

---

## Testing Plan

### Unit Tests (scripts/parsers/tests/)

Create test file for each parser:

- `test_number_parser.py` - 5+ test cases
- `test_dimension_parser.py` - 8+ test cases
- `test_date_parser.py` - 5+ test cases
- `test_person_mapper.py` - 4+ test cases
- `test_vocab_mapper.py` - 5+ test cases

### Integration Test

**Test**: Convert first sample row and validate output

```bash
python -m scripts.convert_row --input output/sample_100_raw.csv --row-index 0
```

**Expected output**: `output/sample_1_muis.csv` with:

1. 3-row header matching reference format
2. 1 data row with 85-88 columns
3. All required fields populated
4. Valid Pydantic validation

**Manual validation**:

1. Open in Excel/LibreOffice
2. Compare with `reference/muis_example_format.csv`
3. Check column alignment
4. Verify no encoding issues (Estonian characters)

### Validation Checklist

- [ ] Number structure parsed correctly (ACR=VBM, TRS/TRJ extracted)
- [ ] Dimensions parsed into measurement sets
- [ ] Dates converted to DD.MM.YYYY format
- [ ] Person names formatted or flagged
- [ ] Vocabularies mapped using converted JSON files
- [ ] CSV has exactly 3 header rows
- [ ] Data row has 85-88 columns
- [ ] Required fields populated (nimetus, number fields)
- [ ] No Pydantic validation errors
- [ ] Estonian characters preserved (õ, ä, ö, ü)

## Expected Output

### Console Output

```text
$ python -m scripts.convert_row --input output/sample_100_raw.csv --row-index 0

Loading row 0 from output/sample_100_raw.csv
Converting ENTU → MUIS...
Validation: ✓ PASSED
Writing to output/sample_1_muis.csv
✓ Conversion complete!

Output file: output/sample_1_muis.csv
Record: Enne lahkumist poiste maja ees, 28. mai 1956...
Number: VBM_20027/117
```

### CSV Output (sample_1_muis.csv)

```csv
[Row 1: Metadata headers]
[Row 2: Column names in Estonian]
[Row 3: Validation rules]
,,,VBM,_,20027,117,,,D,,,,Enne lahkumist poiste maja ees...,[location],Fotokogu,,...
```

## Deliverables

1. **Code**:
   - `scripts/parsers/__init__.py`
   - `scripts/parsers/number_parser.py`
   - `scripts/parsers/dimension_parser.py`
   - `scripts/parsers/date_parser.py`
   - `scripts/parsers/person_mapper.py`
   - `scripts/parsers/vocab_mapper.py`
   - `scripts/convert_row.py`
   - Updated `scripts/muis_writer.py`

2. **Tests**:
   - `tests/test_number_parser.py`
   - `tests/test_dimension_parser.py`
   - `tests/test_date_parser.py`
   - `tests/test_person_mapper.py`
   - `tests/test_vocab_mapper.py`

3. **Output**:
   - `output/sample_1_muis.csv` (validated conversion)

4. **Documentation**:
   - Update `docs/FIELD_MAPPINGS.md` with any discoveries
   - Add conversion log noting edge cases found

## Success Criteria

- [ ] All 5 parser modules implemented with tests
- [ ] Main orchestrator (`convert_row.py`) runs without errors
- [ ] Output CSV has correct 3-row header
- [ ] Sample record converted successfully
- [ ] Pydantic validation passes
- [ ] Manual comparison with reference format matches
- [ ] All tests passing (pytest)
- [ ] Code passes type checking (mypy)

## Timeline

**Estimated time**: 6-8 hours

- Task 1-5 (Parsers): 4-5 hours
- Task 6 (Orchestrator): 1-2 hours
- Task 7 (Writer update): 0.5 hours
- Testing & validation: 1 hour

## Notes

- Focus on getting ONE complete row working end-to-end
- Don't worry about performance yet (that's for Phase 2)
- Flag edge cases found for later handling
- Person mapping is stub only (full implementation in Phase 2)
- Vocabulary lookups use our converted JSON files
- Keep parsers modular - each can be improved independently

## References

- `/docs/FIELD_MAPPINGS.md` - Complete field mapping specification
- `/docs/IMPLEMENTATION_ROADMAP.md` - Overall project plan
- `/reference/muis_example_format.csv` - Target format reference
- `/mappings/*.json` - Converted vocabulary mappings
- `/scripts/models.py` - MuisMuseaal Pydantic model
