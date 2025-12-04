"""
Parsers for transforming ENTU fields to MUIS format.

This package contains atomic conversion functions for each data type:
- number_parser: ENTU codes → 9-column MUIS number structure
- dimension_parser: Dimension strings → measurement sets
- date_parser: ISO dates → DD.MM.YYYY format
- person_mapper: Person IDs/names → MUIS format
- vocab_mapper: Vocabulary paths → MUIS terms
"""
