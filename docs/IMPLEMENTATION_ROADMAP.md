# ENTU → MUIS Implementation Roadmap

**Created**: 2025-12-03

**Status**: Ready for Implementation

**Purpose**: Strategic action plan for Ada (developer) to execute ENTU → MUIS data migration

---

## Current State Assessment

### What's Complete ✅

1. **Environment Setup**
   - Python 3.12.3 virtual environment created
   - Core dependencies installed (pydantic>=2.0.0, pandas>=2.0.0, pytest>=7.4.0)
   - Git repository initialized
   - Project structure exists

2. **Data Models (Pydantic v2)**
   - `scripts/models.py` - Fully migrated to Pydantic v2
   - EntuEksponaat model (44 fields, 4 field validators)
   - MuisMuseaal model (88 fields, 12 model validators)
   - All validators tested and passing
   - Clean Problems panel (0 errors)

3. **Quality Infrastructure**
   - Black formatter configured (100 char line length)
   - Flake8 linter configured
   - Mypy type checker configured (strict mode)
   - Pytest framework with 6 passing tests
   - Test coverage infrastructure in place

4. **Documentation**
   - PLAN.md: 10-phase implementation plan (detailed)
   - README.md: Project overview and quick start
   - pydantic-v2-migration-plan.md: Migration documentation (complete)
   - This roadmap: Strategic action plan

### What's Missing ⏳

1. **Data Exploration** (not started)
   - Load actual ENTU CSV data
   - Validate models against real records
   - Document edge cases discovered

2. **Core Implementation** (not started)
   - ENTU CSV reader (scripts/entu_reader.py)
   - MUIS mapper (scripts/muis_mapper.py)
   - MUIS CSV writer (scripts/muis_writer.py)
   - Person ID coordinator (scripts/person_mapper.py)

3. **Mapping Configuration** (not started)
   - Person ID lookup table (mappings/person_ids.csv)
   - Material vocabulary (mappings/materials.json)
   - Technique vocabulary (mappings/techniques.json)
   - Collection mappings (mappings/collections.json)

4. **Testing** (minimal coverage)
   - Only model validation tests exist
   - No integration tests
   - No end-to-end conversion tests

---

## Document Reorganization Strategy

### Problem: Redundancy and Poor Organization

**Current issues**:

1. **SUMMARY.md duplicates PLAN.md content** - Same information in two places
2. **README.md duplicates PLAN.md sections** - Mapping examples repeated
3. **No clear "what to do next"** - Three documents, unclear entry point
4. **Historical vs current info mixed** - Planning docs contain outdated status

**Solution: Strategic Document Hierarchy**  

```text
Root Level Documents (User Entry Points):
├── README.md           → PROJECT OVERVIEW (what, why, status, quick links)
└── CONTRIBUTING.md     → HOW TO CONTRIBUTE (for developers joining project)

Documentation Folder (Reference Materials):
├── docs/
│   ├── IMPLEMENTATION_ROADMAP.md  → THIS FILE (Ada's action plan)
│   ├── ARCHITECTURE.md            → Technical design (to be created)
│   ├── FIELD_MAPPINGS.md          → Complete field mapping reference
│   ├── pydantic-v2-migration-plan.md → Historical record (archive)
│   └── ARCHIVE/
│       ├── PLAN.md                → Move here (superseded by roadmap)
│       └── SUMMARY.md             → Move here (redundant)
```

### Document Purpose Matrix

