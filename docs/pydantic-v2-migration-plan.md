# Pydantic v2 Migration Plan

**Date**: 2025-12-03

**Objective**: Migrate `scripts/models.py` from Pydantic v1 to v2, fix import collisions, complete TODOs, and establish quality baseline with tests

---

## Issues Identified

### Issue 1: Pydantic v1 Decorators (Breaking)

**Current state**: Using deprecated v1 decorators

```python
from pydantic import validator, root_validator

@validator('code')
def validate_code_format(cls, v):
    ...

@root_validator
def validate_dependencies(cls, values):
    ...
```

**Required**: Pydantic v2 decorators

```python
from pydantic import field_validator, model_validator

@field_validator('code')
@classmethod
def validate_code_format(cls, v: str) -> str:
    ...

@model_validator(mode='after')
def validate_dependencies(self) -> 'ModelName':
    ...
```

**Impact**: Code won't run with Pydantic v2

**Files affected**: `scripts/models.py` (15+ decorators)

---

### Issue 2: Date Import Collision (Type Error)

**Current state**: Variable name shadows type

```python
from datetime import date, datetime

class EntuEksponaat(BaseModel):
    date: Optional[date] = Field(None, description="Primary date (ISO format)")
    # ERROR: Variable 'date' shadows imported type 'date'
```

**Required**: Use alias

```python
from datetime import date as Date, datetime

class EntuEksponaat(BaseModel):
    date: Optional[Date] = Field(None, description="Primary date (ISO format)")
```

**Impact**: Pylance errors, mypy failures

**Files affected**: `scripts/models.py` (line 20, 91, 143, 151)

---

### Issue 3: Missing Type Hints on Validators

**Current state**: Validators lack type annotations

```python
@validator('code')
def validate_code_format(cls, v):  # Parameter 'v' type unknown
    ...
```

**Required**: Full type hints

```python
@field_validator('code')
@classmethod
def validate_code_format(cls, v: str) -> str:
    ...
```

**Impact**: mypy --strict failures, reduced IDE support

**Files affected**: `scripts/models.py` (lines 134, 142)

---

### Issue 4: Incomplete Validators (TODOs)

**Location 1**: `EntuEksponaat.validate_code_format` (line 137)

```python
if v and not re.match(r'^\d{6}/\d{3}$', v):
    # Allow variations but warn
    pass  # TODO: Log format variance
return v
```

**Options**:

1. **Enforce**: Raise ValueError if pattern doesn't match
2. **Log**: Import logging and log variance
3. **Remove**: Delete if not needed

**Location 2**: `MuisMeasurement.validate_parameter` (line 175)

```python
valid = ['kõrgus', 'laius', 'pikkus', 'läbimõõt', 'sügavus', 'kaal', 'diameeter']
if v.lower() not in valid:
    # TODO: Log unmapped parameter
    pass
return v
```

**Same options as above**  

**Impact**: Incomplete validation, unclear intent

---

### Issue 5: No Tests (Quality Gap)

**Current state**: Zero test coverage

**Required**: Comprehensive test suite

- Happy path: Valid data instantiation
- Edge cases: Missing optional fields
- Validation errors: Each validator fires correctly
- Business rules: All conditional dependencies

**Target**: 80%+ coverage

**Files to create**: `tests/test_models.py`

---

## Migration Plan (13 Steps) ✅ COMPLETE

### Phase 1: Dependencies (Steps 1-2)

**Step 1: Create requirements.txt**  

Create `requirements.txt` with:

```text
# Core dependencies
pydantic>=2.0,<3.0
pandas>=2.0,<3.0
openpyxl>=3.1.0
python-dateutil>=2.9.0

# Progress tracking
tqdm>=4.66.0

# Testing
pytest>=8.0.0
pytest-cov>=4.1.0

# Code quality
black>=24.0.0
flake8>=7.0.0
mypy>=1.8.0
types-python-dateutil>=2.9.0
```

**Step 2: Install packages**  

```bash
/home/michelek/Documents/github/vabamu/.venv/bin/python -m pip install -r requirements.txt
```

