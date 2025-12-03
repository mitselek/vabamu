"""
ENTU Dimension Parser.

Parses ENTU dimension strings into MUIS measurement sets.

Example:
    >>> parse_dimensions("ø50;62x70")
    [
        {'parameeter': 'läbimõõt', 'yhik': 'mm', 'vaartus': 50},
        {'parameeter': 'kõrgus', 'yhik': 'mm', 'vaartus': 62},
        {'parameeter': 'laius', 'yhik': 'mm', 'vaartus': 70}
    ]
"""

import re
from typing import Any, Dict, List, Optional


def parse_dimensions(dim_str: Optional[str]) -> List[Dict[str, Any]]:
    """
    Parse ENTU dimensions into MUIS measurement sets.

    Supports multiple formats:
    - Diameter: "ø50" → [{'parameeter': 'läbimõõt', 'yhik': 'mm', 'vaartus': 50}]
    - HxW: "62x70" → height, width measurements
    - Combined: "ø50;62x70" → multiple measurements (semicolon separator)

    Args:
        dim_str: ENTU dimension string (may be None or empty)

    Returns:
        List of measurement dictionaries (max 4), each with:
        - parameeter: Measurement type (läbimõõt, kõrgus, laius, sügavus)
        - yhik: Unit (default "mm")
        - vaartus: Numeric value (int or float)

    Examples:
        >>> parse_dimensions("ø50")
        [{'parameeter': 'läbimõõt', 'yhik': 'mm', 'vaartus': 50}]

        >>> parse_dimensions("62x70")
        [
            {'parameeter': 'kõrgus', 'yhik': 'mm', 'vaartus': 62},
            {'parameeter': 'laius', 'yhik': 'mm', 'vaartus': 70}
        ]

        >>> parse_dimensions("ø50;62x70")
        [
            {'parameeter': 'läbimõõt', 'yhik': 'mm', 'vaartus': 50},
            {'parameeter': 'kõrgus', 'yhik': 'mm', 'vaartus': 62},
            {'parameeter': 'laius', 'yhik': 'mm', 'vaartus': 70}
        ]

        >>> parse_dimensions(None)
        []

        >>> parse_dimensions("unparseable")
        []
    """
    # Handle null/empty input
    if not dim_str or not isinstance(dim_str, str):  # type: ignore[arg-type]
        return []

    dim_str = dim_str.strip()
    if not dim_str:
        return []

    results: List[Dict[str, Any]] = []

    # Split on semicolon for multiple measurements
    parts = dim_str.split(";")

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Try to parse diameter: "ø50" or "d50" or "d:50"
        diameter_match = re.search(r"[ød][:,]?(\d+(?:\.\d+)?)", part)
        if diameter_match:
            value = float(diameter_match.group(1))
            results.append({"parameeter": "läbimõõt", "yhik": "mm", "vaartus": value})

        # Try to parse HxW or HxWxD: "62x70" or "62x70x80"
        hw_match = re.search(r"(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)(?:x(\d+(?:\.\d+)?))?", part)
        if hw_match:
            height = float(hw_match.group(1))
            width = float(hw_match.group(2))
            depth = hw_match.group(3)

            results.append({"parameeter": "kõrgus", "yhik": "mm", "vaartus": height})
            results.append({"parameeter": "laius", "yhik": "mm", "vaartus": width})

            if depth:
                results.append({"parameeter": "sügavus", "yhik": "mm", "vaartus": float(depth)})

    # Enforce max 4 measurements
    return results[:4]
