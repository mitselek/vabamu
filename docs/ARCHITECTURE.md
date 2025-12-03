# System Architecture

## Overview

Vabamu ENTU → MUIS data migration system converts 80,000+ museum object records from ENTU database export (38 CSV files) to MUIS import format (85-88 column CSV with 3-row header).

**Design Philosophy**: TDD-first, modular pipeline with comprehensive validation at each stage.

## System Components

### 1. Data Flow Diagram

```text
┌──────────────────┐
│  ENTU CSVs       │ (38 files, 108K records)
│  - eksponaat     │
│  - klassifikaator│
│  - isik          │
│  - etc.          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  EntuReader      │ Load & validate ENTU data
│                  │ - CSV parsing with pandas
│                  │ - Pydantic model validation (EntuEksponaat)
│                  │ - Related table joins
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  MuisMapper      │ Transform ENTU → MUIS fields
│                  │ - Number parsing (ACR/TRT/TRS/TRJ/KT)
│                  │ - Date conversion (ISO → dd.mm.yyyy)
│                  │ - Dimension parsing (ø50;62x70 → structured)
│                  │ - Material/technique mapping
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  PersonMapper    │ Person name/ID coordination
│                  │ - Extract unique person names
│                  │ - MuIS ID lookup (after coordination)
│                  │ - Format: "Perekonnanimi, Eesnimi"
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  MuisWriter      │ Generate MUIS CSV
│                  │ - 3-row header (metadata/names/validation)
│                  │ - 85-88 columns per row
│                  │ - Validation against MuisMuseaal model
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  MUIS Import     │ (muis_import.csv)
│  CSV Output      │
└──────────────────┘
```

### 2. Component Descriptions

#### EntuReader

**Purpose**: Load ENTU data and validate against Pydantic models

**Responsibilities**:

- Parse eksponaat.csv (main object table)
- Load supporting tables (klassifikaator, isik, kogukategooria, etc.)
- Join related data (materials, techniques, dimensions)
- Validate using EntuEksponaat Pydantic model
- Handle encoding (UTF-8 with BOM)

**Key Methods** (to be implemented):

- `load_eksponaat(path: str, sample: int = None) -> List[EntuEksponaat]`
- `load_supporting_tables(base_path: str) -> Dict[str, pd.DataFrame]`
- `join_related_data(eksponaat_df: pd.DataFrame, supporting: Dict) -> pd.DataFrame`

**Testing**: Unit tests for CSV parsing, validation, edge cases

#### MuisMapper

**Purpose**: Transform ENTU fields to MUIS format

**Responsibilities**:

- Parse ENTU number format → 9-column MUIS structure (ACR, TRT, TRS, TRJ, KT, etc.)
- Convert dates: `2002-12-22` → `22.12.2002`
- Parse dimensions: `ø50;62x70` → 4 sets of (Parameeter, Ühik, Väärtus)
- Map materials/techniques to controlled vocabularies
- Handle missing/null values with business rules

**Key Methods** (to be implemented):

- `parse_number(entu_number: str) -> NumberComponents`
- `convert_date(iso_date: str) -> str`
- `parse_dimensions(dim_string: str) -> List[Dimension]`
- `map_material(entu_material: str) -> str`

**Testing**: Extensive unit tests for parsing edge cases, null handling

#### PersonMapper

**Purpose**: Coordinate person names and MuIS IDs

**Responsibilities**:

- Extract unique person names from all roles (author, manufacturer, etc.)
- Generate person_ids.csv for MuIS ID coordination
- Lookup MuIS IDs after coordination complete
- Format: `"Perekonnanimi, Eesnimi"` or numeric MuIS ID
- Handle missing names (unknown roles)

**Key Methods** (to be implemented):

- `extract_unique_persons(data: List[EntuEksponaat]) -> Set[str]`
- `generate_person_template(persons: Set[str], output_path: str)`
- `lookup_muis_id(person_name: str, mapping: Dict) -> Optional[str]`

