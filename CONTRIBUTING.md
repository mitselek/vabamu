# Contributing to Vabamu ENTU → MUIS Migration

## Overview

This project follows **Ada's TDD-first 8-step workflow** with strict quality gates. All code must pass black, flake8, mypy, and pytest before being considered complete.

## Ada's 8-Step Workflow

### Step 1: Understand Requirements

- Read task description carefully
- Identify inputs, outputs, business rules
- Ask clarifying questions if ambiguous
- Document assumptions

**Example**: For "parse dimensions field"

- Input: String like "ø50;62x70"
- Output: List of Dimension objects (parameter, unit, value)
- Business rule: Max 4 measurements per object
- Edge cases: Unparseable formats, missing units

---

### Step 2: Write Tests FIRST (TDD)

**Critical**: Tests before implementation!

Create test file: `tests/test_<component>.py`

```python
import pytest
from scripts.dimension_parser import parse_dimensions, Dimension

def test_parse_diameter_only():
    """Parse diameter notation (ø50)."""
    result = parse_dimensions("ø50")
    assert len(result) == 1
    assert result[0] == Dimension("läbimõõt", "mm", 50)

def test_parse_height_width():
    """Parse HxW format (62x70)."""
    result = parse_dimensions("62x70")
    assert len(result) == 2
    assert result[0] == Dimension("kõrgus", "mm", 62)
    assert result[1] == Dimension("laius", "mm", 70)

def test_parse_combined_dimensions():
    """Parse combined dimensions (ø50;62x70)."""
    result = parse_dimensions("ø50;62x70")
    assert len(result) == 3
    assert result[0].parameter == "läbimõõt"
    assert result[1].parameter == "kõrgus"
    assert result[2].parameter == "laius"

def test_parse_unparseable_returns_empty():
    """Unparseable dimensions return empty list."""
    result = parse_dimensions("väga suur")
    assert result == []

def test_parse_max_four_measurements():
    """Max 4 measurements enforced."""
    result = parse_dimensions("ø50;62x70x80;90")
    assert len(result) == 4
```

**Test Coverage Requirements**:

- ✅ Happy path (typical input)
- ✅ Edge cases (empty, null, malformed)
- ✅ Boundary conditions (max values, limits)
- ✅ Error handling (exceptions, fallbacks)

---

### Step 3: Create Implementation File

Implement to make tests pass:

```python
# scripts/dimension_parser.py
from dataclasses import dataclass
from typing import List
import re

@dataclass
class Dimension:
    """Represents a single measurement (parameter, unit, value)."""
    parameter: str  # e.g., "läbimõõt", "kõrgus"
    unit: str       # e.g., "mm", "cm"
    value: float    # e.g., 50, 62.5

def parse_dimensions(dim_str: str) -> List[Dimension]:
    """Parse ENTU dimension string to MUIS format.

    Args:
        dim_str: ENTU dimension string (e.g., "ø50;62x70")

    Returns:
        List of Dimension objects (max 4)

    Examples:
        >>> parse_dimensions("ø50")
        [Dimension('läbimõõt', 'mm', 50)]

        >>> parse_dimensions("62x70")
        [Dimension('kõrgus', 'mm', 62), Dimension('laius', 'mm', 70)]
    """
    if not dim_str or not isinstance(dim_str, str):
        return []

    results = []

    # Parse diameter: "ø50"
    diameter_match = re.search(r'ø(\d+(?:\.\d+)?)', dim_str)
    if diameter_match:
        results.append(Dimension("läbimõõt", "mm", float(diameter_match.group(1))))

    # Parse HxW: "62x70"
    hw_match = re.search(r'(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)', dim_str)
    if hw_match:
        results.append(Dimension("kõrgus", "mm", float(hw_match.group(1))))
        results.append(Dimension("laius", "mm", float(hw_match.group(2))))

    # Max 4 measurements
    return results[:4]
```

---

### Step 4: Run Tests

```bash
pytest tests/test_dimension_parser.py -v
```

**Expected Output** (all pass):

```text
tests/test_dimension_parser.py::test_parse_diameter_only PASSED
tests/test_dimension_parser.py::test_parse_height_width PASSED
tests/test_dimension_parser.py::test_parse_combined_dimensions PASSED
tests/test_dimension_parser.py::test_parse_unparseable_returns_empty PASSED
tests/test_dimension_parser.py::test_parse_max_four_measurements PASSED

===================== 5 passed in 0.05s =====================
```

