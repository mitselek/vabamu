# Extract Person and Organization Names for MuIS Registry

## Context

**MuIS Import Requirement**: Per MuIS documentation, all person and organization names must exist in the MuIS registry **before** import.

> "Isikute ja asutuste nimed peavad vastama MuISis olemasolevatele. S.t isikud ja asutused peavad olema MuISi osalejatena sisestatud."

This is a **blocking requirement** for Phase 2 production migration. We must extract all unique persons/organizations from ENTU data, send to MuIS stakeholder for registry entry, and receive back MuIS participant IDs.

## Objective

Create a script to extract all unique person and organization names from the ENTU sample data (`output/sample_100_raw.csv`), then extend to handle full dataset when ready.

## Expected Output

A CSV file (`output/person_registry_request.csv`) with this structure:

```csv
entu_field,entu_value,entity_type,frequency,sample_records
donator,"Jõgiaas, Miia",person,15,"020027/117, 020082/000, ..."
autor,"Tamm, Jaan",person,8,"006562/001, ..."
autor,"Eesti Rahva Muuseum",organization,3,"..."
donator,"Kask, Mari",person,2,"..."
osaleja_1,"Unknown Person",person,1,"..."
```

**Columns**:

- `entu_field`: Which ENTU field the name came from (donator, autor, osaleja_1, etc.)
- `entu_value`: The actual name/organization as it appears in ENTU
- `entity_type`: "person" or "organization" (best guess based on format)
- `frequency`: How many records contain this name
- `sample_records`: First 3-5 record IDs where this name appears (for validation)

## Implementation Tasks

### Task 1: Identify Person/Organization Fields in ENTU

Analyze `output/sample_100_raw.csv` to find all fields that contain person or organization names:

**Known fields**:

- `donator` - Donor/giver (Üleandja in MUIS)
- `autor` - Author/creator
- Possibly: `osaleja_*` fields (participants in events)
- Possibly: Organization fields (need to identify)

**Script**: `scripts/analyze_person_fields.py`

```python
"""
Identify which ENTU fields contain person/organization names.

Usage:
    python -m scripts.analyze_person_fields --input output/sample_100_raw.csv
"""

import csv
from pathlib import Path
from collections import defaultdict
import argparse


def analyze_fields(csv_path: Path) -> dict[str, list[str]]:
    """
    Scan CSV to find fields that likely contain person/org names.

    Returns:
        Dict mapping field names to sample values
    """
    field_samples = defaultdict(list)

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            for field, value in row.items():
                if value and value.strip():
                    # Heuristic: likely person/org if contains name-like patterns
                    if any(keyword in field.lower() for keyword in
                           ['autor', 'donator', 'osaleja', 'nimi', 'name']):
                        if value not in field_samples[field]:
                            field_samples[field].append(value)

    return field_samples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()

    print(f"Analyzing {args.input} for person/org fields...\n")

    fields = analyze_fields(args.input)

    for field, samples in sorted(fields.items()):
        print(f"\n{field}:")
        for sample in samples[:5]:  # Show first 5
            print(f"  - {sample[:80]}")

    print(f"\n✓ Found {len(fields)} potential person/org fields")


if __name__ == '__main__':
    main()
```

**Output**: List of fields to process in Task 2

---

### Task 2: Extract Unique Names

Create extraction script that processes identified fields and generates the registry request CSV.

**Script**: `scripts/extract_person_names.py`

