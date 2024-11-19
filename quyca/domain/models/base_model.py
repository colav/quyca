from typing import Generator

from pydantic import BaseModel, field_validator, Field, conint
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls) -> Generator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str | ObjectId, other: None) -> str:
        if value == "":
            return str(value)
        if not ObjectId.is_valid(value):
            raise ValueError(f"Invalid ObjectId '{str(value)}'")
        return str(value)


class CitationsCount(BaseModel):
    source: str | None
    count: int | None
    provenance: str | None = None


class Type(BaseModel):
    type_class: str | None = None
    code: str | None = None
    level: int | None = None
    provenance: str | None = None
    source: str | None
    type: str | None


class Updated(BaseModel):
    time: int | None
    source: str | None


class Identifier(BaseModel):
    COD_RH: str | None
    COD_PRODUCTO: str | None = None


class ExternalId(BaseModel):
    id: str | int | list[str] | Identifier | None = None
    provenance: str | None = None
    source: str | None = None

    @field_validator("id", mode="after")
    @classmethod
    def id_validator(cls, value: str | int | list[str] | Identifier | None) -> str | int | list[str] | None:
        if isinstance(value, Identifier):
            if value.COD_PRODUCTO and value.COD_RH:
                value = value.COD_RH + "-" + value.COD_PRODUCTO
            else:
                value = value.COD_RH
        return value

    def __hash__(self) -> int:
        return hash(str(self.id) + str(self.source))


class ExternalUrl(BaseModel):
    url: str | int | None = None
    source: str | None = None
    provenance: str | None = None

    def __hash__(self) -> int:
        return hash(str(self.url) + str(self.source))


class Name(BaseModel):
    name: str | None
    lang: str | None
    source: str | None
    provenance: str | None = None


class Ranking(BaseModel):
    date: int | str | None = None
    from_date: int | str | None = None
    issn: str | None = None
    order: str | int | None = None
    rank: str | int | float | None = None
    source: str | None = None
    to_date: int | str | None = None


class Status(BaseModel):
    source: str | None
    status: str | None


class SubjectContent(BaseModel):
    id: PyObjectId | None = None
    external_ids: list[ExternalId] | None = None
    level: int | None = None
    name: str | None

    class Config:
        json_encoders = {ObjectId: str}


class Subject(BaseModel):
    provenance: str | None = None
    source: str | None
    subjects: list[SubjectContent] | None = None


class Address(BaseModel):
    city: str | None = None
    country: str | None = None
    country_code: str | None = None
    lat: float | str | None = None
    lng: float | str | None = None
    postcode: str | None = None
    state: str | None = None


class Publisher(BaseModel):
    id: str | None = None
    country_code: str | None = None
    name: str | float | None = None


class Paid(BaseModel):
    currency: str | None = None
    provenance: str | None = None
    source: str | None = None
    value: int | None = None
    value_usd: int | None = None


class APC(BaseModel):
    charges: int | None = None
    currency: str | None = None
    paid: Paid | None = None


class QueryParams(BaseModel):
    limit: conint(ge=1, le=250) | None = Field(default=10, alias="max")  # type: ignore
    page: conint(ge=1) | None = 1  # type: ignore
    keywords: str | None = None
    plot: str | None = None
    sort: str | None = "citations_desc"
    product_type: str | None = None
    year: str | None = None
    status: str | None = None
    subject: str | None = None
    country: str | None = None
    groups_ranking: str | None = None
    authors_ranking: str | None = None


class Geography(BaseModel):
    city: str | None = None
    region: str | None = None
    country: str | None = None
    country_code: str | None = None
    latitude: float | str | None = None
    longitude: float | str | None = None


class Affiliation(BaseModel):
    id: PyObjectId | None = None
    name: str | None = None
    types: list[Type] | None = None
    start_date: int | str | None = None
    end_date: int | str | None = None

    ror: str | None = None
    geo: Geography | None = Field(default_factory=Geography)
    addresses: list[Address] | None = None
    position: str | None = None
    ranking: list[Ranking] | None = None
    external_ids: list[ExternalId] | None = None

    class Config:
        json_encoders = {ObjectId: str}


class BirthPlace(BaseModel):
    city: str | None = None
    country: str | None = None
    state: str | None = None


class Author(BaseModel):
    id: PyObjectId | None = None
    affiliations: list[Affiliation] | None = Field(default_factory=list[Affiliation])
    full_name: str | None = None

    birth_country: str | None = None
    age: int | None = None
    birthdate: int | str | None = None
    birthplace: BirthPlace | None = None
    countries: list[str] | None = None
    first_names: list[str] | None = None
    last_names: list[str] | None = None
    sex: str | None = None
    external_ids: list[ExternalId] | None = None
    ranking: list[Ranking] | str | None = None

    @field_validator("external_ids")
    @classmethod
    def delete_sensitive_external_ids(cls, value: list | None) -> list | None:
        if value is None:
            return value
        return list(
            filter(
                lambda external_id: external_id.source
                not in ["Cédula de Ciudadanía", "Cédula de Extranjería", "Passport"],
                value,
            )
        )

    class Config:
        json_encoders = {ObjectId: str}


class Group(BaseModel):
    id: PyObjectId | None = None
    name: str | None

    class Config:
        json_encoders = {ObjectId: str}


class Title(BaseModel):
    lang: str | None
    provenance: str | None = None
    source: str | None
    title: str | None


class ProductType(BaseModel):
    name: str | None = None
    source: str | None = None
