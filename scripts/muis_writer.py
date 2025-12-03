"""MUIS CSV writer.

Converts orchestrator output (dict) to MUIS CSV format with:
- Row 1: Metadata/info (3 system columns, rest descriptive)
- Row 2: Column names matching MuisMuseaal model fields
- Row 3: Validation rules/constraints
- Row 4+: Data rows

Handles:
- 88-column MUIS format (all columns from models.py MuisMuseaal)
- UTF-8 encoding with proper Estonian characters (õ, ä, ö, ü)
- Field mapping from orchestrator dict to MUIS columns
- Measurement/material/technique repetition fields (1-4 measurements, 1-3 materials/techniques)
"""

import csv
from pathlib import Path
from typing import Any, Dict, List


# ============================================================================
# MUIS HEADER DEFINITIONS
# ============================================================================

MUIS_COLUMN_NAMES = [
    # System columns (1-3)
    "museaali_ID",
    "Importimise staatus",
    "Kommentaar",
    # Number structure columns (4-12)
    "Acr",
    "Trt",
    "Trs",
    "Trj",
    "Trl",
    "Kt",
    "Ks",
    "Kj",
    "Kl",
    # Basic info columns (13-16)
    "Nimetus",
    "Püsiasukoht",
    "Tulmelegend",
    "Originaal ?",
    # Acquisition columns (17-21)
    "Vastuvõtu nr",
    "Esmane üldinfo",
    "Koguse registreerimise aeg",
    "Üleandja",
    "Muuseumile omandamise viis",
    # Measurement columns (22-33) - 4 measurements x 3 fields
    "Parameeter 1",
    "Ühik 1",
    "Väärtus 1",
    "Parameeter 2",
    "Ühik 2",
    "Väärtus 2",
    "Parameeter 3",
    "Ühik 3",
    "Väärtus 3",
    "Parameeter 4",
    "Ühik 4",
    "Väärtus 4",
    # Material columns (34-40) - 3 materials x 2 fields + color
    "Materjal 1",
    "Materjali 1 kommentaar",
    "Materjal 2",
    "Materjali 2 kommentaar",
    "Materjal 3",
    "Materjali 3 kommentaar",
    "Värvus",
    # Technique columns (41-47) - 3 techniques x 2 fields
    "Tehnika 1",
    "Tehnika 1 kommentaar",
    "Tehnika 2",
    "Tehnika 2 kommentaar",
    "Tehnika 3",
    "Tehnika 3 kommentaar",
    # Nature/type columns (48-49)
    "Olemus 1",
    "Olemus 2",
    # Reference columns (50-51)
    "Viite tyyp",
    "Viite väärtus",
    # Archaeology columns (52-55)
    "Leiukontekst",
    "Leiu liik",
    "Pealkirja keel",
    "Ainese keel",
    # Condition columns (56-57)
    "Seisund",
    "Kahjustused",
    # Event 1 columns (58-68)
    "Sündmuse liik 1",
    "Toimumiskoha tapsustus kohanimi 1",
    "Toimumiskoha tapsustus selgitus 1",
    "Dateering algus 1",
    "On eKr 1",
    "Dateeringu lopp 1",
    "Riik 1",
    "Eesti admin yksus 1",
    "Osaleja 1",
    "Osaleja roll 1",
    "Kihelkond 1",
    # Event 2 columns (69-79)
    "Sündmuse liik 2",
    "Toimumiskoha tapsustus kohanimi 2",
    "Toimumiskoha tapsustus selgitus 2",
    "Dateering algus 2",
    "On eKr 2",
    "Dateeringu lopp 2",
    "Riik 2",
    "Eesti admin yksus 2",
    "Osaleja 2",
    "Osaleja roll 2",
    "Kihelkond 2",
    # Visibility columns (80-81)
    "Avalik",
    "Avalikusta praegused andmed",
    # Description columns (82-85)
    "Teksti tyyp 1",
    "Tekst 1",
    "Teksti tyyp 2",
    "Tekst 2",
    # Alternative name columns (86-87)
    "Nimetuse tyyp",
    "Alt nimetus",
    # Alternative number columns (88-89)
    "Numbri tyyp",
    "Alt number",
]