```python
"""
Extract all unique person and organization names from ENTU data.

This generates a CSV file for MuIS stakeholder to process:
1. Add persons/orgs to MuIS registry
2. Return MuIS participant IDs
3. We use IDs in final conversion

Usage:
    python -m scripts.extract_person_names \
        --input output/sample_100_raw.csv \
        --output output/person_registry_request.csv
"""

import csv
from pathlib import Path
from collections import defaultdict
from typing import Literal
import argparse


# Fields that contain person/organization names
PERSON_ORG_FIELDS = [
    'donator',
    'autor',
    # Add more after Task 1 analysis
]


def classify_entity(name: str) -> Literal['person', 'organization']:
    """
    Classify whether name is a person or organization.

    Heuristics:
    - "Lastname, Firstname" pattern → person
    - Contains "Museum", "Institute", "OÜ", "AS" → organization
    - All caps → likely organization
    - Otherwise → person (default)

    Args:
        name: The name string

    Returns:
        'person' or 'organization'
    """
    name_lower = name.lower()

    # Organization indicators
    org_keywords = ['muuseum', 'museum', 'instituut', 'institute',
                    'oü', 'as', 'sa', 'mtü', 'fond', 'arhiiv']

    if any(keyword in name_lower for keyword in org_keywords):
        return 'organization'

    # Person pattern: "Lastname, Firstname"
    if ',' in name and len(name.split(',')) == 2:
        return 'person'

    # Default to person
    return 'person'


def extract_persons(csv_path: Path) -> list[dict]:
    """
    Extract unique person/org names from ENTU CSV.

    Returns:
        List of dicts with: entu_field, entu_value, entity_type,
                            frequency, sample_records
    """
    # Track: (field, name) → [record_ids]
    name_occurrences = defaultdict(list)

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            record_id = row.get('code', row.get('_id', ''))

            for field in PERSON_ORG_FIELDS:
                value = row.get(field, '').strip()
                if value:
                    name_occurrences[(field, value)].append(record_id)

    # Build output records
    results = []
    for (field, name), record_ids in sorted(name_occurrences.items()):
        results.append({
            'entu_field': field,
            'entu_value': name,
            'entity_type': classify_entity(name),
            'frequency': len(record_ids),
            'sample_records': ', '.join(record_ids[:5])  # First 5
        })

    # Sort by frequency (most common first)
    results.sort(key=lambda x: x['frequency'], reverse=True)

    return results


def write_registry_request(results: list[dict], output_path: Path) -> None:
    """Write results to CSV for MuIS stakeholder."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['entu_field', 'entu_value', 'entity_type',
                      'frequency', 'sample_records', 'muis_participant_id', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for result in results:
            # Add empty columns for MuIS to fill
            result['muis_participant_id'] = ''
            result['notes'] = ''
            writer.writerow(result)


def main():
    parser = argparse.ArgumentParser(
        description='Extract person/org names for MuIS registry'
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path('output/sample_100_raw.csv'),
        help='Input ENTU CSV'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('output/person_registry_request.csv'),
        help='Output CSV for MuIS stakeholder'
    )

    args = parser.parse_args()

    print(f"Extracting persons/orgs from {args.input}...")
    results = extract_persons(args.input)

    print(f"\nExtracted {len(results)} unique persons/organizations:")

    # Summary stats
    persons = sum(1 for r in results if r['entity_type'] == 'person')
    orgs = sum(1 for r in results if r['entity_type'] == 'organization')
    total_occurrences = sum(r['frequency'] for r in results)

    print(f"  Persons: {persons}")
    print(f"  Organizations: {orgs}")
    print(f"  Total occurrences: {total_occurrences}")

    print(f"\nTop 10 most frequent:")
    for result in results[:10]:
        print(f"  {result['frequency']:3d}x  {result['entu_value'][:50]:50s}  ({result['entity_type']})")

    print(f"\nWriting to {args.output}")
    write_registry_request(results, args.output)

    print(f"\n✓ Complete! Next steps:")
    print(f"  1. Review {args.output}")
    print(f"  2. Send to MuIS stakeholder for registry entry")
    print(f"  3. Receive back file with muis_participant_id column filled")
    print(f"  4. Use in Phase 1 person_mapper.py")


if __name__ == '__main__':
    main()
```

---

### Task 3: Write Tests

**Test file**: `tests/test_extract_person_names.py`

```python
"""Tests for person name extraction."""

import csv
from pathlib import Path
import pytest
from scripts.extract_person_names import (
    classify_entity,
    extract_persons,
)


class TestClassifyEntity:
    def test_person_lastname_firstname_format(self):
        assert classify_entity("Tamm, Jaan") == "person"
        assert classify_entity("Jõgiaas, Miia") == "person"

    def test_organization_with_museum_keyword(self):
        assert classify_entity("Eesti Rahva Muuseum") == "organization"
        assert classify_entity("Tartu Ülikooli Museum") == "organization"

    def test_organization_with_company_suffix(self):
        assert classify_entity("Kultuuripärandi OÜ") == "organization"
        assert classify_entity("Muinsuskaitse AS") == "organization"

    def test_default_to_person(self):
        assert classify_entity("Unknown Entity") == "person"


class TestExtractPersons:
    @pytest.fixture
    def sample_csv(self, tmp_path: Path) -> Path:
        csv_path = tmp_path / "sample.csv"
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['code', 'donator', 'autor'])
            writer.writeheader()
            writer.writerow({'code': '001', 'donator': 'Tamm, Jaan', 'autor': ''})
            writer.writerow({'code': '002', 'donator': 'Tamm, Jaan', 'autor': 'Kask, Mari'})
            writer.writerow({'code': '003', 'donator': '', 'autor': 'Eesti Rahva Muuseum'})
        return csv_path

    def test_extract_unique_names(self, sample_csv: Path):
        results = extract_persons(sample_csv)

        # Should have 3 unique entities
        assert len(results) == 3

        # Check frequencies
        tamm_record = next(r for r in results if r['entu_value'] == 'Tamm, Jaan')
        assert tamm_record['frequency'] == 2
        assert tamm_record['entity_type'] == 'person'

        kask_record = next(r for r in results if r['entu_value'] == 'Kask, Mari')
        assert kask_record['frequency'] == 1

        museum_record = next(r for r in results if 'Muuseum' in r['entu_value'])
        assert museum_record['entity_type'] == 'organization'

    def test_sample_records_included(self, sample_csv: Path):
        results = extract_persons(sample_csv)
        tamm_record = next(r for r in results if r['entu_value'] == 'Tamm, Jaan')

        # Should include both record IDs
        assert '001' in tamm_record['sample_records']
        assert '002' in tamm_record['sample_records']
```