| Document | Purpose | Audience | Maintenance |
|----------|---------|----------|-------------|
| **README.md** | Project overview, quick start, current status | All stakeholders | Update status regularly |
| **IMPLEMENTATION_ROADMAP.md** | Ada's task list, phase tracking | Developer (Ada) | Update after each phase |
| **ARCHITECTURE.md** | Technical design decisions, data flow | Developers, technical reviewers | Update when design changes |
| **FIELD_MAPPINGS.md** | Complete source→target field mappings | Developers, Liisi (validation) | Update during implementation |
| **CONTRIBUTING.md** | Developer onboarding, workflow | New developers | Rarely changes |
| **docs/ARCHIVE/** | Historical planning documents | Reference only | No updates (frozen) |

---

## Ada's Implementation Plan

### Phase 0: Document Reorganization (Today, 1 hour)

**Objective**: Eliminate redundancy, create clear task list for Ada

**Tasks**:

1. **Archive superseded documents**
   - Move `docs/PLAN.md` → `docs/ARCHIVE/PLAN.md`
   - Move `docs/SUMMARY.md` → `docs/ARCHIVE/SUMMARY.md`
   - Add README in ARCHIVE explaining why files moved

2. **Create new strategic documents**
   - ✅ `docs/IMPLEMENTATION_ROADMAP.md` (this file)
   - Create `docs/ARCHITECTURE.md` (data flow, technical decisions)
   - Create `docs/FIELD_MAPPINGS.md` (complete mapping reference)
   - Create `CONTRIBUTING.md` (developer workflow)

3. **Refactor README.md**
   - Remove redundant mapping examples (move to FIELD_MAPPINGS.md)
   - Update status to reflect current state
   - Add clear "Next Steps" section linking to roadmap
   - Keep it under 200 lines (concise overview)

4. **Update .gitignore**
   - Ensure `docs/ARCHIVE/` tracked in git (not ignored)
   - Add `output/` to gitignore (generated files)
   - Add `.pytest_cache/`, `__pycache__/` if missing

**Success Criteria**:

- [ ] No duplicate information across documents
- [ ] Clear entry point for Ada: this roadmap
- [ ] Historical docs preserved but archived
- [ ] README.md under 200 lines, links to detailed docs

**Deliverables**:

- Reorganized documentation structure
- Clear task list for Ada to execute

---

### Phase 1: Data Exploration (Next, 4 hours)

**Objective**: Load real ENTU data, validate models, document edge cases

**Why this phase**: Models exist but untested against real data. Must discover actual format variations before implementing transformers.

**Tasks**:

1. **Create data exploration script** (`scripts/explore_data.py`)

   ```python
   """
   Data Exploration Script
   
   Load ENTU CSVs and validate against Pydantic models.
   Document edge cases discovered.
   """
   import pandas as pd
   from pathlib import Path
   from models import EntuEksponaat
   from typing import List, Tuple
   
   def load_sample_eksponaat(limit: int = 100) -> pd.DataFrame:
       """Load first N records from eksponaat.csv"""
       csv_path = Path("entust/eksponaat.csv")
       return pd.read_csv(csv_path, nrows=limit)
   
   def validate_against_model(df: pd.DataFrame) -> Tuple[List[EntuEksponaat], List[dict]]:
       """
       Validate dataframe records against EntuEksponaat model.
       
       Returns:
           (successful_records, failed_records_with_errors)
       """
       successes = []
       failures = []
       
       for idx, row in df.iterrows():
           try:
               record = EntuEksponaat(**row.to_dict())
               successes.append(record)
           except Exception as e:
               failures.append({
                   'row_index': idx,
                   'error': str(e),
                   'data': row.to_dict()
               })
       
       return successes, failures
   
   def main():
       # Load sample
       df = load_sample_eksponaat(limit=100)
       print(f"Loaded {len(df)} records from eksponaat.csv")
       
       # Validate
       successes, failures = validate_against_model(df)
       print(f"✓ Validated: {len(successes)}")
       print(f"✗ Failed: {len(failures)}")
       
       # Document failures
       if failures:
           print("\nValidation Failures:")
           for failure in failures[:5]:  # Show first 5
               print(f"Row {failure['row_index']}: {failure['error']}")
       
       # Save edge cases
       if failures:
           import json
           with open('docs/edge_cases_discovered.json', 'w') as f:
               json.dump(failures, f, indent=2, default=str)
   
   if __name__ == '__main__':
       main()
   ```

2. **Run exploration on increasing sample sizes**
   - 10 records → validate models
   - 100 records → discover common patterns
   - 1000 records → find edge cases
   - Full 80K records → assess data quality

3. **Document findings in `docs/edge_cases_discovered.md`**
   - What field formats actually exist?
   - What dimensions patterns are real?
   - Which fields have high null rates?
   - What date formats appear?
   - Any unexpected data structures?

4. **Adjust models if needed**
   - Add discovered patterns to validators
   - Update field descriptions with real examples
   - Add permissive handling for format variations

5. **Create test fixtures from real data**
   - Extract 10 representative records
   - Save as `tests/fixtures/sample_eksponaat.csv`
   - Use in integration tests

**Success Criteria**:

- [ ] Load all 80K eksponaat records successfully
- [ ] Validate at least 95% of records against EntuEksponaat model
- [ ] Document all edge cases discovered
- [ ] Update models to handle real data variations
- [ ] Create test fixtures for future tests

**Deliverables**:

- `scripts/explore_data.py` - Data exploration script
- `docs/edge_cases_discovered.md` - Documentation of findings
- `tests/fixtures/sample_eksponaat.csv` - Test fixtures
- Updated `scripts/models.py` (if adjustments needed)

**Estimated Time**: 4 hours

**Dependencies**: None (can start immediately)

---

### Phase 2: ENTU CSV Reader (4 hours)

**Objective**: Build robust CSV reader that loads ENTU data into Pydantic models

**Why this phase**: Foundation for all transformations. Must handle real data correctly.

**Tasks**:

1. **Create `scripts/entu_reader.py`**

   ```python
   """
   ENTU CSV Reader
   
   Loads ENTU database export CSVs into Pydantic models.
   Handles related tables and data quality issues.
   """
   from pathlib import Path
   import pandas as pd
   from typing import List, Optional
   from models import EntuEksponaat
   import logging
   
   logger = logging.getLogger(__name__)
   
   class EntuReader:
       """
       Read and parse ENTU CSV exports.
       
       Example:
           >>> reader = EntuReader(data_dir=Path("entust"))
           >>> eksponaat_records = reader.load_eksponaat(limit=100)
           >>> print(f"Loaded {len(eksponaat_records)} records")
       """
       
       def __init__(self, data_dir: Path):
           self.data_dir = data_dir
           self._validate_data_dir()
       
       def _validate_data_dir(self) -> None:
           """Ensure data directory exists and contains expected files"""
           if not self.data_dir.exists():
               raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
           
           required_files = ['eksponaat.csv']
           for filename in required_files:
               filepath = self.data_dir / filename
               if not filepath.exists():
                   raise FileNotFoundError(f"Required file not found: {filepath}")
       
       def load_eksponaat(
           self,
           limit: Optional[int] = None,
           skip_invalid: bool = True
       ) -> List[EntuEksponaat]:
           """
           Load eksponaat.csv records.
           
           Args:
               limit: Max records to load (None = all)
               skip_invalid: If True, log and skip invalid records
           
           Returns:
               List of validated EntuEksponaat models
           """
           csv_path = self.data_dir / "eksponaat.csv"
           df = pd.read_csv(csv_path, nrows=limit)
           
           records = []
           errors = []
           
           for idx, row in df.iterrows():
               try:
                   record = EntuEksponaat(**row.to_dict())
                   records.append(record)
               except Exception as e:
                   error_msg = f"Row {idx}: {e}"
                   if skip_invalid:
                       logger.warning(f"Skipping invalid record: {error_msg}")
                       errors.append((idx, str(e)))
                   else:
                       raise ValueError(error_msg) from e
           
           logger.info(
               f"Loaded {len(records)} valid records, "
               f"skipped {len(errors)} invalid"
           )
           
           return records
   ```

2. **Write unit tests** (`tests/test_entu_reader.py`)

   ```python
   import pytest
   from pathlib import Path
   from scripts.entu_reader import EntuReader
   
   def test_load_eksponaat_sample():
       """
       GIVEN: ENTU data directory with eksponaat.csv
       WHEN: load_eksponaat called with limit=10
       THEN: Returns 10 valid EntuEksponaat records
       """
       reader = EntuReader(data_dir=Path("entust"))
       records = reader.load_eksponaat(limit=10)
       
       assert len(records) == 10
       assert all(hasattr(r, 'id') for r in records)
   
   def test_load_eksponaat_handles_invalid():
       """
       GIVEN: CSV with some invalid records
       WHEN: load_eksponaat called with skip_invalid=True
       THEN: Returns only valid records, logs warnings
       """
       # Test with real data that may have issues
       reader = EntuReader(data_dir=Path("entust"))
       records = reader.load_eksponaat(limit=100, skip_invalid=True)
       
       # Should load most records even if some fail
       assert len(records) >= 90  # At least 90% success rate
   ```

3. **Add logging configuration**
   - Create `scripts/logging_config.py`
   - Configure file and console handlers
   - Use throughout project

4. **Test with real data**
   - Run on 100 records
   - Run on 1000 records
   - Run on full dataset (80K)
   - Verify load time acceptable (<2 minutes)

5. **Handle related tables** (if needed)
   - Implement join logic for cl_* tables
   - Load person names from cl_autor, cl_donator
   - Document table relationships

**Success Criteria**:

- [ ] Load all 80K eksponaat records in <2 minutes
- [ ] Handle missing/null values gracefully
- [ ] Skip invalid records with logging (if skip_invalid=True)
- [ ] All unit tests pass
- [ ] Clean Problems panel (0 errors)

**Deliverables**:

- `scripts/entu_reader.py` - CSV reader implementation
- `tests/test_entu_reader.py` - Unit tests
- `scripts/logging_config.py` - Logging configuration

**Estimated Time**: 4 hours

**Dependencies**: Phase 1 (data exploration findings)

---

### Phase 3: Field Mapping Implementation (6 hours)

**Objective**: Implement all source→target field transformations

**Why this phase**: Core business logic. Must handle all mapping challenges correctly.

**Tasks**:

1. **Create comprehensive field mapping reference** (`docs/FIELD_MAPPINGS.md`)
   - Extract from PLAN.md
   - Add examples from real data exploration
   - Document every target field's source
   - Include edge cases and fallback logic

2. **Implement number parser** (`scripts/parsers/number_parser.py`)

   ```python
   """
   ENTU Number Parser
   
   Parse ENTU codes like "006562/001" into MUIS 9-column structure.
   """
   import re
   from typing import Optional
   from dataclasses import dataclass
   
   @dataclass
   class MuisNumber:
       """MUIS number structure (9 columns)"""
       ACR: str  # Archive/collection code (e.g., "VBM")
       TRT: str  # Type code (e.g., "_")
       TRS: str  # Series number (e.g., "6562")
       TRJ: str  # Sequential number (e.g., "1")
       TRL: str = ""  # Letter suffix
       KT: str = "D"  # Collection type (default "D")
       KS: str = ""  # Collection section
       KJ: str = ""  # Collection sequential
       KL: str = ""  # Collection letter
   
   def parse_entu_code(code: str) -> MuisNumber:
       """
       Parse ENTU code format into MUIS structure.
       
       Examples:
           >>> parse_entu_code("006562/001")
           MuisNumber(ACR='VBM', TRT='_', TRS='6562', TRJ='1', ...)
       
       Args:
           code: ENTU code (format: "NNNNNN/NNN")
       
       Returns:
           MuisNumber with all fields populated
       
       Raises:
           ValueError: If code format invalid
       """
       # Pattern: 6 digits / 3 digits
       match = re.match(r'^(\d{6})/(\d{3})$', code)
       if not match:
           raise ValueError(f"Invalid ENTU code format: {code}")
       
       series = match.group(1).lstrip('0')  # Remove leading zeros
       seq = match.group(2).lstrip('0')
       
       return MuisNumber(
           ACR="VBM",  # All Vabamu objects
           TRT="_",
           TRS=series,
           TRJ=seq,
           KT="D"
       )
   ```

3. **Implement dimension parser** (`scripts/parsers/dimension_parser.py`)
   - Parse "ø50;62x70" format
   - Extract parameter/unit/value tuples
   - Handle 1-4 measurements per object
   - Test on real dimension strings from Phase 1

4. **Implement date converter** (`scripts/parsers/date_parser.py`)
   - ISO "2002-12-22" → Estonian "22.12.2002"
   - Handle null/missing dates
   - Validate date ranges (reasonable years)

5. **Create MUIS mapper** (`scripts/muis_mapper.py`)

   ```python
   """
   MUIS Mapper
   
   Transform EntuEksponaat → MuisMuseaal
   """
   from models import EntuEksponaat, MuisMuseaal
   from scripts.parsers import parse_entu_code, parse_dimensions, convert_date
   
   def transform_eksponaat(entu: EntuEksponaat) -> MuisMuseaal:
       """
       Transform ENTU record to MUIS format.
       
       Args:
           entu: Validated ENTU record
       
       Returns:
           Validated MUIS record
       """
       # Parse number structure
       number = parse_entu_code(entu.code)
       
       # Parse dimensions
       measurements = parse_dimensions(entu.dimensions)
       
       # Convert date
       registration_date = convert_date(entu.date) if entu.date else None
       
       # Build MUIS record
       return MuisMuseaal(
           museaali_id=entu.id,
           ACR=number.ACR,
           TRS=number.TRS,
           TRJ=number.TRJ,
           # ... map all 88 fields
       )
   ```

6. **Write comprehensive unit tests**
   - Test each parser independently
   - Test mapper with real examples
   - Test edge cases from Phase 1
   - Parametrize tests for multiple scenarios

**Success Criteria**:

- [ ] All parsers handle real data from Phase 1
- [ ] Number parser: 100% success on valid codes
- [ ] Dimension parser: Handles all discovered formats
- [ ] Date converter: Handles ISO and Estonian formats
- [ ] Mapper: Transforms complete records successfully
- [ ] All tests pass (black, flake8, mypy, pytest)
- [ ] Clean Problems panel (0 errors)

**Deliverables**:

- `docs/FIELD_MAPPINGS.md` - Complete mapping reference
- `scripts/parsers/number_parser.py` - Number parser
- `scripts/parsers/dimension_parser.py` - Dimension parser
- `scripts/parsers/date_parser.py` - Date converter
- `scripts/muis_mapper.py` - Main mapper
- `tests/test_parsers.py` - Parser tests
- `tests/test_mapper.py` - Mapper tests

**Estimated Time**: 6 hours

**Dependencies**: Phase 1 (edge cases), Phase 2 (reader)

---

### Phase 4: Person ID Coordination (2 hours + wait time)

**Objective**: Extract person names, generate coordination CSV, prepare for external lookup

**Why this phase**: Critical path blocker. Must start early to avoid delays.

**Tasks**:

1. **Create person extractor** (`scripts/extract_persons.py`)

   ```python
   """
   Extract unique person names from ENTU for MuIS coordination.
   """
   from scripts.entu_reader import EntuReader
   from pathlib import Path
   import pandas as pd
   
   def extract_unique_persons() -> pd.DataFrame:
       """
       Extract all unique person names from ENTU data.
       
       Returns:
           DataFrame with columns: entu_id, name, source_field, count
       """
       reader = EntuReader(Path("entust"))
       records = reader.load_eksponaat()
       
       persons = []
       
       for record in records:
           # Extract from various person fields
           if record.autor:
               persons.append({
                   'entu_id': record.autor,
                   'name': record.autor,  # May need lookup
                   'source_field': 'autor',
               })
           
           if record.donator:
               persons.append({
                   'entu_id': record.donator,
                   'name': record.donator,
                   'source_field': 'donator',
               })
       
       # Deduplicate and count
       df = pd.DataFrame(persons)
       df = df.groupby(['entu_id', 'name', 'source_field']).size().reset_index(name='count')
       df = df.sort_values('count', ascending=False)
       
       return df
   
   def generate_coordination_csv(output_path: Path):
       """Generate person_ids.csv for MuIS ID coordination"""
       persons_df = extract_unique_persons()
       
       # Add empty columns for coordination
       persons_df['muis_id'] = ''
       persons_df['formatted_name'] = ''  # "Perekonnanimi, Eesnimi"
       persons_df['notes'] = ''
       
       # Reorder columns
       coordination_df = persons_df[[
           'entu_id', 'name', 'muis_id', 'formatted_name',
           'source_field', 'count', 'notes'
       ]]
       
       coordination_df.to_csv(output_path, index=False)
       print(f"Generated {output_path} with {len(coordination_df)} persons")
   
   if __name__ == '__main__':
       generate_coordination_csv(Path("mappings/person_ids.csv"))
   ```

2. **Run person extraction**
   - Generate `mappings/person_ids.csv`
   - Include entu_id, name, source_field, count
   - Add empty columns: muis_id, formatted_name, notes

3. **Document coordination process** (`docs/PERSON_ID_COORDINATION.md`)
   - Who to send CSV to (Liisi Ploom)
   - What they need to fill (muis_id or formatted_name)
   - Expected turnaround time (1-2 weeks)
   - Fallback strategy if IDs not available

4. **Send coordination request**
   - Email person_ids.csv to Liisi
   - Document request date
   - Set follow-up reminder (1 week)

5. **Implement person mapper** (`scripts/person_mapper.py`)

   ```python
   """
   Person ID Lookup
   
   Map ENTU person IDs to MUIS format using coordination CSV.
   """
   from pathlib import Path
   import pandas as pd
   from typing import Optional
   
   class PersonMapper:
       """
       Lookup person IDs from coordination CSV.
       
       Example:
           >>> mapper = PersonMapper(Path("mappings/person_ids.csv"))
           >>> muis_name = mapper.get_muis_name("139862")
           >>> print(muis_name)  # "Aller, Rudolf"
       """
       
       def __init__(self, csv_path: Path):
           self.csv_path = csv_path
           self.lookup = self._load_lookup()
       
       def _load_lookup(self) -> dict:
           """Load coordination CSV into lookup dict"""
           df = pd.read_csv(self.csv_path)
           
           # Build lookup: entu_id → muis format
           lookup = {}
           for _, row in df.iterrows():
               entu_id = str(row['entu_id'])
               
               # Prefer muis_id if provided, else formatted_name
               if pd.notna(row['muis_id']):
                   lookup[entu_id] = row['muis_id']
               elif pd.notna(row['formatted_name']):
                   lookup[entu_id] = row['formatted_name']
               else:
                   # Fallback: use original name
                   lookup[entu_id] = row['name']
           
           return lookup
       
       def get_muis_name(self, entu_id: str) -> Optional[str]:
           """
           Get MUIS-formatted person name.
           
           Args:
               entu_id: ENTU person ID
           
           Returns:
               MUIS name format or None if not found
           """
           return self.lookup.get(entu_id)
   ```

6. **Write tests for person mapper**
   - Test with sample coordination CSV
   - Test missing persons (fallback behavior)
   - Test both muis_id and formatted_name scenarios

**Success Criteria**:

- [ ] Extract all unique persons from 80K records
- [ ] Generate person_ids.csv with all required columns
- [ ] Send coordination request to Liisi
- [ ] Implement person mapper (ready for CSV when received)
- [ ] All tests pass
- [ ] Document coordination process

**Deliverables**:

- `scripts/extract_persons.py` - Person extractor
- `mappings/person_ids.csv` - Coordination CSV (sent to Liisi)
- `docs/PERSON_ID_COORDINATION.md` - Process documentation
- `scripts/person_mapper.py` - Person lookup implementation
- `tests/test_person_mapper.py` - Tests

**Estimated Time**: 2 hours development + 1-2 weeks wait for coordination

**Dependencies**: Phase 2 (reader)

**Critical Path**: Must start early to avoid blocking final conversion

---

### Phase 5: MUIS CSV Writer (4 hours)

**Objective**: Generate valid MUIS import CSV with 3-row header and correct structure

**Why this phase**: Output format is critical. Must match MUIS requirements exactly.

**Tasks**:

1. **Study reference file in detail**
   - Analyze `massimport_kasetohukirjad.xlsx - Leht1.csv`
   - Document header structure (3 rows)
   - Note column ordering
   - Check CSV escaping and encoding

2. **Create MUIS writer** (`scripts/muis_writer.py`)

   ```python
   """
   MUIS CSV Writer
   
   Generate MUIS import CSV with correct structure.
   """
   import csv
   from pathlib import Path
   from typing import List
   from models import MuisMuseaal
   
   class MuisWriter:
       """
       Write MUIS import CSV with 3-row header.
       
       Example:
           >>> writer = MuisWriter(output_path=Path("output/test.csv"))
           >>> writer.write_records(records)
       """
       
       # MUIS column order (85-88 columns)
       COLUMN_ORDER = [
           'museaali_id', 'importimise_staatus', 'kommentaar',
           'ACR', 'TRT', 'TRS', 'TRJ', 'TRL', 'KT', 'KS', 'KJ', 'KL',
           'nimetus', 'pysiasukoht', 'tulmelegend', 'originaal',
           # ... all 85-88 columns in correct order
       ]
       
       def __init__(self, output_path: Path):
           self.output_path = output_path
           self.output_path.parent.mkdir(parents=True, exist_ok=True)
       
       def write_records(self, records: List[MuisMuseaal]) -> None:
           """
           Write MUIS records to CSV.
           
           Args:
               records: List of validated MUIS records
           """
           with open(self.output_path, 'w', newline='', encoding='utf-8') as f:
               writer = csv.writer(f)
               
               # Write 3-row header
               self._write_header(writer)
               
               # Write data rows
               for record in records:
                   row = self._record_to_row(record)
                   writer.writerow(row)
       
       def _write_header(self, writer) -> None:
           """Write 3-row MUIS header"""
           # Row 1: Metadata and column groups
           row1 = [''] * len(self.COLUMN_ORDER)
           row1[0] = 'Vabamu Museum'
           row1[3] = 'Number (9 columns)'
           # ... populate row1
           
           # Row 2: Column names in Estonian
           row2 = self.COLUMN_ORDER
           
           # Row 3: Validation rules
           row3 = [''] * len(self.COLUMN_ORDER)
           row3[0] = 'Required'
           # ... populate row3
           
           writer.writerow(row1)
           writer.writerow(row2)
           writer.writerow(row3)
       
       def _record_to_row(self, record: MuisMuseaal) -> List[str]:
           """Convert Pydantic model to CSV row"""
           row = []
           for col in self.COLUMN_ORDER:
               value = getattr(record, col, '')
               # Convert None to empty string
               row.append('' if value is None else str(value))
           return row
   ```

3. **Test writer output**
   - Generate sample CSV (10 records)
   - Compare with reference file
   - Validate header structure matches
   - Open in Excel to verify formatting
   - Check encoding (UTF-8 with BOM if needed)

4. **Add validation checks**
   - Verify all required fields populated
   - Check column count (85-88)
   - Validate no data in header rows
   - Check for CSV escaping issues (quotes, commas)

5. **Write unit tests**
   - Test header generation
   - Test record serialization
   - Test column ordering
   - Test with sample records from Phase 1

**Success Criteria**:

- [ ] Generate CSV with correct 3-row header
- [ ] All 85-88 columns in correct order
- [ ] Output opens correctly in Excel
- [ ] Matches reference file structure
- [ ] All tests pass
- [ ] Clean Problems panel (0 errors)

**Deliverables**:

- `scripts/muis_writer.py` - CSV writer implementation
- `tests/test_muis_writer.py` - Unit tests
- Sample output CSV for validation

**Estimated Time**: 4 hours

**Dependencies**: Phase 3 (mapper - for testing with real records)

---

### Phase 6: End-to-End Integration (4 hours)

**Objective**: Connect all components, test full conversion pipeline

**Why this phase**: Verify all pieces work together correctly.

**Tasks**:

1. **Create main conversion script** (`scripts/convert.py`)

   ```python
   """
   ENTU → MUIS Conversion Script
   
   Main entry point for data conversion.
   """
   import argparse
   from pathlib import Path
   from scripts.entu_reader import EntuReader
   from scripts.muis_mapper import transform_eksponaat
   from scripts.muis_writer import MuisWriter
   from scripts.person_mapper import PersonMapper
   from tqdm import tqdm
   import logging
   
   logger = logging.getLogger(__name__)
   
   def convert(
       input_dir: Path,
       output_path: Path,
       person_map_path: Path,
       limit: int = None
   ):
       """
       Convert ENTU data to MUIS format.
       
       Args:
           input_dir: Path to entust/ folder
           output_path: Path to output CSV
           person_map_path: Path to person_ids.csv
           limit: Max records to process (None = all)
       """
       # Initialize components
       reader = EntuReader(input_dir)
       person_mapper = PersonMapper(person_map_path)
       writer = MuisWriter(output_path)
       
       # Load ENTU records
       logger.info("Loading ENTU records...")
       entu_records = reader.load_eksponaat(limit=limit)
       logger.info(f"Loaded {len(entu_records)} records")
       
       # Transform to MUIS
       logger.info("Transforming records...")
       muis_records = []
       errors = []
       
       for entu in tqdm(entu_records, desc="Converting"):
           try:
               muis = transform_eksponaat(entu, person_mapper)
               muis_records.append(muis)
           except Exception as e:
               logger.error(f"Failed to convert {entu.id}: {e}")
               errors.append((entu.id, str(e)))
       
       logger.info(f"Transformed {len(muis_records)} records")
       logger.warning(f"Failed: {len(errors)} records")
       
       # Write output
       logger.info(f"Writing to {output_path}...")
       writer.write_records(muis_records)
       logger.info("Conversion complete!")
       
       # Report errors
       if errors:
           error_path = output_path.parent / "errors.csv"
           import pandas as pd
           pd.DataFrame(errors, columns=['entu_id', 'error']).to_csv(
               error_path, index=False
           )
           logger.info(f"Error report: {error_path}")
   
   def main():
       parser = argparse.ArgumentParser(
           description='Convert ENTU data to MUIS format'
       )
       parser.add_argument(
           '--input', type=Path, default=Path('entust'),
           help='Input directory (ENTU CSV files)'
       )
       parser.add_argument(
           '--output', type=Path, default=Path('output/muis_import.csv'),
           help='Output CSV path'
       )
       parser.add_argument(
           '--persons', type=Path, default=Path('mappings/person_ids.csv'),
           help='Person ID mapping CSV'
       )
       parser.add_argument(
           '--sample', type=int, default=None,
           help='Process only N records (for testing)'
       )
       
       args = parser.parse_args()
       
       convert(
           input_dir=args.input,
           output_path=args.output,
           person_map_path=args.persons,
           limit=args.sample
       )
   
   if __name__ == '__main__':
       main()
   ```

2. **Test conversion with samples**
   - Convert 10 records: `python scripts/convert.py --sample 10`
   - Convert 100 records: `python scripts/convert.py --sample 100`
   - Convert 1000 records: `python scripts/convert.py --sample 1000`
   - Validate output each time

3. **Add progress monitoring**
   - Use tqdm for progress bars
   - Log statistics (records/sec, errors)
   - Estimate time remaining

4. **Add error recovery**
   - Checkpoint progress (save every 1000 records)
   - Resume from checkpoint if interrupted
   - Generate detailed error report

5. **Create integration tests** (`tests/test_integration.py`)

   ```python
   def test_end_to_end_conversion():
       """
       GIVEN: 10 sample ENTU records
       WHEN: Full conversion pipeline runs
       THEN: Generates valid MUIS CSV with 10 records
       """
       # Use test fixtures
       # Run conversion
       # Validate output
       pass
   ```

6. **Performance testing**
   - Measure conversion speed (records/sec)
   - Check memory usage
   - Optimize if needed (batch processing)

**Success Criteria**:

- [ ] Convert 10 records successfully
- [ ] Convert 100 records in <10 seconds
- [ ] Convert 1000 records in <2 minutes
- [ ] Generate error report for failures
- [ ] Progress bar shows during conversion
- [ ] All integration tests pass

**Deliverables**:

- `scripts/convert.py` - Main conversion script
- `tests/test_integration.py` - Integration tests
- Sample output files (10, 100, 1000 records)
- Error reports

**Estimated Time**: 4 hours

**Dependencies**: All previous phases

---

### Phase 7: Full Dataset Processing (2 hours + wait for person IDs)

**Objective**: Process all 80K records and generate final MUIS import CSV

**Why this phase**: Final production run. Requires person ID coordination complete.

**Wait Condition**: ⏸️ Cannot start until person_ids.csv populated by Liisi (Phase 4)

**Tasks**:

1. **Verify person IDs received**
   - Check `mappings/person_ids.csv` populated
   - Validate muis_id or formatted_name columns filled
   - Test PersonMapper with real data

2. **Run full conversion**

   ```bash
   python scripts/convert.py \
       --input entust \
       --output output/muis_import_full.csv \
       --persons mappings/person_ids.csv
   ```

3. **Monitor processing**
   - Watch progress bar
   - Monitor memory usage
   - Check error rate (<5% target)
   - Estimate completion time

4. **Handle batch processing if needed**
   - If memory issues, process in chunks
   - Save checkpoints every 10K records
   - Resume from checkpoint if interrupted

5. **Validate output**
   - Check record count (should be ~80K)
   - Verify file size reasonable (~50MB)
   - Sample check 50 random records
   - Compare field coverage to expectations

6. **Generate statistics report**

   ```python
   # Create report showing:
   # - Total records processed
   # - Success rate
   # - Field coverage (% non-null for each field)
   # - Error breakdown by type
   # - Processing time
   ```

**Success Criteria**:

- [ ] All 80K+ records processed
- [ ] <5% error rate
- [ ] Output CSV valid and opens in Excel
- [ ] All required fields >95% populated
- [ ] Processing completes in <10 minutes
- [ ] Statistics report generated

**Deliverables**:

- `output/muis_import_full.csv` - Final MUIS import file
- `output/errors.csv` - Error report
- `output/statistics.json` - Conversion statistics
- `docs/CONVERSION_REPORT.md` - Summary of results

**Estimated Time**: 2 hours processing + validation

**Dependencies**: Phase 4 complete (person IDs received)

**Critical Path Blocker**: Must wait for external coordination

---

### Phase 8: Quality Assurance (4 hours)

**Objective**: Validate output quality, manual spot-checking, stakeholder approval

**Why this phase**: Final verification before delivery to Liisi/MUIS.

**Tasks**:

1. **Statistical validation**

   ```python
   # Generate QA report with:
   # - Record count validation (ENTU vs MUIS)
   # - Field coverage analysis
   # - Data type validation
   # - Format compliance checks
   # - Error distribution analysis
   ```

2. **Manual spot-checking**
   - Randomly select 50 records
   - Compare ENTU source to MUIS output
   - Verify:
     - Number structure correct
     - Dates formatted properly
     - Person names mapped correctly
     - Dimensions parsed accurately
     - Materials/techniques mapped

3. **Edge case verification**
   - Test records with:
     - Missing optional fields
     - Multiple materials/techniques
     - Complex dimensions (ø50;62x70)
     - Special characters in names
     - Unusual date formats

4. **Generate QA report** (`docs/QA_REPORT.md`)

   ```markdown
   # Quality Assurance Report
   
   ## Summary
   - Source records: 80,178
   - Converted records: 78,934
   - Error rate: 1.5%
   - Field coverage: >95% for required fields
   
   ## Validation Results
   - ✅ Number structure: 100% correct
   - ✅ Date format: 100% correct
   - ✅ Person names: 98% mapped (2% missing from coordination)
   - ✅ Dimensions: 95% parsed successfully
   - ⚠️ Materials: 10% unmapped values (documented)
   
   ## Spot Check Results
   - Manual review: 50 records
   - Critical errors: 0
   - Minor issues: 2 (documented)
   
   ## Recommendations
   - Ready for import to MUIS
   - Follow-up needed: 2% missing person IDs
   - Review unmapped materials with Liisi
   ```

5. **Prepare delivery package**
   - `output/muis_import_full.csv` - Main deliverable
   - `docs/QA_REPORT.md` - Quality report
   - `output/unmapped_values.csv` - Items needing review
   - `docs/USER_GUIDE.md` - How to use/import
   - `docs/FIELD_MAPPINGS.md` - Reference for questions

6. **Stakeholder review**
   - Send sample to Liisi (100 records)
   - Request approval before full delivery
   - Address any feedback
   - Iterate if needed

**Success Criteria**:

- [ ] <2% error rate in final output
- [ ] Manual spot-check: <1% critical errors
- [ ] All required fields >95% populated
- [ ] QA report complete
- [ ] Stakeholder approval obtained
- [ ] Delivery package prepared

**Deliverables**:

- `docs/QA_REPORT.md` - Quality assurance report
- `output/unmapped_values.csv` - Items for review
- `docs/USER_GUIDE.md` - Import instructions
- Stakeholder approval confirmation

**Estimated Time**: 4 hours

**Dependencies**: Phase 7 (full conversion complete)

---

### Phase 9: Documentation & Handoff (2 hours)

**Objective**: Finalize documentation for maintenance and future reference

**Why this phase**: Ensure project can be maintained and understood by others.

**Tasks**:

1. **Update README.md**
   - Reflect final status
   - Add usage examples
   - Document known limitations
   - Update timeline estimates (actual vs planned)

2. **Create architecture documentation** (`docs/ARCHITECTURE.md`)

   ```markdown
   # ENTU → MUIS Architecture
   
   ## System Overview
   [Data flow diagram]
   
   ## Component Descriptions
   - EntuReader: Loads ENTU CSVs
   - MuisMapper: Transforms data
   - PersonMapper: Looks up person IDs
   - MuisWriter: Generates output CSV
   
   ## Design Decisions
   - Why Pydantic for validation
   - Why batch processing approach
   - Why person ID pre-coordination
   
   ## Known Limitations
   - Unmapped material values
   - Missing person IDs fallback
   - Performance with very large files
   ```

3. **Create maintenance guide** (`docs/MAINTENANCE.md`)

   ```markdown
   # Maintenance Guide
   
   ## Adding New Mappings
   [How to add material/technique mappings]
   
   ## Updating Person IDs
   [How to refresh person_ids.csv]
   
   ## Troubleshooting
   [Common issues and solutions]
   
   ## Re-running Conversion
   [How to process new ENTU exports]
   ```

4. **Create CONTRIBUTING.md**
   - Developer workflow (Ada's 8-step process)
   - Quality requirements
   - Testing standards
   - Documentation standards

5. **Archive project artifacts**
   - Git tag: `v1.0-production`
   - Archive `docs/ARCHIVE/` folder
   - Document decisions in DECISION_LOG.md

6. **Handoff meeting preparation**
   - Demo conversion process
   - Walk through QA report
   - Explain known limitations
   - Answer questions
   - Transfer knowledge

**Success Criteria**:

- [ ] All documentation complete
- [ ] README.md accurate and current
- [ ] Architecture documented
- [ ] Maintenance guide created
- [ ] Git tagged with v1.0
- [ ] Handoff meeting completed

**Deliverables**:

- Updated README.md
- `docs/ARCHITECTURE.md`
- `docs/MAINTENANCE.md`
- `CONTRIBUTING.md`
- Git tag: v1.0-production
- Handoff meeting notes

**Estimated Time**: 2 hours

**Dependencies**: Phase 8 (QA complete)

---

## Timeline Summary

| Phase | Duration | Dependencies | Can Start |
|-------|----------|--------------|-----------|
| 0. Document Reorganization | 1 hour | None | Now |
| 1. Data Exploration | 4 hours | None | Now |
| 2. ENTU Reader | 4 hours | Phase 1 | After exploration |
| 3. Field Mapping | 6 hours | Phase 1, 2 | After reader |
| 4. Person ID Coordination | 2 hours + 1-2 weeks wait | Phase 2 | After reader (start early!) |
| 5. MUIS Writer | 4 hours | Phase 3 | After mapper |
| 6. Integration | 4 hours | Phase 2-5 | After all components |
| 7. Full Processing | 2 hours | Phase 4 (wait), Phase 6 | After person IDs received |
| 8. Quality Assurance | 4 hours | Phase 7 | After full conversion |
| 9. Documentation | 2 hours | Phase 8 | After QA |

**Total Development Time**: 33 hours

**Critical Path**: Phase 4 (person ID coordination) - must start early

**Estimated Calendar Time**: 2-3 weeks (including coordination wait)

---

## Success Metrics

### Technical Metrics

- [ ] Code coverage: >80%
- [ ] All quality checks pass (black, flake8, mypy)
- [ ] Problems panel: 0 errors
- [ ] Test suite: 100% passing
- [ ] Conversion speed: >100 records/sec

### Business Metrics

- [ ] Records converted: >78,000 (>97% success rate)
- [ ] Error rate: <5%
- [ ] Required fields populated: >95%
- [ ] Person IDs mapped: >95%
- [ ] Stakeholder approval: Obtained

### Quality Metrics

- [ ] Manual spot-check errors: <1%
- [ ] Critical errors: 0
- [ ] Output format compliance: 100%
- [ ] Documentation complete: 100%

---

## Risk Management

### Risk 1: Person ID Coordination Delays

**Probability**: High

**Impact**: High (blocks Phase 7)

**Mitigation**:

- Start Phase 4 immediately after Phase 2
- Follow up weekly with Liisi
- Prepare fallback: use formatted names if IDs unavailable
- Continue development on other phases in parallel

### Risk 2: Data Quality Issues

**Probability**: Medium

**Impact**: Medium (increases error rate)

**Mitigation**:

- Thorough exploration in Phase 1
- Permissive validation with logging
- Error reports for manual review
- Iterative adjustment based on findings

### Risk 3: Performance Issues

**Probability**: Low

**Impact**: Medium (slow processing)

**Mitigation**:

- Test with increasing sample sizes
- Batch processing strategy
- Progress monitoring
- Optimize critical paths if needed

### Risk 4: Format Mismatches

**Probability**: Low

**Impact**: High (MUIS import fails)

**Mitigation**:

- Study reference file carefully
- Test output structure early (Phase 5)
- Stakeholder review before full run
- Manual validation of samples

---

## Next Actions for Ada

### Immediate (Today)

1. **Execute Phase 0: Document Reorganization**
   - Archive PLAN.md and SUMMARY.md
   - Create ARCHITECTURE.md skeleton
   - Create FIELD_MAPPINGS.md from PLAN.md
   - Refactor README.md (under 200 lines)
   - Commit changes

### Tomorrow (Day 1)

2. **Execute Phase 1: Data Exploration**
   - Create `scripts/explore_data.py`
   - Load sample eksponaat records (10, 100, 1000)
   - Document edge cases discovered
   - Adjust models if needed
   - Create test fixtures

### Day 2

3. **Execute Phase 2: ENTU Reader**
   - Create `scripts/entu_reader.py`
   - Write unit tests
   - Test with full dataset (80K)
   - Verify load time acceptable

4. **START Phase 4: Person ID Coordination** (critical path!)
   - Create `scripts/extract_persons.py`
   - Generate `mappings/person_ids.csv`
   - Send to Liisi immediately
   - Continue with other phases while waiting

### Days 3-4

5. **Execute Phase 3: Field Mapping**
   - Implement all parsers (number, dimension, date)
   - Create `scripts/muis_mapper.py`
   - Write comprehensive tests
   - Test with real data from Phase 1

6. **Execute Phase 5: MUIS Writer**
   - Create `scripts/muis_writer.py`
   - Test header generation
   - Validate output format

### Day 5

7. **Execute Phase 6: Integration**
   - Create `scripts/convert.py`
   - Test end-to-end with samples
   - Add progress monitoring
   - Write integration tests

### Week 2-3 (Wait for Person IDs)

8. **Execute Phase 7: Full Processing** (when person IDs ready)
   - Run full conversion
   - Monitor and validate
   - Generate statistics

9. **Execute Phase 8: Quality Assurance**
   - Statistical validation
   - Manual spot-checking
   - Generate QA report
   - Stakeholder review

10. **Execute Phase 9: Documentation**
    - Finalize all documentation
    - Prepare handoff package
    - Git tag v1.0

---

## References

- **Data Models**: `scripts/models.py` (Pydantic v2, complete)
- **Pydantic Migration**: `docs/pydantic-v2-migration-plan.md` (historical)
- **ENTU Data**: `entust/` (38 CSV files, 108K records)
- **MUIS Reference**: `massimport_kasetohukirjad.xlsx - Leht1.csv`
- **Email Archive**: `kirjavahetus/` (requirements documentation)
- **Ada's Workflow**: `.github/prompts/Ada-the-developer-v3.prompt.md`

---

**Last Updated**: 2025-12-03

**Status**: Ready for execution. Ada can start Phase 0 immediately.

**Next Review**: After Phase 1 completion (data exploration findings)
