# ENTU → MUIS Data Extraction Plan

## Project Goal

Extract museum collection data from ENTU database export (CSV files in `/entust` folder) and convert it into 85-88 column MUIS import format, matching the structure shown in `massimport_kasetohukirjad.xlsx - Leht1.csv`.

## 1. Data Structure Analysis

### 1.1 ENTU Export Structure (Source Data)

The `/entust` folder contains 38 CSV files:

**Main Tables (large datasets):**

- `eksponaat.csv` - 80,178 records - Main museum objects/exhibits
- `eksemplar.csv` - 18,668 records - Specimens/items
- `represseeritu.csv` - 2,221 records - Repressed persons
- `cl_asukoht.csv` - 1,765 records - Locations
- `vastuv6tuakt.csv` - 1,582 records - Acquisition acts
- `cl_tag.csv` - 1,108 records - Tags
- `cl_donator.csv` - 1,040 records - Donors
- `cl_autor.csv` - 925 records - Authors

**Classification Tables (cl\_\*):**

- Location types, keywords, periods, importance levels, etc.
- Reference data for main tables

**System Tables:**

- `entity.csv` - 119 records - Entity definitions/metadata
- `database.csv` - 1 record - Database configuration
- `person.csv` - 64 records - System users/staff
- Various other supporting tables (leping, laenutus, etc.)

### 1.2 MUIS Import Format Structure (Target Format)

The target CSV has 85-88 columns organized in groups:

**Header rows:**

- Row 1: Empty, metadata, column group headers
- Row 2: Column names in Estonian
- Row 3: Validation rules and field descriptions

**Column Groups:**

1. **System fields** (3): museaali_ID, Importimise staatus, Kommentaar
2. **Object Number** (9): Acr, Trt, Trs, Trj, Trl, Kt, Ks, Kj, Kl
3. **Basic Info** (3): Nimetus, Püsiasukoht, Tulmelegend, Originaal
4. **Acquisition** (4): Vastuvõtu nr, Esmane üldinfo, Kogusse registreerimise aeg, Üleandja, Muuseumile omandamise viis
5. **Measurements** (12): Parameeter 1-4, Ühik 1-4, Väärtus 1-4
6. **Materials** (6): Materjal 1-3, Materjali 1-3 kommentaar
7. **Color & Technique** (7): Värvus, Tehnika 1-3, Tehnika 1-3 kommentaar
8. **Nature** (2): Olemus 1-2
9. **References** (2): Viite tüüp, Väärtus
10. **Archaeological/Archive** (4): Leiukontekst, Leiu liik, Pealkirja keel, Ainese keel
11. **Condition** (2): Seisund, Kahjustused
12. **Event 1** (11): Sündmuse liik, Toimumiskoha täpsustus, Dateering, Riik, Admin üksus, Osaleja, Osaleja roll, etc.
13. **Event 2** (11): Same structure as Event 1
14. **Publication** (2): Avalik?, Avalikusta praegused andmed?
15. **Description** (4): Teksti tüüp 1-2, Tekst 1-2
16. **Alternative Names/Numbers** (4): Nimetuse tüüp, Nimetus, Numbri tüüp, Number

## 2. Key Mapping Challenges

### 2.1 Person ID Format

- **ENTU**: Uses numeric IDs (e.g., "139862")
- **MUIS**: Requires "Perekonnanimi, Eesnimi" format OR numeric MuIS ID
- **Strategy**: Pre-coordinate all person names with MuIS IDs (as discussed in emails)

### 2.2 Number Format

- **ENTU code**: "006562/001" → **MUIS**: ACR=VBM, TRT=\_, TRS=6562, TRJ=1, KT=D
- Parse ENTU code format and map to 9-column number structure

### 2.3 Date Format

- **ENTU**: ISO format "2002-12-22"
- **MUIS**: "pp.kk.aaaa" format
- Need conversion logic

### 2.4 Hierarchical Data (Multi-value fields)

- Materials (up to 3)
- Techniques (up to 3)
- Measurements (up to 4 parameter/unit/value sets)
- Events (2 different events)

### 2.5 Classifications/Controlled Vocabularies

- Map ENTU `tyyp` paths like "/meene/medal" to MUIS Olemus
- Map ENTU `kuuluvus` to collection names
- Map conditions, acquisition methods

## 3. Development Tools & Stack

### 3.1 Recommended Tech Stack

**Language**: Python 3.x

**Core Libraries**:

- `pandas` - CSV reading, data manipulation, output generation
- `csv` - Standard library for CSV handling
- `datetime` - Date parsing and formatting
- `pathlib` - File path handling
- `json` - For handling JSON fields in ENTU data

**Optional/Enhancement**:

- `openpyxl` - If Excel output needed
- `pydantic` - Data validation models
- `tqdm` - Progress bars for long operations
- `pytest` - Testing framework

### 3.2 Project Structure