---

### Task 4: Run on Sample Data

Execute on 100-sample dataset:

```bash
# Step 1: Analyze fields
python -m scripts.analyze_person_fields --input output/sample_100_raw.csv

# Step 2: Extract names
python -m scripts.extract_person_names \
    --input output/sample_100_raw.csv \
    --output output/person_registry_request_sample.csv

# Step 3: Review output
cat output/person_registry_request_sample.csv | head -20
```

**Expected outcome**:

- CSV with 10-30 unique persons/organizations from sample
- Entity types classified (person vs organization)
- Frequency counts show which names are most common
- Sample record IDs for validation

---

### Task 5: Documentation

Update `docs/FIELD_MAPPINGS.md` with findings:

````markdown
## Person/Organization Name Extraction

### Fields Containing Names

| ENTU Field  | MUIS Field(s)           | Entity Type | Notes          |
| ----------- | ----------------------- | ----------- | -------------- |
| `donator`   | `Üleandja`, `Osaleja 2` | Person/Org  | Donor/giver    |
| `autor`     | `Osaleja 1`             | Person/Org  | Author/creator |
| [others...] | [...]                   | [...]       | [...]          |

### MuIS Registry Coordination Process

1. **Extract**: Run `scripts/extract_person_names.py` on full dataset
2. **Review**: Validate classification (person vs organization)
3. **Submit**: Send `person_registry_request.csv` to MuIS stakeholder
4. **Wait**: MuIS adds entities to registry (1-2 weeks)
5. **Receive**: Get back CSV with `muis_participant_id` column filled
6. **Implement**: Use IDs in `person_mapper.py` lookup table

### Sample Output (from 100 records)

```csv
entu_field,entu_value,entity_type,frequency,sample_records
donator,"Jõgiaas, Miia",person,15,"020027/117, 020082/000, ..."
autor,"Eesti Rahva Muuseum",organization,8,"006562/001, ..."
```
````

---

## Acceptance Criteria

- [ ] `scripts/analyze_person_fields.py` identifies all person/org fields
- [ ] `scripts/extract_person_names.py` extracts unique names
- [ ] Entity classification (person vs org) is 90%+ accurate on review
- [ ] Output CSV includes all required columns
- [ ] Frequency counts are correct
- [ ] Sample record IDs allow validation
- [ ] 8+ tests written and passing
- [ ] Runs successfully on 100-sample dataset
- [ ] Documentation updated in `FIELD_MAPPINGS.md`
- [ ] Ready to run on full 80K dataset in Phase 1

## Timeline

**Estimated**: 2-3 hours

- Task 1 (Field analysis): 30 minutes
- Task 2 (Extraction script): 1 hour
- Task 3 (Tests): 30 minutes
- Task 4 (Execution & validation): 30 minutes
- Task 5 (Documentation): 30 minutes

## Dependencies

- Requires: `output/sample_100_raw.csv` (already exists)
- Blocks: Phase 1 person_mapper.py implementation
- Blocks: Phase 2 production migration (MuIS import requirement)

## Notes

**CRITICAL**: This is a **blocking requirement** for MuIS import. Per MuIS documentation, all persons and organizations must be pre-registered in the MuIS participant registry before import will succeed.

The output CSV from this task will be sent to the MuIS stakeholder, who will:

1. Add entities to MuIS registry
2. Generate MuIS participant IDs
3. Return the CSV with IDs filled in

We then use these IDs in the person_mapper to ensure import compliance.

## References

- MuIS documentation: "Isikute ja asutuste nimed peavad vastama MuISis olemasolevatele"
- Phase 0.5 analysis: 100% of records potentially affected by person fields
- Cost estimate: `docs/PROJECT_SCOPE_AND_ESTIMATE.md` (Phase 1, task 1)
