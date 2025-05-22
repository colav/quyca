from bson import ObjectId
from pydantic import BaseModel, Field, field_validator, model_validator
from domain.models.base_model import (
    PyObjectId,
    CitationsCount,
    Updated,
    ExternalId,
    Type,
    Identifier,
    Subject,
    Ranking,
    ExternalUrl,
    BirthPlace,
)


class Affiliation(BaseModel):
    id: str | None = None
    name: str | None = None
    position: str | None = None
    start_date: int | str | None = None
    end_date: int | str | None = None
    types: list[Type] | None = Field(default_factory=list)
    external_urls: list[ExternalUrl] | None = Field(default_factory=list)

    @field_validator("start_date")
    @classmethod
    def set_start_date(cls, value: int | str) -> int | str:
        if value == "":
            return -1
        else:
            return value

    @field_validator("end_date")
    @classmethod
    def set_end_date(cls, value: int | str) -> int | str:
        if value == "":
            return -1
        else:
            return value

    class Config:
        json_encoders = {ObjectId: str}


class Degree(BaseModel):
    id: str | None
    date: int | None
    degree: str | None
    institutions: list | None = Field(default_factory=list)
    source: str | None


class Institution(BaseModel):
    id: str | None
    country_code: str | None
    country_id: str | None
    display_name: str | None
    lineage: list[str] | None = Field(default_factory=list)
    ror: str | None
    type: str | None


class RelatedWork(BaseModel):
    id: str | Identifier | None
    institutions: list[Institution] | None = Field(default_factory=list)
    provenance: str | None
    source: str | None
    year: int | None = None


class Person(BaseModel):
    id: str | PyObjectId = Field(alias="_id")
    affiliations: list[Affiliation] | None = Field(default_factory=list)
    aliases: list[str] | None = Field(default_factory=list)
    birthdate: int | str | None = None
    birthplace: BirthPlace | None = None
    citations_count: list[CitationsCount] | None = Field(default_factory=list)
    degrees: list[Degree] | None = Field(default_factory=list)
    external_ids: list[ExternalId] | None = Field(default_factory=list)
    first_names: list[str] | None = Field(default_factory=list)
    full_name: str | None = Field(serialization_alias="name")
    initials: str | None = None
    keywords: list | None = Field(default_factory=list)
    last_names: list[str] | None = Field(default_factory=list)
    marital_status: str | None = None
    products_count: int | None = None
    ranking: list[Ranking] | None = Field(default_factory=list)
    related_works: list[RelatedWork] | None = Field(default_factory=list)
    sex: str | None = None
    subjects: list[Subject] | None = Field(default_factory=list)
    updated: list[Updated] | None = Field(default_factory=list)

    affiliations_data: list[Affiliation] | None = None
    logo: str | None = None

    @field_validator("external_ids")
    @classmethod
    def delete_sensitive_external_ids(cls, value: list) -> list:
        return list(
            filter(
                lambda external_id: external_id.source
                not in ["Cédula de Ciudadanía", "Cédula de Extranjería", "Passport"],
                value,
            )
        )

    class Config:
        json_encoders = {ObjectId: str}

    @model_validator(mode="after")
    def get_logo(self) -> "Person":
        if self.affiliations_data:
            self.logo = next(filter(lambda x: x.source == "logo", self.affiliations_data[0].external_urls)).url  # type: ignore
        return self
