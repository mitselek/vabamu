#!/usr/bin/env python3
"""Batch processor for ENTU to MUIS conversion.

Processes all ENTU eksponaat records and generates separate Excel files
grouped by kuuluvus (collection type).

Usage:
    python scripts/batch_processor.py
    python scripts/batch_processor.py --max-rows-per-file 10000
    python scripts/batch_processor.py --output-dir output/batch
"""

import argparse
import csv
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tqdm import tqdm

from scripts.convert_row import convert_row
from scripts.csv_to_excel import csv_to_excel
from scripts.muis_writer import write_muis_csv

# Constants
DEFAULT_INPUT_FILE = Path("entust/eksponaat.csv")
DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_LOG_DIR = Path("logs")
DEFAULT_MAX_ROWS = 10_000


def setup_logging(log_dir: Path) -> logging.Logger:
    """Set up logging configuration.

    Args:
        log_dir: Directory for log files

    Returns:
        Configured logger instance
    """
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"batch_processor_{datetime.now():%Y%m%d_%H%M%S}.log"

    logger = logging.getLogger("batch_processor")
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def sanitize_filename(name: str) -> str:
    """Sanitize collection name for use in filename.

    Args:
        name: Collection name (kuuluvus value)

    Returns:
        Sanitized filename-safe string
    """
    # Replace problematic characters
    replacements = {
        " ": "_",
        "/": "_",
        "\\": "_",
        ":": "_",
        "*": "_",
        "?": "_",
        '"': "_",
        "<": "_",
        ">": "_",
        "|": "_",
        "\n": "_",
    }
    
    sanitized = name
    for old, new in replacements.items():
        sanitized = sanitized.replace(old, new)
    
    # Remove multiple underscores
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")
    
    return sanitized.strip("_")


def read_and_group_records(
    input_file: Path, logger: logging.Logger
) -> dict[str, list[dict[str, Any]]]:
    """Read ENTU CSV and group records by kuuluvus.

    Args:
        input_file: Path to entust/eksponaat.csv
        logger: Logger instance

    Returns:
        Dictionary mapping kuuluvus -> list of records
    """
    logger.info(f"Reading records from {input_file}...")
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    error_count = 0
    
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in tqdm(reader, desc="Reading records", unit=" records"):
            try:
                kuuluvus = row.get("kuuluvus", "").strip()
                
                if not kuuluvus:
                    kuuluvus = "(no_collection)"
                    logger.warning(f"Record {row.get('_id', 'unknown')} has no kuuluvus")
                
                groups[kuuluvus].append(row)
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error reading record: {e}", exc_info=True)
    
    logger.info(f"Read {sum(len(g) for g in groups.values())} records into {len(groups)} collections")
    if error_count > 0:
        logger.warning(f"Encountered {error_count} errors while reading")
    
    return groups


def split_large_collection(
    records: list[dict[str, Any]], max_rows: int
) -> list[list[dict[str, Any]]]:
    """Split collection into chunks if it exceeds max_rows.

    Args:
        records: List of records in collection
        max_rows: Maximum rows per file

    Returns:
        List of record chunks
    """
    if len(records) <= max_rows:
        return [records]
    
    chunks = []
    for i in range(0, len(records), max_rows):
        chunks.append(records[i : i + max_rows])
    
    return chunks


def convert_collection(
    collection_name: str,
    records: list[dict[str, Any]],
    chunk_num: int | None,
    total_chunks: int,
    output_dir: Path,
    logger: logging.Logger,
) -> tuple[Path | None, int, int]:
    """Convert a collection (or chunk) to MUIS format and Excel.

    Args:
        collection_name: Name of collection (kuuluvus)
        records: List of records to convert
        chunk_num: Chunk number (None if not split)
        total_chunks: Total number of chunks for this collection
        output_dir: Output directory for files
        logger: Logger instance

    Returns:
        Tuple of (excel_path, success_count, error_count)
    """
    # Generate filename
    safe_name = sanitize_filename(collection_name)
    if chunk_num is not None:
        filename = f"vabamu_{safe_name}_{chunk_num}_of_{total_chunks}"
    else:
        filename = f"vabamu_{safe_name}"
    
    csv_path = output_dir / f"{filename}.csv"
    excel_path = output_dir / f"{filename}.xlsx"
    
    logger.info(f"Converting {collection_name}: {len(records)} records -> {excel_path.name}")
    
    # Convert records
    converted_records = []
    error_count = 0
    
    for record in tqdm(records, desc=f"Converting {collection_name}", unit=" records", leave=False):
        try:
            converted = convert_row(record)
            converted_records.append(converted)
        except Exception as e:
            error_count += 1
            record_id = record.get("_id", "unknown")
            logger.error(
                f"Error converting record {record_id} in {collection_name}: {e}",
                exc_info=True,
            )
    
    if not converted_records:
        logger.warning(f"No records successfully converted for {collection_name}")
        return None, 0, error_count
    
    # Write MUIS CSV
    try:
        write_muis_csv(converted_records, csv_path)
        logger.debug(f"Wrote MUIS CSV: {csv_path}")
    except Exception as e:
        logger.error(f"Error writing MUIS CSV for {collection_name}: {e}", exc_info=True)
        return None, len(converted_records), error_count
    
    # Convert to Excel
    try:
        csv_to_excel(csv_path, excel_path)
        logger.debug(f"Converted to Excel: {excel_path}")
    except Exception as e:
        logger.error(f"Error converting to Excel for {collection_name}: {e}", exc_info=True)
        return None, len(converted_records), error_count
    
    return excel_path, len(converted_records), error_count


