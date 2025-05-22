from typing import Generator, Tuple


from infrastructure.generators import person_generator
from domain.models.base_model import QueryParams
from infrastructure.repositories import base_repository
from domain.exceptions.not_entity_exception import NotEntityException
from domain.models.person_model import Person
from infrastructure.mongo import database


def get_person_by_id(person_id: str) -> Person:
    person_data = database["person"].aggregate(
        [
            {"$match": {"_id": person_id}},
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
                "$lookup": {
                    "from": "affiliations",
                    "localField": "filtered_affiliations.id",
                    "foreignField": "_id",
                    "as": "affiliations_data",
                    "pipeline": [
                        {"$match": {"external_urls.source": "logo"}},
                        {"$project": {"_id": 0, "external_urls": 1}},
                    ],
                }
            },
        ]
    )
    person_data = next(person_data, None)
    if not person_data:
        raise NotEntityException(f"The person with id {person_id} does not exist.")
    return Person(**person_data)


def get_persons_by_affiliation(affiliation_id: str) -> list:
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
            "$lookup": {
                "from": "affiliations",  # type: ignore
                "localField": "filtered_affiliations.id",  # type: ignore
                "foreignField": "_id",  # type: ignore
                "as": "affiliations_data",  # type: ignore
                "pipeline": [  # type: ignore
                    {"$match": {"external_urls.source": "logo"}},
                    {"$project": {"_id": 0, "external_urls": 1}},
                ],
            }
        },
    ]
    base_repository.set_search_end_stages(pipeline, query_params, pipeline_params)
    persons = database["person"].aggregate(pipeline)
    count_pipeline = [{"$match": {"$text": {"$search": query_params.keywords}}}] if query_params.keywords else []
    count_pipeline += [
        {"$count": "total_results"},  # type: ignore
    ]
    total_results = next(database["person"].aggregate(count_pipeline), {"total_results": 0})["total_results"]
    return person_generator.get(persons), total_results
