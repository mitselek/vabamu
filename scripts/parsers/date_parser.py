"""
ENTU Date Parser.

Converts ISO dates to MUIS Estonian format (DD.MM.YYYY).

Example:
    >>> convert_date("2002-12-22")
    "22.12.2002"
"""

from datetime import datetime
from typing import Optional


def convert_date(date_str: Optional[str]) -> Optional[str]:
    """
    Convert ENTU date to MUIS Estonian format.

    ENTU: ISO format "YYYY-MM-DD"
    MUIS: Estonian format "DD.MM.YYYY"

    Args:
        date_str: Date string in ISO format or None

    Returns:
        Date string in DD.MM.YYYY format, or None if input is None/invalid

    Examples:
        >>> convert_date("2002-12-22")
        "22.12.2002"

        >>> convert_date("1956-05-28")
        "28.05.1956"

        >>> convert_date(None)
        None

        >>> convert_date("invalid")
        None
    """
    # Handle null/empty input
    if not date_str:
        return None

    try:
        # Parse ISO format
        dt = datetime.fromisoformat(date_str)
        # Format as DD.MM.YYYY
        return dt.strftime("%d.%m.%Y")
    except ValueError:
        # Invalid format, return None
        return None