MUIS_VALIDATION_RULES = [
    # System columns (1-3)
    "Täidab süsteem",
    "Täidab süsteem",
    "Täidab süsteem",
    # Number structure columns (4-12)
    "Peab vastama MuISis olevale ACR-ile",
    "Peab vastama MuISis olevale TRT-le",
    "Peab olema number",
    "Peab olema number",
    "",
    "Peab vastama MuISis olevale KT-le",
    "Peab olema number",
    "Peab olema number",
    "",
    # Basic info columns (13-16)
    "Kohustuslik",
    "Peab olema MuISi asukohapuus olemas",
    "",
    "y (on originaal) või tühi",
    # Acquisition columns (17-21)
    "",
    "",
    "Vastuvõtuakti kinnitamise aeg; Peab olema kujul pp.kk.aaaa",
    "Peab olema MuISis admin osaleja; täidetakse kujul Perekonnanimi, Eesnimi",
    "",
    # Measurement columns (22-33)
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    # Material columns (34-40)
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    # Technique columns (41-47)
    "",
    "",
    "",
    "",
    "",
    "",
    # Nature/type columns (48-49)
    "",
    "",
    # Reference columns (50-51)
    "",
    "",
    # Archaeology columns (52-55)
    "",
    "",
    "",
    "",
    # Condition columns (56-57)
    "",
    "",
    # Event 1 columns (58-68)
    "",
    "",
    "",
    "Peab olema kujul pp.kk.aaaa või kk.aaaa või aaaa",
    "y (on eKr) või tühi",
    "Peab olema kujul pp.kk.aaaa või kk.aaaa või aaaa",
    "",
    "",
    "",
    "",
    "",
    # Event 2 columns (69-79)
    "",
    "",
    "",
    "Peab olema kujul pp.kk.aaaa või kk.aaaa või aaaa",
    "y (on eKr) või tühi",
    "Peab olema kujul pp.kk.aaaa või kk.aaaa või aaaa",
    "",
    "",
    "",
    "",
    "",
    # Visibility columns (80-81)
    "y (avalik) või tühi",
    "y (avalikusta) või tühi",
    # Description columns (82-85)
    "",
    "",
    "",
    "",
    # Alternative name columns (86-87)
    "",
    "",
    # Alternative number columns (88-89)
    "",
    "",
]


# ============================================================================
# WRITER FUNCTIONS
# ============================================================================


