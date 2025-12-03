"""
ENTU Person Mapper (Phase 1 Stub).

Phase 1: Placeholder stub that returns IDs as-is.
Phase 2: Will implement person_ids.csv lookup table.

Example:
    >>> map_person("139862")
    "[Person ID: 139862]"  # Placeholder for Phase 1

    >>> map_person("Jõgiaas, Miia")
    "Jõgiaas, Miia"  # Already formatted
"""

from typing import Optional


def map_person(person_id_or_name: Optional[str]) -> Optional[str]:
    """
    Map ENTU person to MUIS format (Phase 1 stub).

    Phase 1 (current stub):
    - Return None if input is None/empty
    - Return as-is if already formatted (has comma)
    - Return placeholder for IDs (will be replaced in Phase 2)

    Phase 2 (future):
    - Look up person_ids.csv
    - Return MUIS ID or formatted name

    Args:
        person_id_or_name: ENTU person ID (numeric) or name string

    Returns:
        Person identifier for MUIS format, or None

    Examples:
        >>> map_person(None)
        None

        >>> map_person("139862")
        "[Person ID: 139862]"

        >>> map_person("Jõgiaas, Miia")
        "Jõgiaas, Miia"
    """
    # Handle null/empty
    if not person_id_or_name:
        return None

    person_id_or_name = person_id_or_name.strip()

    # Already in "Lastname, Firstname" format - return unchanged
    if "," in person_id_or_name and not person_id_or_name.replace(" ", "").isdigit():
        return person_id_or_name

    # Numeric ID - placeholder for Phase 2 lookup
    if person_id_or_name.isdigit():
        return f"[Person ID: {person_id_or_name}]"

    # Single name or other format - return unchanged
    return person_id_or_name