---

### Phase 2: Import Fixes (Steps 3-4)

**Step 3: Fix date import collision**  

Update line 20:

```python
# Before
from datetime import date, datetime

# After
from datetime import date as Date, datetime
```

Update all usages (lines 91, 143, 151):

```python
# Before
date: Optional[date] = Field(None, ...)
def parse_date(cls, v) -> Optional[date]:
    if isinstance(v, date):
        return datetime.strptime(v, '%Y-%m-%d').date()

# After
date: Optional[Date] = Field(None, ...)
def parse_date(cls, v) -> Optional[Date]:
    if isinstance(v, Date):
        return datetime.strptime(v, '%Y-%m-%d').date()
```

**Step 4: Update Pydantic imports**  

Update line 19:

```python
# Before
from pydantic import BaseModel, Field, validator, root_validator

# After
from pydantic import BaseModel, Field, field_validator, model_validator
```

---

### Phase 3: Decorator Migration (Steps 5-6)

**Step 5: Migrate @validator to @field_validator**  

**Occurrence 1**: `EntuEksponaat.validate_code_format` (line 134)

```python
# Before
@validator('code')
def validate_code_format(cls, v):
    if v and not re.match(r'^\d{6}/\d{3}$', v):
        pass  # TODO: Log format variance
    return v

# After
@field_validator('code')
@classmethod
def validate_code_format(cls, v: str) -> str:
    if v and not re.match(r'^\d{6}/\d{3}$', v):
        pass  # TODO: Log format variance
    return v
```

**Occurrence 2**: `EntuEksponaat.parse_date` (line 142)

```python
# Before
@validator('date', pre=True)
def parse_date(cls, v):
    if not v:
        return None
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        try:
            return datetime.strptime(v, '%Y-%m-%d').date()
        except ValueError:
            return None
    return None

# After
@field_validator('date', mode='before')
@classmethod
def parse_date(cls, v: str | Date | None) -> Date | None:
    if not v:
        return None
    if isinstance(v, Date):
        return v
    if isinstance(v, str):
        try:
            return datetime.strptime(v, '%Y-%m-%d').date()
        except ValueError:
            return None
    return None
```

**Occurrence 3**: `MuisMeasurement.validate_parameter` (line 173)

```python
# Before
@validator('parameeter')
def validate_parameter(cls, v):
    valid = ['kõrgus', 'laius', 'pikkus', 'läbimõõt', 'sügavus', 'kaal', 'diameeter']
    if v.lower() not in valid:
        pass  # TODO: Log unmapped parameter
    return v

# After
@field_validator('parameeter')
@classmethod
def validate_parameter(cls, v: str) -> str:
    valid = ['kõrgus', 'laius', 'pikkus', 'läbimõõt', 'sügavus', 'kaal', 'diameeter']
    if v.lower() not in valid:
        pass  # TODO: Log unmapped parameter
    return v
```

**Occurrence 4**: `MuisEvent.validate_date_format` (line 237)

```python
# Before
@validator('dateering_algus', 'dateering_lopp')
def validate_date_format(cls, v):
    if not v:
        return v
    if not re.match(r'^(\d{4}|\d{2}\.\d{4}|\d{2}\.\d{2}\.\d{4})$', v):
        raise ValueError(f"Invalid date format: {v}. Must be aaaa or kk.aaaa or pp.kk.aaaa")
    return v

# After
@field_validator('dateering_algus', 'dateering_lopp')
@classmethod
def validate_date_format(cls, v: str | None) -> str | None:
    if not v:
        return v
    if not re.match(r'^(\d{4}|\d{2}\.\d{4}|\d{2}\.\d{2}\.\d{4})$', v):
        raise ValueError(f"Invalid date format: {v}. Must be aaaa or kk.aaaa or pp.kk.aaaa")
    return v
```

**Step 6: Migrate @root_validator to @model_validator**  

**Pattern change**:

