# Vabamu ENTU → MUIS Data Migration

Python-based data extraction and conversion system for migrating museum collection data from ENTU database to MUIS (Estonian National Heritage Database) import format.

## Project Overview

This project converts ~80,000 museum object records from Vabamu's ENTU database export (38 CSV files) into the standardized 85-88 column MUIS import format required by Muinsuskaitseamet (Heritage Conservation Department).

## Current Status

**Phase**: Data Models Complete, Implementation Ready

- ✅ Environment setup complete (Python 3.12.3, dependencies installed)
- ✅ Pydantic v2 models complete (EntuEksponaat, MuisMuseaal)
- ✅ Quality infrastructure established (black, flake8, mypy, pytest)
- ✅ 6 model validation tests passing
- ✅ Clean Problems panel (0 errors)
- ✅ Implementation roadmap created ([IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md))
- ⏳ Data exploration: Ready to start
- ⏳ Core implementation: Not started

**Next Steps**: Begin Phase 1 (Data Exploration) - See [Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md)

## Project Structure

```text
vabamu/
├── entust/                        # Source ENTU CSV files (80K+ records)
├── scripts/                       # Python conversion scripts
│   └── models.py                  # ✅ Pydantic v2 models (complete)
├── tests/                         # Unit tests (80% coverage target)
├── docs/                          # Project documentation
│   ├── IMPLEMENTATION_ROADMAP.md  # ✅ Phase-by-phase action plan
│   ├── FIELD_MAPPINGS.md          # Field mapping reference (to be created)
│   ├── ARCHITECTURE.md            # System design (to be created)
│   └── ARCHIVE/                   # Superseded planning documents
├── mappings/                      # Configuration files (to be created)
└── output/                        # Generated MUIS import files (to be created)
```

## Quick Start

```bash
# Activate environment
source venv/bin/activate

# Run tests
pytest tests/ -v --cov=scripts

# Quality checks
black scripts/ tests/
flake8 scripts/ tests/
mypy scripts/
```

## Data Overview

- **Source**: ENTU database export (38 CSV files, 108,867 records)
  - Main: `eksponaat.csv` (80,178 museum objects)
  - Supporting: Classifications, persons, locations, materials, techniques
- **Target**: MUIS import format (85-88 columns, 3-row header)
- **Key Transformations**: See [FIELD_MAPPINGS.md](docs/FIELD_MAPPINGS.md) (to be created)

## Documentation

- **[IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md)** - Complete phase-by-phase plan for Ada
- **[FIELD_MAPPINGS.md](docs/FIELD_MAPPINGS.md)** - Field mappings and examples (to be created)
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and data flow (to be created)
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Developer workflow and standards (to be created)
- **[docs/ARCHIVE/](docs/ARCHIVE/)** - Historical planning documents

## Contact

- **Project Lead**: Liisi Ploom (<liisi.ploom@vabamu.ee>)
- **Technical Partner**: Argo Roots (<argo@roots.ee>)

---

**Last Updated**: 2025-12-03  
**Status**: Phase 0 - Document Reorganization (In Progress)