**If tests fail**: Fix implementation, re-run tests. DO NOT proceed until all tests pass.

---

### Step 5: Quality Checks

Run ALL quality tools:

#### Step 5.1: Black (Code Formatting)

```bash
black scripts/ tests/
```

**Expected**: "All done! ✨ 🍰 ✨ N files left unchanged."

If changes made, review and commit formatting.

#### Step 5.2: Flake8 (Linting)

```bash
flake8 scripts/ tests/ --max-line-length=100
```

**Expected**: No output (all checks pass)

**Common issues**:

- `E501`: Line too long → break into multiple lines
- `F841`: Unused variable → remove or use
- `E302`: Expected 2 blank lines → add spacing

#### Step 5.3: Mypy (Type Checking)

```bash
mypy scripts/ --strict
```

**Expected**: "Success: no issues found in N source files"

**Common issues**:

- Missing type hints → add annotations
- Incompatible types → fix type errors
- Untyped function → add return type

#### Step 5.4: Pytest with Coverage

```bash
pytest tests/ -v --cov=scripts --cov-report=term-missing
```

**Target**: ≥80% coverage for all modules

**Example output**:

```text
---------- coverage: platform linux, python 3.12.3 -----------
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
scripts/dimension_parser.py    25      2    92%   45-46
---------------------------------------------------------
TOTAL                          25      2    92%
```

If coverage <80%, add more tests for uncovered lines.

#### Step 5.5: Integration Test (if applicable)

For components that interact with others, run integration test:

```bash
pytest tests/integration/ -v
```

#### Step 5.6: Problems Panel Verification ⚠️ **CRITICAL**

**Check VS Code Problems panel BEFORE marking task complete:**

1. Open VS Code Problems panel (Ctrl+Shift+M or Cmd+Shift+M)
2. Verify: **0 errors, 0 warnings** (zero tolerance for false positives)
3. If warnings exist, suppress using appropriate comments:

**Common False Positives & Suppression**:

```python
# Pylance + Pydantic compatibility issues
model = EntuEksponaat(number="123")  # type: ignore[call-arg]

# Unused test variables (intentional for readability)
def test_parse_dimensions():
    result = parse_dimensions("ø50")  # noqa: F841
    # ... rest of test
```

**Suppression Guidelines**:

- `# type: ignore[call-arg]` - Pydantic model instantiation warnings
- `# noqa: F841` - Intentionally unused test variables
- `# type: ignore[assignment]` - Type inference mismatches
- Document WHY you're suppressing in comment

**Example**:

```python
# Pylance incorrectly flags Pydantic v2 model_validate as error
obj = EntuEksponaat.model_validate(data)  # type: ignore[call-arg]
```

**NEVER suppress real errors!** Only false positives that:

