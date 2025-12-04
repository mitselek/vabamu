# Edge Cases Discovered During Conversion

## Overview

This document catalogs edge cases discovered during the semi-automatic conversion of 100 representative records from ENTU to MUIS format.

**Conversion Date:** December 4, 2025  
**Sample Size:** 100 records  
**Success Rate:** 100% (all records converted without errors)

---

## 1. Dimension Parsing Edge Cases

### 1.1 Dash-Only Dimensions (`-`)
**Count:** 4 records  
**Example:** `dimensions: "-"`  
**Issue:** Dash used as placeholder for "no dimensions"  
**Solution:** Parser returns empty measurements list (correct behavior)  
**Status:** ✅ Handled

### 1.2 Paper Size Notation (`A4`)
**Count:** 1 record  
**Example:** `dimensions: "A4"`  
**Issue:** Standard paper size notation instead of numeric dimensions  
**Solution:** Currently unparsed - returns empty list  
**Recommendation:** Add paper size lookup table (A4 → 297x210mm)  
**Status:** ⚠️ Enhancement needed for Phase 2

### 1.3 Combined Formats with Semicolon
**Count:** 2 records  
**Example:** `dimensions: "ø50;62x70"`  
**Issue:** Multiple dimension types in single field  
**Solution:** Parser correctly splits on semicolon and parses each part  
**Status:** ✅ Handled

### 1.4 Diameter-Only Format
**Count:** 6 records  
**Example:** `dimensions: "ø50"`  
**Issue:** Circular objects with diameter only  
**Solution:** Parser correctly extracts diameter as single measurement  
**Status:** ✅ Handled

### Summary Table: Dimension Formats

| Format | Count | Parsed | Notes |
|--------|-------|--------|-------|
| HxW (e.g., `168x121`) | 74 | ✅ Yes | Standard photo/document format |
| Empty | 13 | ✅ N/A | No dimensions provided |
| Diameter (e.g., `ø50`) | 6 | ✅ Yes | Circular objects |
| Dash placeholder | 4 | ✅ Skip | Intentionally empty |
| Combined semicolon | 2 | ✅ Yes | Multiple measurements |
| Paper size (A4) | 1 | ⚠️ No | Enhancement needed |

---

## 2. Date Parsing Edge Cases

### 2.1 Empty Dates
**Count:** 54 records (54%)  
**Issue:** No date information provided  
**Solution:** Parser returns None  
**Status:** ✅ Handled

### 2.2 ISO Format Dates
**Count:** 46 records (46%)  
**Example:** `date: "1956-05-28"` → `"28.05.1956"`  
**Issue:** None - standard ISO format  
**Solution:** Correctly converted to Estonian DD.MM.YYYY format  
**Status:** ✅ Handled

### Summary: Date Formats

| Format | Count | Converted | Output Format |
|--------|-------|-----------|---------------|
| ISO (YYYY-MM-DD) | 46 | ✅ Yes | DD.MM.YYYY |
| Empty | 54 | ✅ N/A | None |

---

## 3. Person Mapping Edge Cases

### 3.1 Single Name Format
**Count:** 100 records (100%)  
**Example:** `donator: "Miia Jõgiaas"`  
**Issue:** Names already in displayable format (not "Lastname, Firstname")  
**Solution:** Pass through unchanged  
**Status:** ✅ Handled

### 3.2 Numeric Person IDs
**Count:** 0 records in sample  
**Example:** `donator: "139862"` (expected in full dataset)  
**Issue:** Need to lookup name from person table  
**Solution:** Stub returns placeholder `[Person ID: 139862]`  
**Status:** ⚠️ Stub ready, lookup needed for Phase 2

### Recommendation
The sample data shows all names already formatted. However, the full 80K dataset may contain numeric IDs. The person mapper stub is ready for Phase 2 enhancement.

---

## 4. Code Parsing Edge Cases