```python
# Before (v1)
@root_validator
def validate_dependencies(cls, values):
    if values.get('field_a') and not values.get('field_b'):
        raise ValueError("field_b required when field_a filled")
    return values

# After (v2)
@model_validator(mode='after')
def validate_dependencies(self) -> 'ModelName':
    if self.field_a and not self.field_b:
        raise ValueError("field_b required when field_a filled")
    return self
```

**Files to update** (13 occurrences):

1. `MuisEvent.validate_event_dependencies` (line 226)
2. `MuisMuseaal.validate_measurement_dependencies` (line 425)
3. `MuisMuseaal.validate_material_dependencies` (line 443)
4. `MuisMuseaal.validate_technique_dependencies` (line 455)
5. `MuisMuseaal.validate_event_1_dependencies` (line 467)
6. `MuisMuseaal.validate_event_2_dependencies` (line 492)
7. `MuisMuseaal.validate_description_dependencies` (line 517)
8. `MuisMuseaal.validate_alternative_name_dependencies` (line 534)
9. `MuisMuseaal.validate_alternative_number_dependencies` (line 546)
10. `MuisMuseaal.validate_condition_damage_dependency` (line 558)
11. `MuisMuseaal.validate_reference_dependency` (line 568)
12. `MuisMuseaal.validate_archaeology_dependency` (line 578)

---

### Phase 4: Complete TODOs (Steps 7-8)

**Step 7: Fix validate_parameter TODO**  

**Decision needed**: How to handle unmapped parameters?

**Option A - Strict (recommended)**:

```python
@field_validator('parameeter')
@classmethod
def validate_parameter(cls, v: str) -> str:
    valid = ['kõrgus', 'laius', 'pikkus', 'läbimõõt', 'sügavus', 'kaal', 'diameeter']
    if v.lower() not in valid:
        raise ValueError(
            f"Invalid parameter '{v}'. Must be one of: {', '.join(valid)}"
        )
    return v
```

**Option B - Permissive with logging**:

```python
import logging

logger = logging.getLogger(__name__)

@field_validator('parameeter')
@classmethod
def validate_parameter(cls, v: str) -> str:
    valid = ['kõrgus', 'laius', 'pikkus', 'läbimõõt', 'sügavus', 'kaal', 'diameeter']
    if v.lower() not in valid:
        logger.warning(f"Unmapped parameter: '{v}' (not in MUIS vocabulary)")
    return v
```

**Option C - Remove validation**:

```python
# Delete the entire validator
```

**Step 8: Fix validate_code_format TODO**  

**Same options as Step 7**  

**Option A - Strict**:

```python
@field_validator('code')
@classmethod
def validate_code_format(cls, v: str) -> str:
    if v and not re.match(r'^\d{6}/\d{3}$', v):
        raise ValueError(
            f"Invalid code format: '{v}'. Expected format: XXXXXX/XXX (e.g., 006562/001)"
        )
    return v
```

**Option B - Permissive with logging**:

```python
import logging

logger = logging.getLogger(__name__)

@field_validator('code')
@classmethod
def validate_code_format(cls, v: str) -> str:
    if v and not re.match(r'^\d{6}/\d{3}$', v):
        logger.warning(f"Code format variance: '{v}' (expected XXXXXX/XXX)")
    return v
```

---

### Phase 5: Quality Checks (Steps 9-11)

**Step 9: Run black formatter**  

```bash
black scripts/models.py --line-length=100
```

**Expected**: Code reformatted to consistent style

**Step 10: Run flake8 linter**  

```bash
flake8 scripts/models.py --max-line-length=100
```

**Expected**: No style issues

**Step 11: Run mypy type checker**  

```bash
mypy scripts/models.py --strict
```

**Expected**: No type errors

---

### Phase 6: Validation & Commit (Steps 12-13)

**Step 12: Test model instantiation**  

Create `scripts/test_models_quick.py`:

