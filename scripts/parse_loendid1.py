#!/usr/bin/env python3
"""
Quick script to parse Loendid 1 (Classifiers 1) CSV from MUIS template.
Extracts controlled vocabularies for conversion mapping.
"""

import csv
from typing import TypedDict

# Parse the CSV structure - appears to have multiple vocabulary tables side-by-side
# Each table has: term_et, term_id, parent_term_et?, parent_id?, ...


class VocabularyEntry(TypedDict):
    """Vocabulary entry with term, ID, and parent ID."""

    term_et: str
    term_id: str
    parent_id: str


def parse_loendid1_csv(csv_path: str) -> dict[str, list[VocabularyEntry]]:
    """Parse Loendid 1 CSV with multiple vocabulary columns."""

    vocabularies: dict[str, list[VocabularyEntry]] = {
        'acquisition_methods': [],  # Omandamise viis (columns 0-2)
        'measurement_types': [],    # Mõõt/Mõõtmed (columns 3-5)
        'measurement_units': [],    # Mõõtühikud (columns 6-8)
        'formats': [],              # Formaadid (columns 9-11)
        'colors': [],               # Värv (columns 12-14)
        'patterns': [],             # Muster (columns 15-17)
        'techniques': [],           # Tehnika (columns 18-20)
    }
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for row in reader:
            if not row or not any(row):  # Skip empty rows
                continue
            
            # Parse each vocabulary column group (3 columns each)
            # Column group 0-2: Omandamise viis
            if len(row) > 0 and row[0].strip():
                vocabularies['acquisition_methods'].append({
                    'term_et': row[0].strip(),
                    'term_id': row[1].strip() if len(row) > 1 else '',
                    'parent_id': row[2].strip() if len(row) > 2 else ''
                })
            
            # Column group 3-5: Mõõt types
            if len(row) > 3 and row[3].strip():
                vocabularies['measurement_types'].append({
                    'term_et': row[3].strip(),
                    'term_id': row[4].strip() if len(row) > 4 else '',
                    'parent_id': row[5].strip() if len(row) > 5 else ''
                })
            
            # Column group 6-8: Mõõtühikud
            if len(row) > 6 and row[6].strip():
                vocabularies['measurement_units'].append({
                    'term_et': row[6].strip(),
                    'term_id': row[7].strip() if len(row) > 7 else '',
                    'parent_id': row[8].strip() if len(row) > 8 else ''
                })
            
            # Column group 9-11: Formats
            if len(row) > 9 and row[9].strip():
                vocabularies['formats'].append({
                    'term_et': row[9].strip(),
                    'term_id': row[10].strip() if len(row) > 10 else '',
                    'parent_id': row[11].strip() if len(row) > 11 else ''
                })
            
            # Column group 12-14: Värv (Color)
            if len(row) > 12 and row[12].strip():
                vocabularies['colors'].append({
                    'term_et': row[12].strip(),
                    'term_id': row[13].strip() if len(row) > 13 else '',
                    'parent_id': row[14].strip() if len(row) > 14 else ''
                })
            
            # Column group 15-17: Muster (Pattern)
            if len(row) > 15 and row[15].strip():
                vocabularies['patterns'].append({
                    'term_et': row[15].strip(),
                    'term_id': row[16].strip() if len(row) > 16 else '',
                    'parent_id': row[17].strip() if len(row) > 17 else ''
                })
            
            # Column group 18-20: Tehnika (Technique)
            if len(row) > 18 and row[18].strip():
                vocabularies['techniques'].append({
                    'term_et': row[18].strip(),
                    'term_id': row[19].strip() if len(row) > 19 else '',
                    'parent_id': row[20].strip() if len(row) > 20 else ''
                })
    
    return vocabularies


def main():
    # For now, just parse from the attachment content
    # User will need to provide actual CSV file path
    
    print("Loendid 1 parser ready.")
    print("Vocabularies to extract:")
    print("  1. Omandamise viis (Acquisition methods)")
    print("  2. Mõõt types (Measurement types)")
    print("  3. Mõõtühikud (Measurement units)")
    print("  4. Formaadid (Formats)")
    print("  5. Värv (Colors)")
    print("  6. Muster (Patterns)")
    print("  7. Tehnika (Techniques)")
    print()
    print("Sample entries visible:")
    print("  - Acquisition: 'saadud annetusena', 'saadud kogumistegevusest', 'saadud ostuna'")
    print("  - Measurements: 'diameeter', 'kõrgus', 'laius', 'pikkus', 'kaal'")
    print("  - Units: 'cm', 'm', 'mm', 'g', 'kg'")
    print("  - Formats: '10 x 13 cm', '24 x 30 cm', 'A4', 'A5'")
    print("  - Colors: 'beež', 'hall', 'kollane', 'must', 'punane', 'roheline', 'sinine'")
    print("  - Patterns: '<mustriline>', 'lilleline', 'triibuline'")
    print("  - Techniques: 700+ entries including 'aaderdamine', 'graafika', 'maalimine', etc.")


if __name__ == '__main__':
    main()
