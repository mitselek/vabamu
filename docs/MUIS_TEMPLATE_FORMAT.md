# MUIS Template Formatting Specification

## Header Row Color

**Source**: Extracted from `output/100 juhuslikku eksponaati ver2_1 manual.xlsx`

### Green Header Fill

**Color**: `FFA9D18E` (ARGB format)  
**RGB**: `A9D18E` (light green)  
**Pattern**: `solid`  
**Applied to**: Header rows 1-3

### Implementation (if required by MUIS)

```python
from openpyxl.styles import PatternFill

# MUIS template green header color
MUIS_HEADER_GREEN = PatternFill(
    start_color="FFA9D18E",
    end_color="FFA9D18E",
    fill_type="solid"
)

# Apply to header rows
for row in ws.iter_rows(min_row=1, max_row=3):
    for cell in row:
        cell.fill = MUIS_HEADER_GREEN
```

### Status

**Current**: `scripts/csv_to_excel.py` does NOT apply green color (bold text only)  
**Pending**: Awaiting Liisi's feedback - does MUIS require green header or is content sufficient?

**If green required**:

- Add 5 lines to `csv_to_excel.py`
- Update Issue #12
- Estimated time: 15 minutes

**If content sufficient**:

- Issue #12 complete as-is ✅
- No changes needed

---

**Date**: December 10, 2025  
**Awaiting**: Liisi's response to Mihkel's email (13:08)
