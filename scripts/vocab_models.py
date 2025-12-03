"""
Vocabulary Models with Validation

Pydantic models for validating vocabulary data structures supporting 1-4 column formats.

Schema Evolution:
- 1 column: term
- 2 columns: term + term_id
- 3 columns: term + term_id + parent_id
- 4 columns: term + term_id + parent_id + muis_id

Example:
    from vocab_models import VocabularyEntry1, VocabularyEntry4

    # 1-column vocabulary
    entry = VocabularyEntry1(term="kollane")

    # 4-column vocabulary
    entry = VocabularyEntry4(
        term="kollane",
        term_id="1522",
        parent_id="3",
        muis_id="123"
    )
"""

from pydantic import BaseModel, Field


class VocabularyEntry1(BaseModel):
    """
    Single-column vocabulary entry.

    Validation:
    - term: Required, non-empty string

    Example:
        >>> entry = VocabularyEntry1(term="kollane")
        >>> entry.term
        'kollane'
    """

    term: str = Field(..., description="Term name", min_length=1)

    class Config:
        """Pydantic config"""

        extra = "forbid"


class VocabularyEntry2(BaseModel):
    """
    Two-column vocabulary entry (term + term_id).

    Validation:
    - term: Required, non-empty string
    - term_id: Required, non-empty string (ID from source system)

    Example:
        >>> entry = VocabularyEntry2(term="kollane", term_id="1522")
        >>> entry.term_id
        '1522'
    """

    term: str = Field(..., description="Term name", min_length=1)
    term_id: str = Field(..., description="Term identifier", min_length=1)

    class Config:
        """Pydantic config"""

        extra = "forbid"


class VocabularyEntry3(BaseModel):
    """
    Three-column vocabulary entry (term + term_id + parent_id).

    Validation:
    - term: Required, non-empty string
    - term_id: Required, non-empty string
    - parent_id: Required, non-empty string (enables hierarchical structure)

    Example:
        >>> entry = VocabularyEntry3(
        ...     term="briljantkollane",
        ...     term_id="1524",
        ...     parent_id="1522"
        ... )
        >>> entry.parent_id
        '1522'
    """

    term: str = Field(..., description="Term name", min_length=1)
    term_id: str = Field(..., description="Term identifier", min_length=1)
    parent_id: str = Field(..., description="Parent term ID (for hierarchy)", min_length=1)

    class Config:
        """Pydantic config"""

        extra = "forbid"


class VocabularyEntry4(BaseModel):
    """
    Four-column vocabulary entry (term + term_id + parent_id + muis_id).

    Validation:
    - term: Required, non-empty string
    - term_id: Required, non-empty string
    - parent_id: Required, non-empty string (hierarchical reference)
    - muis_id: Required, non-empty string (MUIS internal reference)

    Example:
        >>> entry = VocabularyEntry4(
        ...     term="briljantkollane",
        ...     term_id="1524",
        ...     parent_id="1522",
        ...     muis_id="123"
        ... )
        >>> entry.muis_id
        '123'
    """

    term: str = Field(..., description="Term name", min_length=1)
    term_id: str = Field(..., description="Term identifier", min_length=1)
    parent_id: str = Field(..., description="Parent term ID (for hierarchy)", min_length=1)
    muis_id: str = Field(..., description="MUIS internal identifier", min_length=1)

    class Config:
        """Pydantic config"""

        extra = "forbid"


class VocabularyMetadata(BaseModel):
    """
    Metadata for vocabulary JSON output.

    Tracks source file, column count, entry count, and usage information.

    Example:
        >>> metadata = VocabularyMetadata(
        ...     source_file="tabel_1.txt",
        ...     column_count=4,
        ...     entry_count=411,
        ...     vocabulary_name="techniques"
        ... )
        >>> metadata.source_file
        'tabel_1.txt'
    """

    source_file: str = Field(..., description="Original source filename")
    column_count: int = Field(..., description="Number of columns in source", ge=1, le=4)
    entry_count: int = Field(..., description="Total entries in vocabulary", ge=0)
    vocabulary_name: str = Field(..., description="Name of vocabulary (lowercase)", min_length=1)

    class Config:
        """Pydantic config"""

        extra = "forbid"


# Type union for any vocabulary entry
VocabularyEntry = VocabularyEntry1 | VocabularyEntry2 | VocabularyEntry3 | VocabularyEntry4
