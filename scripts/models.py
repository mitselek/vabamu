"""
Data models for ENTU → MUIS conversion.

This module defines the single source of truth for data structures using Pydantic.
All validation rules, type constraints, and business logic are centralized here.

Architecture:
- EntuEksponaat: Input model for ENTU museum objects
- MuisMuseaal: Output model for MUIS import format
- Supporting models: Measurements, Materials, Techniques, Events, etc.

Each model includes:
- Type annotations (str, int, Optional, etc.)
- Validation rules (@validator decorators)
- Field constraints (regex, min/max values)
- Documentation (docstrings)
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Literal
from datetime import date as Date, datetime
from enum import Enum
import re


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================


class AcquisitionMethod(str, Enum):
    """Valid acquisition methods for MUIS"""

    DONATION = "saadud annetusena"
    PURCHASE = "ostetud"
    TRANSFER = "üleantud"
    EXCHANGE = "vahetatud"
    OTHER = "muu"


class Condition(str, Enum):
    """Object condition states"""

    EXCELLENT = "väga hea"
    GOOD = "hea"
    SATISFACTORY = "rahuldav"
    POOR = "halb"
    VERY_POOR = "väga halb"


class EventType(str, Enum):
    """Types of events associated with museum objects"""

    DEPORTATION = "küüditamine"
    REPRESSION = "represseerimine"
    CREATION = "loomine"
    USE = "kasutamine"
    ACQUISITION = "omandamine"


# ============================================================================
# ENTU INPUT MODELS (Source Data)
# ============================================================================


class EntuEksponaat(BaseModel):
    """
    ENTU museum object (eksponaat) - Input data model.

    Maps to: entust/eksponaat.csv
    Represents: Single museum object from ENTU database
    """

    # Primary identification
    id: str = Field(..., description="MongoDB ObjectId")
    parent: Optional[str] = Field(None, description="Parent entity reference")
    code: str = Field(..., description="Object code, e.g., '006562/001'")
    name: str = Field(..., description="Object name/title")

    # Descriptive fields
    description: Optional[str] = None
    tyyp: Optional[str] = Field(None, description="Object type/category path")
    kuuluvus: Optional[str] = Field(None, description="Collection membership")
    period: Optional[str] = Field(None, description="Time period")

    # Physical attributes
    dimensions: Optional[str] = Field(None, description="Dimensions, e.g., 'ø50;62x70'")
    condition: Optional[str] = Field(None, description="Object condition")
    amount: Optional[int] = Field(1, description="Quantity")

    # Location
    asukoht: Optional[str] = Field(None, description="Current location path")
    koht: Optional[str] = Field(None, description="Geographic location")

    # Dates
    date: Optional[Date] = Field(None, description="Primary date (ISO format)")
    year: Optional[str] = Field(None, description="Year string")

    # People & acquisition
    autor: Optional[str] = Field(None, description="Creator/author (person ID or name)")
    donator: Optional[str] = Field(None, description="Donor (person ID or name)")
    vastuv6tuakt: Optional[str] = Field(None, description="Acquisition act reference")
    paid: Optional[str] = Field(None, description="Payment method")

    # Repression-related (for special collections)
    represseeritu_o: Optional[str] = Field(None, description="Repressed person (victim)")
    represseeritu_t: Optional[str] = Field(None, description="Repressed person (perpetrator)")
    repr_lisainfo: Optional[str] = None
    repr_memento: Optional[str] = None
    repr_syydistus: Optional[str] = Field(None, description="Charges/accusations")

    # Media
    photo: Optional[str] = Field(None, description="Photo path")
    photo_orig: Optional[str] = Field(None, description="Original photo path")
    video: Optional[str] = Field(None, description="Video path")
    fail: Optional[str] = Field(None, description="File attachments")

    # Additional metadata
    legend: Optional[str] = Field(None, description="Caption/legend")
    public_legend: Optional[str] = None
    note: Optional[str] = Field(None, description="Internal notes")
    m2rks6nad: Optional[str] = Field(None, description="Keywords/tags")
    tag: Optional[str] = None
    olulisus: Optional[str] = Field(None, description="Significance rating")

    # Publishing
    publishing_date: Optional[str] = None
    yleandmistingimus: Optional[str] = Field(None, description="Terms of transfer")

    # Technical fields
    inventeerimisakt: Optional[str] = None
    mahakandmisakt: Optional[str] = None
    lisam2_rkus: Optional[str] = None
    k_m_selgitus: Optional[str] = None
    n2_itus: Optional[str] = None
    sari: Optional[str] = None
    reksponaat: Optional[str] = None

    @field_validator("code")
    @classmethod
    def validate_code_format(cls, v: str) -> str:
        """Ensure code matches expected ENTU format"""
        import logging

        logger = logging.getLogger(__name__)
        if v and not re.match(r"^\d{6}/\d{3}$", v):
            logger.warning(f"Code format variance: '{v}' (expected XXXXXX/XXX format)")
        return v

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: str | Date | None) -> Date | None:
        """Parse date string to date object"""
        if not v:
            return None
        if isinstance(v, Date):
            return v
        # v must be str at this point
        try:
            return datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            return None

    class Config:
        validate_assignment = True


# ============================================================================
# MUIS OUTPUT MODELS (Target Data)
# ============================================================================


class MuisMeasurement(BaseModel):
    """Single measurement (parameter/unit/value set)"""

    parameeter: str = Field(..., description="Measurement type, e.g., 'kõrgus', 'laius'")
    yhik: str = Field(..., description="Unit, e.g., 'mm', 'cm', 'g'")
    vaartus: float = Field(..., description="Numeric value", gt=0)

    @field_validator("parameeter")
    @classmethod
    def validate_parameter(cls, v: str) -> str:
        """Ensure parameter is valid MUIS vocabulary term"""
        import logging

        logger = logging.getLogger(__name__)
        # Common parameters - could be loaded from mapping file
        valid = ["kõrgus", "laius", "pikkus", "läbimõõt", "sügavus", "kaal", "diameeter"]
        if v.lower() not in valid:
            logger.warning(f"Unmapped parameter: '{v}' (not in MUIS vocabulary)")
        return v


class MuisMaterial(BaseModel):
    """Material specification with optional comment"""

    materjal: str = Field(..., description="Material name from MUIS vocabulary")
    kommentaar: Optional[str] = Field(None, description="Additional material details")


class MuisTechnique(BaseModel):
    """Technique specification with optional comment"""

    tehnika: str = Field(..., description="Technique name from MUIS vocabulary")
    kommentaar: Optional[str] = Field(None, description="Additional technique details")


class MuisEvent(BaseModel):
    """
    Event associated with museum object (e.g., deportation, repression).
    MUIS allows 2 events per object (Sündmus 1 and Sündmus 2).
    """

    liik: str = Field(..., description="Event type from EventType enum")
    kohanimi: Optional[str] = Field(None, description="Location name")
    selgitus: Optional[str] = Field(None, description="Location explanation")
    dateering_algus: Optional[str] = Field(
        None, description="Start date (aaaa or kk.aaaa or pp.kk.aaaa)"
    )
    on_ekr: Optional[Literal["y", ""]] = Field("", description="Is BCE? 'y' or empty")
    dateering_lopp: Optional[str] = Field(None, description="End date (if date range)")
    riik: Optional[str] = Field(None, description="Country, must be 'Eesti' if admin_yksus filled")
    eesti_admin_yksus: Optional[str] = Field(None, description="Estonian admin unit")
    osaleja: Optional[str] = Field(
        None, description="Participant (Lastname, Firstname OR org name)"
    )
    osaleja_roll: Optional[str] = Field(
        None, description="Participant role, required if osaleja filled"
    )
    kihelkond: Optional[str] = Field(None, description="Parish")

    @model_validator(mode="after")
    def validate_event_dependencies(self) -> "MuisEvent":
        """Validate conditional field requirements"""
        # If osaleja filled, osaleja_roll is required
        if self.osaleja and not self.osaleja_roll:
            raise ValueError("osaleja_roll required when osaleja is provided")

        # If kohanimi filled, selgitus required
        if self.kohanimi and not self.selgitus:
            raise ValueError("selgitus required when kohanimi is provided")

        # If dateering_lopp filled, dateering_algus must be filled
        if self.dateering_lopp and not self.dateering_algus:
            raise ValueError("dateering_algus required when dateering_lopp is provided")

        # If admin_yksus or kihelkond filled, riik must be 'Eesti'
        if (self.eesti_admin_yksus or self.kihelkond) and self.riik != "Eesti":
            self.riik = "Eesti"

        return self

    @field_validator("dateering_algus", "dateering_lopp")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        """Validate Estonian date format"""
        if not v:
            return v
        # Accept formats: aaaa, kk.aaaa, pp.kk.aaaa
        if not re.match(r"^(\d{4}|\d{2}\.\d{4}|\d{2}\.\d{2}\.\d{4})$", v):
            raise ValueError(f"Invalid date format: {v}. Must be aaaa or kk.aaaa or pp.kk.aaaa")
        return v


class MuisDescription(BaseModel):
    """Text description with type classification"""

    tyyp: str = Field(..., description="Text type, e.g., 'füüsiline kirjeldus'")
    tekst: str = Field(..., description="Description text content")


class MuisAlternativeName(BaseModel):
    """Alternative name/title for object"""

    tyyp: str = Field(..., description="Name type")
    nimetus: str = Field(..., description="Alternative name")


class MuisAlternativeNumber(BaseModel):
    """Alternative number/identifier for object"""

    tyyp: str = Field(..., description="Number type, e.g., 'endine inventarinumber'")
    number: str = Field(..., description="Alternative number")


class MuisMuseaal(BaseModel):
    """
    MUIS museum object - Output data model.

    Represents: Complete MUIS import record (85-88 columns)
    Validation: All MUIS import rules enforced

    This is the single source of truth for MUIS output format.
    """

    # ========================================================================
    # SYSTEM FIELDS (columns 1-3)
    # ========================================================================
    museaali_id: Optional[str] = Field(None, description="System fills this")
    importimise_staatus: Optional[str] = Field(None, description="System fills this")
    kommentaar: Optional[str] = Field(None, description="System fills this")

    # ========================================================================
    # NUMBER STRUCTURE (columns 4-12)
    # ========================================================================
    acr: str = Field(..., description="Archive code, e.g., 'VBM'", pattern=r"^[A-Z]{2,4}$")
    trt: str = Field("_", description="Separator, always '_'", pattern=r"^_$")
    trs: int = Field(..., description="Main series number", ge=1)
    trj: Optional[int] = Field(None, description="Sub-series number", ge=1)
    trl: Optional[str] = Field(None, description="Series letter")
    kt: Optional[str] = Field(None, description="Collection code")
    ks: Optional[int] = Field(None, description="Collection series", ge=1)
    kj: Optional[int] = Field(None, description="Collection sub-series", ge=1)
    kl: Optional[str] = Field(None, description="Collection letter")

    # ========================================================================
    # BASIC INFORMATION (columns 13-16)
    # ========================================================================
    nimetus: str = Field(..., description="Object name/title", min_length=1)
    pysiasukoht: Optional[str] = Field(None, description="Permanent location from MUIS tree")
    tulmelegend: Optional[str] = Field(None, description="Display legend/caption")
    originaal: Optional[Literal["y", ""]] = Field("", description="Is original? 'y' or empty")

    # ========================================================================
    # ACQUISITION (columns 17-21)
    # ========================================================================
    vastuvotu_nr: Optional[str] = Field(None, description="Acquisition act number")
    esmane_yldinfo: Optional[str] = Field(None, description="Initial general info")
    kogusse_registreerimise_aeg: Optional[str] = Field(
        None, description="Registration date, format: pp.kk.aaaa", pattern=r"^\d{2}\.\d{2}\.\d{4}$"
    )
    yleandja: Optional[str] = Field(
        None, description="Donor/transferor (Lastname, Firstname format or MuIS admin ID)"
    )
    muuseumile_omandamise_viis: Optional[str] = Field(None, description="Acquisition method")

    # ========================================================================
    # MEASUREMENTS (columns 22-33) - Up to 4 measurement sets
    # ========================================================================
    parameeter_1: Optional[str] = None
    yhik_1: Optional[str] = None
    vaartus_1: Optional[float] = None

    parameeter_2: Optional[str] = None
    yhik_2: Optional[str] = None
    vaartus_2: Optional[float] = None

    parameeter_3: Optional[str] = None
    yhik_3: Optional[str] = None
    vaartus_3: Optional[float] = None

    parameeter_4: Optional[str] = None
    yhik_4: Optional[str] = None
    vaartus_4: Optional[float] = None

    # ========================================================================
    # MATERIALS (columns 34-40) - Up to 3 materials with comments
    # ========================================================================
    materjal_1: Optional[str] = None
    materjali_1_kommentaar: Optional[str] = None

    materjal_2: Optional[str] = None
    materjali_2_kommentaar: Optional[str] = None

    materjal_3: Optional[str] = None
    materjali_3_kommentaar: Optional[str] = None

    varvus: Optional[str] = Field(None, description="Color")

    # ========================================================================
    # TECHNIQUES (columns 41-47) - Up to 3 techniques with comments
    # ========================================================================
    tehnika_1: Optional[str] = None
    tehnika_1_kommentaar: Optional[str] = None

    tehnika_2: Optional[str] = None
    tehnika_2_kommentaar: Optional[str] = None

    tehnika_3: Optional[str] = None
    tehnika_3_kommentaar: Optional[str] = None

    # ========================================================================
    # NATURE/TYPE (columns 48-49)
    # ========================================================================
    olemus_1: Optional[str] = Field(None, description="Primary nature/type")
    olemus_2: Optional[str] = Field(None, description="Secondary nature/type")

    # ========================================================================
    # REFERENCES (columns 50-51)
    # ========================================================================
    viite_tyyp: Optional[str] = Field(None, description="Reference type")
    viite_vaartus: Optional[str] = Field(None, description="Reference value")

    # ========================================================================
    # ARCHAEOLOGY & ARCHIVE (columns 52-55)
    # ========================================================================
    leiukontekst: Optional[str] = Field(None, description="Find context")
    leiu_liik: Optional[str] = Field(None, description="Find type")
    pealkirja_keel: Optional[str] = Field(None, description="Title language")
    ainese_keel: Optional[str] = Field(None, description="Content language")

    # ========================================================================
    # CONDITION (columns 56-57)
    # ========================================================================
    seisund: Optional[str] = Field(None, description="Condition state")
    kahjustused: Optional[str] = Field(None, description="Damage description")

    # ========================================================================
    # EVENT 1 (columns 58-68) - 11 fields
    # ========================================================================
    syndmuse_liik_1: Optional[str] = None
    toimumiskoha_tapsustus_kohanimi_1: Optional[str] = None
    toimumiskoha_tapsustus_selgitus_1: Optional[str] = None
    dateering_algus_1: Optional[str] = None
    on_ekr_1: Optional[Literal["y", ""]] = ""
    dateeringu_lopp_1: Optional[str] = None
    riik_1: Optional[str] = None
    eesti_admin_yksus_1: Optional[str] = None
    osaleja_1: Optional[str] = None
    osaleja_roll_1: Optional[str] = None
    kihelkond_1: Optional[str] = None

    # ========================================================================
    # EVENT 2 (columns 69-79) - 11 fields
    # ========================================================================
    syndmuse_liik_2: Optional[str] = None
    toimumiskoha_tapsustus_kohanimi_2: Optional[str] = None
    toimumiskoha_tapsustus_selgitus_2: Optional[str] = None
    dateering_algus_2: Optional[str] = None
    on_ekr_2: Optional[Literal["y", ""]] = ""
    dateeringu_lopp_2: Optional[str] = None
    riik_2: Optional[str] = None
    eesti_admin_yksus_2: Optional[str] = None
    osaleja_2: Optional[str] = None
    osaleja_roll_2: Optional[str] = None
    kihelkond_2: Optional[str] = None

    # ========================================================================
    # VISIBILITY (columns 80-81)
    # ========================================================================
    avalik: Optional[Literal["y", ""]] = Field("", description="Is public? 'y' or empty")
    avalikusta_praegused_andmed: Optional[Literal["y", ""]] = Field(
        "", description="Publish current data? 'y' or empty"
    )

    # ========================================================================
    # DESCRIPTIONS (columns 82-85) - Up to 2 text descriptions
    # ========================================================================
    teksti_tyyp_1: Optional[str] = None
    tekst_1: Optional[str] = None

    teksti_tyyp_2: Optional[str] = None
    tekst_2: Optional[str] = None

    # ========================================================================
    # ALTERNATIVE NAMES (columns 86-87)
    # ========================================================================
    nimetuse_tyyp: Optional[str] = None
    alt_nimetus: Optional[str] = None

    # ========================================================================
    # ALTERNATIVE NUMBERS (columns 88-89)
    # ========================================================================
    numbri_tyyp: Optional[str] = None
    alt_number: Optional[str] = None

    # ========================================================================
    # VALIDATORS
    # ========================================================================

    @model_validator(mode="after")
    def validate_measurement_dependencies(self) -> "MuisMuseaal":
        """Validate measurement field dependencies"""
        for i in range(1, 5):
            parameeter = getattr(self, f"parameeter_{i}")
            yhik = getattr(self, f"yhik_{i}")
            vaartus = getattr(self, f"vaartus_{i}")

            # If value filled, parameter required
            if vaartus and not parameeter:
                raise ValueError(f"parameeter_{i} required when vaartus_{i} is filled")

            # If parameter filled, unit usually required (some exceptions)
            if parameeter and not yhik:
                # TODO: Check if this parameter allows missing unit
                pass

            # If parameter filled, value required
            if parameeter and not vaartus:
                raise ValueError(f"vaartus_{i} required when parameeter_{i} is filled")

        return self

    @model_validator(mode="after")
    def validate_material_dependencies(self) -> "MuisMuseaal":
        """Validate material comment dependencies"""
        for i in range(1, 4):
            materjal = getattr(self, f"materjal_{i}")
            kommentaar = getattr(self, f"materjali_{i}_kommentaar")

            # If comment filled, material required
            if kommentaar and not materjal:
                raise ValueError(f"materjal_{i} required when kommentaar is filled")

        return self

    @model_validator(mode="after")
    def validate_technique_dependencies(self) -> "MuisMuseaal":
        """Validate technique comment dependencies"""
        for i in range(1, 4):
            tehnika = getattr(self, f"tehnika_{i}")
            kommentaar = getattr(self, f"tehnika_{i}_kommentaar")

            # If comment filled, technique required
            if kommentaar and not tehnika:
                raise ValueError(f"tehnika_{i} required when kommentaar is filled")

        return self

    @model_validator(mode="after")
    def validate_event_1_dependencies(self) -> "MuisMuseaal":
        """Validate Event 1 field dependencies"""
        # If osaleja filled, role required
        if self.osaleja_1 and not self.osaleja_roll_1:
            raise ValueError("osaleja_roll_1 required when osaleja_1 is filled")

        # If kohanimi filled, selgitus required
        if self.toimumiskoha_tapsustus_kohanimi_1 and not self.toimumiskoha_tapsustus_selgitus_1:
            raise ValueError("selgitus_1 required when kohanimi_1 is filled")

        # If dateering_lopp filled, dateering_algus required
        if self.dateeringu_lopp_1 and not self.dateering_algus_1:
            raise ValueError("dateering_algus_1 required when dateering_lopp_1 is filled")

        # If admin_yksus or kihelkond filled, riik must be 'Eesti'
        if (self.eesti_admin_yksus_1 or self.kihelkond_1) and self.riik_1 != "Eesti":
            self.riik_1 = "Eesti"

        return self

    @model_validator(mode="after")
    def validate_event_2_dependencies(self) -> "MuisMuseaal":
        """Validate Event 2 field dependencies (same as Event 1)"""
        if self.osaleja_2 and not self.osaleja_roll_2:
            raise ValueError("osaleja_roll_2 required when osaleja_2 is filled")

        if self.toimumiskoha_tapsustus_kohanimi_2 and not self.toimumiskoha_tapsustus_selgitus_2:
            raise ValueError("selgitus_2 required when kohanimi_2 is filled")

        if self.dateeringu_lopp_2 and not self.dateering_algus_2:
            raise ValueError("dateering_algus_2 required when dateering_lopp_2 is filled")

        if (self.eesti_admin_yksus_2 or self.kihelkond_2) and self.riik_2 != "Eesti":
            self.riik_2 = "Eesti"

        return self

    @model_validator(mode="after")
    def validate_description_dependencies(self) -> "MuisMuseaal":
        """Validate description field dependencies"""
        # Description 1
        if self.teksti_tyyp_1 and not self.tekst_1:
            raise ValueError("tekst_1 required when teksti_tyyp_1 is filled")
        if self.tekst_1 and not self.teksti_tyyp_1:
            raise ValueError("teksti_tyyp_1 required when tekst_1 is filled")

        # Description 2
        if self.teksti_tyyp_2 and not self.tekst_2:
            raise ValueError("tekst_2 required when teksti_tyyp_2 is filled")
        if self.tekst_2 and not self.teksti_tyyp_2:
            raise ValueError("teksti_tyyp_2 required when tekst_2 is filled")

        return self

    @model_validator(mode="after")
    def validate_alternative_name_dependencies(self) -> "MuisMuseaal":
        """Validate alternative name dependencies"""
        if self.nimetuse_tyyp and not self.alt_nimetus:
            raise ValueError("alt_nimetus required when nimetuse_tyyp is filled")
        if self.alt_nimetus and not self.nimetuse_tyyp:
            raise ValueError("nimetuse_tyyp required when alt_nimetus is filled")

        return self

    @model_validator(mode="after")
    def validate_alternative_number_dependencies(self) -> "MuisMuseaal":
        """Validate alternative number dependencies"""
        if self.numbri_tyyp and not self.alt_number:
            raise ValueError("alt_number required when numbri_tyyp is filled")
        if self.alt_number and not self.numbri_tyyp:
            raise ValueError("numbri_tyyp required when alt_number is filled")

        return self

    @model_validator(mode="after")
    def validate_condition_damage_dependency(self) -> "MuisMuseaal":
        """If condition is 'halb' or 'väga halb', kahjustused is required"""
        if self.seisund in ["halb", "väga halb"] and not self.kahjustused:
            raise ValueError("kahjustused required when seisund is 'halb' or 'väga halb'")

        return self

    @model_validator(mode="after")
    def validate_reference_dependency(self) -> "MuisMuseaal":
        """If reference value filled, type is required"""
        if self.viite_vaartus and not self.viite_tyyp:
            raise ValueError("viite_tyyp required when viite_vaartus is filled")

        return self

    @model_validator(mode="after")
    def validate_archaeology_dependency(self) -> "MuisMuseaal":
        """If leiu_liik filled, leiukontekst is required"""
        if self.leiu_liik and not self.leiukontekst:
            raise ValueError("leiukontekst required when leiu_liik is filled")

        return self

    class Config:
        validate_assignment = True
        use_enum_values = True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_muis_header() -> List[List[str]]:
    """
    Generate the 3-row MUIS CSV header structure.

    Returns:
        List of 3 lists representing header rows (metadata, column names, validation rules)
    """
    # Row 1: Metadata/groupings (simplified - some cells merge in Excel)
    row_1 = [
        "",
        "",
        "",
        "Number",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "Nimetus",
        "Püsiasukoht",
        "Tulmelegend",
        "Originaal ?",
        "Vastuvõtt",
        "",
        "",
        "",
        "",
        "Mõõdud",
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
        "Materjal 1",
        "Materjali 1 kommentaar",
        "Materjal 2",
        "Materjali 2 kommentaar",
        "Materjal 3",
        "Materjali 3 kommentaar",
        "Värvus",
        "Tehnika 1",
        "Tehnika 1 kommentaar",
        "Tehnika 2",
        "Tehnika 2 kommentaar",
        "Tehnika 3",
        "Tehnika 3 kommentaar",
        "Olemus 1",
        "Olemus 2",
        "Viited",
        "",
        "Arheoloogiline museaal",
        "",
        "Arhiiv",
        "",
        "Seisund",
        "Kahjustused",
        "Museaal sündmuses 1",
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
        "Museaal sündmuses 2",
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
        "Avalik?",
        "Avalikusta praegused andmed?",
        "Kirjeldus",
        "",
        "",
        "",
        "Teised nimetused",
        "",
        "Teised numbrid",
        "",
    ]

    # Row 2: Column names (Estonian)
    row_2 = [
        "museaali_ID",
        "Importimise staatus",
        "Kommentaar",
        "Acr",
        "Trt",
        "Trs",
        "Trj",
        "Trl",
        "Kt",
        "Ks",
        "Kj",
        "Kl",
        "",
        "",
        "",
        "",
        "Vastuvõtu nr",
        "Esmane üldinfo",
        "Kogusse registreerimise aeg",
        "Üleandja",
        "Muuseumile omandamise viis",
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
        "",
        "",
        "",
        "Viite tüüp",
        "Väärtus",
        "Leiukontekst",
        "Leiu liik",
        "Pealkirja keel",
        "Ainese keel",
        "",
        "",
        "Sündmuse liik",
        "Toimumiskoha täpsustus: kohanimi",
        "Toimumiskoha täpsustus: selgitus",
        "Dateering/ dateeringu algus",
        "On ekr",
        "Dateeringu lõpp",
        "Riik",
        "Eesti admin üksus",
        "Osaleja",
        "Osaleja roll",
        "Kihelkond",
        "Sündmuse liik",
        "Toimumiskoha täpsustus: kohanimi",
        "Toimumiskoha täpsustus: selgitus",
        "Dateering/ dateeringu algus",
        "On ekr",
        "Dateeringu lõpp",
        "Riik",
        "Eesti admin üksus",
        "Osaleja",
        "Osaleja roll",
        "Kihelkond",
        "",
        "",
        "Teksti tüüp 1",
        "Tekst 1",
        "Teksti tüüp 2",
        "Tekst 2",
        "Nimetuse tüüp",
        "Nimetus",
        "Numbri tüüp",
        "Number",
    ]

    # Row 3: Validation rules (simplified - full text in reference file)
    row_3 = [
        "Täidab süsteem",
        "Täidab süsteem",
        "Täidab süsteem",
        "Peab vastama MuISis olevale ACR-ile",
        "Peab vastama MuISis olevale TRT-le",
        "Peab olema number",
        "Peab olema number",
        "",
        "Peab vastama MuISis olevale KT-le",
        "Peab olema number",
        "Peab olema number",
        "",
        (
            "Peab olema MuISi asukohapuus olemas; "
            "püsiasukoha järgi täidetakse automaatselt jooksev asukoht"
        ),
        "",
        "",
        "y (on originaal) või tühi",
        "",
        "",
        "Vastuvõtuakti kinnitamise aeg; Peab olema kujul pp.kk.aaa",
        "Peab olema MuISis admin osaleja; täidetakse kujul Perekonnanimi, Eesnimi",
        "",
        "Kohustuslik, kui on täidetud väärtus",
        "Enamasti kohustuslik, kui on täidetud parameeter (oleneb parameetrist)",
        "Peab olema number; kohustuslik, kui on täidetud parameeter",
        "Kohustuslik, kui on täidetud väärtus",
        "Enamasti kohustuslik, kui on täidetud parameeter (oleneb parameetrist)",
        "Peab olema number; kohustuslik, kui on täidetud parameeter",
        "Kohustuslik, kui on täidetud väärtus",
        "Enamasti kohustuslik, kui on täidetud parameeter (oleneb parameetrist)",
        "Peab olema number; kohustuslik, kui on täidetud parameeter",
        "Kohustuslik, kui on täidetud väärtus",
        "Enamasti kohustuslik, kui on täidetud parameeter (olenevalt parameetrist)",
        "Peab olema number; kohustuslik, kui on täidetud parameeter",
        "Kohustuslik, kui on täidetud materjali kommentaar",
        "",
        "Kohustuslik, kui on täidetud materjali kommentaar",
        "",
        "Kohustuslik, kui on täidetud materjali kommentaar",
        "",
        "",
        "Kohustuslik, kui on täidetud tehnika kommentaar",
        "",
        "Kohustuslik, kui on täidetud tehnika kommentaar",
        "",
        "Kohustuslik, kui on täidetud tehnika kommentaar",
        "",
        "",
        "",
        "Kohustuslik, kui viite väärtus on täidetud",
        "",
        "Kohustuslik juhul, kui leiu liik täidetud",
        "",
        "",
        "",
        "",
        "",
        'Kohustuslik, kui seisund on "halb" või "väga halb"',
        'Kohustuslik, kui on täidetud mõni teine "Museaal sündmuses 1" andmeväljadest',
        "Kohustuslik, kui toimumiskoha selgitus on täidetud",
        "Kohustuslik, kui toimumiskoha nimi on täidetud",
        (
            "Täidetakse kujul aaaa või kk.aaaa või pp.kk.aaaa; "
            "Käsitletakse täpse dateeringuna, kui dateeringu lõpp ei ole täidetud"
        ),
        "y (on eKr) või tühi (on pKr)",
        (
            "Täidetakse, kui dateeringut soovitakse esitada ajavahemikuna; "
            "Täidetakse kujul aaaa või kk.aaaa või pp.kk.aaaa"
        ),
        'Peab olema "Eesti", kui "Eesti admin üksus" või "Kihelkond" on täidetud',
        "",
        (
            "Peab olema MuISis ajalooline osaleja; "
            "täidetakse kujul Perekonnanimi, Eesnimi VÕI Organisatsiooni nimi (või osaleja ID)"
        ),
        "Kohustuslik, kui osaleja on täidetud",
        "",
        'Kohustuslik, kui on täidetud mõni teine "Museaal sündmuses 2" andmeväljadest',
        "Kohustuslik, kui toimumiskoha selgitus on täidetud",
        "Kohustuslik, kui toimumiskoha nimi on täidetud",
        (
            "Täidetakse kujul aaaa või kk.aaaa või pp.kk.aaaa; "
            "Käsitletakse täpse dateeringuna, kui dateeringu lõpp ei ole täidetud"
        ),
        "y (on eKr) või tühi (on pKr)",
        (
            "Täidetakse, kui dateeringut soovitakse esitada ajavahemikuna; "
            "Täidetakse kujul aaaa või kk.aaaa või pp.kk.aaaa"
        ),
        'Peab olema "Eesti", kui "Eesti admin üksus" või "Kihelkond" on täidetud',
        "",
        (
            "Peab olema MuISis ajalooline osaleja; "
            "täidetakse kujul Perekonnanimi, Eesnimi VÕI Organisatsiooni nimi (või osaleja ID)"
        ),
        "Kohustuslik, kui osaleja on täidetud",
        "",
        "y (on avalik) või tühi",
        "y (avalikusta praegused andmed) või tühi",
        'Kohustuslik, kui on täidetud "Tekst 1"',
        'Kohustuslik, kui on täidetud "Teksti tüüp 1"',
        'Kohustuslik, kui on täidetud "Tekst 2"',
        'Kohustuslik, kui on täidetud "Teksti tüüp 2"',
        'Kohustuslik, kui on täidetud "Nimetus"',
        'Kohustuslik, kui on täidetud "Nimetuse tüüp"',
        'Kohustuslik, kui on täidetud "Number"',
        'Kohustuslik, kui on täidetud "Numbri tüüp"',
    ]

    return [row_1, row_2, row_3]
