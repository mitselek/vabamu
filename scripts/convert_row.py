"""Main orchestrator: convert_row.py

Orchestrates all 5 atomic parsers to convert a single ENTU row to MUIS format.

Pipeline:
1. Number parser: code (NNNNNN/NNN) → acr, trt, trs, trj, trl, kt, ks, kj, kl
2. Dimension parser: dimensions (ø, HxW, HxWxD) → measurements list
3. Date parser: date (ISO) → date (DD.MM.YYYY)
4. Person mapper: donator, autor → mapped names
5. Vocab mapper: materials, techniques, colors → terms

Returns: Dictionary with mapped MUIS fields ready for CSV output
"""

from typing import Any, Dict
from scripts.parsers.number_parser import parse_entu_code
from scripts.parsers.dimension_parser import parse_dimensions
from scripts.parsers.date_parser import convert_date
from scripts.parsers.person_mapper import map_person
from scripts.parsers.vocab_mapper import (
    map_material,
    map_technique,
    map_color,
)


def convert_row(entu_row: Dict[str, Any]) -> Dict[str, Any]:
    """Convert single ENTU row to MUIS format by orchestrating all parsers.

    Args:
        entu_row: Dictionary with ENTU fields (from CSV DictReader)

    Returns:
        Dictionary with MUIS fields ready for CSV output

    Pipeline:
        1. Parse code → number fields (acr, trt, trs, trj, trl, kt, ks, kj, kl)
        2. Parse dimensions → measurements list
        3. Parse date → formatted date string
        4. Map person fields → donator, autor
        5. Map vocabulary → materials, techniques, colors
    """
    # Start with empty result dict
    result: Dict[str, Any] = {}

    # =================================================================
    # PHASE 1: NUMBER PARSER - Parse ENTU code (NNNNNN/NNN)
    # =================================================================
    code = entu_row.get("code", "")
    if code:
        try:
            number_parsed = parse_entu_code(code)
            result.update(number_parsed)
        except (ValueError, KeyError):
            # Code parsing failed - set error indicators
            result["acr"] = None
            result["trt"] = None
            result["trs"] = None
            result["trj"] = None
            result["trl"] = None
            result["kt"] = None
            result["ks"] = None
            result["kj"] = None
            result["kl"] = None
    else:
        # No code provided
        result["acr"] = None
        result["trt"] = None
        result["trs"] = None
        result["trj"] = None
        result["trl"] = None
        result["kt"] = None
        result["ks"] = None
        result["kj"] = None
        result["kl"] = None

    # =================================================================
    # PHASE 2: DIMENSION PARSER - Parse dimensions (ø, HxW, HxWxD)
    # =================================================================
    dimensions = entu_row.get("dimensions", "")
    measurements = parse_dimensions(dimensions)
    result["measurements"] = measurements

    # =================================================================
    # PHASE 3: DATE PARSER - Convert ISO date to DD.MM.YYYY
    # =================================================================
    date_str = entu_row.get("date", "")
    converted_date = convert_date(date_str)
    result["date"] = converted_date

    # =================================================================
    # PHASE 4: PERSON MAPPER - Map donator and autor
    # =================================================================
    donator = entu_row.get("donator", "")
    autor = entu_row.get("autor", "")

    result["donator"] = map_person(donator)
    result["autor"] = map_person(autor)

    # =================================================================
    # PHASE 5: VOCABULARY MAPPER - Map materials, techniques, colors
    # =================================================================
    # Note: These may not be in the row yet (TBD with ENTU export)
    # But we prepare for them here
    materials = entu_row.get("materials", "")
    techniques = entu_row.get("techniques", "")
    colors = entu_row.get("colors", "")

    result["material"] = map_material(materials)
    result["technique"] = map_technique(techniques)
    result["color"] = map_color(colors)

    # =================================================================
    # PHASE 6: PRESERVE OTHER FIELDS
    # =================================================================
    # Pass through fields that don't need parsing
    result["name"] = entu_row.get("name", "")
    result["description"] = entu_row.get("description", "")
    result["donator_direct"] = entu_row.get("donator", "")
    result["autor_direct"] = entu_row.get("autor", "")

    return result
