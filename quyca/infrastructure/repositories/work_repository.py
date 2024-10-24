from typing import Generator, Tuple

from bson import ObjectId

from infrastructure.generators import work_generator
from domain.models.base_model import QueryParams
from domain.models.work_model import Work
from infrastructure.repositories import base_repository
from infrastructure.mongo import database
from domain.exceptions.not_entity_exception import NotEntityException


def get_work_by_id(work_id: str) -> Work:
    work = database["works"].find_one(ObjectId(work_id))
    if not work:
        raise NotEntityException(f"The work with id {work_id} does not exist.")
    return Work(**work)


def get_works_by_affiliation(
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
    set_product_type_filters(pipeline, query_params.product_type)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_by_affiliation_for_api_expert(
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
        {
            "$lookup": {
                "from": "person",
                "localField": "authors.id",
                "foreignField": "_id",
                "as": "authors",
                "pipeline": [
                    {
                        "$project": {
                            "id": "$_id",
                            "sex": 1,
                            "first_names": 1,
                            "last_names": 1,
                            "full_name": 1,
                            "affiliations": 1,
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
                "as": "sources",
                "pipeline": [
                    {
                        "$project": {
                            "names": 1,
                            "id": "$_id",
                            "types": 1,
                            "issn_l": 1,
                            "isbn": 1,
                            "is_in_doaj": 1,
                            "host_organization_name": 1,
                        }
                    },
                ],
            }
        },
        {"$set": {"source": {"$arrayElemAt": ["$sources", 0]}}},
    ]
    set_product_type_filters(pipeline, query_params.product_type)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_available_filters_by_affiliation(affiliation_id: str, query_params: QueryParams) -> dict:
    pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
    ]
    return get_works_available_filters(pipeline, query_params)


def get_works_count_by_affiliation(affiliation_id: str, query_params: QueryParams) -> int:
    pipeline = [
        {
            "$match": {
                "authors.affiliations.id": ObjectId(affiliation_id),
            },
        },
    ]
    set_product_type_filters(pipeline, query_params.product_type)
    pipeline += [{"$count": "total"}]  # type: ignore
    return next(database["works"].aggregate(pipeline), {"total": 0}).get("total", 0)


def get_works_by_person(person_id: str, query_params: QueryParams, pipeline_params: dict | None = None) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    set_product_type_filters(pipeline, query_params.product_type)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_by_person_for_api_expert(
    person_id: str, query_params: QueryParams, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
        {
            "$lookup": {
                "from": "person",
                "localField": "authors.id",
                "foreignField": "_id",
                "as": "authors",
                "pipeline": [
                    {
                        "$project": {
                            "id": "$_id",
                            "sex": 1,
                            "first_names": 1,
                            "last_names": 1,
                            "full_name": 1,
                            "affiliations": 1,
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
                "as": "sources",
                "pipeline": [
                    {
                        "$project": {
                            "names": 1,
                            "id": "$_id",
                            "types": 1,
                            "issn_l": 1,
                            "isbn": 1,
                            "is_in_doaj": 1,
                            "host_organization_name": 1,
                        }
                    },
                ],
            }
        },
        {"$set": {"source": {"$arrayElemAt": ["$sources", 0]}}},
    ]
    set_product_type_filters(pipeline, query_params.product_type)
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    if sort := query_params.sort:
        base_repository.set_sort(sort, pipeline)
    base_repository.set_pagination(pipeline, query_params)
    base_repository.set_project(pipeline, pipeline_params.get("project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_available_filters_by_person(person_id: str, query_params: QueryParams) -> dict:
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    return get_works_available_filters(pipeline, query_params)


def get_works_count_by_person(person_id: str, query_params: QueryParams) -> int:
    pipeline = [{"$match": {"authors.id": ObjectId(person_id)}}]
    set_product_type_filters(pipeline, query_params.product_type)
    pipeline += [{"$count": "total"}]  # type: ignore
    return next(database["works"].aggregate(pipeline), {"total": 0}).get("total", 0)


def search_works(query_params: QueryParams, pipeline_params: dict | None = None) -> Tuple[Generator, int]:
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    set_product_type_filters(pipeline, query_params.product_type)
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    works = database["works"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    set_product_type_filters(count_pipeline, query_params.product_type)
    count_pipeline += [
        {"$count": "total_results"},  # type: ignore
    ]
    total_results = next(database["works"].aggregate(count_pipeline), {"total_results": 0}).get("total_results", 0)
    return work_generator.get(works), total_results


def get_works_available_filters(pipeline: list, query_params: QueryParams) -> dict:
    set_product_type_filters(pipeline, query_params.product_type)
    available_filters: dict = {}
    product_types_pipeline = pipeline.copy() + [
        {"$unwind": "$types"},
        {"$group": {"_id": "$types.source", "types": {"$addToSet": "$types"}}},
    ]
    product_types = database["works"].aggregate(product_types_pipeline)
    available_filters["product_types"] = list(product_types)
    return available_filters


def get_search_works_available_filters(query_params: QueryParams, pipeline_params: dict | None = None) -> dict:
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    return get_works_available_filters(pipeline, query_params)


def get_works_with_source_by_affiliation(
    affiliation_id: str, query_params: QueryParams, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    source_project = pipeline_params.get("source_project", [])
    pipeline = [
        {"$match": {"authors.affiliations.id": ObjectId(affiliation_id)}},
    ]
    set_product_type_filters(pipeline, query_params.product_type)
    pipeline += [
        {
            "$lookup": {
                "from": "sources",  # type: ignore
                "localField": "source.id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "source",  # type: ignore
                "pipeline": [{"$project": {"_id": 1, **{p: 1 for p in source_project}}}],  # type: ignore
            }
        },
        {"$unwind": "$source"},  # type: ignore
    ]
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    base_repository.set_project(pipeline, pipeline_params.get("work_project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def get_works_with_source_by_person(
    person_id: str, query_params: QueryParams, pipeline_params: dict | None = None
) -> Generator:
    if pipeline_params is None:
        pipeline_params = {}
    source_project = pipeline_params.get("source_project", [])
    pipeline = [
        {"$match": {"authors.id": ObjectId(person_id)}},
    ]
    set_product_type_filters(pipeline, query_params.product_type)
    pipeline += [
        {
            "$lookup": {
                "from": "sources",  # type: ignore
                "localField": "source.id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "source",  # type: ignore
                "pipeline": [{"$project": {"_id": 1, **{p: 1 for p in source_project}}}],  # type: ignore
            }
        },
        {"$unwind": "$source"},  # type: ignore
    ]
    base_repository.set_match(pipeline, pipeline_params.get("match"))
    base_repository.set_project(pipeline, pipeline_params.get("work_project"))
    cursor = database["works"].aggregate(pipeline)
    return work_generator.get(cursor)


def set_product_type_filters(pipeline: list, type_filters: str | None) -> None:
    if not type_filters:
        return
    match_filters = []
    for type_filter in type_filters.split(","):
        params = type_filter.split("_")
        if len(params) == 1:
            match_filters.append({"types": {"$elemMatch": {"source": params[0]}}})
        elif len(params) == 2:
            match_filters.append({"types": {"$elemMatch": {"source": params[0], "type": params[1]}}})
        elif len(params) == 3 and params[0] == "scienti":
            match_filters.append(
                {"types": {"$elemMatch": {"source": params[0], "type": params[1], "code": {"$regex": "^" + params[2]}}}}  # type: ignore
            )
    pipeline += [{"$match": {"$or": match_filters}}]
