from typing import Any, Generator
from bson import ObjectId

from quyca.infrastructure.generators import work_generator
from quyca.domain.models.base_model import QueryParams
from quyca.infrastructure.repositories import base_repository, work_repository
from quyca.infrastructure.mongo import database


def get_works_by_affiliation_for_api_expert(
    affiliation_id: str,
    query_params: QueryParams,
    affiliation_type: str,
    pipeline_params: dict | None = None,
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {
            "$match": {"authors.affiliations.id": affiliation_id, "authors.affiliations.types.type": affiliation_type},
        }
    ]
    return get_works_for_api_expert(pipeline, pipeline_params, query_params)


def get_works_by_person_for_api_expert(
    person_id: str, query_params: QueryParams, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [{"$match": {"authors.id": person_id}}]
    return get_works_for_api_expert(pipeline, pipeline_params, query_params)


def get_works_by_source_for_api_expert(
    source_id: str, query_params: QueryParams, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [{"$match": {"source.id": ObjectId(source_id)}}]
    return get_works_for_api_expert(pipeline, pipeline_params, query_params)


def search_works_for_api_expert(query_params: QueryParams, pipeline_params: dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    return get_works_for_api_expert(pipeline, pipeline_params, query_params)


def get_works_for_api_expert(pipeline: list, pipeline_params: dict, query_params: QueryParams) -> Generator:
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)

    if query_params.page and query_params.limit:
        base_repository.set_pagination(pipeline, query_params)

    work_repository.set_product_filters(pipeline, query_params)
    pipeline += [
        {
            "$project": {
                "_id": 1,
                "titles": 1,
                "year_published": 1,
                "doi": 1,
                "authors": {
                    "id": 1,
                    "full_name": 1,
                    "sex": 1,
                    "first_names": 1,
                    "last_names": 1,
                    "external_ids": 1,
                    "ranking": 1,
                    "affiliations": 1,
                },
                "source": {
                    "id": 1,
                    "name": 1,
                    "types": 1,
                    "external_ids": 1,
                    "updated": 1,
                },
            },
        },
    ]
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def count_works_for_api_expert(query_params: QueryParams) -> int:
    return count_works(query_params)


def count_works_by_person_for_api_expert(person_id: str, query_params: QueryParams) -> int:
    base_pipeline = [{"$match": {"authors.id": person_id}}]
    return count_works(query_params, base_pipeline)


def count_works_by_source_for_api_expert(source_id: str, query_params: QueryParams) -> int:
    base_pipeline = [{"$match": {"source.id": ObjectId(source_id)}}]
    return count_works(query_params, base_pipeline)


def count_works_by_affiliation_for_api_expert(
    affiliation_id: str, query_params: QueryParams, affiliation_type: str
) -> int:
    base_pipeline = [
        {"$match": {"authors.affiliations.id": affiliation_id, "authors.affiliations.types.type": affiliation_type}}
    ]
    return count_works(query_params, base_pipeline)


def count_works(query_params: QueryParams, base_pipeline: list[dict[str, Any]] | None = None) -> int:
    base_pipeline = base_pipeline or []
    query_dict = query_params.model_dump(exclude_none=True)
    base_params = {"page", "limit", "sort"}
    is_full_scan = set(query_dict.keys()).issubset(base_params)

    if is_full_scan and not base_pipeline:
        return database["works"].estimated_document_count()

    count_pipeline: list[dict[str, Any]] = list(base_pipeline)

    if query_params.keywords:
        count_pipeline.append({"$match": {"$text": {"$search": query_params.keywords}}})

    work_repository.set_product_filters(count_pipeline, query_params)

    count_pipeline.append({"$count": "total_count"})

    result = next(database["works"].aggregate(count_pipeline), {"total_count": 0})
    return result.get("total_count", 0)
