from typing import Generic, TypeVar, Any, Type
from json import loads

from pydantic import BaseModel

from protocols.mongo.repositories.base import RepositoryBase
from schemas.general import QueryBase, GeneralMultiResponse
from core.logging import get_logger

log = get_logger(__name__)


ModelType = TypeVar("ModelType", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType", bound=RepositoryBase)
ParamsType = TypeVar("ParamsType", bound=QueryBase)
SearchType = TypeVar("SearchType", bound=BaseModel)
InfoType = TypeVar("InfoType", bound=BaseModel)


class ServiceBase(Generic[ModelType, RepositoryType, ParamsType, SearchType, InfoType]):
    def __init__(
        self,
        search_class: SearchType,
        info_class: InfoType,
        repository: RepositoryType = None,
    ):
        self.repository = repository
        self.search_class = search_class
        self.info_class = info_class

    def register_repository(self, repository: RepositoryType):
        log.info(f"Registering {repository.__class__.__name__} repository")
        self.repository = repository

    def get_all(self, *, params: ParamsType) -> dict[str, Any]:
        db_objs = self.repository.get_all(
            query={}, skip=params.skip, limit=params.max, sort=params.sort
        )
        total_results = self.repository.count()
        results = GeneralMultiResponse(total_results=total_results)
        results.data = db_objs
        return loads(results.model_dump_json())

    def get_by_id(self, *, id: str) -> Type[InfoType]:
        db_obj = self.repository.get_by_id(id=id)
        return self.info_class.model_validate_json(db_obj)

    def search(self, *, params: ParamsType) -> GeneralMultiResponse[Type[SearchType]]:
        db_objs, count = self.repository.search(
            keywords=params.keywords,
            skip=params.skip,
            limit=params.max,
            sort=params.sort,
            search=params.get_search,
        )
        results = GeneralMultiResponse[Type[SearchType]](total_results=count, page=params.page)
        data = [self.search_class.model_validate_json(obj.model_dump_json()) for obj in db_objs]
        results.data = data
        results.count = len(data)
        return loads(results.model_dump_json(exclude_none=True))
