from typing import Any
from itertools import chain

from pydantic import BaseModel, Field, field_validator, model_validator

from schemas.general import Type, Updated, ExternalId, ExternalURL, QueryBase
from core.config import settings


class Title(BaseModel):
    title: str | None = None
    lang: str | None = None
    source: str | None = None


class ProductType(BaseModel):
    name: str | None = None
    source: str | None = None


class BiblioGraphicInfo(BaseModel):
    bibtex: str | Any | None
    end_page: str | Any | None
    volume: str | int | None
    issue: str | Any | None
    open_access_status: str | Any | None
    pages: str | Any | None
    start_page: str | Any | None
    is_open_access: bool | Any | None
    open_access_status: str | None


class CitationsCount(BaseModel):
    source: str
    count: int


class Name(BaseModel):
    name: str
    lang: str


class Affiliation(BaseModel):
    id: str | None = None
    name: str | None = None
    types: list[Type] | None = Field(default_factory=list)


class Author(BaseModel):
    id: str
    full_name: str
    affiliations: list[Affiliation] | None = Field(default_factory=list)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    sex: str | None = ""


class Source(BaseModel):
    id: str | None = None
    name: str | Any | None = None
    scimago_quartile: str | None = ""
    serials: Any | None = ""


class SubjectEmbedded(BaseModel):
    id: str
    name: str | None
    level: int


class Subject(BaseModel):
    source: str
    subjects: list[SubjectEmbedded] | None = Field(default_factory=list)


class CitationByYear(BaseModel):
    cited_by_count: int | None
    year: int | None


class CitationsCount(BaseModel):
    source: str | None
    count: int | None


class Ranking(BaseModel):
    date: str | int
    provenance: str
    rank: str | None
    source: str


class Group(BaseModel):
    id: str | None = None
    name: str | None = None


class WorkBase(BaseModel):
    id: str | None
    title: str | None = None
    authors: list[Author] = Field(default_factory=list)

    @field_validator("authors")
    @classmethod
    def unic_authors_by_id(cls, v: list[Author]):
        seen = set()
        unique_authors = []
        for author in v:
            if author.id not in seen:
                seen.add(author.id)
                unique_authors.append(author)
        return unique_authors

    source: Source | None = Field(default_factory=dict)
    citations_count: list[CitationsCount] | int = Field(default_factory=list)
    subjects: list[Subject] | list[dict[str, str]]


class WorkSearch(WorkBase):
    product_type: list[ProductType] | ProductType | None = Field(default_factory=list)
    types: list[Type] = Field(default_factory=list, exclude=True)

    @model_validator(mode="after")
    def get_types(self):
        types = list(
            map(lambda x: ProductType(name=x.type, source=x.source), self.types)
        )
        hierarchy = ["openalex", "scienti", "minciencias", "scholar"]
        v = sorted(types, key=lambda x: hierarchy.index(x.source))
        self.product_type = v[0] if v else None
        return self

    @field_validator("citations_count")
    @classmethod
    def sort_citations_count(cls, v: list[CitationsCount]):
        return list(sorted(v, key=lambda x: x.count, reverse=True))


class WorkListApp(WorkSearch):
    titles: list[Title] = Field(default_factory=list, exclude=True)
    year_published: int | str | None = None
    open_access_status: str | None = ""

    bibliographic_info: BiblioGraphicInfo = Field(exclude=True)

    num_authors: int | None = None

    @model_validator(mode="after")
    def get_title(self):
        def hierarchy_index(x: Title):
            return hierarchy.index(x.source) if x.source in hierarchy else 100

        hierarchy = ["openalex", "scholar", "scienti", "minciencias", "ranking"]
        self.title = sorted(self.titles, key=hierarchy_index)[0].title
        return self

    @model_validator(mode="after")
    def get_biblio_graphic_info(self):
        self.open_access_status = self.bibliographic_info.open_access_status or ""
        self.bibliographic_info = None
        return self

    @model_validator(mode="after")
    def get_first_ten_authors(self):
        if authors := len(self.authors) > 10:
            self.authors = self.authors[:10]
            self.num_authors = authors
        return self


    external_ids: list[ExternalId] | list[dict[str, Any]] = Field(default_factory=list)


