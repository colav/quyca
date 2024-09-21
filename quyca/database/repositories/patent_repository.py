from typing import Optional, Generator, Tuple

from bson import ObjectId

from database.generators import patent_generator
from database.models.base_model import QueryParams
from database.models.patent_model import Patent
from database.repositories import base_repository
from database.mongo import database
from exceptions.not_entity_exception import NotEntityException


def get_patent_by_id(patent_id: str) -> Patent:
    patent = database["patents"].find_one(ObjectId(patent_id))
    if not patent:
        raise NotEntityException(f"The patent with id {patent_id} does not exist.")
    return Patent(**patent)


def get_patents_by_affiliation(
    affiliation_id: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {
            "$match": {
                "authors.affiliations.id": ObjectId(affiliation_id),
            },
        },
    ]
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    base_repository.set_pagination(pipeline, query_params)
    cursor = database["patents"].aggregate(pipeline)
    return patent_generator.get(cursor)


def get_patents_count_by_affiliation(affiliation_id: str) -> int:
    pipeline = get_patents_by_affiliation_pipeline(affiliation_id)
    pipeline += [{"$count": "total"}]
    patents_count = next(database["patents"].aggregate(pipeline), {"total": 0}).get("total", 0)
    return patents_count


def get_patents_by_person(person_id: str, query_params: QueryParams, pipeline_params: dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["patents"].aggregate(pipeline)
    return patent_generator.get(cursor)


def get_patents_count_by_person(person_id: str) -> Optional[int]:
    return (
        database["patents"]
        .aggregate([{"$match": {"authors.id": ObjectId(person_id)}}, {"$count": "total"}])
        .next()
        .get("total", 0)
    )


def search_patents(query_params: QueryParams, pipeline_params: dict | None = None) -> Tuple[Generator, int]:
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    patents = database["patents"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline += [
        {"$count": "total_results"},  # type: ignore
    ]
    total_results = next(database["patents"].aggregate(count_pipeline), {"total_results": 0}).get("total_results", 0)
    return patent_generator.get(patents), total_results


def get_patents_by_affiliation_pipeline(affiliation_id: str) -> list:
    return [
        {
            "$match": {
                "authors.affiliations.id": ObjectId(affiliation_id),
            },
        },
    ]
