from bson import ObjectId
from pydantic import BaseModel, model_validator, field_validator, Field

from domain.models.base_model import (
    Type,
    Updated,
    ExternalUrl,
    CitationsCount,
    Name,
    ExternalId,
    Subject,
    Ranking,
    Address,
)


class DescriptionText(BaseModel):
    TXT_ESTADO_ARTE: str | None
    TXT_OBJETIVOS: str | None
    TXT_PLAN_TRABAJO: str | None
    TXT_PROD_DESTACADA: str | None
    TXT_RETOS: str | None
    TXT_VISION: str | None


class Description(BaseModel):
    description: DescriptionText
    source: str


class Relation(BaseModel):
    id: str | None = Field(default_factory=None, alias="hash")
    hash: str | None = None
    name: str | Name | None = None
    types: list[Type] | None = None
    external_urls: list[ExternalUrl] | None = None

    @field_validator("name")
    @classmethod
    def set_name(cls, value: str) -> str:
        if isinstance(value, Name):
            return value.name
        return value


class Status(BaseModel):
    source: str | None
    status: str | None


class Affiliation(BaseModel):
    id: str = Field(alias="hash")
    hash: str | None = None
    abbreviations: list[str] | None = None
    addresses: list[Address] | Address | None = None
    aliases: list[str] | None = None
    birthdate: str | int | None = None
    citations_count: list[CitationsCount] | None = None
    description: list[Description] | None = None
    external_ids: list[ExternalId] | None = None
    external_urls: list[ExternalUrl] | None = None
    names: list[Name] | None = None
    products_count: int | None = None
    ranking: list[Ranking] | None = None
    relations: list[Relation] | Relation | dict | None = None
    status: list[str] | list[Status] | None = None
    subjects: list[Subject] | None = None
    types: list[Type] | None = None
    updated: list[Updated] | None = None
    year_established: int | None = None

    name: str | None = None
    logo: str | None = None
    affiliations: list[dict | Relation] | None = None
    relations_data: list[Relation] | None = None

    @model_validator(mode="after")
    def get_name(self):  # type: ignore
        es_name = next(filter(lambda x: x.lang == "es", self.names), None)
        self.name = es_name.name if es_name else self.names[0].name
        return self

    class Config:
        json_encoders = {ObjectId: str}
