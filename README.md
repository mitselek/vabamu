# Vabamu ENTU → MUIS Data Migration

Python-based data extraction and conversion system for migrating museum collection data from ENTU database to MUIS (Estonian National Heritage Database) import format.

## Project Overview

This project converts ~80,000 museum object records from Vabamu's ENTU database export (38 CSV files) into the standardized 85-88 column MUIS import format required by Muinsuskaitseamet (Heritage Conservation Department).

## Current Status

**Phase**: Planning & Analysis Complete

- ✅ ENTU data structure analyzed (108,867 total records)
- ✅ MUIS target format documented
- ✅ Mapping challenges identified
- ✅ Development plan created ([PLAN.md](PLAN.md))
- ⏳ Implementation: Not started

## Project Structure

```text
vabamu/
├── entust/                    # Source ENTU CSV files (80K+ records)
├── kirjavahetus/             # Email correspondence archive
├── scripts/                  # Python conversion scripts (to be created)
├── output/                   # Generated MUIS import files (to be created)
├── mappings/                 # Configuration/mapping files (to be created)
├── tests/                    # Unit tests (to be created)
├── PLAN.md                   # Detailed implementation plan
├── README.md                 # This file
└── massimport_kasetohukirjad.xlsx - Leht1.csv  # Reference example
```

## Quick Start (Planned)

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage (Future)

```bash
# Extract all person names for ID coordination
python scripts/extract_persons.py --output mappings/person_ids.csv

# Convert sample dataset (10 records)
python scripts/convert.py --sample 10 --output output/test_import.csv

# Full conversion
python scripts/convert.py --input entust/ --output output/muis_import.csv
```

## Data Overview

### Source Data (ENTU)

- **Main table**: `eksponaat.csv` - 80,178 museum objects
- **Supporting tables**: 37 additional CSVs (classifications, persons, locations, etc.)
- **Total records**: 108,867 across all tables

### Target Format (MUIS)

- **Columns**: 85-88 columns (depending on data)
- **Structure**: 3-row header (metadata, column names, validation rules)
- **Format**: CSV with specific field requirements
- **Example**: `massimport_kasetohukirjad.xlsx - Leht1.csv`

## Key Features (Planned)

### Data Transformation

- [x] Parse ENTU object codes → MUIS number structure (ACR/TRT/TRS/TRJ/KT)
- [x] Convert dates: ISO format → MUIS format (pp.kk.aaaa)
- [x] Extract dimensions → structured measurements (4 parameter/unit/value sets)
- [x] Map materials, techniques, classifications to controlled vocabularies

### Person ID Coordination

- [x] Extract all unique person names from source data
- [ ] Generate person_ids.csv template for MuIS ID assignment
- [ ] Implement validated person name lookup (Perekonnanimi, Eesnimi format)

### Validation & Quality Assurance

- [ ] Required field validation
- [ ] Format validation (dates, numbers, person names)
- [ ] Conditional dependency checks
- [ ] Comprehensive error reporting

### Batch Processing

- [ ] Process 80K+ records efficiently
- [ ] Progress monitoring with tqdm
- [ ] Error recovery and continuation
- [ ] Segmentation by collection/type

## Technical Stack

- **Python 3.x**
- **pandas** - CSV handling and data manipulation
- **pydantic** (optional) - Data validation models
- **tqdm** (optional) - Progress bars
- **pytest** - Unit testing

## Data Mapping Examples

### Number Format

```text
ENTU: "006562/001"
  ↓
MUIS: ACR="VBM", TRT="_", TRS="6562", TRJ="1", KT="D"
```

### Date Format

```text
ENTU: "2002-12-22"
  ↓
MUIS: "22.12.2002"
```

### Dimensions Parsing

```text
ENTU: "ø50;62x70"
  ↓
MUIS:
  Parameeter 1: "läbimõõt", Ühik 1: "mm", Väärtus 1: 50
  Parameeter 2: "kõrgus", Ühik 2: "mm", Väärtus 2: 62
  Parameeter 3: "laius", Ühik 3: "mm", Väärtus 3: 70
```

### Person Names

```text
ENTU: Numeric ID (139862) or name
  ↓
MUIS: "Perekonnanimi, Eesnimi" OR MuIS ID (after coordination)
```

## Documentation

- **[PLAN.md](PLAN.md)** - Comprehensive implementation plan with 10 phases
- **kirjavahetus/** - Email archive documenting project requirements and decisions

## Development Phases

1. **Environment Setup & Data Exploration** - Day 1
2. **Core Data Reading** - Days 1-2
3. **Mapping Logic** - Days 2-3
4. **MUIS CSV Generation** - Day 3
5. **Testing with Sample Data** - Day 4
6. **Person ID Coordination** - Days 4-5
7. **Full Dataset Processing** - Days 5-6
8. **Quality Assurance & Documentation** - Days 6-7

**Estimated Timeline**: 7-10 days development + person ID coordination wait time

## Key Challenges

1. **Person ID Coordination**: ENTU uses numeric IDs, MUIS requires name format or MuIS registry IDs
2. **Number Structure**: Complex parsing of ENTU codes into 9-column MUIS format
3. **Hierarchical Data**: Multiple materials, techniques, measurements per object
4. **Vocabulary Mapping**: Classifications and controlled vocabularies differ between systems
5. **Scale**: Processing 80K+ records efficiently

## Contributing

This is an internal Vabamu Museum project for ENTU → MUIS migration.

## Contact

- **Project Lead**: Liisi Ploom (<liisi.ploom@vabamu.ee>)
- **Developer**: Mihkel Putrinš
- **Technical Partner**: Argo Roots (<argo@roots.ee>)

## License

Internal project - Vabamu Museum / Okupatsioonide ja vabaduse muuseum

---

**Last Updated**: 2025-12-03  
**Status**: Planning Complete, Implementation Pending
