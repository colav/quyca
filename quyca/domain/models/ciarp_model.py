from dataclasses import dataclass

"""
Domain entity for CIARP records (research products metadata).
"""


@dataclass
class CIARP:
    """Represents a CIARP research product record."""

    academic_unit_code: str
    document_type: str
    identification: str
    year: int
    title: str
    product_country: str

    academic_subunit_code: str | None = None
    language: str | None = None
    journal: str | None = None
    publisher: str | None = None
    doi: str | None = None
    issn: str | None = None
    isbn: str | None = None
    volumen: str | None = None
    issue: str | None = None
    first_page: str | None = None
    last_page: str | None = None
    awarding_entity: str | None = None
    ranking: str | None = None
