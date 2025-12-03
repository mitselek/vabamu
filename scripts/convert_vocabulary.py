#!/usr/bin/env python3
"""
Command-line interface for vocabulary file conversion.

Converts tab-separated vocabulary files to JSON format with automatic column detection.

Usage:
    python scripts/convert_vocabulary.py <input_file> <vocabulary_name> [--output <output_file>]

Examples:
    # Auto-detect columns, create <vocabulary_name>.json
    python scripts/convert_vocabulary.py tabel_1.txt techniques

    # Specify custom output path
    python scripts/convert_vocabulary.py tabel_1.txt techniques --output custom.json

    # Process all files
    python scripts/convert_vocabulary.py tabel_1.txt loendid_1
    python scripts/convert_vocabulary.py tabel_2.txt loendid_2
    python scripts/convert_vocabulary.py tabel_3.txt loendid_3
    python scripts/convert_vocabulary.py tabel_4.txt loendid_4
"""

import sys
from pathlib import Path
from argparse import ArgumentParser, ArgumentTypeError
from scripts.vocab_converter import VocabularyConverter


def valid_path(path_str: str) -> Path:
    """Validate that path is a valid file."""
    path = Path(path_str)
    if not path.exists():
        raise ArgumentTypeError(f"File not found: {path}")
    if not path.is_file():
        raise ArgumentTypeError(f"Not a file: {path}")
    return path


def main() -> None:
    """Parse arguments and run converter."""
    parser = ArgumentParser(
        description="Convert tab-separated vocabulary files to JSON format",
        prog="convert_vocabulary.py",
    )

    parser.add_argument(
        "input_file",
        type=valid_path,
        help="Input TSV file (1-4 columns supported)",
    )

    parser.add_argument(
        "vocabulary_name",
        help="Name for vocabulary (used as JSON array key)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output JSON file path (default: <vocabulary_name>.json)",
    )

    parser.add_argument(
        "--no-auto-detect",
        action="store_true",
        help="Disable automatic column detection (not recommended)",
    )

    parser.add_argument(
        "--column-count",
        "-c",
        type=int,
        choices=[1, 2, 3, 4],
        help="Explicit column count (overrides auto-detection)",
    )

    args = parser.parse_args()

    # Determine output file
    output_file = args.output or Path(f"{args.vocabulary_name}.json")

    # Create converter
    converter = VocabularyConverter(auto_detect_columns=not args.no_auto_detect)

    try:
        # Run conversion
        converter.convert(
            input_file=args.input_file,
            vocabulary_name=args.vocabulary_name,
            output_file=output_file,
            column_count=args.column_count,
        )

        print(f"✓ Successfully converted {args.input_file} to {output_file}")
        print(f"  Vocabulary name: {args.vocabulary_name}")

    except FileNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
