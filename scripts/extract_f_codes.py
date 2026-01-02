#!/usr/bin/env python3
"""Extract f-prefix codes from Fotokogu collection and create separate files.

This script:
1. Reads output/handover 1/vabamu_Fotokogu.csv (converted MUIS format)
2. Extracts all records with f-prefix codes (f000XXX/YYY format)
3. Creates vabamu_Fotokogu_f_koodid.xlsx with f-prefix records only
4. Regenerates vabamu_Fotokogu.xlsx without f-prefix records

Per Liisi's decision (Issue #16):
- F-prefix codes need manual handling before RIK mass import
- Some contain non-photo material that was incorrectly classified
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import csv
import re
from typing import Any
from tqdm import tqdm

from scripts.csv_to_excel import csv_to_excel


def is_f_prefix_code(trs_value: str) -> bool:
    """Check if TRS value is an f-prefix code.
    
    F-prefix codes have format: f000XXX where XXX is a number.
    After parsing, they appear in TRS column without leading zeros.
    
    Args:
        trs_value: Value from TRS column (5th column)
        
    Returns:
        True if this is an f-prefix code
    """
    if not trs_value:
        return False
    
    trs_clean = str(trs_value).strip()
    
    # Check for numeric values that might be from f-codes
    # Original: f000046 -> after parsing: 46 (leading zeros removed)
    # So we need to check the original ENTU code
    # But we're working with already-converted data, so we need a different approach
    
    return False  # Will implement after checking data structure


def extract_f_codes_from_source() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Re-process ENTU eksponaat.csv to extract f-prefix codes.
    
    Returns:
        Tuple of (f_code_records, regular_records)
    """
    from scripts.convert_row import convert_row
    
    input_file = Path("entust/eksponaat.csv")
    
    f_code_records = []
    regular_records = []
    
    print(f"\n📖 Reading ENTU eksponaat.csv to identify f-prefix codes")
    
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in tqdm(reader, desc="Reading records", unit=" records"):
            kuuluvus = row.get("kuuluvus", "").strip()
            
            # Only process Fotokogu records
            if kuuluvus != "Fotokogu":
                continue
            
            code = row.get("code", "").strip()
            
            # Check if this is an f-prefix code
            if re.match(r'^f\d{6}/\d{3}$', code):
                # Convert and add to f-code list
                try:
                    converted = convert_row(row)
                    if converted:
                        f_code_records.append(converted)
                except Exception as e:
                    print(f"❌ Error converting f-code record {code}: {e}")
            else:
                # Convert and add to regular list
                try:
                    converted = convert_row(row)
                    if converted:
                        regular_records.append(converted)
                except Exception as e:
                    print(f"❌ Error converting record {code}: {e}")
    
    return f_code_records, regular_records


def write_csv_with_headers(records: list[dict[str, Any]], output_path: Path) -> None:
    """Write MUIS CSV with proper headers."""
    from scripts.muis_writer import write_muis_csv
    
    write_muis_csv(records, output_path)
    print(f"✓ CSV written: {output_path}")


def main() -> int:
    """Main entry point."""
    
    print("\n" + "="*70)
    print("F-prefix Code Extraction (Issue #16)")
    print("="*70)
    
    output_dir = Path("output/handover 1")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Extract f-codes from source
    f_code_records, regular_records = extract_f_codes_from_source()
    
    print(f"\n📊 Statistics:")
    print(f"  F-prefix codes found: {len(f_code_records):,}")
    print(f"  Regular Fotokogu records: {len(regular_records):,}")
    print(f"  Total: {len(f_code_records) + len(regular_records):,}")
    
    if not f_code_records:
        print("⚠️  No f-prefix codes found!")
        return 1
    
    # Write f-prefix codes to separate file
    print(f"\n🔄 Creating vabamu_Fotokogu_f_koodid files")
    f_csv_path = output_dir / "vabamu_Fotokogu_f_koodid.csv"
    write_csv_with_headers(f_code_records, f_csv_path)
    
    f_excel_path = csv_to_excel(f_csv_path)
    print(f"✓ Excel created: {f_excel_path}")
    
    # Regenerate main Fotokogu file without f-codes
    print(f"\n🔄 Regenerating vabamu_Fotokogu (without f-codes)")
    regular_csv_path = output_dir / "vabamu_Fotokogu.csv"
    write_csv_with_headers(regular_records, regular_csv_path)
    
    regular_excel_path = csv_to_excel(regular_csv_path)
    print(f"✓ Excel created: {regular_excel_path}")
    
    # Final summary
    print(f"\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"  F-prefix codes extracted: {len(f_code_records):,}")
    print(f"    → {f_excel_path}")
    print(f"\n  Regular Fotokogu (updated): {len(regular_records):,}")
    print(f"    → {regular_excel_path}")
    
    print(f"\n✅ F-code separation complete!")
    print(f"\n⚠️  Note: F-codes require manual review before RIK import")
    print(f"   (may contain non-photo materials)")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
