# Field Mappings: ENTU → MUIS

## Overview

This document defines field-by-field mappings from ENTU database export to MUIS import format. Updated with real data examples during implementation (Phase 1-3).

## Source Data Structure

### Primary Table: eksponaat.csv (80,178 records)

Key fields used in conversion:

- `id` - Internal ENTU ID
- `number` - Object code (e.g., "006562/001")
- `nimetus` - Object title
- `date_str` - Date in ISO format (e.g., "2002-12-22")
- `dimensions` - Dimension string (e.g., "ø50;62x70")
- `tyyp` - Object type classification (e.g., "/meene/medal")
- `kuuluvus` - Collection membership
- `donator` - Donor ID (references cl_donator)
- `autor` - Author ID (references cl_autor)

### Supporting Tables (37 additional CSVs)

- `cl_donator.csv` - Donor names (1,040 records)
- `cl_autor.csv` - Author names (925 records)
- `cl_asukoht.csv` - Location data (1,765 records)
- `cl_materjal.csv` - Material classifications
- `cl_tehnika.csv` - Technique classifications
- `vastuv6tuakt.csv` - Acquisition records (1,582)

## Target Format: MUIS Import CSV (85-88 columns)

### Header Structure

```csv
Row 1: Empty, metadata, column group headers
Row 2: Column names in Estonian
Row 3: Validation rules and field descriptions
Row 4+: Data rows (one per object)
```

## Detailed Field Mappings

### 1. System Fields (3 columns)

| MUIS Column           | ENTU Source | Transformation         | Example |
| --------------------- | ----------- | ---------------------- | ------- |
| `museaali_ID`         | -           | Empty (MuIS generates) | (empty) |
| `Importimise staatus` | -           | Empty                  | (empty) |
| `Kommentaar`          | -           | Empty                  | (empty) |

**Notes**: All system fields left empty for MuIS to populate.

---

### 2. Object Number (9 columns)

ENTU code format: `"NNNNNN/NNN"` (e.g., "006562/001")

| MUIS Column | ENTU Source | Transformation          | Example |
| ----------- | ----------- | ----------------------- | ------- |
| `ACR`       | `number`    | Fixed: "VBM" (Vabamu)   | VBM     |
| `TRT`       | `number`    | Fixed: "\_"             | \_      |
| `TRS`       | `number`    | Parse digits before "/" | 6562    |
| `TRJ`       | `number`    | Parse digits after "/"  | 1       |
| `TRL`       | `number`    | Empty                   | (empty) |
| `KT`        | `kuuluvus`  | Map collection → code   | D       |
| `KS`        | -           | Empty                   | (empty) |
| `KJ`        | -           | Empty                   | (empty) |
| `KL`        | -           | Empty                   | (empty) |

**Parsing Logic**:

```python
# Example: "006562/001"
entu_number = "006562/001"
trs = int(entu_number.split('/')[0])  # 6562 (strip leading zeros)
trj = int(entu_number.split('/')[1])  # 1
```

**Collection Code Mapping** (KT field):

- ENTU `kuuluvus="/kogud/dokumendikogu"` → MUIS `KT="D"`
- ENTU `kuuluvus="/kogud/esemekogu"` → MUIS `KT="E"`
- (Add more mappings during Phase 1 data exploration)

---

### 3. Basic Information (4 columns)

| MUIS Column   | ENTU Source   | Transformation       | Example                  |
| ------------- | ------------- | -------------------- | ------------------------ |
| `Nimetus`     | `nimetus`     | Direct copy          | Medalikomplekt           |
| `Püsiasukoht` | `asukoht`     | Join with cl_asukoht | Väike-Ameerika 1, ruum X |
| `Tulmelegend` | `description` | Copy if exists       | ...                      |
| `Originaal`   | -             | Empty (default)      | (empty)                  |

**Notes**: Most objects are originals, leave empty unless specifically copy/reproduction.

---

### 4. Acquisition Information (5 columns)

| MUIS Column                   | ENTU Source          | Transformation                        | Example      |
| ----------------------------- | -------------------- | ------------------------------------- | ------------ |
| `Vastuvõtu nr`                | `vastuv6tuakt`       | Join with vastuv6tuakt.csv            | VVA-2002-123 |
| `Esmane üldinfo`              | `acquisition_notes`  | Copy if exists                        | ...          |
| `Kogusse registreerimise aeg` | `registration_date`  | Convert date format                   | 22.12.2002   |
| `Üleandja`                    | `donator`            | Join with cl_donator + person mapping | Tamm, Jaan   |
| `Muuseumile omandamise viis`  | `acquisition_method` | Map to controlled vocab               | ost          |