```
vabamu/
├── entust/                    # Source ENTU CSV files
├── kirjavahetus/             # Email correspondence (archived)
├── scripts/                  # Python conversion scripts
│   ├── __init__.py
│   ├── entu_reader.py       # Read and parse ENTU CSVs
│   ├── muis_mapper.py       # Core mapping logic
│   ├── validators.py        # Data validation
│   ├── person_mapper.py     # Person ID coordination
│   └── convert.py           # Main execution script
├── output/                   # Generated MUIS import files
├── mappings/                 # Configuration files
│   ├── person_ids.csv       # Person name to MuIS ID mapping
│   ├── collections.json     # Collection mappings
│   ├── materials.json       # Material vocabulary
│   └── techniques.json      # Technique vocabulary
├── tests/                    # Unit tests
├── PLAN.md                   # This file
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

## 4. Detailed Implementation Plan

### Phase 1: Environment Setup & Data Exploration (Day 1)

**Tasks**:

1. ✅ Analyze ENTU CSV structure
2. ✅ Analyze MUIS target format
3. ✅ Identify mapping challenges
4. Create Python virtual environment
5. Install dependencies
6. Create project structure
7. Write data exploration notebook/script

**Deliverables**:

- Project structure created
- Requirements.txt with dependencies
- Initial data analysis report/notebook

### Phase 2: Core Data Reading (Day 1-2)

**Tasks**:

1. Build ENTU CSV reader classes
   - Parse `eksponaat.csv` main fields
   - Handle related tables (join logic)
   - Extract hierarchical data (materials, techniques)
2. Create data models (Pydantic or dataclasses)
3. Write unit tests for readers

**Key Files**:

- `scripts/entu_reader.py`
- `scripts/models.py`
- `tests/test_reader.py`

**Challenges**:

- Handle missing/NULL values
- Parse JSON fields in represseeritu
- Join multiple tables efficiently

### Phase 3: Mapping Logic (Day 2-3)

**Tasks**:

1. Number parsing/mapping
   - Parse ENTU code format
   - Generate ACR/TRT/TRS/TRJ structure
2. Person ID mapping system
   - Extract all unique person names from ENTU
   - Create person_ids.csv template
   - Implement lookup/validation
3. Date format conversion
4. Measurement parsing (dimensions field)
5. Material/technique extraction
6. Location/asukoht mapping
7. Classification vocabulary mapping

**Key Files**:

- `scripts/muis_mapper.py`
- `scripts/person_mapper.py`
- `mappings/person_ids.csv`
- `mappings/*.json` (vocabularies)

**Complex Mappings**:

```python
# Example: Parse dimensions "ø50;62x70" → multiple Parameeter/Ühik/Väärtus
dimensions = "ø50;62x70"
# → Parameeter 1: "läbimõõt", Ühik 1: "mm", Väärtus 1: 50
# → Parameeter 2: "kõrgus", Ühik 2: "mm", Väärtus 2: 62
# → Parameeter 3: "laius", Ühik 3: "mm", Väärtus 3: 70
```

### Phase 4: MUIS CSV Generation (Day 3)

**Tasks**:

1. Build MUIS CSV writer
   - Generate 3-row header structure
   - Apply column ordering (85-88 columns)
   - Handle CSV escaping/encoding
2. Implement validation rules
   - Check required fields
   - Validate conditional dependencies
   - Format validation (dates, numbers)
3. Error reporting system
   - Log unmapped values
   - Track validation failures
   - Generate error report

**Key Files**:

- `scripts/muis_writer.py`
- `scripts/validators.py`

### Phase 5: Testing with Sample Data (Day 4)

**Tasks**:

1. Select test dataset (10-20 eksponaat records)
2. Run full conversion pipeline
3. Compare with manual `massimport_kasetohukirjad.xlsx` example
4. Validate against MUIS requirements
5. Iterate on mappings

**Validation Points**:

- All 85-88 columns present
- Header rows formatted correctly
- Required fields populated
- Date formats correct (pp.kk.aaaa)
- Person names in correct format
- Numbers properly structured

### Phase 6: Person ID Coordination (Day 4-5)

**Tasks**:

1. Extract all unique person names from:
   - donator field
   - autor field
   - receiver field (vastuv6tuakt)
   - represseeritu names
2. Generate person_ids.csv with columns:
   - ENTU_name
   - MuIS_ID (empty, to be filled)
   - Notes
3. Coordinate with Liisi/RIK for MuIS ID assignment
4. Implement validated person lookup

**Output**: `mappings/person_ids.csv`

### Phase 7: Full Dataset Processing (Day 5-6)

**Tasks**:

1. Process all ~80K eksponaat records
2. Batch processing strategy (1000 records at a time)
3. Progress monitoring
4. Error handling and recovery
5. Generate final MUIS import CSVs

**Considerations**:

- Memory management for large dataset
- Parallel processing if needed
- Segmentation strategy (by collection/tyyp/shelf)

### Phase 8: Quality Assurance & Documentation (Day 6-7)

**Tasks**:

1. Statistical validation
   - Count records processed
   - Track mapping success rates
   - Identify common errors
2. Generate reports:
   - Conversion summary
   - Unmapped values report
   - Data quality issues
3. Documentation:
   - Update README with usage instructions
   - Document mapping decisions
   - Create troubleshooting guide
4. Prepare test import file for Liisi

## 5. Data Flow Diagram

```text
┌─────────────────┐
│  ENTU CSVs      │
│  - eksponaat    │
│  - eksemplar    │
│  - represseeritu│
│  - cl_* tables  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ENTU Reader    │
│  - Parse CSVs   │
│  - Join tables  │
│  - Extract data │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  Data Models    │◄─────┤  Mappings    │
│  - Eksponaat    │      │  - person_ids│
│  - Measurements │      │  - materials │
│  - Materials    │      │  - techniques│
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│  MUIS Mapper    │
│  - Transform    │
│  - Validate     │
│  - Format       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MUIS CSV       │
│  - 85-88 cols   │
│  - 3-row header │
│  - Validated    │
└─────────────────┘
```

## 6. Critical Decision Points

### 6.1 Person ID Strategy

**Decision**: Use pre-coordination approach

- Extract all names first
- Get MuIS IDs before main conversion
- Use "Perekonnanimi, Eesnimi" format initially
- Fallback to numeric ID if coordinated

### 6.2 Segmentation Strategy

**Options**:

1. By collection (kuuluvus)
2. By type (tyyp hierarchy)
3. By acquisition date (vastuv6tuakt)
4. By location (asukoht)

**Recommendation**: Start with collection-based segmentation, as mentioned in emails.

### 6.3 Image/File Handling

ENTU has photo/fail fields with paths.
**Decision needed**:

- Include file references in MUIS CSV?
- Coordinate separate file upload process?

### 6.4 Missing Required Fields

When ENTU data lacks MUIS required field:
**Options**:

1. Skip record (with warning)
2. Use default value
3. Mark for manual review

**Recommendation**: Mark for manual review in separate error report.

## 7. Risk Mitigation

### 7.1 Data Quality Risks

- **Risk**: Missing required MUIS fields in ENTU data
- **Mitigation**: Generate comprehensive error reports, create manual review queue

### 7.2 Person ID Coordination Delays

- **Risk**: Waiting for RIK to assign MuIS IDs
- **Mitigation**: Use name format initially, provide ID update script

### 7.3 Vocabulary Mismatches

- **Risk**: ENTU classifications don't map to MUIS controlled vocabularies
- **Mitigation**: Create mapping tables, document unmapped values, coordinate with Liisi

### 7.4 Large Dataset Performance

- **Risk**: 80K records may be slow to process
- **Mitigation**: Batch processing, progress monitoring, optimization

## 8. Next Steps (Immediate Actions)

1. **Setup Python environment**

   ```bash
   cd /home/michelek/Documents/github/vabamu
   python3 -m venv venv
   source venv/bin/activate
   pip install pandas openpyxl
   ```

2. **Create project structure**

   ```bash
   mkdir -p scripts tests output mappings
   touch scripts/__init__.py
   ```

3. **Start with data exploration script**

   - Read sample of eksponaat.csv
   - Parse number format
   - Extract dimension patterns
   - Identify all person name fields

4. **Create person extraction script**

   - Generate complete list of unique names
   - Create person_ids.csv template
   - Send to Liisi for coordination

5. **Build incremental prototype**
   - Convert 1 record manually
   - Automate that conversion
   - Scale to 10 records
   - Validate against example file

## 9. Success Criteria

✅ **Phase completion criteria:**

- [ ] All 80K+ eksponaat records converted to MUIS format
- [ ] Generated CSV passes MUIS import validation
- [ ] Person IDs coordinated and mapped
- [ ] Less than 5% error rate requiring manual intervention
- [ ] Comprehensive error reports generated
- [ ] Documentation complete for handoff

✅ **Quality metrics:**

- All required MUIS fields populated (when source data available)
- Number format correctly structured (ACR/TRT/TRS structure)
- Dates in correct format (pp.kk.aaaa)
- Person names validated against MuIS registry
- Materials/techniques mapped to controlled vocabularies

## 10. Timeline Estimate

- **Phase 1-2**: 1-2 days (Setup + Core Reading)
- **Phase 3-4**: 2-3 days (Mapping + CSV Generation)
- **Phase 5**: 1 day (Testing with samples)
- **Phase 6**: 1-2 days (Person ID coordination - may overlap)
- **Phase 7**: 1 day (Full processing)
- **Phase 8**: 1 day (QA + Documentation)

**Total**: 7-10 days of development time
**Note**: Person ID coordination with RIK may add waiting time

---

**Last Updated**: 2025-12-03
**Next Review**: After Phase 1 completion
