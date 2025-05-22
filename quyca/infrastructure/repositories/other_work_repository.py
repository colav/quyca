from typing import Generator, Tuple

from bson import ObjectId

from infrastructure.generators import other_work_generator
from domain.models.base_model import QueryParams
from domain.models.other_work_model import OtherWork
from infrastructure.repositories import base_repository
from infrastructure.mongo import database
from domain.exceptions.not_entity_exception import NotEntityException


def get_other_work_by_id(other_work_id: str) -> OtherWork:
    other_work = database["works_misc"].find_one(ObjectId(other_work_id))
    if not other_work:
        raise NotEntityException(f"The other work with id {other_work_id} does not exist.")
    return OtherWork(**other_work)


def get_other_works_by_affiliation(
    affiliation_id: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {
            "$match": {
                "authors.affiliations.id": affiliation_id,
            },
        },
    ]
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works_misc"].aggregate(pipeline)
    return other_work_generator.get(cursor)


def get_other_works_count_by_affiliation(affiliation_id: str) -> int:
    pipeline = get_other_works_by_affiliation_pipeline(affiliation_id)
    pipeline += [{"$count": "total"}]
    return next(database["works_misc"].aggregate(pipeline), {"total": 0}).get("total", 0)


def get_other_works_by_person(
    person_id: str, query_params: QueryParams, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": person_id}},
    ]
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works_misc"].aggregate(pipeline)
    return other_work_generator.get(cursor)


def get_other_works_count_by_person(person_id: str) -> int:
    pipeline = [{"$match": {"authors.id": person_id}}, {"$count": "total"}]
    return next(database["works_misc"].aggregate(pipeline), {"total": 0}).get("total", 0)


def search_other_works(query_params: QueryParams, pipeline_params: dict | None = None) -> Tuple[Generator, int]:
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    other_works = database["works_misc"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline += [
        {"$count": "total_results"},  # type: ignore
    ]
    total_results = next(database["works_misc"].aggregate(count_pipeline), {"total_results": 0}).get("total_results", 0)
    return other_work_generator.get(other_works), total_results


def get_other_works_by_affiliation_pipeline(affiliation_id: str) -> list:
    return [
        {
            "$match": {
                "authors.affiliations.id": affiliation_id,
            },
        },
    ]
