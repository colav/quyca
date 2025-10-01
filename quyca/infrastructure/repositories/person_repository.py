from typing import Generator, Tuple
from bson import ObjectId

from quyca.infrastructure.generators import person_generator
from quyca.domain.models.base_model import QueryParams
from quyca.infrastructure.repositories import base_repository
from quyca.domain.exceptions.not_entity_exception import NotEntityException
from quyca.domain.models.person_model import Person
from quyca.infrastructure.mongo import database


def get_person_by_id(person_id: str, pipeline_params: dict = {}) -> Person:
    old_id = None
    try:
        old_id = ObjectId(person_id)
    except Exception:
        pass

    match_stage = {
        "$match": {
            "$or": [{"_id": person_id}] + ([{"_id_old": old_id}] if old_id else [])
        }
    }

    pipeline = [
        match_stage,
        {
            "$addFields": {
                "filtered_affiliations": {
                    "$filter": {
                        "input": "$affiliations",
                        "as": "affiliation",
                        "cond": {"$eq": ["$$affiliation.end_date", -1]},
                    }
                }
            }
        },
        {
            "$addFields": {
                "affiliations_data": {
                    "$map": {
                        "input": "$filtered_affiliations",
                        "as": "filtered_aff",
                        "in": {
                            "external_urls": {
                                "$filter": {
                                    "input": "$$filtered_aff.external_urls",
                                    "as": "external_url",
                                    "cond": {"$eq": ["$$external_url.source", "logo"]},
                                }
                            }
                        },
                    }
                }
            }
        },
    ]

    base_repository.set_project(pipeline, pipeline_params.get("project"))

    person_data = database["person"].aggregate(pipeline)
    person_data = next(person_data, None)
    if not person_data:
        raise NotEntityException(f"The person with id {person_id} does not exist.")
    return Person(**person_data)


def get_persons_by_affiliation(affiliation_id: str) -> Generator:
    pipeline = [
        {"$match": {"affiliations.id": affiliation_id}},
        {"$sort": {"products_count": -1}},
        {"$project": {"_id": 1, "full_name": 1}},
    ]
    cursor = database["person"].aggregate(pipeline)
    return person_generator.get(cursor)


def search_persons(query_params: QueryParams, pipeline_params: dict | None = None) -> Tuple[Generator, int]:
    if pipeline_params is None:
        pipeline_params = {}
    pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    pipeline += [
        {
            "$addFields": {
                "filtered_affiliations": {
                    "$filter": {
                        "input": "$affiliations",
                        "as": "affiliation",
                        "cond": {"$eq": ["$$affiliation.end_date", -1]},
                    }
                }
            }
        },
        {
            "$addFields": {
                "affiliations_data": {
                    "$map": {
                        "input": "$filtered_affiliations",
                        "as": "filtered_aff",
                        "in": {
                            "external_urls": {
                                "$filter": {
                                    "input": "$$filtered_aff.external_urls",
                                    "as": "external_url",
                                    "cond": {"$eq": ["$$external_url.source", "logo"]},
                                }
                            }
                        },
                    }
                }
            }
        },
    ]
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    persons = database["person"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline += [
        {"$count": "total_results"},
    ]
    total_results = next(database["person"].aggregate(count_pipeline), {"total_results": 0})["total_results"]
    return person_generator.get(persons), total_results
