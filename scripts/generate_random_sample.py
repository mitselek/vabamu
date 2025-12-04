#!/usr/bin/env python3
"""Generate a random sample of ENTU records and convert to MUIS format.

This script:
1. Reads all records from entust/eksponaat.csv
2. Selects a random sample of N records
3. Saves the raw sample to output/random_N_raw.csv
4. Converts the sample to MUIS format using the full pipeline
5. Saves the MUIS output to output/random_N_muis.csv

Usage:
    python scripts/generate_random_sample.py [--count N] [--seed S]
    
Arguments:
    --count N : Number of random records to sample (default: 100)
    --seed S  : Random seed for reproducibility (default: random)
"""

import argparse
import csv
import random
import sys
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Project imports
from scripts.convert_row import convert_row
from scripts.muis_writer import write_muis_csv


def load_entu_records(input_path: Path) -> list[dict[str, str]]:
    """Load all records from ENTU eksponaat.csv."""
    records: list[dict[str, str]] = []
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)  # Uses comma delimiter (default)
        for row in reader:
            # Filter out any None keys that might appear in malformed rows
            clean_row: dict[str, str] = {k: v for k, v in row.items() if k is not None}
            records.append(clean_row)
    return records


def save_sample_raw(records: list[dict[str, str]], output_path: Path) -> None:
    """Save raw ENTU sample to CSV."""
    if not records:
        return
    
    fieldnames = list(records[0].keys())
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)  # Uses comma delimiter (default)
        writer.writeheader()
        writer.writerows(records)


def convert_sample(records: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Convert ENTU records to MUIS format using orchestrator."""
    converted: list[dict[str, Any]] = []
    errors: list[str] = []
    
    for i, record in enumerate(records, 1):
        try:
            result = convert_row(record)
            converted.append(result)
        except Exception as e:
            errors.append(f"Record {i} (code: {record.get('code', 'unknown')}): {e}")
    
    if errors:
        print(f"\n⚠️  {len(errors)} conversion errors:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"   - {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more errors")
    
    return converted


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate random sample of ENTU records and convert to MUIS"
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=100,
        help="Number of random records to sample (default: 100)"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    args = parser.parse_args()
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    input_path = project_root / "entust" / "eksponaat.csv"
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)
    
    raw_output = output_dir / f"random_{args.count}_raw.csv"
    muis_output = output_dir / f"random_{args.count}_muis.csv"
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        print(f"🎲 Using random seed: {args.seed}")
    
    # Load all records
    print(f"📖 Loading records from {input_path}...")
    all_records = load_entu_records(input_path)
    print(f"   Found {len(all_records):,} total records")
    
    # Sample random records
    sample_size = min(args.count, len(all_records))
    print(f"\n🎯 Selecting {sample_size} random records...")
    sample = random.sample(all_records, sample_size)
    
    # Save raw sample
    print(f"💾 Saving raw sample to {raw_output}...")
    save_sample_raw(sample, raw_output)
    
    # Convert to MUIS format
    print(f"\n🔄 Converting to MUIS format...")
    converted = convert_sample(sample)
    print(f"   Successfully converted: {len(converted)} records")
    
    # Save MUIS output
    print(f"💾 Saving MUIS output to {muis_output}...")
    write_muis_csv(converted, muis_output)
    
    print(f"\n✅ Done!")
    print(f"   Raw sample: {raw_output}")
    print(f"   MUIS output: {muis_output}")


if __name__ == "__main__":
    main()