**Date Conversion**:

```python
# ENTU: "2002-12-22" → MUIS: "22.12.2002"
from datetime import datetime
entu_date = "2002-12-22"
muis_date = datetime.fromisoformat(entu_date).strftime("%d.%m.%Y")
```

**Person Name Format**:

- ENTU: Numeric ID (139862) or structured name
- MUIS: "Perekonnanimi, Eesnimi" OR MuIS ID (after Phase 4 coordination)

---

### 5. Measurements (12 columns - 4 sets)

ENTU `dimensions` field examples:

- `"ø50"` - Diameter only
- `"62x70"` - Height × width
- `"H:50 L:60 S:70"` - Labeled dimensions
- `"ø50;62x70"` - Multiple objects/parts

| MUIS Columns   | ENTU Source  | Transformation             | Example  |
| -------------- | ------------ | -------------------------- | -------- |
| `Parameeter 1` | `dimensions` | Parse 1st measurement type | läbimõõt |
| `Ühik 1`       | `dimensions` | Default "mm" or parse unit | mm       |
| `Väärtus 1`    | `dimensions` | Parse 1st number           | 50       |
| `Parameeter 2` | `dimensions` | Parse 2nd measurement type | kõrgus   |
| `Ühik 2`       | `dimensions` | Default "mm" or parse unit | mm       |
| `Väärtus 2`    | `dimensions` | Parse 2nd number           | 62       |
| `Parameeter 3` | `dimensions` | Parse 3rd measurement type | laius    |
| `Ühik 3`       | `dimensions` | Default "mm" or parse unit | mm       |
| `Väärtus 3`    | `dimensions` | Parse 3rd number           | 70       |
| `Parameeter 4` | `dimensions` | Parse 4th measurement type | (empty)  |
| `Ühik 4`       | `dimensions` | Default "mm" or parse unit | (empty)  |
| `Väärtus 4`    | `dimensions` | Parse 4th number           | (empty)  |

**Parsing Logic**:

```python
# Example: "ø50;62x70"
def parse_dimensions(dim_str: str) -> List[Dimension]:
    results = []

    # Handle diameter: "ø50"
    if 'ø' in dim_str:
        value = extract_number_after('ø', dim_str)
        results.append(Dimension("läbimõõt", "mm", value))

    # Handle "HxW" format: "62x70"
    if 'x' in dim_str:
        parts = dim_str.split('x')
        results.append(Dimension("kõrgus", "mm", int(parts[0])))
        results.append(Dimension("laius", "mm", int(parts[1])))

    # Handle labeled: "H:50 L:60"
    # ... (implement during Phase 3)

    return results[:4]  # Max 4 measurements
```

**Parameter Mapping** (Estonian terms):

- `"H"` or `"K"` → `"kõrgus"` (height)
- `"L"` or `"W"` → `"laius"` (width)
- `"S"` or `"D"` → `"sügavus"` (depth)
- `"ø"` → `"läbimõõt"` (diameter)
- `"P"` → `"pikkus"` (length)

---

### 6. Materials (6 columns - 3 materials)

| MUIS Columns             | ENTU Source       | Transformation       | Example |
| ------------------------ | ----------------- | -------------------- | ------- |
| `Materjal 1`             | `materials`       | Parse 1st material   | metall  |
| `Materjali 1 kommentaar` | `materials_notes` | Notes for material 1 | pronks  |
| `Materjal 2`             | `materials`       | Parse 2nd material   | (empty) |
| `Materjali 2 kommentaar` | `materials_notes` | Notes for material 2 | (empty) |
| `Materjal 3`             | `materials`       | Parse 3rd material   | (empty) |
| `Materjali 3 kommentaar` | `materials_notes` | Notes for material 3 | (empty) |

**Material Vocabulary Mapping** (to be built during Phase 1):

- ENTU classification paths like `/materjalid/metall` → MUIS "metall"
- Specific materials in kommentaar field (e.g., "pronks", "raud", "kuld")

---

### 7. Color & Technique (7 columns)

| MUIS Columns           | ENTU Source        | Transformation        | Example          |
| ---------------------- | ------------------ | --------------------- | ---------------- |
| `Värvus`               | `color`            | Direct copy or map    | hõbe             |
| `Tehnika 1`            | `techniques`       | Parse 1st technique   | kaunistustehnika |
| `Tehnika 1 kommentaar` | `techniques_notes` | Notes for technique 1 | reljeef          |
| `Tehnika 2`            | `techniques`       | Parse 2nd technique   | (empty)          |
| `Tehnika 2 kommentaar` | `techniques_notes` | Notes for technique 2 | (empty)          |
| `Tehnika 3`            | `techniques`       | Parse 3rd technique   | (empty)          |
| `Tehnika 3 kommentaar` | `techniques_notes` | Notes for technique 3 | (empty)          |

