# ENTU → MUIS Conversion: Summary

## Task Complete ✅

Created comprehensive plan and documentation for extracting Vabamu museum collection data from ENTU database export and converting to MUIS import format.

## What Was Done

### 1. Structure Analysis

- **Analyzed ENTU export**: 38 CSV files, 108,867 total records
  - Main table: `eksponaat.csv` with 80,178 museum objects
  - Supporting tables: classifications, persons, locations, acquisition records
- **Analyzed MUIS format**: 85-88 column structure from example file
  - 3-row header (metadata, names, validation rules)
  - Complex field groups: numbering, measurements, materials, events

### 2. Created Documentation

#### PLAN.md (Comprehensive Implementation Plan)

- **10 development phases** with detailed tasks
- **Data flow diagrams** showing transformation pipeline
- **Technical stack recommendations**: Python, pandas, validation frameworks
- **Timeline**: 7-10 days estimated
- **Risk mitigation strategies** for each challenge

#### README.md (Project Overview)

- Quick start guide (for future implementation)
- Project structure
- Data mapping examples
- Key challenges documented

### 3. Key Findings

**Major Mapping Challenges Identified:**

1. **Person IDs**

   - ENTU: Numeric IDs (e.g., "139862")
   - MUIS: "Perekonnanimi, Eesnimi" format OR MuIS registry ID
   - **Solution**: Pre-coordination strategy (extract all names → get MuIS IDs)

2. **Number Structure**

   - ENTU: Simple code like "006562/001"
   - MUIS: 9-column structure (ACR/TRT/TRS/TRJ/TRL/KT/KS/KJ/KL)
   - **Solution**: Pattern parsing with rules

3. **Date Formats**

   - ENTU: ISO "2002-12-22"
   - MUIS: Estonian "22.12.2002"

4. **Hierarchical Data**

   - Materials (up to 3)
   - Techniques (up to 3)
   - Measurements (up to 4 sets)
   - Events (2 separate events)

5. **Scale**
   - 80,178 museum objects to process
   - Batch processing needed
   - Error handling critical

## Development Tools Chosen

**Language**: Python 3.8+

**Core Libraries**:

- `pandas` - Data manipulation, CSV I/O
- `csv` - Standard library CSV handling
- `datetime` - Date conversion
- `pathlib` - File operations

**Optional Enhancements**:

- `pydantic` - Data validation models
- `tqdm` - Progress bars
- `pytest` - Unit testing

## Project Structure (To Be Created)

```text
vabamu/
├── scripts/          # Conversion scripts
│   ├── entu_reader.py
│   ├── muis_mapper.py
│   ├── person_mapper.py
│   └── convert.py
├── mappings/         # Configuration files
│   ├── person_ids.csv
│   ├── materials.json
│   └── techniques.json
├── output/           # Generated MUIS files
├── tests/            # Unit tests
├── PLAN.md          # ✅ Created
└── README.md        # ✅ Created
```

## Next Steps (Implementation Phase)

### Immediate Actions

1. **Set up Python environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install pandas openpyxl
   ```

2. **Create project structure**

   ```bash
   mkdir -p scripts tests output mappings
   ```

3. **Start with data exploration**

   - Read sample eksponaat records
   - Parse number formats
   - Extract dimension patterns
   - Identify all person fields

4. **Build person extraction script**

   - Generate complete list of unique names
   - Create person_ids.csv template
   - Send to Liisi for MuIS ID coordination

5. **Incremental development**
   - Convert 1 record manually → validate
   - Automate for 10 records → validate
   - Scale to full dataset

### Phase Timeline

- **Phase 1-2**: 1-2 days (Setup + Reading)
- **Phase 3-4**: 2-3 days (Mapping + Generation)
- **Phase 5**: 1 day (Testing)
- **Phase 6**: 1-2 days (Person coordination)
- **Phase 7**: 1 day (Full processing)
- **Phase 8**: 1 day (QA)

**Total**: 7-10 days + coordination wait time

## Success Criteria

- [ ] All 80K+ records converted to MUIS format
- [ ] Generated CSV passes MUIS validation
- [ ] Person IDs coordinated with MuIS registry
- [ ] <5% error rate requiring manual intervention
- [ ] Complete documentation for handoff
- [ ] Error reports generated for manual review

## Key Decisions Made

1. **Person Strategy**: Pre-coordinate all names with MuIS IDs before main conversion
2. **Segmentation**: By collection (kuuluvus) for manageability
3. **Error Handling**: Generate error reports, don't skip records
4. **Testing**: Validate against `massimport_kasetohukirjad.xlsx` example

## Files Created

1. ✅ `/home/michelek/Documents/github/vabamu/PLAN.md` (5,500+ words)
2. ✅ `/home/michelek/Documents/github/vabamu/README.md` (project overview)
3. ✅ This summary document

## Reference Materials

- **Example MUIS file**: `massimport_kasetohukirjad.xlsx - Leht1.csv`
- **Email archive**: `kirjavahetus/` folder (7 emails documenting requirements)
- **ENTU export**: `entust/` folder (38 CSV files)

---

## Ready for Implementation

All planning and analysis complete. Next step: Begin Phase 1 (Environment Setup) when ready to start development.

**Last Updated**: 2025-12-03  
**Status**: ✅ Planning Complete
