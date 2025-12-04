"""
Identify which ENTU fields contain person/organization names.

This script analyzes the ENTU CSV to find all fields that likely contain
person or organization names, showing sample values for manual review.

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

    Args:
        csv_path: Path to ENTU CSV file

    Returns:
        Dict mapping field names to sample values (up to 20 samples each)
    """
    field_samples: dict[str, list[str]] = defaultdict(list)

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Keywords that indicate person/org fields
        name_keywords = [
            "autor",
            "donator",
            "osaleja",
            "nimi",
            "name",
            "represseeritu",
            "person",
            "organization",
        ]

        for row in reader:
            for field, value in row.items():
                if value and value.strip():
                    # Check if field name suggests it contains names
                    if any(
                        keyword in field.lower() for keyword in name_keywords
                    ):
                        # Avoid duplicates, keep max 20 samples per field
                        if (
                            value not in field_samples[field]
                            and len(field_samples[field]) < 20
                        ):
                            field_samples[field].append(value)

    return dict(field_samples)


def main() -> None:
    """Run field analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze ENTU CSV for person/organization fields"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("output/sample_100_raw.csv"),
        help="Input ENTU CSV file",
    )
    args = parser.parse_args()

    print(f"Analyzing {args.input} for person/org fields...\n")

    fields = analyze_fields(args.input)

    if not fields:
        print("No person/organization fields found.")
        return

    print("=" * 70)
    for field, samples in sorted(fields.items()):
        print(f"\n{field}: ({len(samples)} samples)")
        for sample in samples[:10]:  # Show first 10
            # Truncate long values, show first line if multiline
            display = sample.split("\n")[0][:70]
            print(f"  - {display}")
        if len(samples) > 10:
            print(f"  ... and {len(samples) - 10} more samples")

    print("\n" + "=" * 70)
    print(f"\n✓ Found {len(fields)} potential person/org fields:")
    for field in sorted(fields.keys()):
        print(f"  - {field}")

    print("\nNext step: Update PERSON_ORG_FIELDS in extract_person_names.py")


if __name__ == "__main__":
    main()