**Testing**: Person name extraction, format validation, lookup logic

**Critical Path**: Must start early (Phase 4) due to 1-2 week external coordination wait

#### MuisWriter

**Purpose**: Generate valid MUIS import CSV

**Responsibilities**:

- Build 3-row header (metadata, column names, validation rules)
- Write 85-88 columns per object row
- Validate against MuisMuseaal Pydantic model
- Handle encoding (UTF-8 with BOM, Excel compatibility)
- Generate error report for invalid records

**Key Methods** (to be implemented):

- `write_header(output: TextIO)`
- `write_object_row(obj: MuisMuseaal, output: TextIO)`
- `validate_output(output_path: str) -> ValidationReport`

**Testing**: Header format, column order, encoding, validation

## Data Models

### EntuEksponaat (Source Model)

**Status**: ✅ Complete (scripts/models.py, 6 tests passing)

**Key Fields**:

- `number: str` - ENTU object number (e.g., "006562/001")
- `title: str` - Object title
- `date_str: Optional[str]` - Date in ISO format
- `dimensions: Optional[str]` - Dimension string (e.g., "ø50;62x70")
- `materials: List[str]` - Material classifications
- `techniques: List[str]` - Technique classifications
- `authors: List[str]` - Creator/author names
- `manufacturers: List[str]` - Manufacturer names

**Validation**: Pydantic v2 model with field validators

### MuisMuseaal (Target Model)

**Status**: ✅ Complete (scripts/models.py, 6 tests passing)

**Key Fields**:

- Number components: `ACR, TRT, TRS, TRJ, KT, ALAMNR, TNRKL, ALATNRKL, TNRMUU`
- Dates: `DateeringKp, DateeringKuni, DateeringTahtpaev, DateeringTahtpaev2`
- Dimensions: 4 sets of `Parameeter/Ühik/Väärtus` (1-4)
- Classifications: `RühmadeJaAlaliikideTabel`, `ObjektLiik`
- Persons: `Autor`, `Valmistaja`, `MuuIsik1-3` (with roles)

**Validation**: Pydantic v2 model with 85-88 optional fields

## Design Decisions

### 1. Pydantic for Validation

**Decision**: Use Pydantic v2 for data validation at both ENTU input and MUIS output stages

**Rationale**:

- Type safety and runtime validation
- Clear error messages for invalid data
- Self-documenting models
- Easy to test

**Trade-offs**: Slight performance overhead for 80K+ records (acceptable for batch processing)

### 2. Pandas for CSV Handling

**Decision**: Use pandas for CSV reading/writing and DataFrame operations

**Rationale**:

- Efficient for large datasets
- Built-in CSV encoding handling (UTF-8 with BOM)
- Easy DataFrame joins for related tables
- Industry standard

**Trade-offs**: Memory usage for 80K records (acceptable on modern hardware)

### 3. Modular Pipeline

**Decision**: Separate components (Reader → Mapper → Writer) instead of monolithic script

**Rationale**:

- Testable in isolation
- Reusable components
- Clear separation of concerns
- Easier debugging

**Trade-offs**: More files, slightly more complex setup

### 4. Person ID Coordination

**Decision**: Two-phase approach - extract persons first, then process after MuIS ID assignment

**Rationale**:

- External dependency (Liisi Ploom assigns MuIS IDs)
- 1-2 week wait time → must start early
- Allows parallel development of other components

**Implementation**: Generate person_ids.csv early (Phase 4), continue other phases during wait

### 5. TDD-First Development

