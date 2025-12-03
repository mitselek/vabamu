"""
ENTU Number Parser.

Parses ENTU object codes (format: NNNNNN/NNN) into MUIS 9-column structure.

Example:
    >>> parse_entu_code("020027/117")
    {'acr': 'VBM', 'trt': '_', 'trs': 20027, 'trj': 117, ...}
"""

import re
from typing import Any, Dict


def parse_entu_code(code: str) -> Dict[str, Any]:
    """
    Parse ENTU object number into MUIS 9-column structure.

    ENTU format: "NNNNNN/NNN" (e.g., "020027/117")
    MUIS output: Dictionary with 9 fields (ACR, TRT, TRS, TRJ, TRL, KT, KS, KJ, KL)

    Args:
        code: ENTU object number string

    Returns:
        Dictionary with parsed number components:
        - acr: "VBM" (always, Vabamu archive code)
        - trt: "_" (always, underscore separator)
        - trs: int (main series, leading zeros stripped)
        - trj: int (sub-series/sequential number)
        - trl: None (not used for Vabamu)
        - kt: None (collection type, set elsewhere)
        - ks: None (not used)
        - kj: None (not used)
        - kl: None (not used)

    Raises:
        ValueError: If code format is invalid or unparseable

    Examples:
        >>> parse_entu_code("020027/117")
        {'acr': 'VBM', 'trt': '_', 'trs': 20027, 'trj': 117, ...}

        >>> parse_entu_code("006562/001")
        {'acr': 'VBM', 'trt': '_', 'trs': 6562, 'trj': 1, ...}
    """
    # Validate input
    if not code or not isinstance(code, str):  # type: ignore[arg-type]
        raise ValueError(f"Code must be a non-empty string, got: {code}")

    # Strip whitespace
    code = code.strip()

    # Pattern: NNNNNN/NNN (6 digits, slash, 3 digits)
    pattern = r"^(\d{6})/(\d{3})$"
    match = re.match(pattern, code)

    if not match:
        raise ValueError(
            f"Invalid ENTU code format: '{code}'. Expected format: NNNNNN/NNN (e.g., 020027/117)"
        )

    # Parse components
    series_str = match.group(1)  # e.g., "020027"
    seq_str = match.group(2)  # e.g., "117"

    # Convert to integers, stripping leading zeros
    trs = int(series_str)  # 20027 (leading zero stripped)
    trj = int(seq_str)  # 117

    return {
        "acr": "VBM",  # Always "VBM" for Vabamu
        "trt": "_",  # Always underscore
        "trs": trs,  # Main series (integer, leading zeros stripped)
        "trj": trj,  # Sub-series (integer)
        "trl": None,  # Not used
        "kt": None,  # Collection type (set by caller based on kuuluvus)
        "ks": None,  # Not used
        "kj": None,  # Not used
        "kl": None,  # Not used
    }
