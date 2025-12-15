#!/usr/bin/env python3
"""Process specific collections for testing.

Usage:
    python scripts/process_collections.py Digidokumendikogu Militaaria
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import csv
from typing import Any
from tqdm import tqdm

from scripts.convert_row import convert_row
from scripts.csv_to_excel import csv_to_excel
from scripts.muis_writer import write_muis_csv


def process_collection(collection_name: str, output_dir: Path) -> None:
    """Process a single collection."""
    
    print(f"\n{'='*70}")
    print(f"Processing: {collection_name}")
    print(f"{'='*70}")
    
    # Read all records
    input_file = Path("entust/eksponaat.csv")
    records: list[dict[str, Any]] = []
    
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in tqdm(reader, desc=f"Reading {collection_name}", unit=" records"):
            kuuluvus = row.get("kuuluvus", "").strip()
            if kuuluvus == collection_name:
                records.append(row)
    
    if not records:
        print(f"⚠️  No records found for collection: {collection_name}")
        return
    
    print(f"Found {len(records):,} records")
    
    # Convert records
    converted_rows: list[dict[str, Any]] = []
    success_count = 0
    error_count = 0
    
    for row in tqdm(records, desc="Converting", unit=" records"):
        try:
            converted = convert_row(row)
            if converted:
                converted_rows.append(converted)
                success_count += 1
        except Exception as e:
            error_count += 1
            print(f"Error converting record {row.get('_id')}: {e}")
    
    # Write CSV
    sanitized_name = collection_name.replace(" ", "_").replace("/", "_")
    csv_path = output_dir / f"{sanitized_name}.csv"
    
    write_muis_csv(converted_rows, csv_path)
    print(f"✓ CSV written: {csv_path}")
    
    # Convert to Excel
    excel_path = csv_to_excel(csv_path)
    print(f"✓ Excel created: {excel_path}")
    
    # Summary
    print(f"\nSummary:")
    print(f"  Total records: {len(records):,}")
    print(f"  Successfully converted: {success_count:,} ({success_count/len(records)*100:.1f}%)")
    print(f"  Errors: {error_count:,}")
    
    # Check legend fields
    public_legend_count = sum(1 for r in converted_rows if r.get("public_legend"))
    legend_count = sum(1 for r in converted_rows if r.get("legend"))
    
    if public_legend_count > 0 or legend_count > 0:
        print(f"\n  Legend fields:")
        print(f"    Public legends: {public_legend_count:,} ({public_legend_count/len(records)*100:.1f}%)")
        print(f"    Internal legends: {legend_count:,} ({legend_count/len(records)*100:.1f}%)")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/process_collections.py <collection_name> [<collection_name> ...]")
        print("\nExample:")
        print("  python scripts/process_collections.py Digidokumendikogu Militaaria")
        return 1
    
    collection_names = sys.argv[1:]
    output_dir = Path("output/test_collections")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"Output directory: {output_dir.absolute()}")
    
    for collection_name in collection_names:
        try:
            process_collection(collection_name, output_dir)
        except Exception as e:
            print(f"\n❌ Error processing {collection_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print(f"All done! Files in: {output_dir.absolute()}")
    print(f"{'='*70}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