**Decision**: Write tests before implementation (Ada's 8-step workflow)

**Rationale**:

- Catch bugs early
- Document expected behavior
- Confidence for refactoring
- 80% coverage minimum

**Quality Gates**: black, flake8, mypy, pytest must pass before merge

## Known Limitations

### 1. Person ID Coordination Dependency

**Issue**: Cannot complete full conversion until person_ids.csv coordinated with Liisi Ploom

**Impact**: 1-2 week external wait time on critical path

**Mitigation**: Start Phase 4 (person extraction) early, continue other phases in parallel

### 2. Vocabulary Mapping Ambiguity

**Issue**: ENTU classifications may not have exact MUIS equivalents

**Impact**: May require manual review for edge cases

**Mitigation**: Document mapping decisions, create fallback logic, flag ambiguous cases

### 3. Dimension Parsing Complexity

**Issue**: ENTU dimension strings vary widely (e.g., "ø50", "62x70", "H:50 L:60 S:70")

**Impact**: Complex parsing logic with many edge cases

**Mitigation**: Extensive unit tests, regex patterns, fallback to null with warning

### 4. Scale (80K Records)

**Issue**: Large dataset may reveal performance bottlenecks

**Impact**: Slow processing, memory issues

**Mitigation**: Process in batches, use pandas chunking, profile and optimize hotspots

## Error Handling Strategy

### 1. Validation Errors

- **Strategy**: Collect all validation errors, write error report (errors.csv)
- **Goal**: <1% error rate on full dataset
- **Action**: Review error report, adjust models/mappers, reprocess failed records

### 2. Missing Data

- **Strategy**: Use business rules for fallback values (e.g., unknown author → "Autor teadmata")
- **Goal**: Maximize successful conversions (97%+ target)
- **Action**: Document fallback logic, validate with Liisi Ploom

### 3. Encoding Issues

- **Strategy**: Enforce UTF-8 with BOM for ENTU input and MUIS output
- **Goal**: No garbled Estonian characters (ä, ö, ü, õ)
- **Action**: Test with real data early, validate encoding in QA phase

### 4. Critical Failures

- **Strategy**: Fail fast with clear error messages, preserve progress
- **Goal**: Resume from last successful batch, not start over
- **Action**: Checkpoint after each batch, log progress

## Performance Targets

- **Load Time**: <2 minutes for 80K records (ENTU CSV → memory)
- **Conversion Time**: <5 minutes for full dataset (ENTU → MUIS)
- **Memory Usage**: <2GB peak (reasonable for modern machines)
- **Test Suite**: <30 seconds for full test run

## Testing Strategy

### Unit Tests

- **Coverage**: 80% minimum (pytest-cov)
- **Focus**: Parsers, validators, edge cases
- **Examples**: Number parsing, date conversion, dimension parsing

### Integration Tests

- **Coverage**: End-to-end pipeline with sample data (10, 100, 1000 records)
- **Focus**: Component interactions, data flow
- **Examples**: Load ENTU → convert → write MUIS → validate output

### Regression Tests

- **Coverage**: Known edge cases from data exploration
- **Focus**: Prevent regressions during refactoring
- **Examples**: Unusual dimension formats, missing fields, special characters

### Quality Assurance (Phase 8)

- **Coverage**: Full 80K dataset processing
- **Focus**: Error rate, output validation, manual review sample
- **Target**: <1% error rate, 97%+ successful conversions

## Future Enhancements

### 1. Web UI for Person ID Coordination

- Replace manual person_ids.csv with web form
- Real-time MuIS ID lookup/assignment
- Reduce coordination wait time

### 2. Incremental Updates

- Track changes in ENTU export
- Only process new/modified objects
- Maintain conversion history

### 3. Direct MuIS API Integration

- Replace CSV import with direct API calls
- Immediate feedback on validation errors
- Eliminate manual import step

### 4. Automated Vocabulary Mapping

- Machine learning for classification mapping
- Confidence scores for ambiguous cases
- Human review queue for low-confidence matches

---

**Document Status**: Skeleton created, to be expanded during implementation  
**Last Updated**: 2025-12-03  
**Owner**: Ada (development), Liisi Ploom (business requirements)