1. You've verified are incorrect
2. Have a documented explanation
3. Are specific (not broad # type: ignore)

---

### Step 6: Document Output Format

Add output message showing completion:

```markdown
**Task Complete**: Parse dimensions field

**Implementation**:

- File: scripts/dimension_parser.py
- Tests: tests/test_dimension_parser.py (5 tests, 100% pass)
- Coverage: 92%

**Quality Checks**:

- ✅ Black: Formatted
- ✅ Flake8: No issues
- ✅ Mypy: Type-safe
- ✅ Pytest: 5/5 tests pass
- ✅ Coverage: 92% (target: 80%)
- ✅ Problems Panel: 0 errors (0 expected)

**Key Functions**:

- `parse_dimensions(dim_str: str) -> List[Dimension]`
- Supports: diameter (ø), HxW format, combined
- Max 4 measurements enforced

**Edge Cases Handled**:

- Empty/null input → empty list
- Unparseable format → empty list
- More than 4 dimensions → truncate to 4
```

---

### Step 7: Git Commit

Commit with descriptive message:

```bash
git add scripts/dimension_parser.py tests/test_dimension_parser.py
git commit -m "feat: Add dimension parser with TDD

- Parse diameter notation (ø50)
- Parse HxW format (62x70)
- Parse combined dimensions (ø50;62x70)
- Enforce max 4 measurements
- 5 tests, 92% coverage
- All quality checks pass"
```

**Commit Message Format**:

```text
<type>: <Short summary (50 chars)>

<Detailed description>
- Bullet points for key changes
- Test coverage and quality checks
- Edge cases handled

<Optional footer with issue reference>
```

**Types**: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`

---

### Step 8: Mark Task Complete

Update TODO list or task tracker:

```markdown
- [x] Parse dimensions field (Step 2.3)
  - ✅ Tests written (5 tests)
  - ✅ Implementation complete
  - ✅ Quality checks pass
  - ✅ 92% coverage
  - ✅ Committed
```

---

## Quality Requirements

### Test Coverage

- **Minimum**: 80% line coverage
- **Target**: 90%+ coverage
- **Critical paths**: 100% coverage (e.g., data validation, number parsing)

**Check coverage**:

```bash
pytest tests/ --cov=scripts --cov-report=html
# Open htmlcov/index.html to see detailed report
```

### Code Style

- **Black**: 100% formatted (zero tolerance)
- **Flake8**: Zero warnings (max-line-length=100)
- **Mypy**: Strict mode, zero errors

### Type Hints

All functions must have type hints:

```python
# Good
def parse_number(entu_number: str) -> NumberComponents:
    """Parse ENTU number to MUIS components."""
    ...

# Bad (no type hints)
def parse_number(entu_number):
    ...
```

### Documentation

- **Module docstrings**: Purpose, examples
- **Function docstrings**: Args, returns, examples
- **Complex logic**: Inline comments explaining WHY (not WHAT)

**Example**:

```python
def parse_dimensions(dim_str: str) -> List[Dimension]:
    """Parse ENTU dimension string to MUIS format.

    Supports multiple formats:
    - Diameter: "ø50" → [(läbimõõt, mm, 50)]
    - HxW: "62x70" → [(kõrgus, mm, 62), (laius, mm, 70)]
    - Combined: "ø50;62x70" → 3 measurements

    Args:
        dim_str: ENTU dimension string (may contain ø, x, ;)

    Returns:
        List of Dimension objects (max 4, in order found)

    Examples:
        >>> parse_dimensions("ø50")
        [Dimension('läbimõõt', 'mm', 50)]

        >>> parse_dimensions("62x70")
        [Dimension('kõrgus', 'mm', 62), Dimension('laius', 'mm', 70)]
    """
    # Implementation using regex for robust parsing
    # (not simple split, handles malformed input)
    ...
```

---

## Testing Standards

### Unit Test Structure

```python
import pytest
from scripts.my_module import my_function

class TestMyFunction:
    """Unit tests for my_function."""

    def test_happy_path(self):
        """Test typical valid input."""
        result = my_function("valid_input")
        assert result == expected_output

    def test_edge_case_empty(self):
        """Test empty input handling."""
        result = my_function("")
        assert result == []

    def test_edge_case_null(self):
        """Test None input handling."""
        result = my_function(None)
        assert result == []

    def test_error_invalid_format(self):
        """Test error handling for invalid format."""
        with pytest.raises(ValueError):
            my_function("invalid_format")
```

### Fixture Usage

For reusable test data:

```python
import pytest

@pytest.fixture
def sample_entu_data():
    """Sample ENTU eksponaat record for testing."""
    return {
        "number": "006562/001",
        "nimetus": "Medalikomplekt",
        "date_str": "2002-12-22",
        "dimensions": "ø50"
    }

def test_with_fixture(sample_entu_data):
    """Test using fixture data."""
    result = parse_eksponaat(sample_entu_data)
    assert result.number == "006562/001"
```

### Parametrized Tests

For testing multiple inputs:

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("ø50", [Dimension("läbimõõt", "mm", 50)]),
    ("62x70", [Dimension("kõrgus", "mm", 62), Dimension("laius", "mm", 70)]),
    ("", []),
    (None, []),
])
def test_parse_dimensions_multiple(input, expected):
    """Test dimension parsing with various inputs."""
    result = parse_dimensions(input)
    assert result == expected
```

---

## Error Handling Best Practices

### Validation Errors

Use Pydantic for data validation:

```python
from pydantic import BaseModel, validator

class EntuEksponaat(BaseModel):
    number: str
    nimetus: str

    @validator('number')
    def validate_number_format(cls, v):
        """Validate ENTU number format (NNNNNN/NNN)."""
        if not re.match(r'^\d{6}/\d{3}$', v):
            raise ValueError(f"Invalid number format: {v}")
        return v
```

### Parsing Errors

Log and continue (don't crash):

```python
import logging

logger = logging.getLogger(__name__)

def parse_dimensions(dim_str: str) -> List[Dimension]:
    """Parse dimensions with error logging."""
    try:
        # Parsing logic
        return results
    except Exception as e:
        logger.warning(f"Failed to parse dimensions '{dim_str}': {e}")
        return []  # Return empty, don't crash
```

### Error Reporting

Generate error report for QA review:

```python
# Collect errors during processing
errors = []

for record in records:
    try:
        process_record(record)
    except ValidationError as e:
        errors.append({
            "record_id": record.id,
            "error": str(e),
            "data": record.dict()
        })

# Write error report
write_error_report("errors.csv", errors)
```

---

## Git Workflow

### Branch Strategy

```bash
# Main branch: main (protected)
# Feature branches: feat/<task-name>
# Fix branches: fix/<issue-name>

git checkout -b feat/dimension-parser
# ... implement, test, commit
git push origin feat/dimension-parser
# Create pull request (if team review needed)
```

### Commit Frequency

- Commit after EACH completed step (test + implementation + quality)
- Use descriptive commit messages
- Don't commit broken code (all tests must pass)

### Commit Message Examples

```text
Good:
feat: Add dimension parser with regex support

- Parse diameter (ø), HxW, and combined formats
- Max 4 measurements enforced
- 5 tests, 92% coverage
- All quality checks pass

Bad:
Update code
```

---

## Code Review Checklist

Before marking task complete, verify:

- [ ] All tests pass (pytest)
- [ ] Coverage ≥80% (pytest --cov)
- [ ] Black formatted (black scripts/ tests/)
- [ ] Flake8 clean (flake8 scripts/ tests/)
- [ ] Mypy clean (mypy scripts/ --strict)
- [ ] **Problems panel: 0 errors, 0 warnings (false positives suppressed)**
- [ ] Docstrings complete (module, functions)
- [ ] Type hints on all functions
- [ ] Edge cases tested
- [ ] Error handling implemented
- [ ] Committed with descriptive message
- [ ] Task marked complete in tracker

---

## Tools & Commands Reference

### Setup

```bash
# Activate environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Development

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=scripts --cov-report=term-missing

# Format code
black scripts/ tests/

# Lint code
flake8 scripts/ tests/ --max-line-length=100

# Type check
mypy scripts/ --strict
```

### Debugging

```bash
# Run single test file
pytest tests/test_dimension_parser.py -v

# Run single test function
pytest tests/test_dimension_parser.py::test_parse_diameter_only -v

# Print output during tests
pytest tests/ -v -s

# Drop into debugger on failure
pytest tests/ --pdb
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Writing implementation before tests

**Problem**: No test coverage, bugs slip through

**Solution**: ALWAYS write tests first (TDD)

### Pitfall 2: Ignoring quality checks

**Problem**: Code style inconsistent, type errors in production

**Solution**: Run all quality checks (Step 5) before marking complete

### Pitfall 3: Skipping edge case testing

**Problem**: Crashes on real data (null, empty, malformed)

**Solution**: Test happy path + edge cases + error conditions

### Pitfall 4: Committing broken code

**Problem**: Main branch broken, blocks other work

**Solution**: Never commit if tests fail or quality checks fail

### Pitfall 5: Poor test names

**Problem**: Hard to understand what failed

**Solution**: Use descriptive test names:

```python
# Good
def test_parse_diameter_returns_diameter_measurement():
    ...

# Bad
def test_parse():
    ...
```

### Pitfall 6: Leaving false positives in Problems panel

**Problem**: Real errors hidden by noise, reduced code quality confidence

**Solution**:

- Suppress false positives with specific comments (`# type: ignore[call-arg]`)
- Document WHY you're suppressing
- Verify 0 errors in Problems panel before marking complete (Step 5.6)

---

## Getting Help

### Documentation

- [Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md) - Phase-by-phase plan
- [Field Mappings](docs/FIELD_MAPPINGS.md) - ENTU → MUIS field reference
- [Architecture](docs/ARCHITECTURE.md) - System design and components

### Project Contacts

- **Project Lead**: Liisi Ploom (<liisi.ploom@vabamu.ee>) - Business requirements
- **Technical Partner**: Argo Roots (<argo@roots.ee>) - Technical questions

---

**Document Status**: Complete  
**Last Updated**: 2025-12-03  
**Owner**: Ada (workflow author)
