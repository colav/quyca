from typing import Generator

from bson import ObjectId

from infrastructure.generators import work_generator
from domain.models.base_model import QueryParams
from infrastructure.repositories import base_repository, work_repository
from infrastructure.mongo import database


def get_works_by_affiliation_for_api_expert(
    affiliation_id: str,
    query_params: QueryParams,
    pipeline_params: dict | None = None,
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {
            "$match": {"authors.affiliations.id": affiliation_id},
        }
    ]
    return get_works_for_api_expert(pipeline, pipeline_params, query_params)


def get_works_by_person_for_api_expert(
    person_id: str, query_params: QueryParams, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [{"$match": {"authors.id": ObjectId(person_id)}}]
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
    pipeline += [
        {
            "$lookup": {
                "from": "person",
                "localField": "authors.id",
                "foreignField": "_id",
                "as": "authors_data",
                "pipeline": [
                    {
                        "$project": {
                            "id": "$_id",
                            "sex": 1,
                            "birthplace.country": 1,
                            "birthdate": 1,
                            "first_names": 1,
                            "last_names": 1,
                            "affiliations.id": 1,
                            "affiliations.start_date": 1,
                            "affiliations.end_date": 1,
                            "affiliations.name": 1,
                            "affiliations.types": 1,
                            "ranking": 1,
                            "external_ids": 1,
                        }
                    },
                ],
            }
        },
        {
            "$lookup": {
                "from": "sources",
                "localField": "source.id",
                "foreignField": "_id",
                "as": "source_data",
                "pipeline": [
                    {
                        "$project": {
                            "names": 1,
                            "id": "$_id",
                            "types": 1,
                            "external_ids": 1,
                            "updated": 1,
                        }
                    },
                ],
            }
        },
        {
            "$lookup": {
                "from": "affiliations",
                "localField": "authors.affiliations.id",
                "foreignField": "_id",
                "as": "affiliations_data",
                "pipeline": [{"$project": {"id": "$_id", "addresses": 1, "external_ids": 1}}],
            },
        },
    ]
    work_repository.set_product_filters(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    base_repository.set_pagination(pipeline, query_params)
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)
