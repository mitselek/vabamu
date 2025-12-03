# Reference Files

This directory contains reference materials for the ENTU → MUIS conversion project.

## Files

### muis_example_format.csv

**Source**: `massimport_kasetohukirjad.xlsx - Leht1.csv` (birch bark letters example)  
**Purpose**: Target format specification for MUIS import  
**Records**: 30 birch bark letter records from Rudolf Aller collection

**Structure**:

- **Row 1**: Metadata headers and field groupings (some cells merged in original Excel)
- **Row 2**: Estonian column names (Acr, Trt, Nimetus, Vastuvõtu nr, etc.)
- **Row 3**: Validation rules and constraints (e.g., "Peab olema number", "Kohustuslik kui...")

**Key Features**:

- 85-88 columns (varies slightly by record)
- Complex multi-value fields (up to 3 materials, 3 techniques, 4 measurements)
- Two separate event sections (Museaal sündmuses 1, Museaal sündmuses 2)
- Person fields require "Perekonnanimi, Eesnimi" format
- Date format: pp.kk.aaaa (e.g., 02.04.2000)
- Number structure: ACR/TRT/TRS/TRJ/TRL/KT/KS/KJ/KL

**Column Groups**:

1. System fields (museaali_ID, status, comments)
2. Number (9 columns: ACR, TRT, TRS, TRJ, TRL, KT, KS, KJ, KL)
3. Basic info (Nimetus, Püsiasukoht, Tulmelegend, Originaal)
4. Acquisition (Vastuvõtt: number, info, date, donor, method)
5. Measurements (4 parameter/unit/value sets)
6. Materials (3 material/comment pairs + color)
7. Techniques (3 technique/comment pairs)
8. Nature/Type (Olemus 1, Olemus 2)
9. References (Viited: type, value)
10. Archaeology context (Leiukontekst, Leiu liik)
11. Archive info (Pealkirja keel, Ainese keel)
12. Condition (Seisund, Kahjustused)
13. Event 1 (11 fields: type, location, dates, participants)
14. Event 2 (11 fields: type, location, dates, participants)
15. Visibility (Avalik, Avalikusta)
16. Descriptions (2 text type/text pairs)
17. Alt names/numbers (2 name type/name pairs, 2 number type/number pairs)

**Usage**: Use this file as the authoritative reference when:

- Designing output CSV structure
- Implementing column mapping logic
- Validating generated records
- Writing unit tests