**Technique Vocabulary Mapping** (to be built during Phase 1):

- ENTU classification paths → MUIS controlled vocabulary
- Specific techniques in kommentaar field

---

### 8. Nature/Type (2 columns)

| MUIS Columns | ENTU Source | Transformation           | Example          |
| ------------ | ----------- | ------------------------ | ---------------- |
| `Olemus 1`   | `tyyp`      | Map classification path  | märgistus (märk) |
| `Olemus 2`   | `tyyp`      | Secondary classification | (empty)          |

**Classification Mapping** (examples):

- ENTU `tyyp="/meene/medal"` → MUIS `Olemus 1="märgistus (märk)"`
- ENTU `tyyp="/dokument/foto"` → MUIS `Olemus 1="fotomaterjal"`
- (Build complete mapping during Phase 1)

---

### 9. References (2 columns)

| MUIS Columns | ENTU Source       | Transformation     | Example |
| ------------ | ----------------- | ------------------ | ------- |
| `Viite tüüp` | `reference_type`  | Map reference type | (empty) |
| `Väärtus`    | `reference_value` | Reference value    | (empty) |

**Notes**: Rarely used, leave empty unless specific reference data exists.

---

### 10. Archaeological/Archive (4 columns)

| MUIS Columns     | ENTU Source        | Transformation         | Example |
| ---------------- | ------------------ | ---------------------- | ------- |
| `Leiukontekst`   | `context`          | Archaeological context | (empty) |
| `Leiu liik`      | `find_type`        | Find type              | (empty) |
| `Pealkirja keel` | `title_language`   | Title language         | et      |
| `Ainese keel`    | `content_language` | Content language       | et      |

**Notes**: Most Vabamu objects are Estonian language, default to "et".

---

### 11. Condition (2 columns)

| MUIS Columns  | ENTU Source | Transformation     | Example        |
| ------------- | ----------- | ------------------ | -------------- |
| `Seisund`     | `condition` | Map condition term | hea            |
| `Kahjustused` | `damages`   | Damage description | kulunud servad |

**Condition Vocabulary**:

- `"hea"` - Good condition
- `"rahuldav"` - Fair condition
- `"halb"` - Poor condition

---

### 12. Event 1 (11 columns)

| MUIS Columns                | ENTU Source         | Transformation              | Example       |
| --------------------------- | ------------------- | --------------------------- | ------------- |
| `Sündmuse liik 1`           | `event_type`        | Event type                  | valmistamine  |
| `Toimumiskoha täpsustus 1`  | `event_location`    | Location detail             | Tallinn       |
| `Dateering kp 1`            | `event_date_start`  | Start date (dd.mm.yyyy)     | 01.01.2002    |
| `Dateering kuni 1`          | `event_date_end`    | End date (dd.mm.yyyy)       | 31.12.2002    |
| `Dateering tähtpäev 1`      | `event_date_exact`  | Exact date                  | (empty)       |
| `Riik 1`                    | `event_country`     | Country                     | Eesti         |
| `Admin üksus 1`             | `event_admin`       | Admin unit                  | Harju maakond |
| `Osaleja 1`                 | `autor`             | Person name (after mapping) | Tamm, Jaan    |
| `Osaleja roll 1`            | -                   | Fixed: "autor"              | autor         |
| `Osaleja päritolu 1`        | -                   | Empty                       | (empty)       |
| `Viide toimumisaja kohta 1` | `event_date_source` | Date source reference       | (empty)       |

**Event Type Mapping**:

- Creation event: `Sündmuse liik 1 = "valmistamine"`
- Acquisition event: Use Event 2 (below)

---

### 13. Event 2 (11 columns)

Same structure as Event 1, typically used for acquisition:

| MUIS Columns      | ENTU Source      | Transformation             | Example    |
| ----------------- | ---------------- | -------------------------- | ---------- |
| `Sündmuse liik 2` | -                | Fixed: "omandamine"        | omandamine |
| `Osaleja 2`       | `donator`        | Donor name (after mapping) | Kask, Mari |
| `Osaleja roll 2`  | -                | Fixed: "annetaja"          | annetaja   |
| (other columns)   | (as per Event 1) | ...                        | ...        |