def orchestrator_to_muis_row(
    orchestrator_output: Dict[str, Any],
) -> Dict[str, Any]:
    """Convert orchestrator dict output to MUIS row dict.

    Args:
        orchestrator_output: Dict from convert_row() orchestrator

    Returns:
        Dict with all 88 MUIS columns (aligned with MUIS_COLUMN_NAMES)
    """
    muis_row: Dict[str, Any] = {}

    # =====================================================================
    # SYSTEM COLUMNS (1-3) - Leave empty for import system
    # =====================================================================
    muis_row["museaali_ID"] = None
    muis_row["Importimise staatus"] = None
    muis_row["Kommentaar"] = None

    # =====================================================================
    # NUMBER STRUCTURE (4-12) - From number parser
    # =====================================================================
    muis_row["Acr"] = orchestrator_output.get("acr")
    muis_row["Trt"] = orchestrator_output.get("trt")
    muis_row["Trs"] = orchestrator_output.get("trs")
    muis_row["Trj"] = orchestrator_output.get("trj")
    muis_row["Trl"] = orchestrator_output.get("trl")
    muis_row["Kt"] = orchestrator_output.get("kt")
    muis_row["Ks"] = orchestrator_output.get("ks")
    muis_row["Kj"] = orchestrator_output.get("kj")
    muis_row["Kl"] = orchestrator_output.get("kl")

    # =====================================================================
    # BASIC INFO (13-16)
    # =====================================================================
    muis_row["Nimetus"] = orchestrator_output.get("name")
    muis_row["Püsiasukoht"] = None  # TODO: From asukoht mapping
    muis_row["Tulmelegend"] = orchestrator_output.get("description")
    muis_row["Originaal ?"] = ""  # Default empty

    # =====================================================================
    # ACQUISITION (17-21)
    # =====================================================================
    muis_row["Vastuvõtu nr"] = None  # TODO: From vastuv6tuakt
    muis_row["Esmane üldinfo"] = orchestrator_output.get("description")
    muis_row["Koguse registreerimise aeg"] = None  # TODO: From acquisition date
    muis_row["Üleandja"] = orchestrator_output.get("donator")
    muis_row["Muuseumile omandamise viis"] = None  # TODO: From paid field

    # =====================================================================
    # MEASUREMENTS (22-33) - From dimension parser (up to 4)
    # =====================================================================
    measurements = orchestrator_output.get("measurements", [])
    for i in range(1, 5):
        if i - 1 < len(measurements):
            m = measurements[i - 1]
            muis_row[f"Parameeter {i}"] = m.get("parameeter")
            muis_row[f"Ühik {i}"] = m.get("yhik")
            muis_row[f"Väärtus {i}"] = m.get("vaartus")
        else:
            muis_row[f"Parameeter {i}"] = None
            muis_row[f"Ühik {i}"] = None
            muis_row[f"Väärtus {i}"] = None

    # =====================================================================
    # MATERIALS (34-40) - From vocab mapper (up to 3)
    # =====================================================================
    material = orchestrator_output.get("material")
    muis_row["Materjal 1"] = material if material else None
    muis_row["Materjali 1 kommentaar"] = None
    muis_row["Materjal 2"] = None
    muis_row["Materjali 2 kommentaar"] = None
    muis_row["Materjal 3"] = None
    muis_row["Materjali 3 kommentaar"] = None
    muis_row["Värvus"] = orchestrator_output.get("color")

    # =====================================================================
    # TECHNIQUES (41-47) - From vocab mapper (up to 3)
    # =====================================================================
    technique = orchestrator_output.get("technique")
    muis_row["Tehnika 1"] = technique if technique else None
    muis_row["Tehnika 1 kommentaar"] = None
    muis_row["Tehnika 2"] = None
    muis_row["Tehnika 2 kommentaar"] = None
    muis_row["Tehnika 3"] = None
    muis_row["Tehnika 3 kommentaar"] = None

    # =====================================================================
    # NATURE/TYPE (48-49)
    # =====================================================================
    muis_row["Olemus 1"] = None
    muis_row["Olemus 2"] = None

    # =====================================================================
    # REFERENCES (50-51)
    # =====================================================================
    muis_row["Viite tyyp"] = None
    muis_row["Viite väärtus"] = None

    # =====================================================================
    # ARCHAEOLOGY (52-55)
    # =====================================================================
    muis_row["Leiukontekst"] = None
    muis_row["Leiu liik"] = None
    muis_row["Pealkirja keel"] = None
    muis_row["Ainese keel"] = None

    # =====================================================================
    # CONDITION (56-57)
    # =====================================================================
    muis_row["Seisund"] = None
    muis_row["Kahjustused"] = None

    # =====================================================================
    # EVENT 1 (58-68) - Optional, leave empty for now
    # =====================================================================
    muis_row["Sündmuse liik 1"] = None
    muis_row["Toimumiskoha tapsustus kohanimi 1"] = None
    muis_row["Toimumiskoha tapsustus selgitus 1"] = None
    muis_row["Dateering algus 1"] = None
    muis_row["On eKr 1"] = ""
    muis_row["Dateeringu lopp 1"] = None
    muis_row["Riik 1"] = None
    muis_row["Eesti admin yksus 1"] = None
    muis_row["Osaleja 1"] = None
    muis_row["Osaleja roll 1"] = None
    muis_row["Kihelkond 1"] = None

    # =====================================================================
    # EVENT 2 (69-79) - Optional, leave empty for now
    # =====================================================================
    muis_row["Sündmuse liik 2"] = None
    muis_row["Toimumiskoha tapsustus kohanimi 2"] = None
    muis_row["Toimumiskoha tapsustus selgitus 2"] = None
    muis_row["Dateering algus 2"] = None
    muis_row["On eKr 2"] = ""
    muis_row["Dateeringu lopp 2"] = None
    muis_row["Riik 2"] = None
    muis_row["Eesti admin yksus 2"] = None
    muis_row["Osaleja 2"] = None
    muis_row["Osaleja roll 2"] = None
    muis_row["Kihelkond 2"] = None

    # =====================================================================
    # VISIBILITY (80-81)
    # =====================================================================
    muis_row["Avalik"] = ""  # Default not public
    muis_row["Avalikusta praegused andmed"] = ""

    # =====================================================================
    # DESCRIPTIONS (82-85) - Up to 2 descriptions
    # =====================================================================
    muis_row["Teksti tyyp 1"] = None
    muis_row["Tekst 1"] = orchestrator_output.get("description")
    muis_row["Teksti tyyp 2"] = None
    muis_row["Tekst 2"] = None

    # =====================================================================
    # ALTERNATIVE NAMES (86-87)
    # =====================================================================
    muis_row["Nimetuse tyyp"] = None
    muis_row["Alt nimetus"] = None

    # =====================================================================
    # ALTERNATIVE NUMBERS (88-89)
    # =====================================================================
    muis_row["Numbri tyyp"] = None
    muis_row["Alt number"] = None

    return muis_row


def write_muis_csv(
    orchestrator_outputs: List[Dict[str, Any]],
    output_path: str | Path,
) -> None:
    """Write list of orchestrator outputs to MUIS CSV file.

    Creates MUIS import format with:
    - Row 1: Metadata (3 system columns + info)
    - Row 2: Column names
    - Row 3: Validation rules
    - Row 4+: Data

    Args:
        orchestrator_outputs: List of dicts from convert_row() orchestrator
        output_path: Path to write MUIS CSV file

    Encoding: UTF-8
    """
    output_path = Path(output_path)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MUIS_COLUMN_NAMES)

        # Write metadata row (mostly empty, system-filled)
        metadata_row = {col: "" for col in MUIS_COLUMN_NAMES}
        metadata_row["Kommentaar"] = "Tabel uuendatud konversiooni teel"
        writer.writerow(metadata_row)

        # Write column names row
        writer.writerow({col: col for col in MUIS_COLUMN_NAMES})

        # Write validation rules row
        validation_row = {col: rule for col, rule in zip(MUIS_COLUMN_NAMES, MUIS_VALIDATION_RULES)}
        writer.writerow(validation_row)

        # Write data rows
        for orch_output in orchestrator_outputs:
            muis_row = orchestrator_to_muis_row(orch_output)
            writer.writerow(muis_row)