```python
"""Quick validation that models work after Pydantic v2 migration"""

from models import EntuEksponaat, MuisMuseaal
from datetime import date

# Test EntuEksponaat instantiation
print("Testing EntuEksponaat...")
entu = EntuEksponaat(
    _id="12345",
    code="006562/001",
    name="Test Object",
    date="2024-01-15"
)
print(f"✓ Created: {entu.code} - {entu.name}")
print(f"✓ Date parsed: {entu.date}")

# Test MuisMuseaal instantiation
print("\nTesting MuisMuseaal...")
muis = MuisMuseaal(
    acr="VBM",
    trt="_",
    trs=1,
    nimetus="Test Object"
)
print(f"✓ Created: {muis.acr}{muis.trt}{muis.trs} - {muis.nimetus}")

# Test validation: osaleja_1 requires osaleja_roll_1
print("\nTesting validation (should raise error)...")
try:
    invalid = MuisMuseaal(
        acr="VBM",
        trt="_",
        trs=1,
        nimetus="Test",
        osaleja_1="John Doe"  # Missing osaleja_roll_1
    )
    print("✗ FAILED: Should have raised ValidationError")
except ValueError as e:
    print(f"✓ Validation works: {e}")

print("\n✓ All quick tests passed!")
```

Run:

```bash
/home/michelek/Documents/github/vabamu/.venv/bin/python scripts/test_models_quick.py
```

**Step 13: Commit changes**  

```bash
git add requirements.txt scripts/models.py
git commit -m "Migrate models.py to Pydantic v2

- Update imports: validator → field_validator, root_validator → model_validator
- Fix date import collision (date → Date alias)
- Add type hints to all validator methods
- Migrate 4 @field_validator decorators
- Migrate 12 @model_validator decorators
- Update validator signatures for Pydantic v2
- Complete TODOs in validate_parameter and validate_code_format
- Run quality checks: black, flake8, mypy all pass
- Validate model instantiation works correctly

Breaking change: Requires Pydantic v2 (installed via requirements.txt)
"
```

---

## Success Criteria

- [ ] All dependencies installed successfully
- [ ] No import errors when importing models module
- [ ] `black` formats code without changes
- [ ] `flake8` reports zero issues
- [ ] `mypy --strict` reports zero errors
- [ ] Quick validation script runs without errors
- [ ] Models instantiate correctly
- [ ] Validators fire on invalid data
- [ ] Git commit created with clean history

---

## Next Steps (After Migration)

1. **Write comprehensive test suite** (`tests/test_models.py`)

   - Test all validators
   - Test all conditional dependencies
   - Target 80%+ coverage

2. **Create transformation functions**

   - `entu_to_muis()` mapper function
   - Dimension parsing helpers
   - Date format converters

3. **Build data pipeline**
   - CSV reader using EntuEksponaat
   - Batch processor
   - CSV writer using MuisMuseaal

---

## Risk Assessment

| Risk                         | Likelihood | Impact | Mitigation                                        |
| ---------------------------- | ---------- | ------ | ------------------------------------------------- |
| Pydantic v2 breaking changes | High       | High   | Follow official migration guide, test thoroughly  |
| Validator logic changes      | Medium     | High   | Careful review of each validator, add tests       |
| Type hint errors             | Medium     | Medium | Run mypy --strict, fix incrementally              |
| TODO decisions unclear       | Low        | Medium | Document options, get user input if needed        |
| Tests reveal bugs            | Medium     | High   | Fix bugs before proceeding to transformation code |

---

## Timeline Estimate

- **Phase 1 (Dependencies)**: 5 minutes
- **Phase 2 (Import fixes)**: 5 minutes
- **Phase 3 (Decorators)**: 20 minutes (15 decorators)
- **Phase 4 (TODOs)**: 10 minutes (decision + implementation)
- **Phase 5 (Quality)**: 10 minutes (black, flake8, mypy)
- **Phase 6 (Validation)**: 10 minutes (quick tests + commit)

**Total**: ~60 minutes

---

## References

- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/2.0/migration/)
- [Pydantic v2 Validators](https://docs.pydantic.dev/2.0/concepts/validators/)
- [Pydantic v2 Model Validators](https://docs.pydantic.dev/2.0/concepts/validators/#model-validators)