---

### 14. Publication (2 columns)

| MUIS Columns                   | ENTU Source | Transformation           | Example |
| ------------------------------ | ----------- | ------------------------ | ------- |
| `Avalik?`                      | `public`    | Map boolean → "jah"/"ei" | jah     |
| `Avalikusta praegused andmed?` | -           | Fixed: "jah"             | jah     |

**Notes**: Most objects should be public, default to "jah" unless restricted.

---

### 15. Description (4 columns)

| MUIS Columns    | ENTU Source   | Transformation     | Example           |
| --------------- | ------------- | ------------------ | ----------------- |
| `Teksti tüüp 1` | -             | Fixed: "kirjeldus" | kirjeldus         |
| `Tekst 1`       | `description` | Direct copy        | Hõbedane medal... |
| `Teksti tüüp 2` | -             | Empty or "märkus"  | (empty)           |
| `Tekst 2`       | `notes`       | Copy if exists     | (empty)           |

---

### 16. Alternative Names/Numbers (4 columns)

| MUIS Columns    | ENTU Source       | Transformation          | Example |
| --------------- | ----------------- | ----------------------- | ------- |
| `Nimetuse tüüp` | `alt_title_type`  | Alternative title type  | (empty) |
| `Nimetus`       | `alt_title`       | Alternative title       | (empty) |
| `Numbri tüüp`   | `alt_number_type` | Alternative number type | (empty) |
| `Number`        | `alt_number`      | Alternative number      | (empty) |

**Notes**: Rarely used, leave empty unless alternative identifiers exist.

---

## Business Rules & Fallback Logic

### Person/Organization Name Extraction (Phase 1 Prerequisite)

**MuIS Import Requirement**: Per MuIS documentation, all person and organization names must exist in the MuIS registry **before** import.

> "Isikute ja asutuste nimed peavad vastama MuISis olemasolevatele. S.t isikud ja asutused peavad olema MuISi osalejatena sisestatud."

This is a **blocking requirement** for Phase 2 production migration.

#### Fields Containing Person/Organization Names

| ENTU Field        | MUIS Field(s)              | Entity Type | Sample Size Statistics |
| ----------------- | -------------------------- | ----------- | ---------------------- |
| `donator`         | `Üleandja`, `Osaleja 2`    | Person/Org  | 43 unique (100 sample) |
| `represseeritu_o` | `Osaleja` (Event context)  | Person      | 8 unique (multiline)   |
| `represseeritu_t` | `Osaleja` (Event context)  | Person      | 16 unique (multiline)  |
| `autor`           | `Osaleja 1` (Event 1)      | Person/Org  | 0 in sample (full TBD) |

**Multiline Format**: Some fields (represseeritu_*) contain multiple names separated by newlines:

```text
Tamm, Jaan, Mihkel
Kask, Mari, Peeter
Lepp, Ants, Jüri
```

#### Entity Classification Heuristics

1. **Person Pattern** (checked first): Contains comma → `"Perekonnanimi, Eesnimi"` → Person
2. **Organization Keywords**:
   - Estonian: `muuseum`, `instituut`, `fond`, `arhiiv`, `ülikool`
   - Company suffixes: `OÜ`, `AS`, `SA`, `MTÜ` (with space prefix to avoid false matches)
3. **Default**: Person (most common case)

#### Extraction Process

**Script**: `scripts/extract_person_names.py`

```bash
# Extract from sample data
python -m scripts.extract_person_names \
    --input output/sample_100_raw.csv \
    --output output/person_registry_request_sample.csv
```

**Output Format**: CSV with columns for MuIS stakeholder to complete

```csv
entu_field,entu_value,entity_type,frequency,sample_records,muis_participant_id,notes
donator,Heiki Ahonen,person,11,"019212/002, 015580/006, ...",<TO_BE_FILLED>,
donator,Valmi Kallion,person,11,"020417/000, 020414/000, ...",<TO_BE_FILLED>,
represseeritu_t,"Jaosaar, Richard, Mihkel",person,2,"020004/008, 020004/004",<TO_BE_FILLED>,
```

#### Coordination Steps

1. **Extract**: Run `extract_person_names.py` on full 80K dataset
2. **Review**: Validate entity classification (person vs organization)
3. **Submit**: Send CSV to MuIS stakeholder (Liisi Ploom)
4. **Wait**: MuIS adds entities to participant registry (1-2 weeks estimate)
5. **Receive**: Get back CSV with `muis_participant_id` column filled
6. **Implement**: Use IDs in `person_mapper.py` lookup table for final conversion

