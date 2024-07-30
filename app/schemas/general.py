from typing import TypeVar, Any, Generic

from typing_extensions import Self

from pydantic import BaseModel, Field, model_validator, field_validator
from odmantic.bson import BSON_TYPES_ENCODERS
from core.config import settings

DBSchemaType = TypeVar("DBSchemaType", bound=BaseModel)


class CitationsCount(BaseModel):
    source: str | None = None
    count: int | None = None

class Type(BaseModel):
    source: str
    type: str | None


class Updated(BaseModel):
    time: int | None
    source: str | None


class Identifier(BaseModel):
    COD_RH: str | None = None
    COD_PRODUCTO: str | None = None


class ExternalId(BaseModel):
    id: str | int | list[str] | Identifier | None = None
    source: str | None
    provenance: str | None = None

    @field_validator("id", mode="after")
    def id_validator(cls, v: str | int | list[str] | dict | Identifier):
        if isinstance(v, dict):
            id = []
            id += [v.get("COD_RH")] if isinstance(v.get("COD_RH", None), str) else []
            id += (
                [v.get("COD_PRODUCTO")]
                if isinstance(v.get("COD_PRODUCTO", None), str)
                else []
            )
            return "-".join(id)
        if isinstance(v, Identifier):
            id = []
            id += [v.COD_RH] if isinstance(v.COD_RH, str) else []
            id += [v.COD_PRODUCTO] if isinstance(v.COD_PRODUCTO, str) else []
            return "-".join(id)
        return v


class ExternalURL(BaseModel):
    url: str | int | None
    source: str | None


class Name(BaseModel):
    name: str | None
    lang: str | None


class Status(BaseModel):
    source: str | None
    status: str | None


class QueryBase(BaseModel):
    max: int = Field(10, gt=0)
    page: int = Field(1, gt=0)
    keywords: str | None = ""
    sort: str = ""

    skip: int | None = None

    @field_validator("max")
    def limit_validator(cls, v):
        return v if v < 250 else 250

    @model_validator(mode="after")
    def skip_validator(self) -> Self:
        self.skip = self.skip if self.skip else (self.page - 1) * self.max
        return self

    @property
    def get_search(self) -> dict[str, Any]:
        return {}

    def next_query(self) -> str:
        return (
            f"max={self.max}&page={self.page + 1}&"
            f"sort={self.sort}&keywords={self.keywords}"
        )

    def previous_query(self) -> str | None:
        return (
            f"max={self.max}&page={self.page - 1}&"
            f"sort={self.sort}&keywords={self.keywords}"
        )

    def get_cursor(self, path: str, total: int = 0) -> dict[str, str]:
        """
        Compute the cursor for the given path and query.
        """
        return {
            "next": (
                f"{settings.APP_DOMAIN}{path}?{self.next_query()}"
                if self.skip + self.max < total
                else None
            ),
            "previous": (
                f"{settings.APP_DOMAIN}{path}?{self.previous_query()}"
                if self.page > 1
                else None
            ),
        }


class GeneralMultiResponse(BaseModel, Generic[DBSchemaType]):
    total_results: int | None = None
    data: list[DBSchemaType] | None = Field(default_factory=list)
    count: int | None = None
    page: int | None = None

    model_config = {"json_encoders": BSON_TYPES_ENCODERS}
