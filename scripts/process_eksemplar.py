#!/usr/bin/env python3
"""Process eksemplar.csv (book specimens) for Raamatukogu collection.

This script processes the eksemplar.csv file which contains library book specimens,
separate from the eksponaat.csv museum objects.

Usage:
    python scripts/process_eksemplar.py
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


def process_eksemplar() -> None:
    """Process all eksemplar records and generate Raamatukogu Excel file."""
    
    print("\n" + "="*70)
    print("Processing: Eksemplar (Book Specimens)")
    print("="*70)
    
    input_file = Path("entust/eksemplar.csv")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Statistics
    stats = {
        "total": 0,
        "raamatukogu": 0,
        "auviste": 0,
        "no_kuuluvus": 0,
        "success": 0,
        "errors": 0,
    }
    
    # Read all eksemplar records
    records: list[dict[str, Any]] = []
    
    print(f"\n📖 Reading eksemplar records from {input_file}")
    
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in tqdm(reader, desc="Reading records", unit=" records"):
            stats["total"] += 1
            
            kuuluvus = row.get("kuuluvus", "").strip()
            
            if kuuluvus == "Raamatukogu":
                stats["raamatukogu"] += 1
                records.append(row)
            elif kuuluvus == "Auviste kogu":
                stats["auviste"] += 1
                records.append(row)
            elif not kuuluvus:
                stats["no_kuuluvus"] += 1
                # Include kuuluvuseta records (they'll be in the same file)
                records.append(row)
            else:
                # Unknown kuuluvus - should not happen based on Issue #16
                print(f"⚠️  Unknown kuuluvus: '{kuuluvus}' for record {row.get('_id')}")
    
    print(f"\n📊 Statistics:")
    print(f"  Total eksemplar records: {stats['total']:,}")
    print(f"  Raamatukogu kuuluvus: {stats['raamatukogu']:,}")
    print(f"  Auviste kogu: {stats['auviste']:,}")
    print(f"  No kuuluvus: {stats['no_kuuluvus']:,}")
    print(f"  Selected for export: {len(records):,}")
    
    if not records:
        print("⚠️  No records found to process!")
        return
    
    # Convert records using existing pipeline
    print(f"\n🔄 Converting records to MUIS format")
    converted_rows: list[dict[str, Any]] = []
    
    for row in tqdm(records, desc="Converting", unit=" records"):
        try:
            # Note: eksemplar has 'author' field, but convert_row expects 'autor'
            # Create a normalized copy with 'autor' for compatibility
            normalized_row = dict(row)
            if "author" in row and not row.get("autor"):
                normalized_row["autor"] = row["author"]
            
            converted = convert_row(normalized_row)
            if converted:
                converted_rows.append(converted)
                stats["success"] += 1
        except Exception as e:
            stats["errors"] += 1
            print(f"\n❌ Error converting record {row.get('code', 'unknown')}: {e}")
    
    # Write CSV
    csv_path = output_dir / "vabamu_Raamatukogu.csv"
    write_muis_csv(converted_rows, csv_path)
    print(f"\n✓ CSV written: {csv_path}")
    
    # Convert to Excel
    excel_path = csv_to_excel(csv_path)
    print(f"✓ Excel created: {excel_path}")
    
    # Final summary
    print(f"\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"  Total records processed: {len(records):,}")
    print(f"  Successfully converted: {stats['success']:,} ({stats['success']/len(records)*100:.1f}%)")
    print(f"  Errors: {stats['errors']:,}")
    
    # Check legend fields
    public_legend_count = sum(1 for r in converted_rows if r.get("public_legend"))
    legend_count = sum(1 for r in converted_rows if r.get("legend"))
    
    if public_legend_count > 0 or legend_count > 0:
        print(f"\n  Legend fields:")
        print(f"    Public legends: {public_legend_count:,} ({public_legend_count/len(records)*100:.1f}%)")
        print(f"    Internal legends: {legend_count:,} ({legend_count/len(records)*100:.1f}%)")
    
    print(f"\n✅ Raamatukogu export complete!")
    print(f"   Output: {excel_path}")


def main() -> int:
    """Main entry point."""
    try:
        process_eksemplar()
        return 0
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