#### Sample Statistics (100 records)

- **Total unique persons/orgs**: 77
- **Entity breakdown**: 77 persons, 0 organizations
- **Total occurrences**: 137
- **Most frequent**: Heiki Ahonen (11x), Valmi Kallion (11x), Urve Rukki (7x)
- **Fields used**: donator (100%), represseeritu_o (8%), represseeritu_t (16%)

#### Known Edge Cases

1. **Multiline names**: Handled via `parse_multiline_names()` function
2. **Estonian characters**: UTF-8 encoding preserved (Jõgiaas, Tikerpäe)
3. **False matches avoided**: "as" in "Jõgiaas" vs company suffix " AS"
4. **Empty fields**: Gracefully handled (ignored)

---

### Required Fields (Must be populated)

1. **Nimetus** (Title): If missing → `"Nimetu objekt"`
2. **Object Number** (TRS): Required for MuIS import
3. **Collection Code** (KT): Required, map from kuuluvus

### Conditional Dependencies

1. If `Osaleja 1` populated → `Osaleja roll 1` required
2. If `Dateering kp 1` populated → `Sündmuse liik 1` required
3. If `Materjal 1` populated → Use `Materjali 1 kommentaar` for specifics

### Missing Data Handling

| Field       | Fallback Strategy                           |
| ----------- | ------------------------------------------- |
| Date        | Leave empty (do not guess)                  |
| Person name | Use "Autor teadmata" or "Annetaja teadmata" |
| Material    | Leave empty if unknown                      |
| Dimensions  | Leave empty if unparseable                  |
| Location    | Use default "Tallinn" if missing            |

---

## Parsing Examples

### Example 1: Complete Medal Object

**ENTU Data**:

```python
{
    "number": "006562/001",
    "nimetus": "Medalikomplekt",
    "date_str": "2002-12-22",
    "dimensions": "ø50",
    "tyyp": "/meene/medal",
    "kuuluvus": "/kogud/esemekogu",
    "autor": 139862,  # → "Tamm, Jaan" after person mapping
    "material": "/materjalid/metall",
    "material_note": "pronks"
}
```

**MUIS Output** (key fields):

```csv
...,VBM,_,6562,1,,E,,,Medalikomplekt,...,läbimõõt,mm,50,...,metall,pronks,...,märgistus (märk),...,valmistamine,...,22.12.2002,...,Tamm\, Jaan,autor,...
```

### Example 2: Document with Multiple Dimensions

**ENTU Data**:

```python
{
    "number": "012345/002",
    "nimetus": "Fotograafia",
    "dimensions": "62x70",
    "tyyp": "/dokument/foto"
}
```

**MUIS Output** (measurements):

```csv
...,kõrgus,mm,62,laius,mm,70,,,,...
```

---

## Edge Cases & Known Issues

### 1. Unparseable Dimensions

**Example**: `"dimensions": "väga suur"`
**Strategy**: Leave Parameeter/Ühik/Väärtus empty, log warning

### 2. Missing Person Names

**Example**: `"autor": null`
**Strategy**: Use `"Autor teadmata"` or leave empty, flag for review

### 3. Multiple Objects in One Record

**Example**: `"dimensions": "ø50;ø55;ø60"` (3 medals)
**Strategy**: Create separate MUIS rows or use first value, flag for manual review

### 4. Non-Standard Number Formats

**Example**: `"number": "VBM-D-123"` (already includes ACR)
**Strategy**: Detect format, parse accordingly, log warning

### 5. Date Ranges

**Example**: `"date_str": "2002-2005"`
**Strategy**: Split to `Dateering kp` and `Dateering kuni`, parse both

---

## Validation Checklist

After conversion, validate:

- ✅ All required fields populated (TRS, KT, Nimetus)
- ✅ Dates in correct format (dd.mm.yyyy, not ISO)
- ✅ Person names in "Perekonnanimi, Eesnimi" format
- ✅ Number structure valid (ACR + TRS minimum)
- ✅ No trailing commas or formatting errors
- ✅ UTF-8 encoding preserved (Estonian characters: ä, ö, ü, õ)
- ✅ 3-row header structure correct

---

## Document Status

**Status**: Initial skeleton created from archived PLAN.md  
**Next Update**: After Phase 1 (Data Exploration) - add real data examples and edge cases  
**Maintenance**: Living document, updated throughout implementation  
**Owner**: Ada (technical), Liisi Ploom (business rules validation)

**Last Updated**: 2025-12-03
