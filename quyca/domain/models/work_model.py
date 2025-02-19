from typing import Any

from bson import ObjectId
from pydantic import BaseModel, Field

from domain.models.base_model import (
    PyObjectId,
    CitationsCount,
    Type,
    ExternalId,
    ExternalUrl,
    Subject,
    Updated,
    Ranking,
    Publisher,
    APC,
    Author,
    Group,
    Title,
    Affiliation,
    ProductType,
    Name,
)


class BiblioGraphicInfo(BaseModel):
    bibtex: str | None = None
    issue: str | None = None
    pages: str | None = None
    start_page: str | None = None
    end_page: str | None = None
    volume: str | int | None = None


class OpenAccess(BaseModel):
    is_open_access: bool | None = None
    open_access_status: str | None = None
    url: str | None = None
    has_repository_fulltext: bool | None = None


class CitationByYear(BaseModel):
    cited_by_count: int | None
    year: int | None


class Source(BaseModel):
    id: PyObjectId | str | None = None
    name: str | Any | None = None

    issn_l: str | None = None
    is_in_doaj: bool | None = None
    types: list[Type] | None = None
    names: list[Name] | None = None
    scimago_quartile: str | None = None
    serials: dict | None = None
    external_urls: list[ExternalUrl] | None = None
    external_ids: list[ExternalId] | None = None
    ranking: list[Ranking] | None = None
    publisher: Publisher | str | None = None
    apc: APC | None = None
    updated: list[Updated] | None = None

    class Config:
        json_encoders = {ObjectId: str}


class Abstract(BaseModel):
    abstract: dict | None = None
    lang: str | None = None
    provenance: str | None = None
    source: str | None = None


class AutorWork(Author):
    """
    The difference with Author is that in the work the author is marked with a type of author (ex: advisor, co-advisor, author etc..)
    this value is only assigned in the work.
    """

    type: str | None = None


class Work(BaseModel):
    id: PyObjectId = Field(alias="_id")
    abstracts: list[Abstract] | None = None
    apc: APC | None = Field(default_factory=APC)
    authors_count: int | None = Field(default_factory=int, alias="author_count")
    authors: list[AutorWork] | str | None = Field(default_factory=list[AutorWork])
    bibliographic_info: BiblioGraphicInfo | None = None
    citations: list | None = Field(default_factory=list)
    citations_by_year: list[CitationByYear] | None = None
    citations_count: list[CitationsCount] | str | None = None
    date_published: int | None = None
    external_ids: list[ExternalId] | None = None
    external_urls: list[ExternalUrl] | None = None
    groups: list[Group] | str | None = None
    keywords: list | None = None
    open_access: OpenAccess | None = Field(default_factory=OpenAccess)
    ranking: list[Ranking] | str | None = None
    references: list | None = None
    references_count: int | None = None
    source: Source | None = None
    subjects: list[Subject] | str | None = None
    subtitle: str | None = None
    titles: list[Title] | None = None
    types: list[Type] | None = None
    updated: list[Updated] | None = None
    year_published: int | str | None = None
    abstract: dict | None = None
    authors_data: list[Author] | None = None
    affiliations_data: list[Affiliation] | None = None
    countries: str | None = None
    openalex_citations_count: str | int | None = None
    scholar_citations_count: str | int | None = None
    institutions: str | None = None
    departments: str | None = None
    faculties: str | None = None
    groups_ranking: str | None = None
    pages: str | None = None
    start_page: str | None = None
    end_page: str | None = None
    bibtex: str | None = None
    doi: str | None = None
    issue: str | None = None
    language: str | None = None
    open_access_status: str | None = None
    product_types: list[ProductType] | None = None
    publisher: str | None = None
    openalex_types: str | None = None
    scienti_types: str | None = None
    scimago_quartile: str | None = None
    source_apc: str | None = None
    source_data: Source | list[Source] | None = None
    source_name: str | None = None
    source_urls: str | None = None
    title: str | None = None
    volume: str | int | None = None

    class Config:
        json_encoders = {ObjectId: str}