class WorkProccessed(WorkListApp):
    abstract: str | None = ""

    language: str | None = ""
    volume: str | int | None = None
    issue: str | None = None

    @model_validator(mode="after")
    def get_biblio_graphic_info(self):
        self.open_access_status = self.bibliographic_info.open_access_status
        self.volume = self.bibliographic_info.volume
        self.issue = self.bibliographic_info.issue
        self.bibliographic_info = None
        return self

    # @field_validator("subjects")
    # @classmethod
    # def get_openalex_source(cls, v: list[Subject]):
    #     open_alex_subjects = list(filter(lambda x: x.source == "openalex", v))
    #     maped_embedded_subjects = list(map(lambda x: x.subjects, open_alex_subjects))
    #     return (
    #         list(map(lambda x: {"name": x.name, "id": x.id}, *maped_embedded_subjects))
    #         if maped_embedded_subjects
    #         else []
    #     )

    @model_validator(mode="after")
    def get_first_ten_authors(self):
        return self

    external_urls: list[ExternalURL] | None = Field(default_factory=list)

    # Machete
    @model_validator(mode="before")
    @classmethod
    def get_openalex_url(cls, data: dict[str, Any]):
        openalex = next(
            filter(lambda x: x["source"] == "openalex", data["external_ids"]), None
        )
        if openalex:
            data["external_urls"] += [
                ExternalURL(url=openalex["id"], source="openalex")
            ]
        return data

    @field_validator("external_ids")
    @classmethod
    def append_urls_external_ids(cls, v: list[ExternalId]):
        return list(
            map(
                lambda x: (
                    {
                        "id": x.id,
                        "source": x.source,
                        "url": settings.EXTERNAL_IDS_MAP.get(x.source, "").format(
                            id=x.id
                        ),
                    }
                ),
                filter(lambda x: x.source in settings.EXTERNAL_IDS_MAP, v),
            )
        )

    @field_validator("citations_count")
    @classmethod
    def get_citations_count(cls, v: list[CitationsCount]):
        return v[0].count if v else 0


class WorkCsv(WorkProccessed):
    date_published: int | float | str | None = None
    start_page: str | None = None
    end_page: str | None = None
    doi: str | None = ""
    source_name: str | None = ""
    subject_names: str = ""
    scimago_quartile: str | None = ""

    @model_validator(mode="after")
    def get_doi_source_name(self):
        doi = next(
            filter(lambda x: x["source"] == "doi", self.external_ids),
            {"id": ""},
        )
        self.doi = doi["id"]
        self.source_name = self.source.name or ""
        self.scimago_quartile = self.source.scimago_quartile or ""
        return self

    @field_validator("external_ids")
    @classmethod
    def append_urls_external_ids(cls, v: list[ExternalId]):
        scienti = list(filter(lambda x: x.provenance == "scienti", v))
        v += (
            [ExternalId(id=f"{scienti[0].id}-{scienti[1].id}", source="scienti")]
            if len(scienti) == 2
            else []
        )

        return list(
            map(
                lambda x: (
                    {
                        "id": x.id,
                        "source": x.source,
                        "url": settings.EXTERNAL_IDS_MAP.get(x.source, "").format(
                            id=x.id
                        ),
                    }
                ),
                filter(lambda x: x.source in settings.EXTERNAL_IDS_MAP, v),
            )
        )

    @model_validator(mode="after")
    def get_biblio_graphic_info(self):
        self.open_access_status = self.bibliographic_info.open_access_status
        self.volume = self.bibliographic_info.volume
        self.issue = self.bibliographic_info.issue
        self.start_page = self.bibliographic_info.start_page
        self.end_page = self.bibliographic_info.end_page
        self.bibliographic_info = None
        self.subject_names = " | ".join(
            chain.from_iterable(
                map(
                    lambda x: [
                        sub.name for sub in x.subjects if x.source == "openalex"
                    ],
                    self.subjects,
                )
            )
        )
        return self


class Work(BaseModel):
    id: str
    updated: list[Updated] | None = Field(default_factory=list)
    subtitle: str
    abstract: str
    keywords: list[str] | None = Field(default_factory=list)
    types: list[Type] | None = Field(default_factory=list)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    external_urls: list[ExternalURL] | None = Field(default_factory=list)
    date_published: int | None = None
    year_published: int | str | None = None
    bibligraphic_info: BiblioGraphicInfo | None = Field(default_factory=list)
    references_count: int | None
    references: list[Any] | None = Field(default_factory=list)
    citations_count: list[CitationsCount] | None = Field(default_factory=list)
    author_count: int | None = None
    authors: list[Author] = Field(default_factory=list)
    titles: list[Title] = Field(default_factory=list)
    source: Source | None = Field(default_factory=dict)
    ranking: list[Ranking] | None = Field(default_factory=list)
    subjects: list[Subject] | None = Field(default_factory=list)
    citations_by_year: list[CitationByYear] | None = Field(default_factory=list)
    groups: list[Group] | None = Field(default_factory=list)


class WorkQueryParams(QueryBase):
    start_year: int | None = None
    end_year: int | None = None
    sort: str | None = "title"
    type: str | None = None

    def get_filter(self) -> dict[str, Any]:
        return {
            "start_year": self.start_year,
            "end_year": self.end_year,
            "type": self.type,
        }