### 4.1 Standard Format
**Count:** 100 records (100%)  
**Example:** `code: "020027/117"` → `trs=20027, trj=117`  
**Issue:** None - all codes follow NNNNNN/NNN pattern  
**Solution:** Correctly parsed with leading zeros stripped  
**Status:** ✅ Handled

### 4.2 Zero Sub-Series
**Count:** ~15 records  
**Example:** `code: "020082/000"` → `trs=20082, trj=0`  
**Issue:** Sub-series number is 000  
**Solution:** Correctly parsed as integer 0  
**Status:** ✅ Handled

---

## 5. Character Encoding Edge Cases

### 5.1 Estonian Characters
**Examples:** `õ, ä, ö, ü, Õ, Ä, Ö, Ü`  
**Found in:** Names (Jõgiaas, Tikerpäe), descriptions  
**Solution:** UTF-8 encoding throughout pipeline  
**Status:** ✅ Handled

### 5.2 Special Characters in Descriptions
**Examples:** Quotes, dashes, line breaks  
**Issue:** Multi-line descriptions with embedded newlines  
**Solution:** CSV quoting handles correctly  
**Status:** ✅ Handled

---

## 6. Missing Field Edge Cases

### 6.1 Optional Fields
Many MUIS fields have no corresponding ENTU source:

| MUIS Field | ENTU Source | Status |
|------------|-------------|--------|
| Püsiasukoht | asukoht | ⚠️ Needs mapping |
| Vastuvõtu nr | vastuv6tuakt | ⚠️ Needs mapping |
| Materjal | - | ⚠️ Not in sample |
| Tehnika | - | ⚠️ Not in sample |
| Värvus | - | ⚠️ Not in sample |

### 6.2 Event Fields
Event 1 and Event 2 fields (11 columns each) are not populated in Phase 1.
**Recommendation:** Map repression-related fields in Phase 2.

---

## 7. Summary Statistics

### Conversion Success
| Metric | Value |
|--------|-------|
| Total Records | 100 |
| Successful Conversions | 100 (100%) |
| Codes Parsed | 100 (100%) |
| Dimensions Parsed | 82 (82%) |
| Dates Converted | 46 (46%) |
| Donators Mapped | 100 (100%) |

### Edge Cases by Category
| Category | Handled | Needs Enhancement |
|----------|---------|-------------------|
| Dimension formats | 5 | 1 (paper sizes) |
| Date formats | 2 | 0 |
| Person formats | 1 | 1 (numeric IDs) |
| Code formats | 2 | 0 |
| Encoding | 2 | 0 |

---

## 8. Recommendations for Phase 2

### High Priority
1. **Paper Size Lookup** - Add A3, A4, A5 → dimensions mapping
2. **Person ID Lookup** - Implement person.csv lookup for numeric IDs
3. **Location Mapping** - Map ENTU asukoht paths to MUIS Püsiasukoht tree

### Medium Priority
4. **Material/Technique/Color** - Extract from ENTU vocabulary paths
5. **Event Mapping** - Map repression fields to MUIS Event 1/2 structure
6. **Acquisition Act** - Map vastuv6tuakt to MUIS Vastuvõtu nr

### Low Priority
7. **Alternative Numbers** - Preserve original ENTU codes as alt numbers
8. **Description Types** - Classify descriptions into MUIS text types

---

## 9. Validation Checklist

- [x] All 100 records converted without errors
- [x] MUIS CSV has correct 88-column structure
- [x] 3-row header format verified
- [x] UTF-8 encoding verified for Estonian characters
- [x] Number fields correctly parsed (acr, trt, trs, trj)
- [x] Measurements correctly extracted where present
- [x] Dates converted to DD.MM.YYYY format
- [ ] Submit to MUIS for validation (pending)
- [ ] Document MUIS feedback (pending)

---

*Document generated: December 4, 2025*  
*Conversion pipeline version: 1.0.0 (Phase 1)*