def create_archive_readme(collection_name: str, output_dir: Path) -> None:
    """Create README file for archive-only collections.

    Args:
        collection_name: Name of archive collection
        output_dir: Output directory for README
    """
    readme_content = f"""# {collection_name} - Arhiivikogud

⚠️ **TÄHELEPANU**: See fail on ainult arhiiviviite eesmärgil.

## Miks ei impordi MuISi?

Kogu "{collection_name}" sisaldab museaale, mis on:
- Juba maha kantud kogudest
- Arhiivraamatukogus (ei ole muuseumikogud)
- Mitte ettenähtud MuISi massimpordi jaoks

## Kasutamine

Seda faili saab kasutada:
- Ajalooliste andmete võrdlemiseks
- Arhiiviviidete kontrollimiseks
- Statistiliste aruannete koostamiseks

## MUIS Import

❌ **Ära impordi seda faili MuISi!**

Kontrolli Liisi või teiste kureerimise vastutajatega, kui on küsimusi.

---
Genereeritud: {datetime.now():%Y-%m-%d %H:%M}
"""
    
    safe_name = sanitize_filename(collection_name)
    readme_path = output_dir / f"README_{safe_name}.txt"
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)


def generate_summary_report(
    groups: dict[str, list[dict[str, Any]]],
    results: dict[str, tuple[list[Path], int, int]],
    output_dir: Path,
    logger: logging.Logger,
) -> None:
    """Generate summary report of batch processing.

    Args:
        groups: Original grouped records
        results: Processing results per collection
        output_dir: Output directory
        logger: Logger instance
    """
    report_path = output_dir / f"batch_summary_{datetime.now():%Y%m%d_%H%M%S}.txt"
    
    total_input = sum(len(g) for g in groups.values())
    total_success = sum(r[1] for r in results.values())
    total_errors = sum(r[2] for r in results.values())
    total_files = sum(len(r[0]) for r in results.values())
    
    report = [
        "=" * 70,
        "BATCH PROCESSING SUMMARY",
        "=" * 70,
        f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}",
        "",
        "TOTALS:",
        f"  Input records:        {total_input:>10,}",
        f"  Successfully converted: {total_success:>10,} ({total_success/total_input*100:.2f}%)",
        f"  Conversion errors:    {total_errors:>10,} ({total_errors/total_input*100:.2f}%)",
        f"  Excel files generated: {total_files:>10}",
        "",
        "COLLECTIONS:",
        "-" * 70,
    ]
    
    # Sort by record count descending
    sorted_collections = sorted(
        results.items(), key=lambda x: sum(len(g) for g in groups.values() if g), reverse=True
    )
    
    for collection_name, (files, success, errors) in sorted_collections:
        input_count = len(groups[collection_name])
        report.append(
            f"  {collection_name:<30} {input_count:>6,} records -> {len(files):>2} file(s)"
        )
        if errors > 0:
            report.append(f"    ⚠️  {errors} errors")
    
    report.extend([
        "",
        "=" * 70,
        f"Output directory: {output_dir.absolute()}",
        "=" * 70,
    ])
    
    report_text = "\n".join(report)
    
    # Write to file
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    # Print to console and log
    logger.info("\n" + report_text)
    print("\n" + report_text)


def main() -> int:
    """Main entry point for batch processor.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Batch process ENTU records to MUIS Excel files by collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_FILE,
        help=f"Input CSV file (default: {DEFAULT_INPUT_FILE})",
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=DEFAULT_LOG_DIR,
        help=f"Log directory (default: {DEFAULT_LOG_DIR})",
    )
    
    parser.add_argument(
        "--max-rows-per-file",
        type=int,
        default=DEFAULT_MAX_ROWS,
        help=f"Maximum rows per file (default: {DEFAULT_MAX_ROWS})",
    )
    
    args = parser.parse_args()
    
    # Setup
    args.output_dir.mkdir(exist_ok=True, parents=True)
    logger = setup_logging(args.log_dir)
    
    logger.info("=" * 70)
    logger.info("BATCH PROCESSOR STARTED")
    logger.info("=" * 70)
    logger.info(f"Input: {args.input}")
    logger.info(f"Output: {args.output_dir}")
    logger.info(f"Max rows per file: {args.max_rows_per_file:,}")
    
    try:
        # Read and group records
        groups = read_and_group_records(args.input, logger)
        
        # Process each collection
        results: dict[str, tuple[list[Path], int, int]] = {}
        
        for collection_name, records in groups.items():
            logger.info(f"\nProcessing collection: {collection_name} ({len(records):,} records)")
            
            # Split if needed
            chunks = split_large_collection(records, args.max_rows_per_file)
            total_chunks = len(chunks)
            
            if total_chunks > 1:
                logger.info(f"  Splitting into {total_chunks} files ({args.max_rows_per_file:,} rows each)")
            
            collection_files = []
            collection_success = 0
            collection_errors = 0
            
            for i, chunk in enumerate(chunks, start=1):
                chunk_num = i if total_chunks > 1 else None
                
                excel_path, success, errors = convert_collection(
                    collection_name,
                    chunk,
                    chunk_num,
                    total_chunks,
                    args.output_dir,
                    logger,
                )
                
                if excel_path:
                    collection_files.append(excel_path)
                collection_success += success
                collection_errors += errors
            
            results[collection_name] = (collection_files, collection_success, collection_errors)
            
            # Create README for archive collections
            if collection_name in ["Maha kantud", "Arhiivraamatukogu"]:
                create_archive_readme(collection_name, args.output_dir)
                logger.info(f"  Created archive README for {collection_name}")
        
        # Generate summary
        generate_summary_report(groups, results, args.output_dir, logger)
        
        logger.info("\n" + "=" * 70)
        logger.info("BATCH PROCESSOR COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
