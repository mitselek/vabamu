"""
ENTU Vocabulary Mapper.

Maps ENTU vocabulary paths to MUIS terms.
Examples: "/materjalid/metall" → "metall"

Used for materials, techniques, colors, etc.
"""

from typing import Optional


def map_material(material_path: Optional[str]) -> Optional[str]:
    """
    Map ENTU material path to MUIS material term.

    Args:
        material_path: ENTU path like "/materjalid/metall" or term like "metall"

    Returns:
        MUIS material term or None

    Examples:
        >>> map_material("/materjalid/metall")
        "metall"

        >>> map_material("metall")
        "metall"

        >>> map_material(None)
        None
    """
    if not material_path:
        return None

    material_path = material_path.strip()

    # If it's a path, extract last component
    if "/" in material_path:
        parts = material_path.split("/")
        # Filter out empty parts (from leading/trailing slashes)
        parts = [p for p in parts if p]
        if parts:
            return parts[-1]
        return None

    return material_path if material_path else None


def map_technique(technique_path: Optional[str]) -> Optional[str]:
    """
    Map ENTU technique to MUIS term.

    Uses same logic as map_material.

    Args:
        technique_path: ENTU path or term

    Returns:
        MUIS technique term or None
    """
    return map_material(technique_path)


def map_color(color_path: Optional[str]) -> Optional[str]:
    """
    Map ENTU color to MUIS term.

    Uses same logic as map_material.

    Args:
        color_path: ENTU path or term

    Returns:
        MUIS color term or None
    """
    return map_material(color_path)
