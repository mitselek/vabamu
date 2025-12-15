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


# Fields that contain person/organization names (from full dataset analysis)
PERSON_ORG_FIELDS = [
    "autor",        # Creators/authors
    "donator",      # Donors
    "represseeritu_o",  # Repressed persons (victims)
    "represseeritu_t",  # Repressed persons (perpetrators/related)
]


def parse_multiline_names(text: str) -> list[str]:
    """
    Parse multiline name field into individual names.

    Some ENTU fields contain multiple names separated by newlines.
    Example: "Tamm, Jaan\nKask, Mari\nLepp, Peeter"

    Args:
        text: Raw text from ENTU field

    Returns:
        List of individual names (whitespace trimmed, empty lines removed)
    """
    lines = text.replace("\r\n", "\n").split("\n")
    return [line.strip() for line in lines if line.strip()]


def classify_entity(name: str) -> Literal["person", "organization"]:
    """
    Classify whether name is a person or organization.

    Heuristics:
    - "Lastname, Firstname" pattern → person (checked first)
    - Contains "Museum", "Institute", "OÜ", "AS" → organization
    - All caps → likely organization
    - Otherwise → person (default)

    Args:
        name: The name string

    Returns:
        'person' or 'organization'
    """
    # Person pattern first: "Lastname, Firstname" or "Lastname, Firstname, Middlename"
    # This prevents false matches like "Jõgiaas" matching "as"
    if "," in name:
        return "person"

    name_lower = name.lower()

    # Organization indicators (Estonian and English)
    # Must have word boundaries to avoid matching in surnames (e.g., "Saks", "Saul")
    org_keywords = [
        "muuseum",
        "museum",
        "instituut",
        "institute",
        " mtü",  # NGO (must have space before)
        "fond",
        "arhiiv",
        "archive",
        "ülikool",
        "university",
    ]
    
    # Company suffixes must be at word boundaries or end of string
    # Check these separately to avoid false matches
    org_suffixes = [" oü", " as", " sa"]
    
    # Check general org keywords
    if any(keyword in name_lower for keyword in org_keywords):
        return "organization"
    
    # Check company suffixes (must be at end or followed by non-letter)
    for suffix in org_suffixes:
        # Check if suffix is at end of string
        if name_lower.endswith(suffix):
            return "organization"
        # Check if suffix is followed by space or punctuation
        if suffix + " " in name_lower or suffix + "," in name_lower:
            return "organization"

    # Default to person (most common case)
    return "person"


def extract_persons(csv_path: Path) -> list[dict[str, str | int]]:
    """
    Extract unique person/org names from ENTU CSV.

    Args:
        csv_path: Path to ENTU CSV file

    Returns:
        List of dicts with: entu_field, entu_value, entity_type,
                            frequency, sample_records
    """
    # Track: (field, name) → [record_ids]
    name_occurrences: dict[tuple[str, str], list[str]] = defaultdict(list)

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            record_id = row.get("code", row.get("_id", ""))

            for field in PERSON_ORG_FIELDS:
                value = row.get(field, "").strip()
                if value:
                    # Parse multiline names (some fields have multiple names)
                    names = parse_multiline_names(value)

                    for name in names:
                        name_occurrences[(field, name)].append(record_id)

    # Build output records
    results: list[dict[str, str | int]] = []
    for (field, name), record_ids in sorted(name_occurrences.items()):
        results.append(
            {
                "entu_field": field,
                "entu_value": name,
                "entity_type": classify_entity(name),
                "frequency": len(record_ids),
                "sample_records": ", ".join(record_ids[:5]),  # First 5
            }
        )

    # Sort by frequency (most common first)
    results.sort(key=lambda x: int(x["frequency"]), reverse=True)

    return results


def write_registry_request(
    results: list[dict[str, str | int]], output_path: Path
) -> None:
    """
    Write results to CSV for MuIS stakeholder.

    Adds empty columns for MuIS to fill in:
    - muis_participant_id: To be filled by MuIS after registry entry
    - notes: For any comments or clarifications

    Args:
        results: List of extracted person/org records
        output_path: Path to output CSV file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "entu_field",
            "entu_value",
            "entity_type",
            "frequency",
            "sample_records",
            "muis_participant_id",
            "notes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for result in results:
            # Add empty columns for MuIS to fill
            result["muis_participant_id"] = ""
            result["notes"] = ""
            writer.writerow(result)


def main() -> None:
    """Run person/org extraction."""
    parser = argparse.ArgumentParser(
        description="Extract person/org names for MuIS registry"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("output/sample_100_raw.csv"),
        help="Input ENTU CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/person_registry_request.csv"),
        help="Output CSV for MuIS stakeholder",
    )

    args = parser.parse_args()

    print(f"Extracting persons/orgs from {args.input}...")
    results = extract_persons(args.input)

    print(f"\nExtracted {len(results)} unique persons/organizations:")

    # Summary stats
    persons = sum(1 for r in results if r["entity_type"] == "person")
    orgs = sum(1 for r in results if r["entity_type"] == "organization")
    total_occurrences = sum(int(r["frequency"]) for r in results)

    print(f"  Persons: {persons}")
    print(f"  Organizations: {orgs}")
    print(f"  Total occurrences: {total_occurrences}")

    print(f"\nTop 10 most frequent:")
    for result in results[:10]:
        freq = int(result["frequency"])
        name = str(result["entu_value"])[:50]
        entity = result["entity_type"]
        print(f"  {freq:3d}x  {name:50s}  ({entity})")

    print(f"\nWriting to {args.output}")
    write_registry_request(results, args.output)

    print(f"\n✓ Complete! Next steps:")
    print(f"  1. Review {args.output}")
    print(f"  2. Send to MuIS stakeholder for registry entry")
    print(
        f"  3. Receive back file with muis_participant_id column filled"
    )
    print(f"  4. Use IDs in person_mapper.py")


if __name__ == "__main__":
    main()
